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

    for flux_fn, met_fn in zip(flux_files, met_files):
        (site, df_flx, df_met) = open_file(flux_fn, met_fn)
        #print(site)
        # Mask crap stuff
        if d[site] == "EBF":
            print(site, np.unique(df_flx.index.year))

def get_three_most_hottest_weeks(df):
    df_w = df.resample("W").mean()

    missing = False

    try:
        df_w = df_w.sort_values("Tair", ascending=False)[:3]
        weeks = df_w.index.week
    except KeyError:
        missing = True
        weeks = None

    return (weeks, missing)

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
