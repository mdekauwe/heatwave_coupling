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

def main(flux_dir, cable_dir):

    sites = ["Tumbarumba"]

    pfts = ["EBF"]

    d = dict(zip(sites, pfts))

    plot_dir = "plots"
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)

    cable_files = sorted(glob.glob(os.path.join(cable_dir, "*_out.nc")))

    for cable_fn in cable_files:
        (site, df_mod) = open_file(cable_fn)
        if site == "Tumbarumba":
            df_mod = resample_timestep(df_mod)
            plt.plot(df_mod.index, df_mod.TVeg)
            plt.show()



def open_file(cable_fn):
    site = os.path.basename(cable_fn).split("OzFlux")[0]
    ds = xr.open_dataset(cable_fn)
    time = pd.to_datetime(ds.time.values)
    df_mod = ds[['Qle','TVeg']].squeeze(drop=True).to_dataframe()
    df_mod['time'] = time
    df_mod = df_mod.set_index('time')
    print(time)
    return (site, df_mod)

def resample_timestep(df):

    SEC_2_HOUR = 3600.

    # kg/m2/s -> mm/hour
    df['TVeg'] *= SEC_2_HOUR
    method = {'TVeg':'sum', "Qle":"mean"}
    df = df.resample("D").agg(method)

    return df

if __name__ == "__main__":

    flux_dir = "/Users/mdekauwe/research/OzFlux"
    cable_dir = "/Users/mdekauwe/research/CABLE_runs/runs/ozflux/outputs"

    main(flux_dir, cable_dir)
