import itertools
import logging
import pathlib
import urllib.parse

import netCDF4
import pandas as pd
import numpy as np
import pyproj
import matplotlib.cm
import scipy.interpolate

from . import utils

logger = logging.getLogger(__name__)

# allow to use a local dataset


DATASETS = {
    'transect': {
        'origin': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/jarkus/profiles/transect.nc' # noqa E501
    },
    'BKL_TKL_TND': {
        'origin': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/BKL_TKL_MKL/BKL_TKL_TND.nc' # noqa E501
    },
    'DF': {
        'origin': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/DuneFoot/DF.nc' # noqa E501
    },
    'MKL': {
        'origin': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/BKL_TKL_MKL/MKL.nc' # noqa E501
    },
    'strandbreedte': {
        'origin': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/strandbreedte/strandbreedte.nc' # noqa E501
    },
    'MHW_MLW': {
        'origin': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/MHW_MLW/MHW_MLW.nc' # noqa E501
    },
    'nourishments': {
        'origin': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/suppleties/nourishments.nc' # noqa E501
    },
    'faalkans': {
        'origin': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/faalkans/faalkans.nc', # noqa E501
    }
}


dataset_source = 'url'
data_dir = pathlib.Path('.')
if pathlib.Path('/data/transect.nc').exists():
    dataset_source = "root"
    data_dir = pathlib.Path('/data')
elif pathlib.Path('data/transect.nc').exists():
    dataset_source = 'local'
    data_dir = pathlib.Path('data')

logger.info('using %s source', dataset_source)
for dataset in DATASETS.values():
    # parse the url
    parsed = urllib.parse.urlparse(dataset['origin'])
    # extract the filename
    parsed_name = pathlib.Path(parsed.path).name
    if dataset_source == 'url':
        dataset['url'] = dataset['origin']
    elif dataset_source in {'root', 'local'}:
        # concat directory and convert to string
        dataset['url'] = str(data_dir / parsed_name)
    else:
        raise ValueError("unexpected dataset_source {}".format(dataset_source))


# global variables
with netCDF4.Dataset(DATASETS['transect']['url']) as ds:
    # keep these global, for faster indexing
    ids = ds.variables['id'][:]


def overview():
    """generate a lod overview"""
    # read relevant variables
    with netCDF4.Dataset(DATASETS['transect']['url']) as ds:
        variables = {
            'id': {"var": 'id', "slice": np.s_[:]},
            'lat_0': {"var": 'lat', "slice": np.s_[:, 0]},
            'lat_1': {"var": 'lat', "slice": np.s_[:, -1]},
            'lon_0': {"var": 'lon', "slice": np.s_[:, 0]},
            'lon_1': {"var": 'lon', "slice": np.s_[:, -1]},
            'rsp_lon': {"var": 'rsp_lon', "slice": np.s_[:]},
            'rsp_lat': {"var": 'rsp_lat', "slice": np.s_[:]}
        }
        data = {}
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
    # put in a table
    df = pd.DataFrame(data=data)
    delta = 0.002
    df['north'] = df['rsp_lat'] + delta
    df['south'] = df['rsp_lat'] - delta
    df['east'] = df['rsp_lon'] + delta
    df['west'] = df['rsp_lon'] - delta

    # transform for kml file
    def line_coords(record):
        return utils.textcoordinates(
            x0=record.lon_0,
            y0=record.lat_0,
            x1=record.lon_1,
            y1=record.lat_1
        )
    df['line_coords'] = df.apply(line_coords, axis=1)

    def point_coords(record):
        return utils.textcoordinates(
            x0=record.rsp_lat,
            y0=record.rsp_lon
        )
    df['point_coords'] = df.apply(point_coords, axis=1)

    def bbox(record):
        return {
            'north': record.north,
            'south': record.south,
            'east': record.east,
            'west': record.west
        }
    df['bbox'] = df.apply(bbox, axis=1)

    n_pixels = itertools.islice(
        itertools.cycle([64, 32, 64, 16, 64, 32, 64, 8]),
        len(df)
    )
    df['min_lod_pixels'] = list(n_pixels)
    return df


