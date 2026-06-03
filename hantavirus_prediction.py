import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import NegativeBinomial
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# 1. LOAD REAL CDC DATA (1993-2023)
# ---------------------------------------------------------
def load_cdc_data():
    """Loads the fully parsed 30-year CDC dataset."""
    df = pd.read_csv('cdc_hantavirus_1993_2023.csv')
    
    df = df.rename(columns={'state': 'county', 'cases': 'hantavirus_cases'})
    df = df[df['county'] != 'Total']
    df['hantavirus_cases'] = pd.to_numeric(df['hantavirus_cases'], errors='coerce')
    df = df.dropna(subset=['hantavirus_cases'])
    df['hantavirus_cases'] = df['hantavirus_cases'].astype(int)
    
    # --- ADD THESE TWO LINES HERE ---
    four_corners = ['Arizona', 'Colorado', 'New Mexico', 'Utah']
    df = df[df['county'].isin(four_corners)]
    # --------------------------------
    
    print("✅ CDC Data Loaded Successfully!")
    print(f"Total records: {len(df)}")
    
    return df

# ---------------------------------------------------------
# 2. LOAD REAL NOAA WEATHER DATA (1992-2023)
# ---------------------------------------------------------
def load_real_noaa_weather():
    """Load and process the REAL NOAA monthly weather data from 4328282.csv"""
    
    # 1. Read the CSV (dtype=str prevents mixed-type warnings)
    weather_df = pd.read_csv('4328282.csv', header=0, dtype=str)
    weather_df.columns = weather_df.columns.str.strip()
    
    # 2. Extract Year from the DATE column (format is 'YYYY-MM')
    weather_df['year'] = weather_df['DATE'].str[:4].astype(int)
    
    # 3. Convert numeric columns (handles empty missing values safely)
    for col in ['PRCP', 'TAVG']:
        if col in weather_df.columns:
            weather_df[col] = pd.to_numeric(weather_df[col], errors='coerce')
            
    # 4. Aggregate by year to match the CDC annual data
    # Note: Since you selected "Standard" units on NOAA, PRCP is already in inches 
    # and TAVG is already in Fahrenheit!
    annual_weather = weather_df.groupby('year').agg({
        'PRCP': 'sum',    # Sum daily/monthly precip to get total annual inches
        'TAVG': 'mean'    # Average the monthly temps to get annual avg temp
    }).reset_index()
    
    annual_weather = annual_weather.rename(columns={
        'PRCP': 'precipitation',
        'TAVG': 'avg_temperature'
    })
    
    # Drop any years that have no data
    annual_weather = annual_weather.dropna()
    
    print("\n✅ Real NOAA Weather Data Loaded:")
    print(annual_weather.head())
    
    return annual_weather[['year', 'precipitation', 'avg_temperature']]

# ---------------------------------------------------------
# 3. MERGE DATASETS
# ---------------------------------------------------------
def merge_datasets(cases_df, climate_df):
    """Merge hantavirus cases with climate data"""
    
    # We merge ONLY on 'year' because our weather data is a regional proxy (Cortez, CO)
    # and we are applying it to the regional Four Corners states.
    merged_df = pd.merge(
        cases_df, 
        climate_df, 
        on=['year'], 
        how='inner' 
    )
    
    print(f"\n✅ Merged dataset: {len(merged_df)} records")
    
    return merged_df

# ---------------------------------------------------------
# 4. CREATE LAG VARIABLES
# ---------------------------------------------------------
def create_lag_variables(df):
    """Create 12-month (1-year) and 18-month (approx 2-year) lag variables"""
    
    df_sorted = df.sort_values(by=['county', 'year']).copy()
    
    for state in df_sorted['county'].unique():
        mask = df_sorted['county'] == state
        
        # 12-month lag (shift by 1 year)
        df_sorted.loc[mask, 'precip_lag_12'] = df_sorted.loc[mask, 'precipitation'].shift(1)
        df_sorted.loc[mask, 'temp_lag_12'] = df_sorted.loc[mask, 'avg_temperature'].shift(1)
        
        # 18/24-month lag (shift by 2 years)
        df_sorted.loc[mask, 'precip_lag_18'] = df_sorted.loc[mask, 'precipitation'].shift(2)
        df_sorted.loc[mask, 'temp_lag_18'] = df_sorted.loc[mask, 'avg_temperature'].shift(2)
    
    # Remove rows with missing lag values
    df_clean = df_sorted.dropna()
    
    print(f"\n✅ After creating lags: {len(df_clean)} records ready for modeling")
    
    return df_clean

