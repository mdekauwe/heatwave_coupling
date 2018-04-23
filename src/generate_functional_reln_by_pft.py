#!/usr/bin/env python

"""
As in Teuling et al., generate plots of functional relationships between midday
surface fluxes of sensible heat, latent heat and environmental conditions for
the Ozflux sites.

Reference:
==========
* Teuling et al. (2010) Contrasting response of European forest and grassland
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
import itertools
from pygam import LinearGAM
from pygam.utils import generate_X_grid

def main(flux_dir):
    K_TO_C = 273.15
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
    id = dict(zip(sites, pd.factorize(pfts)[0]))

    plot_dir = "plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    flux_files = sorted(glob.glob(os.path.join(flux_dir, "*_flux.nc")))
    met_files = sorted(glob.glob(os.path.join(flux_dir, "*_met.nc")))

    data_qle = []
    data_qh = []
    data_tair = []
    data_sw = []
    pft_ids = []

    # collect up data
    for flux_fn, met_fn in zip(flux_files, met_files):
        (site, df_flx, df_met) = open_file(flux_fn, met_fn)

        if d[site] != "NA":
            pft = d[site]
            colour_id = id[site]

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

            df_flx = df_flx.between_time("09:00", "13:00")
            df_met = df_met.between_time("09:00", "13:00")

            if len(df_flx) > 0 and len(df_met) > 0:
                #data_qle[pft].append(df_flx.Qle.values)
                #data_qh[pft].append(df_flx.Qh.values)
                #data_tair[pft].append(df_met.Tair.values - K_TO_C)
                #data_sw[pft].append(df_met.SWdown.values)

                data_qle.append(df_flx.Qle.values)
                data_qh.append(df_flx.Qh.values)
                data_tair.append(df_met.Tair.values - K_TO_C)
                data_sw.append(df_met.SWdown.values)
                pft_ids.append([pft]* len(df_flx) )


    pft_ids = list(itertools.chain(*pft_ids))
    data_qle = list(itertools.chain(*data_qle))
    data_qh = list(itertools.chain(*data_qh))
    data_sw = list(itertools.chain(*data_sw))
    data_tair = list(itertools.chain(*data_tair))

    data_qle = np.asarray(data_qle)
    data_qh = np.asarray(data_qh)
    data_tair = np.asarray(data_tair)
    data_sw = np.asarray(data_sw)
    pft_ids = np.asarray(pft_ids)



    colours = ["red", "green", "blue", "yellow", "pink"]

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

    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    colour_id = 0
    for pft in np.unique(pfts):

        if pft != "NA":
            qle = data_qle[np.argwhere(pft_ids == pft)]
            qh = data_qh[np.argwhere(pft_ids == pft)]
            tair = data_tair[np.argwhere(pft_ids == pft)]
            sw = data_sw[np.argwhere(pft_ids == pft)]

            print(pft, len(qle), len(qh), len(tair), len(sw))

            gam = LinearGAM(n_splines=20).gridsearch(sw, qh)
            XX = generate_X_grid(gam)
            CI = gam.confidence_intervals(XX, width=.95)

            ax1.plot(XX, gam.predict(XX), color=colours[colour_id], ls='-', lw=2.0)
            ax1.fill_between(XX[:,0], CI[:,0], CI[:,1], color=colours[colour_id],
                             alpha=0.7)

            gam = LinearGAM(n_splines=20).gridsearch(sw, qle)
            XX = generate_X_grid(gam)
            CI = gam.confidence_intervals(XX, width=.95)

            ax2.plot(XX, gam.predict(XX), color=colours[colour_id], ls='-', lw=2.0)
            ax2.fill_between(XX[:,0], CI[:,0], CI[:,1], color=colours[colour_id],
                             alpha=0.7)

            gam = LinearGAM(n_splines=20).gridsearch(tair, qh)
            XX = generate_X_grid(gam)
            CI = gam.confidence_intervals(XX, width=.95)
            ax3.plot(XX, gam.predict(XX), color=colours[colour_id], ls='-', lw=2.0)
            ax3.fill_between(XX[:,0], CI[:,0], CI[:,1], color=colours[colour_id],
                             alpha=0.7)

            gam = LinearGAM(n_splines=20).gridsearch(tair, qle)
            XX = generate_X_grid(gam)
            CI = gam.confidence_intervals(XX, width=.95)
            ax4.plot(XX, gam.predict(XX), color=colours[colour_id], ls='-', lw=2.0)
            ax4.fill_between(XX[:,0], CI[:,0], CI[:,1], color=colours[colour_id],
                             alpha=0.7)

            colour_id += 1

    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)

    ax1.set_xlim(0, 1300)
    ax1.set_ylim(0, 1000)
    ax2.set_xlim(0, 45)
    ax2.set_ylim(0, 1000)
    ax3.set_xlabel("SW down (W m$^{-2}$)")
    ax4.set_xlabel("Tair ($^\circ$C)")
    ax1.set_ylabel("Qh flux (W m$^{-2}$)")
    ax2.set_ylabel("Qle flux (W m$^{-2}$)")
    #ax1.legend(numpoints=1, loc="best")
    #fig.savefig(os.path.join(plot_dir, "%s.pdf" % (site)),
    #            bbox_inches='tight', pad_inches=0.1)


    fig.savefig(os.path.join(plot_dir, "ozflux_by_pft.png"),
                bbox_inches='tight', pad_inches=0.1, dpi=150)




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


if __name__ == "__main__":

    flux_dir = "/Users/mdekauwe/research/OzFlux"
    main(flux_dir)
