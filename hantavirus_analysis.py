import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import NegativeBinomial
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import argparse

# Constants
FOUR_CORNERS = ['Arizona', 'Colorado', 'New Mexico', 'Utah', 'Nevada']
CDC_FILE = 'cdc_hantavirus_1993_2023.csv'
WEATHER_FILE = '4328282.csv'
RAW_CDC_FILE = 'raw_cdc_data.txt'

def generate_cdc_csv():
    """Parse raw CDC data text file into CSV"""
    if not os.path.exists(RAW_CDC_FILE):
        print(f"❌ Error: {RAW_CDC_FILE} not found")
        return False
    
    with open(RAW_CDC_FILE, 'r') as f:
        text = f.read()
    
    tables = re.split(r'Table of U\.S\. Hantavirus Cases by (\d{4}) \(All States\)', text)
    data = []
    
    for i in range(1, len(tables), 2):
        year = int(tables[i])
        for line in tables[i+1].strip().split('\n'):
            nums = re.findall(r'\d+', line)
            if len(nums) >= 4:
                state_name = re.split(r'\d+', line)[0].strip()
                if state_name and state_name not in ['State', 'Total', 'Year', 'Month']:
                    data.append({
                        'year': year,
                        'state': state_name,
                        'cases': int(nums[-1])
                    })
    
    pd.DataFrame(data).to_csv(CDC_FILE, index=False)
    print(f"✅ Created {CDC_FILE} with {len(data)} records")
    return True

def load_and_process_data():
    """Load and process CDC and weather data, return merged dataframe"""
    # Load and process CDC data
    cdc = pd.read_csv(CDC_FILE)
    cdc_fc = cdc[cdc['state'].isin(FOUR_CORNERS)].copy()
    
    # Load and process weather data
    weather = pd.read_csv(WEATHER_FILE, dtype=str)
    weather['year'] = weather['DATE'].str[:4].astype(int)
    weather['PRCP'] = pd.to_numeric(weather['PRCP'], errors='coerce')
    weather['TAVG'] = pd.to_numeric(weather['TAVG'], errors='coerce')
    annual_weather = weather.groupby('year').agg({'PRCP': 'sum', 'TAVG': 'mean'}).reset_index()
    
    # Merge and create lag variables
    merged = pd.merge(cdc_fc, annual_weather, on='year', how='inner')
    merged = merged.sort_values(['state', 'year'])
    merged['precip_lag_12'] = merged.groupby('state')['PRCP'].shift(1)
    merged['temp_lag_12'] = merged.groupby('state')['TAVG'].shift(1)
    
    return merged.dropna()

def run_models_and_generate_graphs(df):
    """Run Negative Binomial models and generate visualizations"""
    # Prepare data for modeling
    X_p = sm.add_constant(df[['precip_lag_12']])
    X_t = sm.add_constant(df[['temp_lag_12']])
    y = df['cases']
    
    # Fit models
    model_p = NegativeBinomial(y, X_p).fit(disp=0)
    model_t = NegativeBinomial(y, X_t).fit(disp=0)
    
    # Generate AIC comparison chart
    plt.figure(figsize=(8, 5))
    models = ['Precipitation\n(1-Year Lag)', 'Temperature\n(1-Year Lag)']
    aics = [model_p.aic, model_t.aic]
    colors = ['#3498db', '#e74c3c']
    
    bars = plt.bar(models, aics, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5)
    plt.ylabel('AIC Score (Lower is Better)', fontsize=12, fontweight='bold')
    plt.title('Model Comparison: Predicting Hantavirus in the Four Corners', fontsize=14, fontweight='bold')
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), 
                 ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('final_aic_comparison.png', dpi=300)
    print("✅ Saved 'final_aic_comparison.png'")
    
    # Generate correlation heatmap
    plt.figure(figsize=(8, 6))
    corr_cols = ['cases', 'PRCP', 'TAVG', 'precip_lag_12', 'temp_lag_12']
    corr_data = df[corr_cols].corr()
    
    # Rename for clarity
    new_names = ['Hanta Cases', 'Current Rain', 'Current Temp', 'Rain (1 Yr Lag)', 'Temp (1 Yr Lag)']
    corr_data.columns = new_names
    corr_data.index = new_names
    
    sns.heatmap(corr_data, annot=True, cmap='coolwarm', vmin=-0.2, vmax=0.5, center=0, 
                fmt='.3f', linewidths=1, linecolor='black', annot_kws={"size": 11})
    
    plt.title('Correlation Matrix: Climate Variables vs. Hantavirus Cases', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig('final_correlation_heatmap.png', dpi=300)
    print("✅ Saved 'final_correlation_heatmap.png'")
    
    # Print model summary
    print("\n" + "="*60)
    print("MODEL RESULTS SUMMARY")
    print("="*60)
    print(f"Precipitation Model AIC: {model_p.aic:.2f}")
    print(f"Temperature Model AIC: {model_t.aic:.2f}")
    print(f"\nBest model: {'Precipitation' if model_p.aic < model_t.aic else 'Temperature'}")
    print(f"IRR (Incidence Rate Ratio): {np.exp(model_p.params['precip_lag_12']):.4f}")
    print("(Interpretation: Each additional inch of precipitation is associated with a " 
          f"{(np.exp(model_p.params['precip_lag_12']) - 1) * 100:.1f}% increase in expected cases)")

def main():
    parser = argparse.ArgumentParser(description='Hantavirus Prediction Analysis')
    parser.add_argument('--generate-csv', action='store_true', 
                       help='Generate CDC CSV from raw text file')
    parser.add_argument('--skip-csv-check', action='store_true',
                       help='Skip checking if CSV exists (use with caution)')
    args = parser.parse_args()
    
    print("="*60)
    print("HANTAVIRUS PREDICTION ANALYSIS")
    print("="*60)
    
    # Generate CSV if requested
    if args.generate_csv:
        generate_cdc_csv()
    
    # Check if CDC CSV exists
    if not args.skip_csv_check and not os.path.exists(CDC_FILE):
        print(f"\n❌ Error: {CDC_FILE} not found")
        if os.path.exists(RAW_CDC_FILE):
            print("Run with --generate-csv to create it from raw data")
        return
    
    # Load and process data
    print("\nLoading and processing data...")
    try:
        merged_df = load_and_process_data()
        print(f"✅ Data loaded: {len(merged_df)} records")
        
        # Run models and generate graphs
        print("\nRunning models and generating graphs...")
        run_models_and_generate_graphs(merged_df)
        
        print("\n🎉 Analysis complete! Check your folder for the graph files.")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()