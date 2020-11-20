import pathlib
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm
from matplotlib.patches import Rectangle
import numpy as np
import cmocean
import scipy.interpolate
import pandas as pd
import json

import coastviewer.extra_cm


def timestack(data):
    fig, ax = plt.subplots(figsize=(8, 3))
    pc = ax.pcolorfast(
        data['cross_shore'],
        data['time_num'],
        data['filled_z'],
        vmin=-20,
        vmax=20,
        cmap=coastviewer.extra_cm.GMT_drywet_r
    )
    ax.contour(
        data['cross_shore'],
        data['time_num'],
        data['z'],
        levels=[data['mean_low_water'], data['mean_high_water'], 3],
        cmap='PuBu'
    )
    # legend
    cb = plt.colorbar(pc, ax=ax)

    # labels
    cb.set_label('Height to NAP [$m$]')
    ax.set_xlabel('Cross shore distance [$m$]')
    ax.set_ylabel('Measurement time [$years$]')

    # date format
    date_locator = matplotlib.dates.AutoDateLocator()
    date_formatter = matplotlib.dates.AutoDateFormatter(date_locator)
    ax.yaxis.set_major_formatter(date_formatter)
    return fig, ax

def eeg(data):
    """Transforms the raw data representing the Jarkus raaien for every year in a JSON"""
    #extract the years from the data
    years = [str(x.year) for x in data['time'].tolist()]
    #create a dataframe with the data z
    df = pd.DataFrame(data = data['z'])
    df.insert(0,column = '',value=years)

    #store indexes of nan values in a list
    NaN_columns = df.columns[df.isna().all()].tolist()
    #delete elements of cross_shore with nan_indexes list
    data['cross_shore']  = np.delete(data['cross_shore'], NaN_columns)
    #cross_shore from numpy to list
    cross_shore = ['cross_shore']+ data['cross_shore'].tolist()

    #drop columns where nan values
    df.dropna(axis = 1, how='all', inplace=True)
    #add cross shore to first row of dataframe
    df.loc[-1] = cross_shore
    df.index = df.index +1 
    df = df.sort_index()

    # this will make sure it is numeric (float32) before applying the interpolation
    # can't say if that is needed, but it should not harm.
    s = df.iloc[1:,1:].apply(lambda x: pd.to_numeric(x, downcast='float', errors='coerce'))
    # s.info # checks that it is indeed float32

    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.interpolate.html
    df.iloc[1:,1:] = s.interpolate(method='linear', limit_area='inside', limit=5, axis=1)

    response = df.to_json(orient='values')
    parsed = json.loads(response)

    return parsed


def indicators(transect, mkl, bkltkltnd, mean_water, dune_foot, faalkans, nourishment):

    n_t = nourishment['time'].reset_index()
    n_y = nourishment.drop('time', axis=1).reset_index()

    fig, ax = plt.subplots(4, figsize=(13, 16), sharex=True)

    ax[0].plot(
        bkltkltnd['time'],
        bkltkltnd['basal_coastline'],
        'o',
        color='purple',
        alpha=0.7,
        label='Basiskustlijn'
    ) #'Basal Coastline'
    ax[0].grid(True)
    ax[0].plot(
        bkltkltnd['time'].values[-1],
        bkltkltnd['testing_coastline'].values[-1],
        'o',
        color='green',
        alpha=0.7,
        label='Toetsing Kustlijn'
    ) #'Testing Coastline'
    ax[0].plot(
        mkl['time_MKL'],
        mkl['momentary_coastline'],
        'o',
        color='blue',
        alpha=0.7,
        label='Momentane Kustlijn'
    ) #'Momentary Coastline'
    ax[1].plot(
        mean_water['time'],
        mean_water['mean_high_water_cross'],
        'ro',
        alpha=0.7,
        label='Mean High Water'
    )
    ax[1].grid(True)
    ax[1].plot(
        mean_water['time'],
        mean_water['mean_low_water_cross'],
        'bo',
        alpha=0.7,
        label='Mean Low Water'
    )
    ax[1].plot(
        dune_foot['time'],
        dune_foot['dune_foot_threeNAP_cross'],
        'go',
        alpha=0.7,
        label='Dune Foot 3NAP'
    )
    ax[2].plot(
        faalkans['time'],
        faalkans['probability_failure'],
        'ko',
        alpha=0.7,
        label='Probability of Failure'
    )
    ax[2].set_yscale('log')
    ax[2].grid(True)
    # set the x,y axis
    # TODO: fix this, this crashes
    #ax[0].set_xlim(np.min(mean_water['time']), np.max(mean_water['time']))
    #ax[1].set_xlim(np.min(mean_water['time']), np.max(mean_water['time']))
    #ax[2].set_xlim(np.min(mean_water['time']), np.max(mean_water['time']))
    # set axis labels
    ax[0].set_ylabel('Cross shore distance [$m$]')
    ax[1].set_ylabel('Cross shore distance [$m$]')
    ax[2].set_ylabel('Probability of failure [$-$]')
    # set legend
    ax[0].legend(loc='upper left')
    ax[1].legend(loc='upper left')

    nour_max = np.max(np.max(n_y[[
        'volume_beach',
        'volume_shoreface',
        'volume_dune',
        'volume_other'
    ]]))

    if nour_max!=0 and ~np.isnan(nour_max):
        color = ['yellow', 'blue', 'orange', 'red']
        lab = ['beach', 'shoreface', 'dune', 'other']
        boxes = [[],[],[],[]]
        ii = -150; # distance if overlapping

        for cc, ll, box in zip(color, lab, boxes):
            ii = ii+50; # distance if overlapping

            for tt, yy in zip(n_t['time'], n_y[str('volume_'+ll)]):
                startTime = tt.to_pydatetime()
                start = matplotlib.dates.date2num(startTime)
                r = Rectangle(
                    (start+ii,0),
                    width=365,
                    height=yy,
                    facecolor=cc,
                    edgecolor='black',
                    alpha=0.5,
                    label=ll
                )
                box.append(r) # duration of one year

                pc = matplotlib.collections.PatchCollection(box, facecolor=cc, edgecolor='black', alpha=0.5)


            ax[3].add_collection(pc)

        # TODO: fix this, this crashes
        #ax[3].set_xlim(np.min(mean_water['time']), np.max(mean_water['time']))
        ax[3].set_ylim(0, nour_max+50)
        ax[3].legend(tuple([bb[0] for bb in boxes]), tuple(lab), loc='upper left')


    ax[3].grid(True)
    ax[3].set_ylabel('Nourishments [$m^3/m$]')
    ax[3].set_xlabel('Measurement time [$years$]')

    # assign labels to other axes too
    ax[0].xaxis.set_tick_params(labelbottom=True)
    ax[1].xaxis.set_tick_params(labelbottom=True)
    ax[2].xaxis.set_tick_params(labelbottom=True)

    date_locator = matplotlib.dates.AutoDateLocator()
    date_formatter = matplotlib.dates.AutoDateFormatter(date_locator)

    return fig, ax
