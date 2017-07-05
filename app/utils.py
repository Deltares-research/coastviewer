# by convention.
import io
import zipfile
import re

import numpy as np


def compress_kml(kml):
    """
    Returns compressed KMZ from the given KML string.

    >>> kml = "<kml>"
    >>> # returns a zip file containing a doc.xml
    >>> compress_kml(kml)[:2]
    'PK'
    """

    kmz = io.BytesIO()
    zf = zipfile.ZipFile(kmz, 'a', zipfile.ZIP_DEFLATED)
    # kmz file is a zip file that contains a doc.kml file
    zf.writestr('doc.kml', kml)
    zf.close()
    kmz.seek(0)
    return kmz.read()

def textcoordinates(x0, y0, z0=None, x1=None, y1=None, z1=None):
    """
    convert the coordinates to a string so they can be used by kml

    # Example usage:
    >>> x = np.array([1,1,1])
    >>> y = np.array([1,-2e10,3.0000001])
    >>> print(textcoordinates(x, y))
    1.0,1.0,0.0
    1.0,-20000000000.0,0.0
    1.0,3.0000001,0.0
    <BLANKLINE>
    >>> # Allow for coordinate pairs
    >>> x0 = x
    >>> y0 = y
    >>> x1 = x
    >>> y1 = y
    >>> print(textcoordinates(x0=x0, y0=y0, x1=x1, y1=y1))
    1.0,1.0,0.0 1.0,1.0,0.0
    1.0,-20000000000.0,0.0 1.0,-20000000000.0,0.0
    1.0,3.0000001,0.0 1.0,3.0000001,0.0
    <BLANKLINE>
    >>> x = np.array([1])
    >>> y = np.array([1])
    >>> z = np.array([np.nan])
    >>> print(textcoordinates(x, y, z))
    <BLANKLINE>

    """
    if z0 is None:
        z0 = np.zeros_like(x0)
    if x1 is None:
        coordinates = np.vstack([x0, y0, z0]).T
    else:
        if z1 is None:
            z1 = np.zeros(x1.shape)
        coordinates = np.vstack([x0, y0, z0, x1, y1, z1]).T
    # only write coordinates where none is nan
    filter = np.isnan(coordinates).any(1)
    # use cStringIO for performance
    output = io.BytesIO()
    # save coordinates to string buffer
    # I think this is faster than other methods
    # Use %s to get reduced string output
    np.savetxt(output, coordinates[~filter], delimiter=',', fmt='%s')
    coord_bytes = output.getvalue()
    coord_str = coord_bytes.decode()
    if x1 is not None:
        # replace all the 3rd , by a space...
        # TODO double check this regex
        coord_str = re.sub(r'(.*?,.*?,.*?),(.*)',  r'\1 \2', coord_str)
    return coord_str


def kmldate(date):
    """
    print date in kml format

    # Example usage
    >>> import datetime
    >>> date = datetime.datetime.fromtimestamp(0)
    >>> # this breaks if tzdata changed after 1970, pff
    >>> date = datetime.datetime(year=2000, month=1, day=1)
    >>> kmldate(date)
    '2000-01-01T00:00:00Z'

    """
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")
