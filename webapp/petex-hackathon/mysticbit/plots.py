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


def make_log_plot(df_logs, well_name, cols=['GR', 'DT', 'CALI'], ztop=None, zbot=None, fig_size=(8, 12)):
    """ Single well log plot, both GR and Resistivity """

    logs = df_logs[df_logs['HACKANAME'] == well_name]
    logs = logs.sort_values(by='TVDSS')

    if not ztop:
        ztop = logs.TVDSS.min()
    if not zbot:
        zbot = logs.TVDSS.max()

    f, ax = plt.subplots(nrows=1, ncols=len(cols), figsize=fig_size)

    for i in range(len(ax)):
        log_name = cols[i]
        ax[i].scatter(logs[log_name], logs['TVDSS'], marker='+')
        ax[i].set_xlabel(log_name)
        ax[i].set_ylim(ztop, zbot)
        ax[i].invert_yaxis()
        ax[i].grid()
        ax[i].locator_params(axis='x', nbins=3)

        if i > 0:
            ax[i].set_yticklabels([])

    # ax[0].set_xlabel("GR")
    # ax[0].set_xlim(0, 150)
    # ax[1].set_xlabel("RESD")
    # ax[1].set_xscale('log')
    # ax[1].set_xlim(0.2, 2000)

    # ax[1].set_yticklabels([])

    f.suptitle('Well: {}'.format(well_name), fontsize=14, y=0.94)

    return f, ax

