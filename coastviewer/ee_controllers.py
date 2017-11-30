import logging

import flask
import flask_cors
import ee
import ee.ee_exception

from . import palettes

logger = logging.getLogger(__name__)

ee_pages = flask.Blueprint(
    'ee_pages',
    __name__,
    template_folder='templates'
)

ee_available = True
try:
    ee.Initialize()
except ee.ee_exception.EEException:
    logger.exception("Couldn't authenticate. If you are running docker, make sure you authenticate using earthenginge authenticate or pass the GEE_AUTHORIZATION_CODE to the environment of the docker container.")


@ee_pages.route('/vaklodingen')
@flask_cors.cross_origin()
def vaklodingen():
    images = ee.ImageCollection('users/gena/vaklodingen').filterDate(
        '2007-01-01', '2015-01-01'
    )
    sorted_images = images.sort('system:time_start', False)
    bathymetry = sorted_images.reduce(
        ee.Reducer.firstNonNull()
    ).divide(1000)
    palette = palettes.pycpt2gee()
    map = bathymetry.getMapId({
        "min": -5,
        "max": 2,
        'palette': palette
    })

    info = {
        'mapid': map['mapid'],
        'token': map['token']
    }
    return flask.jsonify(info)
