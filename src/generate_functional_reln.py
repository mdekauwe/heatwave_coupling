#!/usr/bin/env python

"""
As in Teuling et al., generate plots of functional relationships between midday
surface fluxes of sensible heat, latent heat and environmental conditions for
the Ozflux sites.

Reference:
==========
* Teuling et al. (2010) Contrasting response of European for- est and grassland
energy exchange to heatwaves, Nat. Geosci., 3, 722–727.

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
import pandas as pd

from pygam import LinearGAM
from pygam.utils import generate_X_grid

def main(flux_dir):

    sites = ["AdelaideRiver","Calperum","CapeTribulation","CowBay",\
             "CumberlandPlains","DalyPasture","DalyUncleared",\
             "DryRiver","Emerald","Gingin","GreatWesternWoodlands",\
             "HowardSprings","Otway","RedDirtMelonFarm","RiggsCreek",\
             "Samford","SturtPlains","Tumbarumba","Whroo",\
             "WombatStateForest","Yanco"]

    pfts = ["SAV","SHB","TRF","TRF","EBF","GRA","SAV",\
            "SAV","NA","EBF","EBF",\
            "SAV","GRA","NA","GRA",\
            "GRA","GRA","EBF","EBF",\
            "EBF","GRA"]

    d = dict(zip(sites, pfts))

    plot_dir = "plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    flux_files = sorted(glob.glob(os.path.join(flux_dir, "*_flux.nc")))
    met_files = sorted(glob.glob(os.path.join(flux_dir, "*_met.nc")))


    for flux_fn, met_fn in zip(flux_files, met_files):
        (site, df_flx, df_met) = open_file(flux_fn, met_fn)
        print(site)

        #if site != "CowBay" and site != "Tumbarumba":
        make_plot(plot_dir, site, df_flx, df_met)

        sys.exit()

def open_file(flux_fn, met_fn):
    site = os.path.basename(flux_fn).split("OzFlux")[0]
    ds = xr.open_dataset(flux_fn)
    dates = pd.to_datetime(ds.time.values)
    df_flx = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()
    df_flx['dates'] = dates
    df_flx = df_flx.set_index('dates')

    ds = xr.open_dataset(met_fn)
    dates = pd.to_datetime(ds.time.values)
    df_met = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()
    df_met['dates'] = dates
    df_met = df_met.set_index('dates')

    return (site, df_flx, df_met)

def make_plot(plot_dir, site, df_flx, df_met):

    K_TO_C = 273.15

    #golden_mean = 0.6180339887498949
    #width = 6*2*(1/golden_mean)
    #height = width * golden_mean

    fig = plt.figure(figsize=(14, 4))
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.1)
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

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    # Mask crap stuff
    df_met.where(df_flx.Qle_qc == 1, inplace=True)
    df_met.where(df_flx.Qh_qc == 1, inplace=True)

    df_flx.where(df_flx.Qle_qc == 1, inplace=True)
    df_flx.where(df_flx.Qh_qc == 1, inplace=True)
    #df_flx.where(df_met.Tair_qc == 1, inplace=True)
    #df_flx.where(df_met.SWdown == 1, inplace=True)

    #df_met.where(df_met.SWdown == 1, inplace=True)
    #df_met.where(df_met.Tair_qc == 1, inplace=True)

    # Mask dew
    df_met.where(df_flx.Qle > 0., inplace=True)
    df_flx.where(df_flx.Qle > 0., inplace=True)

    df_flx.dropna(inplace=True)
    df_met.dropna(inplace=True)


    if len(df_flx) > 0 and len(df_met) > 0:
        print(site, len(df_flx), len(df_met))

        alpha = 0.07

        # < "Midday" data
        df_flx = df_flx.between_time("09:00", "13:00")
        df_met = df_met.between_time("09:00", "13:00")

        ax1.plot(df_met.SWdown, df_flx.Qle, ls=" ", marker="o",
                 color="salmon", alpha=alpha)
        ax1.plot(df_met.SWdown, df_flx.Qh, ls=" ", marker="o",
                 color="royalblue", alpha=alpha)

        gam = LinearGAM(n_splines=20).gridsearch(df_met.SWdown, df_flx.Qle)
        XX = generate_X_grid(gam)
        ax1.plot(XX, gam.predict(XX), color="salmon", ls='-', lw=2.0,
                 label="Qle")
        ax1.plot(XX, gam.prediction_intervals(XX, width=.95), color='salmon',
                 ls='--')

        gam = LinearGAM(n_splines=20).gridsearch(df_met.SWdown, df_flx.Qh)
        XX = generate_X_grid(gam)
        ax1.plot(XX, gam.predict(XX), color="royalblue", ls='-', lw=2.0,
                 label="Qh")
        ax1.plot(XX, gam.prediction_intervals(XX, width=.95), color='royalblue',
                 ls='--')

        ax2.plot(df_met.Tair - K_TO_C, df_flx.Qle, ls=" ", marker="o",
                 color="salmon", alpha=alpha, label="Qle")
        ax2.plot(df_met.Tair - K_TO_C, df_flx.Qh, ls=" ", marker="o",
                 color="royalblue", alpha=alpha, label="Qh")

        gam = LinearGAM(n_splines=20).gridsearch(df_met.Tair - K_TO_C, df_flx.Qle)
        XX = generate_X_grid(gam)
        ax2.plot(XX, gam.predict(XX), color="salmon", ls='-', lw=2.0)
        ax2.plot(XX, gam.prediction_intervals(XX, width=.95), color='salmon',
                 ls='--')

        gam = LinearGAM(n_splines=20).gridsearch(df_met.Tair - K_TO_C, df_flx.Qh)
        XX = generate_X_grid(gam)
        ax2.plot(XX, gam.predict(XX), color="royalblue", ls='-', lw=2.0)
        ax2.plot(XX, gam.prediction_intervals(XX, width=.95), color='royalblue',
                 ls='--')
        plt.setp(ax2.get_yticklabels(), visible=False)

        ax1.set_xlim(0, 1300)
        ax1.set_ylim(0, 1000)
        ax2.set_xlim(0, 45)
        ax2.set_ylim(0, 1000)
        ax1.set_xlabel("SW down (W m$^{-2}$)")
        ax2.set_xlabel("Tair (deg C)")
        ax1.set_ylabel("Daytime flux (W m$^{-2}$)")
        ax1.legend(numpoints=1, loc="best")
        #fig.savefig(os.path.join(plot_dir, "%s.pdf" % (site)),
        #            bbox_inches='tight', pad_inches=0.1)

        fig.savefig(os.path.join(plot_dir, "%s.png" % (site)),
                    bbox_inches='tight', pad_inches=0.1, dpi=100)




if __name__ == "__main__":

    flux_dir = "/Users/mdekauwe/research/OzFlux"
    main(flux_dir)
