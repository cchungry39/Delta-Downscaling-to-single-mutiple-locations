# Delta-Downscaling-to-single-mutiple-locations
This Python script is designed for downscaling climate model precipitation data to a finer resolution based on historical observations.
# 1. Calculate Monthly Mean for Observed and Climate Model Data

ds_pr_obs_monthlymean = ds_pr_obs.resample(time="1M").mean().pre  # Calculate monthly mean for observed data

ds_pr_gcm = ds_pr_gcm.pr * 86400  # Convert climate model precipitation data from "mm/day" to standard "mm/day"

ds_pr_gcm_monthlymean = ds_pr_gcm.resample(time="MS").mean()

**Description:**
The first line calculates the monthly mean precipitation from the observed data (ds_pr_obs).
The second line converts the precipitation data from the climate model (ds_pr_gcm) from units of "mm/day" to the standard "mm/day" (by multiplying by 86400, which is the number of seconds in a day).
The third line uses "Month Start" (MS) resampling to compute the monthly mean for the climate model precipitation data, handling potential missing data from leap years.



# 2.Calculate Precipitation Deviation (GCM/Obs)
delta_pr = ds_pr_gcm_monthlymean.groupby('time.month').mean() / ds_pr_obs_monthlymean.groupby('time.month').mean()

delta_pr = delta_pr.values.squeeze()  # Calculate deviation and convert to a 1D array

**Description:**
This part calculates the monthly precipitation deviation (ratio of GCM to Observed data) by dividing the monthly means of the climate model by those of the observed data. 
The result (delta_pr) is then converted to a 1D array for easier use in the downscaling process.


# 3. Downscale the Climate Model Data
result = []  # List to store processed monthly precipitation data

for i in range(1, 13):  # Loop over each month

tmp_pr = ds_pr_gcm.sel(time=ds_pr_gcm.time.dt.month == i)  # Extract data for the current month

gcm_pr_downscaled = tmp_pr * delta_pr[i - 1]  # Adjust the climate model data according to the deviation

result.append(gcm_pr_downscaled)  # Store the data for the current month in the result list

**Description:**
A loop runs over all 12 months of the year.
For each month, the climate model precipitation data (ds_pr_gcm) is extracted, and the monthly precipitation is adjusted by multiplying it with the corresponding deviation (delta_pr).
The downscaled precipitation data for each month is stored in the result list.
