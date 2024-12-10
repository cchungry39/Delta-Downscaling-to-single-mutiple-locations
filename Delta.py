#!/usr/bin/env python
# coding: utf-8

# Import required libraries
import xarray as xr  # For handling NetCDF climate data
import os, glob  # File operation libraries
import matplotlib.pyplot as plt  # For plotting
import numpy as np  # For mathematical computations
import pandas as pd  # For data processing
import pymannkendall  # For Mann-Kendall trend analysis (not used here)
from sklearn.metrics import r2_score, mean_squared_error  # For evaluating regression model performance (not used here)
import warnings  # For controlling warnings
import tkinter as tk
from tkinter import filedialog

warnings.filterwarnings("ignore")  # Ignore warning messages

# Set working directory to the path where the data is stored
os.chdir("working directory")  # For Windows path, ensure to use forward slashes or escape backslashes

def get_file_path(file_type, title):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title=title, filetypes=file_type)

# Read climate model data (historical data)
file_path = get_file_path([("NetCDF files", "*.nc"), ("all files", "*.*")], "Select the historical GCM Data File")
ds_pr_gcm_raw = xr.open_dataset(file_path)
ds_pr_gcm_raw = ds_pr_gcm_raw.sel(time=ds_pr_gcm_raw.time.dt.year.isin(range(1961, 2015)))

# Read observed data (historical precipitation data)
file_path = get_file_path([("NetCDF files", "*.nc"), ("all files", "*.*")], "Select the observed Data File")
ds_pr_obs_raw = xr.open_dataset(file_path)
ds_pr_obs_19792014 = ds_pr_obs_raw.sel(time=ds_pr_obs_raw.time.dt.year.isin(range(1961, 2015)))

# Read latitude and longitude data
csv_file_path = get_file_path([("CSV files", "*.csv"), ("all files", "*.*")], "Select the Point.CSV File")
lat_lon_df = pd.read_csv(csv_file_path)

# Read SSP GCM data
file_path1 = get_file_path([("NetCDF files", "*.nc"), ("all files", "*.*")], "Select the SSP GCM Data File")
df_pr_gcm_raw1 = xr.open_dataset(file_path1)

# General function for downscaling and saving data
def process_and_save_gcm_data(ds_pr_gcm_raw, ds_pr_obs_19792014, model_name, lat_lon_df, delta_pr, ssp=False):
    for index, row in lat_lon_df.iterrows():
        lon, lat = row['lon'], row['lat']  # Get the longitude and latitude of each point

        # Interpolate climate model data: extract data at the given latitude and longitude
        ds_pr_gcm = ds_pr_gcm_raw.interp(lon=lon, lat=lat)

        # Interpolate observed data: extract data at the given latitude and longitude
        ds_pr_obs = ds_pr_obs_19792014.interp(lon=lon, lat=lat)

        # Calculate monthly mean and deviation
        ds_pr_obs_monthlymean = ds_pr_obs.resample(time="1M").mean().pre  # Calculate monthly mean for observed data
        ds_pr_gcm = ds_pr_gcm.pr * 86400  # Convert climate model precipitation data from "mm/day" to standard "mm/day"
        # For missing leap year data, use MS resampling to obtain monthly starting data
        ds_pr_gcm_monthlymean = ds_pr_gcm.resample(time="MS").mean()

        # Calculate precipitation deviation for each month (GCM/Obs)
        delta_pr = ds_pr_gcm_monthlymean.groupby('time.month').mean() / ds_pr_obs_monthlymean.groupby('time.month').mean()
        delta_pr = delta_pr.values.squeeze()  # Calculate deviation and convert to a 1D array

        # Downscaling operation: adjust the climate model data based on delta_pr
        result = []  # List to store processed monthly precipitation data
        for i in range(1, 13):  # Loop over each month
            tmp_pr = ds_pr_gcm.sel(time=ds_pr_gcm.time.dt.month == i)  # Extract data for the current month
            gcm_pr_downscaled = tmp_pr * delta_pr[i - 1]  # Adjust the climate model data according to the deviation
            result.append(gcm_pr_downscaled)  # Store the data for the current month in the result list

        # Merge data for each month to get the final downscaled data
        gcm_pr_downscaled_final = xr.merge(result)

        # Construct filename
        first_date = str(gcm_pr_downscaled_final.time.values[0])[:10]  # Get the date of the first time point
        model_suffix = "_ssp126" if ssp else "_his"
        save_path = filedialog.asksaveasfilename(defaultextension=".nc", filetypes=(("NetCDF files", "*.nc"), ("all files", "*.*")))
        if save_path:  # Only save if the user selects a path
            gcm_pr_downscaled_final.to_netcdf(save_path)
            print(f"Processed {lon}, {lat}; Saved as {save_path}")

# Process historical data
process_and_save_gcm_data(ds_pr_gcm_raw, ds_pr_obs_19792014, "CanESM5pr", lat_lon_df, delta_pr)

# Process SSP126 data
df_pr_gcm_raw1 = df_pr_gcm_raw1.sel(time=df_pr_gcm_raw1.time.dt.year.isin(range(2015, 2101)))
process_and_save_gcm_data(df_pr_gcm_raw1, ds_pr_obs_19792014, "CanESM5pr", lat_lon_df, delta_pr, ssp=True)