def move_by(lon, lat, distance):
    """
    Move the x,y coordinates by distance, perpendicular, assuming that they
    are lat,lon and that we can move in EPSG:28992
    >>> lon = array([4.0])
    >>> lat = array([51.0])
    >>> x,y = move_by(lat, lon, 1000)
    >>> x, y  # doctest:+ELLIPSIS
    (array([ 3.999...]), array([ 51.0089...]))
    """
    # project from wgs84 to rd, assuming x,y are lon, lat
    # compute the angle from the transect coordinates
    rd = pyproj.Proj('+init=epsg:28992')

    x, y = rd(lon, lat)

    dx = x[-1] - x[0]
    dy = y[-1] - y[0]

    # rotate by 90 degrees
    angle = np.arctan2(dy, dx) + np.pi * 0.5

    x += distance * np.cos(angle)
    y += distance * np.sin(angle)

    lon, lat = rd(x, y, inverse=True)

    return lon, lat


def get_transect(id_, exaggeration=1.0, lift=0.0, move=0.0):
    """lookup information for transect"""

    transect_idx = np.searchsorted(ids, id_)
    variables = {
        'lat': {"var": 'lat', "slice": np.s_[transect_idx, :]},
        'lon': {"var": 'lon', "slice": np.s_[transect_idx, :]},
        'z': {"var": 'altitude', "slice": np.s_[:, transect_idx, :]},
        "t": {"var": 'time', "slice": np.s_[:]},
        'id': {"var": 'id', "slice": np.s_[transect_idx]}
    }
    data = {}
    with netCDF4.Dataset(DATASETS['transect']['url']) as ds:
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
        time_units = ds.variables['time'].units

    # df = pandas.DataFrame(data=data)
    years = []
    for i, (t, row) in enumerate(zip(data['t'], data['z'])):
        item = {}

        lon, lat = move_by(data['lon'], data['lat'], distance=i*move)
        coords = pd.DataFrame(data=dict(
            lon=lon,
            lat=lat,
            z=row * exaggeration + lift
        ))
        item['coordinates'] = coords.dropna()
        item['line_coordinates'] = utils.textcoordinates(
            x0=item['coordinates']['lon'],
            y0=item['coordinates']['lat'],
            z0=item['coordinates']['z']
        )
        date = netCDF4.num2date(t, time_units)
        item['properties'] = {
            "t": date,
        }
        item['properties']['year'] = date.year
        item['properties']['begin_date'] = date
        item['properties']['end_date'] = date.replace(year=date.year+1)
        years.append(item)
    years = pd.DataFrame.from_records(years)
    transect = {
        "years": years,
        "id": data['id']
    }
    return transect


def get_transect_data(id_=7003900):
    transect_idx = np.searchsorted(ids, id_)
    variables = {
        'id': {"var": 'id', "slice": np.s_[transect_idx]},
        'lat': {"var": 'lat', "slice": np.s_[transect_idx, :]},
        'lon': {"var": 'lon', "slice": np.s_[transect_idx, :]},
        'z': {"var": 'altitude', "slice": np.s_[:, transect_idx, :]},
        't': {"var": 'time', "slice": np.s_[:]},
        'cross_shore': {"var": "cross_shore", "slice": np.s_[:]},
        'alongshore': {"var": "alongshore", "slice": np.s_[transect_idx]},
        'mean_high_water': {
            "var": 'mean_high_water',
            "slice": np.s_[transect_idx]
        },
        'mean_low_water': {
            "var": 'mean_low_water',
            "slice": np.s_[transect_idx]
        },
        'areacode': {"var": 'areacode', "slice": np.s_[transect_idx]},
        'areaname': {"var": 'areaname', "slice": np.s_[transect_idx]},
        'angle': {"var": 'angle', "slice": np.s_[transect_idx]},
        'rsp_x': {"var": 'rsp_x', "slice": np.s_[transect_idx]},
        'rsp_y': {"var": 'rsp_y', "slice": np.s_[transect_idx]},
        'rsp_lon': {"var": 'rsp_lon', "slice": np.s_[transect_idx]},
        'rsp_lat': {"var": 'rsp_lat', "slice": np.s_[transect_idx]},
    }
    data = {}
    with netCDF4.Dataset(DATASETS['transect']['url']) as ds:
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
        time_units = ds.variables['time'].units
    data['time'] = netCDF4.num2date(data['t'], time_units)
    data['filled_z'] = fill(data['z'])
    data['time_num'] = matplotlib.dates.date2num(data['time'])
    data['areaname'] = netCDF4.chartostring(data['areaname']).item().strip()
    return data


