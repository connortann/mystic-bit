import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_well_map(df_logs, fig_size=(10, 10)):
    """ Simple map of locations of nearby wells """

    f, ax = plt.subplots(figsize=fig_size)

    df = df_logs.drop_duplicates(subset=['HACKANAME', 'X', 'Y'])

    plt.scatter(df['X'], df['Y'])
    plt.axis('scaled')

    for label, x, y in zip(df['HACKANAME'], df['X'], df['Y']):
        plt.annotate(label,
                     xy=(x, y),
                     xytext=(-10, 10),
                     textcoords='offset points')
    return f, ax


def make_log_plot(well_logs, strata, well_index, ztop=None, zbot=None, fig_size=(8,12)):
    """ Single well log plot, both GR and Resistivity """

    logs = well_logs[well_logs['WELL_INDEX'] == well_index]
    logs = logs.sort_values(by='DEPT')

    if not ztop:
        ztop = logs.DEPT.min()
    if not zbot:
        zbot = logs.DEPT.max()

    f, ax = plt.subplots(nrows=1, ncols=2, figsize=fig_size)
    ax[0].plot(logs.GR, logs.DEPT, '-g')
    ax[1].plot(logs.RESD, logs.DEPT, '-')

    for i in range(len(ax)):
        ax[i].set_ylim(ztop, zbot)
        ax[i].invert_yaxis()
        ax[i].grid()
        ax[i].locator_params(axis='x', nbins=3)

    ax[0].set_xlabel("GR")
    ax[0].set_xlim(0, 150)
    ax[1].set_xlabel("RESD")
    ax[1].set_xscale('log')
    ax[1].set_xlim(0.2, 2000)

    ax[1].set_yticklabels([])

    f.suptitle('Well: %s' % logs.iloc[0]['WELL_INDEX'], fontsize=14, y=0.94)

    # Plot strata picks
    cdict = get_colours(strata)
    well_strata = strata.loc[well_index][3:]
    for zone, depth in well_strata.iteritems():
        if ztop < depth < zbot:
            for i in range(len(ax)):
                ax[i].axhline(y=depth, color=cdict[zone])

            # Labels on rightmost axis
            pos_x = ax[-1].get_xlim()[1]
            ax[-1].text(pos_x, depth, zone)
    return ax