# ---------------------------------------------------------
# 5. RUN NEGATIVE BINOMIAL MODELS
# ---------------------------------------------------------
def run_negative_binomial_model(df, predictor, outcome='hantavirus_cases'):
    """Fit a Negative Binomial regression model"""
    
    X = df[[predictor]]
    X = sm.add_constant(X)  # Add intercept
    y = df[outcome]
    
    try:
        model = NegativeBinomial(y, X).fit(disp=0)
        
        return {
            'predictor': predictor,
            'aic': model.aic,
            'pseudo_r2': model.prsquared,
            'coefficient': model.params[predictor],
            'p_value': model.pvalues[predictor],
            'irr': np.exp(model.params[predictor])  # Incidence Rate Ratio
        }
    except Exception as e:
        return None

# ---------------------------------------------------------
# 6. MAIN ANALYSIS PIPELINE
# ---------------------------------------------------------
def main():
    print("="*60)
    print("HANTAVIRUS PREDICTION ANALYSIS (FINAL VERSION)")
    print("="*60)
    
    # Step 1: Load real data
    cases_df = load_cdc_data()
    climate_df = load_real_noaa_weather()
    
    # Step 2: Merge and create lags
    merged_df = merge_datasets(cases_df, climate_df)
    df_lagged = create_lag_variables(merged_df)
    
    # Step 3: Test models
    models_to_test = [
        'precip_lag_12',  # 12-month lag precipitation
        'precip_lag_18',  # 18-month lag precipitation
        'temp_lag_12',    # 12-month lag temperature
        'temp_lag_18',    # 18-month lag temperature
    ]
    
    results = []
    print("\n" + "="*60)
    print("RUNNING STATISTICAL MODELS")
    print("="*60)
    
    for predictor in models_to_test:
        result = run_negative_binomial_model(df_lagged, predictor)
        if result:
            results.append(result)
            print(f"Tested {predictor}: AIC = {result['aic']:.2f}")
    
    # Step 4: Compare and visualize
    results_df = pd.DataFrame(results).sort_values('aic')
    
    best_model = results_df.iloc[0]
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"🏆 Best Predictor: {best_model['predictor']}")
    print(f"   AIC Score: {best_model['aic']:.2f} (Lower is better)")
    print(f"   P-value: {best_model['p_value']:.4f}")
    
    # Create Heatmap
    plt.figure(figsize=(8, 6))
    corr_cols = ['hantavirus_cases', 'precipitation', 'avg_temperature', 
                 'precip_lag_12', 'precip_lag_18']
    sns.heatmap(df_lagged[corr_cols].corr(), annot=True, cmap='coolwarm', center=0, fmt='.2f')
    plt.title('Correlation Matrix: Real Climate Data vs Hantavirus Cases')
    plt.tight_layout()
    plt.savefig('real_correlation_heatmap.png', dpi=300)
    print("\n✅ Saved 'real_correlation_heatmap.png'")
    
    # Create AIC Bar Chart
    plt.figure(figsize=(10, 6))
    colors = ['skyblue' if 'precip' in x else 'salmon' for x in results_df['predictor']]
    plt.bar(range(len(results_df)), results_df['aic'], color=colors, alpha=0.7)
    plt.xticks(range(len(results_df)), results_df['predictor'], rotation=45, ha='right')
    plt.ylabel('AIC Score (lower is better)')
    plt.title('Model Comparison: Which Climate Lag Best Predicts Hantavirus?')
    plt.tight_layout()
    plt.savefig('real_model_comparison.png', dpi=300)
    print("✅ Saved 'real_model_comparison.png'")
    
    print("\n ANALYSIS COMPLETE! Check your folder for the graphs.")

if __name__ == "__main__":
    main()