def fill(z):
    """fill z by space and then time"""

    def fill_space(z):
        """fill space"""
        # if we have no data...
        if z.mask.all():
            # nothing to interpolate, just return missings
            z_filled = np.ma.masked_all_like(z)
            return z_filled

        x = np.arange(z.shape[0])
        F = scipy.interpolate.interp1d(
            x[~z.mask],
            z[~z.mask],
            bounds_error=False
        )
        z_interp = F(x)
        z_filled = np.ma.masked_invalid(z_interp)
        return z_filled

    def fill_time(z):
        """fill time"""
        z_filled = np.ma.masked_all_like(z)
        for i in range(z.shape[1]):
            arr = z[:, i]
            # if there's no data, continue
            if arr.mask.all():
                continue
            # interpolate in time
            xp = np.arange(len(arr))
            z_filled[:, i] = scipy.interp(xp, xp[~arr.mask], arr[~arr.mask])
        return z_filled

    filled_z = np.ma.apply_along_axis(fill_space, 1, z)
    filled_z = fill_time(filled_z)
    return filled_z


def get_mean_water_df(id_=7003900):
    transect_idx = np.searchsorted(ids, id_)

    variables = {
        'mean_high_water_cross': {
            "var": 'mean_high_water_cross',
            "slice": np.s_[:, transect_idx]
        },
        'mean_low_water_cross': {
            "var": 'mean_low_water_cross',
            "slice": np.s_[:, transect_idx]
        },
        "t": {"var": 'time', "slice": np.s_[:]}
    }
    data = {}
    with netCDF4.Dataset(DATASETS['MHW_MLW']['url']) as ds:
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
        time_units = ds.variables['time'].units
    data['time'] = netCDF4.num2date(data['t'], time_units)

    shoreline_df = pd.DataFrame(data)
    return shoreline_df


def get_dune_foot_df(id_=7003900):
    transect_idx = np.searchsorted(ids, id_)

    variables = {
        'dune_foot_upperMKL_cross': {
            "var": 'dune_foot_upperMKL_cross',
            "slice": np.s_[:, transect_idx]
        },
        'dune_foot_threeNAP_cross': {
            "var": 'dune_foot_threeNAP_cross',
            "slice": np.s_[:, transect_idx]
        },
        "t": {"var": 'time', "slice": np.s_[:]}
    }
    data = {}
    with netCDF4.Dataset(DATASETS['DF']['url']) as ds:
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
        time_units = ds.variables['time'].units
    data['time'] = netCDF4.num2date(data['t'], time_units)

    shoreline_df = pd.DataFrame(data)
    return shoreline_df


def get_faalkans_df(id=7003900):
    transect_idx = np.searchsorted(ids, id)

    variables = {
        'probability_failure': {"var": 'probability_failure', "slice": np.s_[:, transect_idx]},
        "t": {"var": 'time', "slice": np.s_[:]}
    }
    data = {}
    with netCDF4.Dataset(DATASETS['faalkans']['url']) as ds:
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
        time_units = ds.variables['time'].units
    data['time'] = netCDF4.num2date(data['t'], time_units)

    faalkans_df = pd.DataFrame(data)
    return faalkans_df


