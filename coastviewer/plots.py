import pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm
from matplotlib.patches import Rectangle
import numpy as np
import cmocean
import scipy.interpolate
import pandas as pd


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

#old eeg that return as stream the img of the plot
""" def eeg(data, format, stream):
    print ('eeg function is called')
    print ('parameters', data, format, stream)
    t = data['time_num']
    x = data['cross_shore']
    # and data
    z = data['z']
    nrows, nsamples = z.shape

    # create a line for each timeseries
    segs = []
    ticklocs = []
    for i, row in enumerate(z):
        # add a line, scale it by the y axis each plot has a range of the
        # elevation divided by 7.5 (~2 years up and down)
        pts = np.c_[
            x[~z[i, :].mask],
            z[i, ~z[i, :].mask].filled()*365.0/7.5
        ]

        segs.append(pts)

        ticklocs.append(t[i])   # use date for yloc
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
    ax.set_xlabel('Cross shore distance [$m$]')
    ax.set_ylabel('Measurement time [$years$]')

    date_locator = matplotlib.dates.AutoDateLocator()
    date_formatter = matplotlib.dates.AutoDateFormatter(date_locator)
    ax.yaxis.set_major_formatter(date_formatter)
    
    dpi = 72
    if format in ('pdf', 'png', 'svg'):
        dpi = 300
        fig.savefig(stream, bbox_inches='tight', dpi=dpi, format=format)
    else:
        fig.savefig(stream, bbox_inches='tight', dpi=dpi, format='png')
    plt.close(fig)
    
    return stream #fig, ax """
""" 
#new eeg that returns a json of the data in order to create
#an echart in the front end
""" 
    
def eeg(data):
    
    #print ('data', data)
    #extract the years from the data
    years = [str(x.year) for x in data['time'].tolist()]
    #create a dataframe with the data z
    df = pd.DataFrame(data = data['z'])
    df.insert(0,column = '',value=years)

    #store indexes of nan values in a list
    NaN_indexes = df.columns[df.isna().all()].tolist()
    #delete elements of cross_shore with nan_indexes list
    data['cross_shore']  = np.delete(data['cross_shore'], NaN_indexes)
    #cross_shore from numpy to list
    cross_shore = ['cross_shore']+ data['cross_shore'].tolist()

    #drop columns where nan values
    df.dropna(axis = 1, how='all', inplace=True)
    #add cross shore to first row of dataframe
    df.loc[-1] = cross_shore
    df.index = df.index +1 
    df = df.sort_index()
    response = df.to_json(orient='values')
    
    return response 


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
