import pandas as pd

print("Processing 4328282.csv and CDC data...")

# 1. Load and clean the Weather Data
weather = pd.read_csv('4328282.csv', dtype=str)

# Clean up quotes and spaces in column names
weather.columns = [c.strip().replace('"', '') for c in weather.columns]
weather['DATE'] = weather['DATE'].str.replace('"', '')

# Extract year from the YYYY-MM format
weather['year'] = weather['DATE'].str[:4].astype(int)

# Convert to numbers (turns empty missing spots into NaN)
weather['PRCP'] = pd.to_numeric(weather['PRCP'], errors='coerce')
weather['TAVG'] = pd.to_numeric(weather['TAVG'], errors='coerce')

# Aggregate to Annual (Sum precipitation, Average temperature)
annual_weather = weather.groupby('year').agg({
    'PRCP': 'sum',
    'TAVG': 'mean'
}).reset_index()
annual_weather.columns = ['year', 'precipitation', 'avg_temperature']

# 2. Load and clean CDC Data
# (Make sure you generated cdc_hantavirus_1993_2023.csv in the previous step!)
cdc = pd.read_csv('cdc_hantavirus_1993_2023.csv')

# Filter to Four Corners states
fc_states = ['Arizona', 'Colorado', 'New Mexico', 'Utah', 'Nevada']
cdc_fc = cdc[cdc['state'].isin(fc_states)].copy()

# Aggregate to Annual Total Cases
cdc_annual = cdc_fc.groupby('year')['cases'].sum().reset_index()
cdc_annual.columns = ['year', 'hantavirus_cases']

# 3. Merge datasets
merged = pd.merge(cdc_annual, annual_weather, on='year', how='inner')
merged = merged.sort_values('year').reset_index(drop=True)

# 4. Create Lag Variables
merged['precip_lag_12'] = merged['precipitation'].shift(1)
merged['temp_lag_12'] = merged['avg_temperature'].shift(1)

# Drop the first row (1993) because it doesn't have a 1992 lag in the merged CDC data 
# (Wait, weather starts in 1992, so 1993 WILL have a lag! But we drop NaNs just in case)
merged = merged.dropna().reset_index(drop=True)

# 5. Format for the table
merged['precipitation'] = merged['precipitation'].round(2)
merged['avg_temperature'] = merged['avg_temperature'].round(2)
merged['precip_lag_12'] = merged['precip_lag_12'].round(2)
merged['temp_lag_12'] = merged['temp_lag_12'].round(2)

# 6. PRINT THE MARKDOWN TABLE FOR YOUR GOOGLE DOC
print("\n" + "="*70)
print("COPY THE TABLE BELOW INTO YOUR GOOGLE DOC:")
print("="*70)
print("| Year | HPS_Cases | Precip_Current | Temp_Current | Precip_Lag_12 | Temp_Lag_12 |")
print("|------|-----------|----------------|--------------|---------------|-------------|")

for _, row in merged.iterrows():
    print(f"| {int(row['year'])} | {int(row['hantavirus_cases'])} | {row['precipitation']} | {row['avg_temperature']} | {row['precip_lag_12']} | {row['temp_lag_12']} |")

# Also save it as a CSV just in case
merged.to_csv('final_data_alignment_table.csv', index=False)
print("\n✅ Saved as 'final_data_alignment_table.csv'")