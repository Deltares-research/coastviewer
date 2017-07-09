import itertools

import netCDF4
import pandas
import numpy as np

import utils

DATASETS = {
    'transect': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/jarkus/profiles/transect.nc',  # nopep8
    'BKL_TKL_TND': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/BKL_TKL_MKL/BKL_TKL_TND.nc',  # nopep8
    'DF': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/DuneFoot/DF.nc',  # nopep8
    'mkl': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/BKL_TKL_MKL/MKL.nc',  # nopep8
    'strandbreedte': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/strandbreedte/strandbreedte.nc',  # nopep8
    'strandlijnen': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/MHW_MLW/MHW_MLW.nc',  # nopep8
    'suppleties': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/suppleties/suppleties.nc',  # nopep8
    'faalkans': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/faalkans_PC-Ring/faalkans.nc'  # nopep8
}

# global variables
with netCDF4.Dataset(DATASETS['transect']) as ds:
    # keep these global, for faster indexing
    ids = ds.variables['id'][:]


def overview():
    """generate a lod overview"""
    # read relevant variables
    with netCDF4.Dataset(DATASETS['transect']) as ds:
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
    df = pandas.DataFrame(data=data)
    df['north'] = df['rsp_lat'] + 0.002
    df['south'] = df['rsp_lat'] - 0.002
    df['east'] = df['rsp_lon'] + .0025
    df['west'] = df['rsp_lon'] - .0025

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


def get_transect(id_):
    """lookup information for transect"""

    transect_idx = np.searchsorted(ids, id_)
    variables = {
        'lat': {"var": 'lat', "slice": np.s_[transect_idx, :]},
        'lon': {"var": 'lon', "slice": np.s_[transect_idx, :]},
        'z': {"var": 'altitude', "slice": np.s_[:, transect_idx, :]},
        "t": {"var": 'time', "slice": np.s_[:]}

    }
    data = {}
    with netCDF4.Dataset(DATASETS['transect']) as ds:
        for var, props in variables.items():
            data[var] = ds.variables[props['var']][props['slice']]
        time_units = ds.variables['time'].units

    # df = pandas.DataFrame(data=data)
    years = []
    for t, row in zip(data['t'], data['z']):
        item = {}
        coords = pandas.DataFrame(data=dict(
            lon=data['lon'],
            lat=data['lat'],
            z=row
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
    years = pandas.DataFrame.from_records(years)
    transect = {
        "years": years,
        "id": id_
    }
    return transect
