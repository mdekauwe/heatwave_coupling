#!/usr/bin/env python

"""
For each of the Ozflux sites, plot LE & GPP as a function of Tair to probe
decoupling

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (18.12.2017)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import glob
import netCDF4 as nc
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

def main(flux_dir):

    plot_dir = "plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    flux_files = sorted(glob.glob(os.path.join(flux_dir, "*_flux.nc")))
    met_files = sorted(glob.glob(os.path.join(flux_dir, "*_met.nc")))

    for flux_fn, met_fn in zip(flux_files, met_files):
        (site, df_flx, df_met) = open_file(flux_fn, met_fn)
        print(site)
        make_plot(plot_dir, site, df_flx, df_met)


def open_file(flux_fn, met_fn):
    site = os.path.basename(flux_fn).split("OzFlux")[0]
    ds = xr.open_dataset(flux_fn)
    df_flx = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()
    ds = xr.open_dataset(met_fn)
    df_met = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()

    return (site, df_flx, df_met)

def make_plot(plot_dir, site, df_flx, df_met):

    K_TO_C = 273.15

    #golden_mean = 0.6180339887498949
    #width = 6*2*(1/golden_mean)
    #height = width * golden_mean

    fig = plt.figure(figsize=(9, 6))
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.2)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color'] = almost_black
    plt.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color'] = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor'] = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    ax1 = fig.add_subplot(111)

    colour_list = ["#E69F00","#56B4E9", "#009E73", "#CC79A7"]

    # Mask crap stuff
    df_flx.where(df_flx.GPP_qc == 1, inplace=True)
    df_flx.where(df_flx.Qle_qc == 1, inplace=True)
    df_flx.where(df_met.Tair_qc == 1, inplace=True)

    df_met.where(df_flx.GPP_qc == 1, inplace=True)
    df_met.where(df_flx.Qle_qc == 1, inplace=True)
    df_met.where(df_met.Tair_qc == 1, inplace=True)

    # Mask dew
    df_met.where(df_flx.Qle > 0., inplace=True)
    df_flx.where(df_flx.Qle > 0., inplace=True)

    # daylight hours
    #df_flx = df_flx.between_time("07:00", "20:00")
    #df_met = df_met.between_time("07:00", "20:00")
    z = df_met.Tair.values - K_TO_C

    x = df_flx.Qle.values
    y = df_flx.GPP.values





    x2 = x[(z>30.)&(z<=35)]
    y2 = y[(z>30.)&(z<=35)]
    x1 = x[(z>35.)&(z<=40)]
    y1 = y[(z>35.)&(z<=40)]
    x3 = x[(z>40.)]
    y3 = y[(z>40.)]

    ax1.plot(x1, y1, ls=" ", marker="o", label="30-35 deg C",
             color=colour_list[1], alpha=0.1, zorder=1)
    ax1.plot(x2, y2, ls=" ", marker="o", label="35-40 deg C",
             color=colour_list[2], alpha=0.2, zorder=2)
    ax1.plot(x3, y3, ls=" ", marker="o", label=">40 deg C",
             color=colour_list[3], alpha=0.3, zorder=10)

    ax1.legend(numpoints=1, loc="best")
    #ax1.set_xlim(0, 45)
    #ax1.set_ylim(0, 40)
    #ax2.set_xlim(0, 45)
    ax1.set_xlim(0, 300)
    ax1.set_ylim(0, 25)
    #ax1.set_xlabel("Tair (deg C)")
    #ax1.xaxis.set_label_coords(1.05, -0.1)
    #ax1.set_ylabel(r"GPP (umol m$^{-2}$ s$^{-1}$)")
    #ax2.set_ylabel(r"LE (W m$^{-2}$)")

    fig.savefig(os.path.join(plot_dir, "%s_scatter.pdf" % (site)),
                bbox_inches='tight', pad_inches=0.1)

    #sys.exit()

if __name__ == "__main__":

    flux_dir = "/Users/mdekauwe/research/OzFlux"
    main(flux_dir)
