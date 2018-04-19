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
import pandas as pd

import constants as c

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

    allx = {}
    sites = []
    for flux_fn, met_fn in zip(flux_files, met_files):
        (site, df_flx, df_met) = open_file(flux_fn, met_fn)
        #print(site)

        # daylight hours
        df_flx = df_flx.between_time("06:00", "20:00")
        df_met = df_met.between_time("06:00", "20:00")

        (df_flx, df_met) = mask_crap_days(df_flx, df_met)
        df_met.Tair -= c.DEG_2_KELVIN

        allx[site] = {}

        #if d[site] == "EBF" or d[site] == "SAV" or d[site] == "TRF":
        if d[site] == "EBF" or d[site] == "SAV":
            (Tairs, Qles, B) = get_hottest_day(df_flx, df_met)

            allx[site]["Tair"] = Tairs
            allx[site]["Qle"] = Qles
            allx[site]["B"] = B
            sites.append(site)

    #width  = 12.0
    #height = width / 1.618
    #print(width, height)
    #sys.exit()
    width = 20
    height = 6
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

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    for site in sites:
        #print(site)
        #print(allx[site]["Tair"])
        #print(allx[site]["Qle"])
        #print(allx[site]["B"])
        #print("\n")

        ax1.plot(allx[site]["Tair"], allx[site]["Qle"], label=site, ls="--",
                 marker="o")
        ax2.plot(allx[site]["Tair"], allx[site]["B"], label=site, ls="--",
                 marker="o")
    ax1.set_ylabel('Temperature ($^\circ$C)', position=(1.0, 0.5))
    ax1.set_ylabel("Qle (W m$^{-2}$)")
    ax2.set_ylabel("B (-)")
    ax1.legend(numpoints=1, loc="best", ncol=1, frameon=False)
    fig.savefig("/Users/mdekauwe/Desktop/Qle_bowen_Txx_minus5.pdf",
                bbox_inches='tight', pad_inches=0.1)
    fig.savefig("/Users/mdekauwe/Desktop/Qle_bowen_Txx_minus5.png", dpi=150,
                bbox_inches='tight', pad_inches=0.1)
    plt.show()

def get_hottest_day(df_flx, df_met):
    df_dm = df_met.resample("D").max()
    df_df = df_flx.resample("D").mean()

    Txx_idx = df_dm.sort_values("Tair", ascending=False)[:1].index.values[0]
    Txx_idx_minus_five = Txx_idx - pd.Timedelta(4, unit='d')



    Tairs = df_dm[(df_dm.index >= Txx_idx_minus_five) &
                 (df_dm.index <= Txx_idx)].Tair.values
    Qles = df_df[(df_dm.index >= Txx_idx_minus_five) &
                 (df_dm.index <= Txx_idx)].Qle.values
    Qhs = df_df[(df_dm.index >= Txx_idx_minus_five) &
                 (df_dm.index <= Txx_idx)].Qh.values
    B = Qhs / Qles

    return(Tairs, Qles, B)


def mask_crap_days(df_flx, df_met):
    # Mask crap stuff
    df_flx.where(df_flx.Qle_qc == 1, inplace=True)
    df_flx.where(df_flx.Qh_qc == 1, inplace=True)
    df_flx.where(df_met.Tair_qc == 1, inplace=True)


    df_met.where(df_flx.Qle_qc == 1, inplace=True)
    df_met.where(df_flx.Qh_qc == 1, inplace=True)
    df_met.where(df_met.Tair_qc == 1, inplace=True)

    # Mask dew
    df_met.where(df_flx.Qle > 0., inplace=True)
    df_flx.where(df_flx.Qle > 0., inplace=True)

    df_met = df_met.reset_index()
    df_met = df_met.set_index('time')
    df_flx = df_flx.reset_index()
    df_flx = df_flx.set_index('time')

    return df_flx, df_met

def open_file(flux_fn, met_fn):
    site = os.path.basename(flux_fn).split("OzFlux")[0]
    ds = xr.open_dataset(flux_fn)
    df_flx = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()
    ds = xr.open_dataset(met_fn)
    df_met = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()

    df_met = df_met.reset_index()
    df_met = df_met.set_index('time')

    df_flx = df_flx.reset_index()
    df_flx = df_flx.set_index('time')

    return (site, df_flx, df_met)

if __name__ == "__main__":

    flux_dir = "/Users/mdekauwe/research/OzFlux"
    main(flux_dir)