def get_nourishment_grid_df(id_=7003900):
    transect_idx = np.searchsorted(ids, id_)
    variables = {
        'type': {"var": 'type', "slice": np.s_[:]},
        "volume": {"var": "volume", "slice": np.s_[transect_idx, :, :]},
        "time_num_start": {
            "var": "time_start",
            "slice": np.s_[transect_idx, :, :]
        },
        "time_num_end": {
            "var": "time_end",
            "slice": np.s_[transect_idx, :, :]
        },
        "t": {"var": 'time', "slice": np.s_[:]}
    }

    data = {}
    with netCDF4.Dataset(DATASETS['nourishments']['url']) as ds:
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
        time_units = ds.variables['time'].units
        time_start_units = ds.variables['time_start'].units
        # time_end had a bug
        time_end_units = ds.variables['time_start'].units

    # https://github.com/numpy/numpy/blob/master/doc/release/1.11.0-notes.rst#futurewarnings
    data["time_num_start"]._sharedmask = False
    data["time_num_start"][
        np.isnan(data["time_num_start"])
    ] = 0
    data["time_num_end"]._sharedmask = False
    data["time_num_end"][
        np.isnan(data["time_num_end"])
    ] = 0
    data["time_start"] = netCDF4.num2date(
        data["time_num_start"],
        time_start_units
    )
    data["time_end"] = netCDF4.num2date(data["time_num_end"], time_end_units)
    data['time'] = netCDF4.num2date(data['t'], time_units)

    short_description = {
        1: "beach",
        2: "shoreface",
        3: "dune",
        4: "other"
    }

    cols_vol = ['volume_'+ityp for ityp in list(short_description.values())]
    cols_tstart = [
        'time_start_'+ityp
        for ityp
        in list(short_description.values())
    ]
    cols_tend = ['time_end_'+ityp for ityp in list(short_description.values())]
    del data["type"]
    nourishment_grid_df = pd.DataFrame(
        np.c_[
            np.array(data['volume']),
            np.array(data['time_start']),
            np.array(data['time_end']),
            np.array(data['time'])
        ],
        columns=np.r_[
            cols_vol,
            cols_tstart,
            cols_tend,
            ['time']
        ]
    )
    # make it a pandas timestamp
    nourishment_grid_df['time'] = nourishment_grid_df['time'].apply(
        lambda x: pd.Timestamp(x)
    )

    nourishment_grid_df = nourishment_grid_df.loc[
        (
            nourishment_grid_df[
                [
                    'volume_beach',
                    'volume_shoreface',
                    'volume_dune',
                    'volume_other'
                ]
            ] !=0
        ).any(axis=1)
    ]

    return nourishment_grid_df


