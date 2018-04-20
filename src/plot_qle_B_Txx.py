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

def main(fname):

    plot_dir = "plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    df = pd.read_csv(fname)
    df = df[df.pft == "EBF"]

    #width  = 12.0
    #height = width / 1.618
    #print(width, height)
    #sys.exit()
    width = 18
    height = 8
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

    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    sites = np.unique(df.site)
    for site in sites:
        df_site = df[df.site == site]
        temps = df_site["temp"].values
        ax1.plot(df_site["temp"], df_site["Qle"], label=site, ls="-",
                 marker="o")
        ax2.plot(df_site["temp"], df_site["B"], label=site, ls="-",
                 marker="o")
        ax3.plot(df_site["temp2"], df_site["Qle2"], label=site, ls="-",
                 marker="o")
        ax4.plot(df_site["temp2"], df_site["B2"], label=site, ls="-",
                 marker="o")
    ax3.set_xlabel('Temperature ($^\circ$C)', position=(1.0, 0.5))
    ax1.set_ylabel("Qle (W m$^{-2}$)", position=(0.5, 0.0))
    ax2.set_ylabel("B (-)", position=(0.5, 0.0))
    ax1.legend(numpoints=1, loc="best", ncol=1, frameon=False)

    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)

    ax1.set_ylim(0, 250)
    ax2.set_ylim(0, 10)
    ax3.set_ylim(0, 250)
    ax4.set_ylim(0, 10)
    fig.savefig("/Users/mdekauwe/Desktop/Qle_bowen_Txx_minus5.pdf",
                bbox_inches='tight', pad_inches=0.1)
    #fig.savefig("/Users/mdekauwe/Desktop/Qle_bowen_Txx_minus5.png", dpi=150,
    #            bbox_inches='tight', pad_inches=0.1)
    #plt.show()

if __name__ == "__main__":

    data_dir = "outputs/"
    fname = "ozflux.csv"
    fname = os.path.join(data_dir, fname)
    main(fname)
