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
