import pandas as pd

print("="*60)
print("DEBUGGING YOUR DATA")
print("="*60)

# Check CDC data
try:
    cdc_df = pd.read_csv('cdc_hantavirus_1993_2023.csv')
    print(f"\n✅ CDC file loaded: {len(cdc_df)} records")
    print(f"Columns: {list(cdc_df.columns)}")
    print(f"Years: {sorted(cdc_df['year'].unique()) if 'year' in cdc_df.columns else 'NO YEAR COLUMN'}")
    print(f"States: {cdc_df['state'].unique() if 'state' in cdc_df.columns else 'NO STATE COLUMN'}")
except Exception as e:
    print(f"\n❌ CDC file error: {e}")

# Check Weather data  
try:
    weather_df = pd.read_csv('4328282.csv')
    print(f"\n✅ Weather file loaded: {len(weather_df)} records")
    print(f"Columns: {list(weather_df.columns)}")
    print(f"Date range: {weather_df['DATE'].min()} to {weather_df['DATE'].max()}")
except Exception as e:
    print(f"\n❌ Weather file error: {e}")

print("\n" + "="*60)