def get_nourishment_df(id_=7003900):
    """get nourishment information"""

    # TODO: this might not work as expected, what will happen if id_ is not in ids
    # TODO: where is transect_idx used???
    transect_idx = np.searchsorted(
        ids,
        id_
    )
    # TODO: I think this queries the whole dataset
    variables = {
        'n_code': {"var": 'n_code', "slice": np.s_[:]},
        "date": {"var": "date", "slice": np.s_[:]},
        "stretch": {"var": "stretch", "slice": np.s_[:]},
        "kustvak": {"var": "kustvak", "slice": np.s_[:]},
        "location": {"var": "location", "slice": np.s_[:]},
        "type_flag": {"var": "type_flag", "slice": np.s_[:]},
        "authorizing_department": {
            "var": "authorizing_department",
            "slice": np.s_[:]
        },
        "purpose": {"var": "purpose", "slice": np.s_[:]},
        "coastal_defense": {"var": "coastal_defense", "slice": np.s_[:]},
        "vol": {"var": "vol", "slice": np.s_[:]},
        "vol_per_metre": {"var": "vol_per_metre", "slice": np.s_[:]}
    }

    data = {}
    with netCDF4.Dataset(DATASETS['nourishments']['url']) as ds:
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
        date_units = ds.variables["date"].units
    for key, val in data.items():
        if val.dtype.kind in {'U', 'S'}:
            data[key] = netCDF4.chartostring(val)
    # split into 2 columns
    data["date_start"] = netCDF4.num2date(data["date"][:, 0], date_units)
    data["date_end"] = netCDF4.num2date(data["date"][:, 1], date_units)
    del data["date"]
    data["stretch_start"] = data["stretch"][:, 0]
    data["stretch_end"] = data["stretch"][:, 1]
    del data["stretch"]

    data['type_flag']
    long_description = {
        1: "strandsuppletie, strandsuppletie banket, strandsuppletie+vooroever, banket, strand (zwakke sch.), strand-duinsuppletie, strandsuppletie+duinverzwaring",
        2: "onderwatersuppletie, vooroever, vooroeversuppletie, geulwand, geulwandsuppletie",
        3: "duin, duinverzwaring, landwaartse duinverzwaring, zeewaartse duinverzwaring, dijkverzwaring, duinverzwaring en strandsuppletie, zeewaartse duinverzwaring en strandsuppletie",
        4: "other"
    }
    short_description = {
        1: "beach",
        2: "shoreface",
        3: "dune",
        4: "other"
    }
    data['type'] = np.fromiter(
        (
            short_description[x]
            for x
            in data["type_flag"]
        ),
        dtype='S10'
    )
    nourishment_df = pd.DataFrame(data=data)
    return nourishment_df


def get_mkl_df(id_=7003900):
    """read the mkl dataset"""

    transect_idx = np.searchsorted(ids, id_)
    variables = {
        'momentary_coastline': {"var": 'momentary_coastline', "slice": np.s_[:, transect_idx]},
        'time_num': {"var": 'time', "slice": np.s_[:]},
        'time_MKL_num': {"var": 'time_MKL', "slice": np.s_[:, transect_idx]},
        'high_boundary_MKL': {"var": 'high_boundary_MKL', "slice": np.s_[:, transect_idx]},
        'low_boundary_MKL': {"var": 'low_boundary_MKL', "slice": np.s_[:, transect_idx]},
        'seaward_boundary_MKL': {"var": 'seaward_boundary_MKL', "slice": np.s_[:, transect_idx]},
        'landward_boundary_MKL': {"var": 'landward_boundary_MKL', "slice": np.s_[:, transect_idx]},
        'volume_MKL': {"var": 'volume_MKL', "slice": np.s_[:, transect_idx]}
    }
    data = {}
    with netCDF4.Dataset(DATASETS['MKL']['url']) as ds:
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
        date_units = ds.variables["time_MKL"].units

    data['time'] = netCDF4.num2date(data['time_num'], date_units)

    mkl_df = pd.DataFrame(data)
    mkl_df = mkl_df[mkl_df['momentary_coastline'].notna()]
    if len(mkl_df):
        mkl_df['time_MKL'] = netCDF4.num2date(
            mkl_df['time_MKL_num'].values,
            date_units
        )
    else:
        mkl_df['time_MKL'] = []
    return mkl_df


def get_bkltkltnd_df(id_=7003900):

    transect_idx = np.searchsorted(ids, id_)
    variables = {
        'basal_coastline': {"var": 'basal_coastline', "slice": np.s_[:, transect_idx]},
        'time_num': {"var": 'time', "slice": np.s_[:]},
        'testing_coastline': {"var": 'testing_coastline', "slice": np.s_[:, transect_idx]},
        'trend': {"var": 'trend', "slice": np.s_[transect_idx]}
    }
    data = {}
    with netCDF4.Dataset(DATASETS['BKL_TKL_TND']['url']) as ds:
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
        date_units = ds.variables["time"].units

    data['time'] = netCDF4.num2date(data['time_num'], date_units)

    bkltkltnd_df = pd.DataFrame(data)
    #bkltkltnd_df = bkltkltnd_df.dropna()
    return bkltkltnd_df
