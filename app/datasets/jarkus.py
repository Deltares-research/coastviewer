import netCDF4

DATASETS = {
    'transect': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/jarkus/profiles/transect.nc',
    'BKL_TKL_TND': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/BKL_TKL_MKL/BKL_TKL_TND.nc',
    'DF': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/DuneFoot/DF.nc',
    'MKL': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/BKL_TKL_MKL/MKL.nc',
    'strandbreedte': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/strandbreedte/strandbreedte.nc',
    'strandlijnen': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/MHW_MLW/MHW_MLW.nc',
    'suppleties': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/suppleties/suppleties.nc',
    'faalkans': 'http://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/faalkans_PC-Ring/faalkans.nc',
}


def kml_overview():
    with netCDF4.Dataset(DATASETS['transect']) as ds:
        id = ds.variables['id'][:]
        lon0 = ds.variables['lon'][:, 0]
        lat0 = ds.variables['lat'][:, 1]
        lon1 = ds.variables['lon'][:, -1]
        lat1 = ds.variables['lat'][:, -1]
        rsp_lon = ds.variables['rsp_lon'][:]
        rsp_lat = ds.variables['rsp_lat'][:]

    overview = {}
    overview['lon0'] = lon0
    overview['lon1'] = lon1
    overview['lat0'] = lat0
    overview['lat1'] = lat1

    # few
    overview['north'] = rsp_lat + 0.002
    overview['south'] = rsp_lat - 0.002

    # HACK: not circle safe...
    overview['east'] = rsp_lon + .0025
    overview['west'] = rsp_lon - .0025
    overview['id'] = id

    result = {}
    result['overview'] = overview
    lines = []
    # TODO: clean this up a bit...
    for (id,
         north,
         south,
         east,
         west,
         lat0,
         lat1,
         lon0,
         lon1) in zip(overview['id'],
                      overview['north'],
                      overview['south'],
                      overview['east'],
                      overview['west'],
                      overview['lat0'],
                      overview['lat1'],
                      overview['lon0'],
                      overview['lon1']):
        line = {}
        bbox = {
            'north': north,
            'south': south,
            'east': east,
            'west': west
            }
        coordinates = helpers.textcoordinates(x0=lon0, y0=lat0, x1=lon1, y1=lat1)
        line['coordinates'] = coordinates
        line['point_coordinates'] = helpers.textcoordinates(x0=lon0, y0=lat0)
        line['bbox'] = bbox
        line['id'] = id
        lines.append(line)
    result['lines'] = lines
    return result
