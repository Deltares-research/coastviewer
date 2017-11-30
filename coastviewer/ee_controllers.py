import flask
import flask_cors
import ee
# import pycpt

ee_pages = flask.Blueprint(
    'ee_pages',
    __name__,
    template_folder='templates'
)

ee.Initialize()

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
    palette = [
        "08306b",
        "08519c",
        "2171b5",
        "4292c6",
        "6baed6",
        "9ecae1",
        "c6dbef",
        "deebf7",
        "f7fbff"
    ]
    map = bathymetry.getMapId({
        "min":-20,
        "max":5,
        'palette': ",".join(palette)
    })

    info = {
        'mapid': map['mapid'],
        'token': map['token']
    }
    return flask.jsonify(info)
