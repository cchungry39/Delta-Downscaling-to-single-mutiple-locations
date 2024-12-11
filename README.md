# Delta-Downscaling-to-single-mutiple-locations
The `delta.exe` in the `dist` directory is packaged based on `delta.py`.

This Python script is designed for downscaling climate model precipitation data to a finer resolution based on historical observations.
# 1. Calculate Monthly Mean for Observed and Climate Model Data

ds_pr_obs_monthlymean = ds_pr_obs.resample(time="1M").mean().pre  

ds_pr_gcm = ds_pr_gcm.pr * 86400  

ds_pr_gcm_monthlymean = ds_pr_gcm.resample(time="MS").mean()

**Description:**
The first line calculates the monthly mean precipitation from the observed data (ds_pr_obs).
The second line converts the precipitation data from the climate model (ds_pr_gcm) from units of "mm/day" to the standard "mm/day" (by multiplying by 86400, which is the number of seconds in a day).
The third line uses "Month Start" (MS) resampling to compute the monthly mean for the climate model precipitation data, handling potential missing data from leap years.



# 2.Calculate Precipitation Deviation (GCM/Obs)
delta_pr = ds_pr_gcm_monthlymean.groupby('time.month').mean() / ds_pr_obs_monthlymean.groupby('time.month').mean()

delta_pr = delta_pr.values.squeeze()  

**Description:**
This part calculates the monthly precipitation deviation (ratio of GCM to Observed data) by dividing the monthly means of the climate model by those of the observed data. 
The result (delta_pr) is then converted to a 1D array for easier use in the downscaling process.


# 3. Downscale the Climate Model Data
result = []

for i in range(1, 13): 

tmp_pr = ds_pr_gcm.sel(time=ds_pr_gcm.time.dt.month == i) 

gcm_pr_downscaled = tmp_pr * delta_pr[i - 1]  

result.append(gcm_pr_downscaled) 

**Description:**
A loop runs over all 12 months of the year.
For each month, the climate model precipitation data (ds_pr_gcm) is extracted, and the monthly precipitation is adjusted by multiplying it with the corresponding deviation (delta_pr).
The downscaled precipitation data for each month is stored in the result list.

# 4. Software
The .exe file are attached to the release

# 5. Data requist
(1) Historical climate data (GCMs,nc)

(2) Projected climate data (GCMs,nc)

(3) Observed data (nc)

(4) Locations with latitude and longitute(csv)
