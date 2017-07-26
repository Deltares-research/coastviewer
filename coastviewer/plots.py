import pathlib
import matplotlib.pyplot as plt
import matplotlib.cm
import numpy as np
import netCDF4
import cmocean
import colorcet
import scipy.interpolate


import coastviewer.extra_cm

def time_map(data):
    fig, ax = plt.subplots(figsize=(8, 3))
    pc = ax.pcolorfast(data['cross_shore'], data['time_num'], data['filled_z'], vmin=-20, vmax=20, cmap=coastviewer.extra_cm.GMT_drywet_r)
    cont = ax.contour(
        data['cross_shore'], 
        data['time_num'], 
        data['z'],
        levels=[data['mean_low_water'], data['mean_high_water'], 3],
        cmap='PuBu'
    )
    # legend
    cb = plt.colorbar(pc, ax=ax)

    # labels
    cb.set_label('Height to NAP [m]')
    ax.set_xlabel('Cross shore distance [m]')
    ax.set_ylabel('Measurement time [y]')

    # date format
    date_locator = matplotlib.dates.AutoDateLocator()
    date_formatter = matplotlib.dates.AutoDateFormatter(date_locator)
    ax.yaxis.set_major_formatter(date_formatter)
    return fig, ax

def eeg(data):
    t = data['time_num']
    x = data['cross_shore']
    # and data
    z = data['z']
    nrows, nsamples = z.shape

    # create a line for each timeseries
    segs = []
    ticklocs = []
    for i, row in enumerate(z):
        # add a line, scale it by the y axis each plot has a range of the elevation divided by 7.5 (~2 years up and down)
        pts = np.c_[
            x[~z[i, :].mask],
            z[i, ~z[i,:].mask].filled()*365.0/7.5
        ]

        segs.append(pts)

        ticklocs.append(t[i]) # use date for yloc
    # create an offset for each line
    offsets = np.zeros((nrows, 2), dtype=float)
    offsets[:, 1] = ticklocs
    # create the lines
    lines = matplotlib.collections.LineCollection(segs, offsets=offsets)
    # create a new figure
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.add_collection(lines)
    # set the x axis
    ax.set_xlim(x.min(), x.max())
    # set the y axis (add a bit of room cause the wiggles go over a few years)
    # changed maximum correction days to 1000 from 730 (2 years), because
    # sometimes upper line was outside the y limits
    ax.set_ylim(t.min()-730, t.max()+1000)
    ax.set_xlabel('Cross shore distance [m]')
    ax.set_ylabel('Measurement time [y]')

    date_locator = matplotlib.dates.AutoDateLocator()
    date_formatter = matplotlib.dates.AutoDateFormatter(date_locator)
    ax.yaxis.set_major_formatter(date_formatter)
    return fig, ax
