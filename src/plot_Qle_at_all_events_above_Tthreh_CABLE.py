#!/usr/bin/env python

"""
For each of the OzFlux/FLUXNET2015 sites, plot the TXx and T-4 days
Qle and bowen ratio

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (20.04.2018)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import glob
import netCDF4 as nc
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd

import constants as c

def main(fname, supp=False):

    plot_dir = "plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    df = pd.read_csv(fname)
    df = df[df.pft == "EBF"]

    #width  = 12.0
    #height = width / 1.618
    #print(width, height)
    #sys.exit()
    width = 14
    height = 5
    fig = plt.figure(figsize=(width, height))
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.1)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14


    count = 0
    sites = np.unique(df.site)
    for site in sites:

        ax = fig.add_subplot(2,4,1+count)

        df_site = df[df.site == site]
        events = int(len(df_site)/4)

        cnt = 0
        for e in range(0, events):

            from scipy import stats
            x = df_site["temp"][cnt:cnt+4]
            y = df_site["Qle"][cnt:cnt+4]
            slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

            if supp:
                if slope < 0.0 and p_value <= 0.05:
                    ax.plot(df_site["temp"][cnt:cnt+4], df_site["Qle"][cnt:cnt+4],
                            label=site, ls="-", marker="o", zorder=100)
                elif slope < 0.0 and p_value > 0.05:
                    ax.plot(df_site["temp"][cnt:cnt+4], df_site["Qle"][cnt:cnt+4],
                            label=site, ls="-", marker="o", color="lightgrey",
                            zorder=1)
            else:
                if slope > 0.0 and p_value <= 0.05:
                    ax.plot(df_site["temp"][cnt:cnt+4], df_site["Qle"][cnt:cnt+4],
                            label=site, ls="-", marker="o", zorder=100)
                elif slope > 0.0 and p_value > 0.05:
                    ax.plot(df_site["temp"][cnt:cnt+4], df_site["Qle"][cnt:cnt+4],
                            label=site, ls="-", marker="o", color="lightgrey",
                            zorder=1)
            cnt += 4

        if count == 0:
            ax.set_ylabel("Qle (W m$^{-2}$)", position=(0.5, 0.0))
        if count == 5:
            ax.set_xlabel('Temperature ($^\circ$C)', position=(1.0, 0.5))

        if count < 4:
            plt.setp(ax.get_xticklabels(), visible=False)

        if count != 0 and count != 4:
            plt.setp(ax.get_yticklabels(), visible=False)

        props = dict(boxstyle='round', facecolor='white', alpha=1.0,
                     ec="white")
        ax.text(0.04, 0.95, site,
                transform=ax.transAxes, fontsize=14, verticalalignment='top',
                bbox=props)

        ax.set_ylim(0, 320)
        ax.set_xlim(15, 50)
        count += 1

    ofdir = "/Users/mdekauwe/Dropbox/fluxnet_heatwaves_paper/figures/figs"
    if supp:
        fig.savefig(os.path.join(ofdir, "all_events_Qle_CABLE_supp.pdf"),
                    bbox_inches='tight', pad_inches=0.1)
    else:
        fig.savefig(os.path.join(ofdir, "all_events_Qle_CABLE.pdf"),
                    bbox_inches='tight', pad_inches=0.1)
    #plt.show()

if __name__ == "__main__":

    data_dir = "outputs/"
    fname = "ozflux_all_events_CABLE.csv"
    fname = os.path.join(data_dir, fname)
    main(fname)

    fname = "ozflux_all_events_CABLE.csv"
    fname = os.path.join(data_dir, fname)
    main(fname, supp=True)
