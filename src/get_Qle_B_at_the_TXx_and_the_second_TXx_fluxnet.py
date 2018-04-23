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

    if oz_flux:
        flux_files = sorted(glob.glob(os.path.join(flux_dir, "*_flux.nc")))
        met_files = sorted(glob.glob(os.path.join(flux_dir, "*_met.nc")))
    else:
        flux_files = sorted(glob.glob(os.path.join(flux_dir, "*_Flux.nc")))
        met_files = sorted(glob.glob(os.path.join(flux_dir, "*_Met.nc")))

    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if oz_flux:
        d = get_ozflux_pfts()

    cols = ['site','pft','TXx','temp','Qle','B','TXx2','temp2','Qle2','B2']
    df = pd.DataFrame(columns=cols)
    for flux_fn, met_fn in zip(flux_files, met_files):
        (site, df_flx, df_met) = open_file(flux_fn, met_fn, oz_flux=oz_flux)

        # daylight hours
        #df_flx = df_flx.between_time("06:00", "20:00")
        #df_met = df_met.between_time("06:00", "20:00")

        (df_flx, df_met) = mask_crap_days(df_flx, df_met)
        df_met.Tair -= c.DEG_2_KELVIN

        (TXx, Tairs, Qles, B) = get_hottest_day(df_flx, df_met)
        (TXx2, Tairs2, Qles2, B2) = get_second_hottest_day(df_flx, df_met)
        no_TXx2 = False
        if len(Tairs) != len(Tairs2):
            no_TXx2 = True

        if oz_flux:
            pft = d[site]

        lst = []
        for i in range(len(Tairs)):
            if no_TXx2:
                lst.append([site,d[site],TXx,Tairs[i],Qles[i],B[i],
                            np.nan,np.nan,np.nan,np.nan])
            else:
                lst.append([site,d[site],TXx,Tairs[i],Qles[i],B[i],
                            TXx2,Tairs2[i],Qles2[i],B2[i]])
        dfx = pd.DataFrame(lst, columns=cols)
        dfx = dfx.reindex(index=dfx.index[::-1]) # reverse the order hot to cool
        df = df.append(dfx)

    df.to_csv(os.path.join(output_dir, ofname), index=False)


def get_hottest_day(df_flx, df_met):

    TXx = df_met.sort_values("Tair", ascending=False)[:1].Tair.values[0]
    year = df_met.sort_values("Tair", ascending=False)[:1].index.year[0]
    doy = df_met.sort_values("Tair", ascending=False)[:1].index.dayofyear[0]

    for i in range(0,5, 4):
        print(i)
        Qle = df_flx[(df_flx.index.year == year) & (df_flx.index.dayofyear == doy-i)].Qle

        plt.plot(Qle.index.hour, Qle)
    plt.show()
    sys.exit()
    TXx_idx_minus_four= TXx_idx - pd.Timedelta(4, unit='d')

    Tairs = df_dm[(df_dm.index >= TXx_idx_minus_four) &
                  (df_dm.index <= TXx_idx)].Tair.values
    Qles = df_df[(df_dm.index >= TXx_idx_minus_four) &
                 (df_dm.index <= TXx_idx)].Qle.values
    Qhs = df_df[(df_dm.index >= TXx_idx_minus_four) &
                (df_dm.index <= TXx_idx)].Qh.values
    B = Qhs / Qles

    if len(Tairs) != 5:
        # Drop this event and try again
        df_dm = df_dm[(df_dm.index < TXx_idx_minus_four) |
                       (df_dm.index > TXx_idx)]
        df_df = df_df[(df_df.index < TXx_idx_minus_four) |
                       (df_df.index > TXx_idx)]

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

def get_second_hottest_day(df_flx, df_met):
    df_dm = df_met.resample("D").max()
    df_df = df_flx.resample("D").mean()

    TXx = df_dm.sort_values("Tair", ascending=False)[:1].Tair.values[0]
    TXx_idx = df_dm.sort_values("Tair", ascending=False)[:1].index.values[0]
    TXx_idx_minus_four= TXx_idx - pd.Timedelta(4, unit='d')

    # Drop the hottest event
    df_dm = df_dm[(df_dm.index < TXx_idx_minus_four) |
                   (df_dm.index > TXx_idx)]
    df_df = df_df[(df_df.index < TXx_idx_minus_four) |
                   (df_df.index > TXx_idx)]

    # Then get next TXx
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

    if len(Tairs) != 5:
        # Drop this event and try again
        df_dm = df_dm[(df_dm.index < TXx_idx_minus_four) |
                       (df_dm.index > TXx_idx)]
        df_df = df_df[(df_df.index < TXx_idx_minus_four) |
                       (df_df.index > TXx_idx)]

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

    pfts = ["SAV","EBF","TRF","TRF","EBF","GRA","SAV",\
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

def open_file(flux_fn, met_fn, oz_flux=True):
    site = os.path.basename(flux_fn).split("OzFlux")[0]

    ds = xr.open_dataset(flux_fn)
    #print(ds)
    df_flx = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()
    df_flx = df_flx.reset_index()
    df_flx = df_flx.set_index('time')

    ds = xr.open_dataset(met_fn)
    df_met = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()
    df_met = df_met.reset_index()
    df_met = df_met.set_index('time')

    return (site, df_flx, df_met)

if __name__ == "__main__":

    oz_flux = True
    if oz_flux:
        flux_dir = "/Users/mdekauwe/research/OzFlux"
        ofname = "ozflux.csv"
    else:
        flux_dir = "/srv/ccrc/data04/z3509830/Fluxnet_data/Data_for_Jiafu/Daily/Nc_files"
        flux_dir = "/Users/mdekauwe/Desktop/test"
        ofname = "fluxnet2015.csv"
    main(flux_dir, ofname, oz_flux=oz_flux)
