#!/usr/bin/env python

"""
For each of the Ozflux sites, plot LE & GPP as a function of Tair to probe
decoupling

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (08.11.2017)"
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

    for fname in glob.glob(os.path.join(flux_dir, "*_flux.nc")):
        site = os.path.basename(fname).split("OzFlux")[0]
        ds = xr.open_dataset(fname)
        df = ds.to_dataframe()

        df = ds.squeeze(dim=["x","y"], drop=True).to_dataframe()

        col_names = list(df)
        print(col_names)
        print(site)

        sys.exit()

def calc_pet(Qh, Qle):
    """ Energy only PET

    This follows Milly and Dunne but I'm dropping the G bit for now

    Reference:
    ==========
    * Milly & Dunne (2016) Nature Climate Change, DOI: 10.1038/NCLIMATE3046

    """
    pet = 0.8 * (Qh + Qle)

    return pet

if __name__ == "__main__":

    flux_dir = "/Users/mdekauwe/research/OzFlux"
    main(flux_dir)
