import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import NegativeBinomial

print("Starting analysis...")

# 1. Load and Filter CDC Data to ONLY Four Corners States
cdc = pd.read_csv('cdc_hantavirus_1993_2023.csv')
cdc = cdc.rename(columns={'state': 'county', 'cases': 'cases'})
fc_states = ['Arizona', 'Colorado', 'New Mexico', 'Utah', 'Nevada']
cdc_fc = cdc[cdc['county'].isin(fc_states)].copy()

# 2. Load and Process Weather Data
weather = pd.read_csv('4328282.csv', dtype=str)
weather['year'] = weather['DATE'].str[:4].astype(int)
weather['PRCP'] = pd.to_numeric(weather['PRCP'], errors='coerce')
weather['TAVG'] = pd.to_numeric(weather['TAVG'], errors='coerce')
annual_weather = weather.groupby('year').agg({'PRCP': 'sum', 'TAVG': 'mean'}).reset_index()

# 3. Merge and Create Lags
merged = pd.merge(cdc_fc, annual_weather, on='year', how='inner')
merged = merged.sort_values(['county', 'year'])

# Create 1-year lags (approx 12 months)
merged['precip_lag_12'] = merged.groupby('county')['PRCP'].shift(1)
merged['temp_lag_12'] = merged.groupby('county')['TAVG'].shift(1)
merged = merged.dropna()

print(f"Total rows ready for modeling: {len(merged)}")
print(f"Years in data: {sorted(merged['year'].unique())}")

# 4. Run Models and Print Plain Text
print("\n--- MODEL RESULTS ---")
models_to_test = {
    'precip_lag_12': 'Precipitation 1-Year Lag', 
    'temp_lag_12': 'Temperature 1-Year Lag'
}

for col, name in models_to_test.items():
    X = sm.add_constant(merged[[col]])
    y = merged['cases']
    try:
        res = NegativeBinomial(y, X).fit(disp=0)
        print(f"{name} AIC Score: {round(res.aic, 2)}")
    except Exception as e:
        print(f"{name} failed to run.")

# 5. Print Correlation Safely
print("\n--- CORRELATIONS ---")
corr_p = merged['cases'].corr(merged['precip_lag_12'])
corr_t = merged['cases'].corr(merged['temp_lag_12'])
print(f"Correlation (Cases vs Precip Lag): {round(corr_p, 3)}")
print(f"Correlation (Cases vs Temp Lag): {round(corr_t, 3)}")
print("\nDone! Type these numbers to your assistant.")