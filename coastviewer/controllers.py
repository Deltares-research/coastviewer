import logging
import datetime
import io
import json

import flask
import pandas as pd
import numpy as np
import matplotlib.cm
import matplotlib.colors

from . import datasets
from . import utils
from . import plots

logger = logging.getLogger(__name__)

MIMES = {
    'png': 'image/png',
    'svg': 'image/svg+xml',
    'pdf': 'application/pdf',
    'csv': 'text/csv',
    'json': 'application/json',
    'xls': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

def index(api: object) -> str:
    # can't name this index (already taken by conexxion)
    return flask.render_template("main.html", api=api)


def transect(id: int) -> object:
    logger.info(flask.request)
    return {}


def transect_overview() -> list:
    logger.info(flask.request)
    return []


def transect_overview_kml() -> str:
    """create an overview of all transects"""
    lines = datasets.overview()
    return flask.render_template('lod.kml', lines=lines)


def transect_kml(
        id: int,
        extrude: bool,
        exaggeration: float,
        lift: float,
        move: float
) -> str:
    """create a kml for a specific transect"""
    # only available on runtime
    flask.current_app.jinja_env.filters['kmldate'] = utils.kmldate
    transect = datasets.get_transect(int(id), exaggeration, lift, move)
    return flask.render_template("transect.kml", transect=transect, extrude=int(extrude))


def transect_info(id: int) -> str:
    transect = datasets.get_transect_data(int(id))
    transect_df = pd.Series(data=transect).to_frame('transect')
    point = 'geojson(%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{lon}%2C{lat}%5D%7D)'.format(
        lon=transect['rsp_lon'],
        lat=transect['rsp_lat']
    )
    static_url = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lon},{lat},13.25,{angle},60/600x300?access_token=pk.eyJ1Ijoic2lnZ3lmIiwiYSI6ImNqNmFzMTN5YjEyYzYzMXMyc2JtcTdpdDQifQ.Cxyyltmdyy1K_lvPY2MTrQ'.format(
        lon=transect['rsp_lon'],
        lat=transect['rsp_lat'],
        angle=np.mod(transect['angle'] + 90, 360)
    )
    return flask.render_template("info.html", transect=transect_df, static_url=static_url, dir=dir, **transect)


def transect_placemark(id: int) -> str:
    transect = datasets.get_transect_data(int(id))
    transect_df = pd.Series(data=transect).to_frame('transect')
    transect_df['id'] = id
    return flask.render_template("placemark.html", transect=transect_df, id=id)


def timestack(id: int) -> str:
    data = datasets.get_transect_data(int(id))
    fig, ax = plots.timestack(data)
    stream = io.BytesIO()
    fig.savefig(stream,bbox_inches='tight',dpi=300)
    return stream.getvalue()


def eeg(id: int, format: str='') -> str:
    """export eeg plot or data"""
    stream = io.BytesIO()

    plot = True
    as_attachment = False

    if format in ('csv', 'json', 'xls'):
        plot = False

    if format:
        as_attachment = True

    data = datasets.get_transect_data(int(id))

    # if we only need data
    if not plot:
        # flatten data
        records = []
        for t, row in zip(data['time'], data['filled_z']):
            for x, col in zip(data['cross_shore'], row):
                record = {
                    "z": col.item(),
                    "t": t,
                    "x": x
                }
                records.append(record)

        df = pd.DataFrame.from_records(records)
        if format == 'json':
            stream = io.StringIO()
            df.to_json(stream, orient='records')
        if format == 'csv':
            stream = io.StringIO()
            df.to_csv(stream)
        if format == 'xls':
            writer = pd.ExcelWriter(stream, engine='openpyxl')
            data.to_xls(writer)
            writer.save()
    else:
        # we need the plot
        fig, ax = plots.eeg(data)
        dpi = 72
        if format in ('pdf', 'png', 'svg'):
            dpi = 300
            fig.savefig(stream, bbox_inches='tight', dpi=dpi, format=format)
        else:
            fig.savefig(stream, bbox_inches='tight', dpi=dpi, format='png')
    mimetype = MIMES.get(format, 'application/png')
    headers = {}
    stream.seek(0)
    if as_attachment:
        filename = 'eeg.{}'.format(format)
        # this is the way to send a filename
        headers = {"Content-Disposition": "attachment;filename={}".format(filename)}
    response = flask.Response(
        stream,
        mimetype=mimetype,
        headers=headers
    )
    return response


def indicators(id: int) -> str:
    data = datasets.get_transect_data(int(id))
    data_mkl = datasets.get_mkl_df(int(id))
    data_bkltkltnd = datasets.get_bkltkltnd_df(int(id))
    data_mean_water = datasets.get_mean_water_df(int(id))
    data_dune_foot = datasets.get_dune_foot_df(int(id))
    data_nourishment_grid = datasets.get_nourishment_grid_df(int(id))
    fig, ax = plots.indicators(transect=data,mkl=data_mkl,bkltkltnd=data_bkltkltnd,mean_water=data_mean_water,dune_foot=data_dune_foot,nourishment=data_nourishment_grid)
    stream = io.BytesIO()
    fig.savefig(stream,bbox_inches='tight',dpi=300)
    return stream.getvalue()


def styles(poly_alpha: float, outline: int, colormap: str) -> str:
    """return style information"""

    context = {}

    poly_alpha = int(float(poly_alpha) * 255)
    context['poly_alpha'] = '{:02X}'.format(poly_alpha)
    context['outline'] = int(outline)

    # Get a colormap based on the ?colormap parameter
    colormap_name = colormap
    colormap = matplotlib.cm.cmap_d.get(colormap_name, matplotlib.cm.viridis)
    colors = {}
    current_year = datetime.datetime.now().year
    N = matplotlib.colors.Normalize(1964, current_year + 1)
    for year in range(1964, current_year + 1):
        # call with float 0..1 (or int 0 .. 255)
        r, g, b, alpha = colormap(N(year))
        # r and b reversed in the google, don't forget to add alpha
        color = matplotlib.colors.rgb2hex((b, g, r)).replace('#', '')
        colors['year{0}'.format(year)] = color
    context['colors'] = colors
    return flask.render_template("styles.kml", context=context)
