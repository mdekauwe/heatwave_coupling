#!/usr/bin/env python

"""
For each of the OzFlux/FLUXNET2015 sites, figure out the TXx and save the
Qle and bowen ratio for that day and the previous 4 days.

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (20.04.2017)"
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

def main(flux_dir, ofname, oz_flux=True):

    flux_files = sorted(glob.glob(os.path.join(flux_dir, "*_flux.nc")))
    met_files = sorted(glob.glob(os.path.join(flux_dir, "*_met.nc")))

    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if oz_flux:
        d = get_ozflux_pfts()

    cols = ['site','pft','TXx','temp','Qle','B']
    df = pd.DataFrame(columns=cols)
    for flux_fn, met_fn in zip(flux_files, met_files):
        (site, df_flx, df_met) = open_file(flux_fn, met_fn)

        # daylight hours
        df_flx = df_flx.between_time("06:00", "20:00")
        df_met = df_met.between_time("06:00", "20:00")

        (df_flx, df_met) = mask_crap_days(df_flx, df_met)
        df_met.Tair -= c.DEG_2_KELVIN

        (TXx, Tairs, Qles, B) = get_hottest_day(df_flx, df_met)

        if oz_flux:
            pft = d[site]

        lst = []
        for i in range(len(Tairs)):
            lst.append([site,d[site],TXx,Tairs[i],Qles[i],B[i]])
        dfx = pd.DataFrame(lst, columns=cols)
        dfx = dfx.reindex(index=dfx.index[::-1]) # reverse the order hot to cool
        df = df.append(dfx)

    df.to_csv(os.path.join(output_dir, ofname), index=False)


def get_hottest_day(df_flx, df_met):
    df_dm = df_met.resample("D").max()
    df_df = df_flx.resample("D").mean()

    TXx = df_dm.sort_values("Tair", ascending=False)[:1].Tair.values[0]
    TXx_idx = df_dm.sort_values("Tair", ascending=False)[:1].index.values[0]
    TXx_idx_minus_four= TXx_idx - pd.Timedelta(4, unit='d')

    Tairs = df_dm[(df_dm.index >= TXx_idx_minus_four) &
                  (df_dm.index <= TXx_idx)].Tair.values
    Qles = df_df[(df_dm.index >= TXx_idx_minus_four) &
                 (df_dm.index <= TXx_idx)].Qle.values
    Qhs = df_df[(df_dm.index >= TXx_idx_minus_four) &
                (df_dm.index <= TXx_idx)].Qh.values
    B = Qhs / Qles

    return(TXx, Tairs, Qles, B)

def get_ozflux_pfts():

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

    return d

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
    df_flx = df_flx.reset_index()
    df_flx = df_flx.set_index('time')

    ds = xr.open_dataset(met_fn)
    df_met = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()
    df_met = df_met.reset_index()
    df_met = df_met.set_index('time')

    return (site, df_flx, df_met)

if __name__ == "__main__":

    flux_dir = "/Users/mdekauwe/research/OzFlux"
    ofname = "ozflux.csv"
    main(flux_dir, ofname, oz_flux=True)
