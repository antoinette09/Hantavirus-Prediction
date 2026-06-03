import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import NegativeBinomial
import matplotlib.pyplot as plt
import seaborn as sns

print("Generating final professional graphs...")

# 1. Load and prep the real data
cdc = pd.read_csv('cdc_hantavirus_1993_2023.csv')
cdc = cdc.rename(columns={'state': 'county', 'cases': 'cases'})
fc_states = ['Arizona', 'Colorado', 'New Mexico', 'Utah', 'Nevada']
cdc_fc = cdc[cdc['county'].isin(fc_states)].copy()

weather = pd.read_csv('4328282.csv', dtype=str)
weather['year'] = weather['DATE'].str[:4].astype(int)
weather['PRCP'] = pd.to_numeric(weather['PRCP'], errors='coerce')
weather['TAVG'] = pd.to_numeric(weather['TAVG'], errors='coerce')
annual_weather = weather.groupby('year').agg({'PRCP': 'sum', 'TAVG': 'mean'}).reset_index()

merged = pd.merge(cdc_fc, annual_weather, on='year', how='inner')
merged = merged.sort_values(['county', 'year'])
merged['precip_lag_12'] = merged.groupby('county')['PRCP'].shift(1)
merged['temp_lag_12'] = merged.groupby('county')['TAVG'].shift(1)
merged = merged.dropna()

# 2. Run the models to get the AIC scores
X_p = sm.add_constant(merged[['precip_lag_12']])
X_t = sm.add_constant(merged[['temp_lag_12']])
y = merged['cases']

model_p = NegativeBinomial(y, X_p).fit(disp=0)
model_t = NegativeBinomial(y, X_t).fit(disp=0)

# ==========================================
# GRAPH 1: AIC Comparison Bar Chart
# ==========================================
plt.figure(figsize=(8, 5))
models = ['Precipitation\n(1-Year Lag)', 'Temperature\n(1-Year Lag)']
aics = [model_p.aic, model_t.aic]
colors = ['#3498db', '#e74c3c'] # Blue for rain, Red for temp

bars = plt.bar(models, aics, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5)
plt.ylabel('AIC Score (Lower is Better)', fontsize=12, fontweight='bold')
plt.title('Model Comparison: Predicting Hantavirus in the Four Corners', fontsize=14, fontweight='bold')

# Add the exact numbers on top of the bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), 
             ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('final_aic_comparison.png', dpi=300)
print("✅ Saved 'final_aic_comparison.png'")

# ==========================================
# GRAPH 2: Correlation Heatmap
# ==========================================
plt.figure(figsize=(8, 6))
corr_cols = ['cases', 'PRCP', 'TAVG', 'precip_lag_12', 'temp_lag_12']
corr_data = merged[corr_cols].corr()

# Rename for a professional-looking heatmap
corr_data.columns = ['Hanta Cases', 'Current Rain', 'Current Temp', 'Rain (1 Yr Lag)', 'Temp (1 Yr Lag)']
corr_data.index = ['Hanta Cases', 'Current Rain', 'Current Temp', 'Rain (1 Yr Lag)', 'Temp (1 Yr Lag)']

# We set vmin and vmax to -0.5 and 0.5 so the colors look balanced
sns.heatmap(corr_data, annot=True, cmap='coolwarm', vmin=-0.2, vmax=0.5, center=0, 
            fmt='.3f', linewidths=1, linecolor='black', annot_kws={"size": 11})

plt.title('Correlation Matrix: Climate Variables vs. Hantavirus Cases', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('final_correlation_heatmap.png', dpi=300)
print("✅ Saved 'final_correlation_heatmap.png'")

print("\n🎉 ALL DONE! Check your folder for the two image files!")