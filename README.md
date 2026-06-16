Hantavirus Prediction Using Climate Data (1993-2023)
Overview
Investigates whether historical weather data can predict Hantavirus Pulmonary Syndrome (HPS) outbreaks in the Four Corners region. Analyzes 31 years of CDC surveillance data alongside NOAA climate records to test the "bottom-up ecological cascade" hypothesis—increased precipitation promotes vegetation growth, leading to larger deer mouse populations and increased human exposure risk.

Key Findings
Precipitation is a better predictor than temperature (lower AIC score)
12-month lag shows strongest correlation with HPS cases
Statistically significant relationship between antecedent rainfall and cases
Supports ecological cascade theory: Wet conditions → more vegetation → larger rodent populations → increased human risk
Data Sources
Source	Details
CDC	National Notifiable Diseases Surveillance System (NNDSS), 1993-2023
NOAA	Cortez, CO weather station (USC00051886), 1992-2023
Setup
Install dependencies
pip install pandas numpy statsmodels matplotlib seaborn
Run the analysis
bash

# First time (generates CSV from raw data)
python hantavirus_analysis.py --generate-csv

# After that
python hantavirus_analysis.py
Repository Structure
text

hantavirus-prediction/
├── hantavirus_analysis.py      # Main script (all functionality)
├── raw_cdc_data.txt            # Original CDC tables (source data)
├── 4328282.csv                 # NOAA weather data (Cortez, CO)
├── cdc_hantavirus_1993_2023.csv # Generated CDC case data
├── final_aic_comparison.png    # Output: Model comparison chart
├── final_correlation_heatmap.png # Output: Correlation matrix
└── README.md
Methodology
Parse raw CDC tables into structured data
Aggregate NOAA monthly data to annual totals
Merge datasets and create 12-month lag variables
Fit Negative Binomial regression models (appropriate for overdispersed count data)
Compare models using Akaike Information Criterion (AIC)
Output Graphs
AIC Comparison Bar Chart
Compares precipitation vs. temperature lag models—lower AIC indicates better fit.

Correlation Heatmap
Shows relationships between climate variables (current and lagged) and HPS case counts.

Public Health Implications
This research demonstrates the feasibility of climate-based early warning systems for hantavirus. Public health officials could:

Monitor precipitation patterns to identify high-risk periods 12 months in advance
Target prevention campaigns to high-risk counties following wet years
Allocate surveillance and education resources more effectively
Skills Demonstrated
Data Science: Data cleaning, feature engineering, statistical modeling
Python: pandas, NumPy, statsmodels, matplotlib, seaborn
Statistics: Negative Binomial Regression, AIC model selection
Epidemiology: Disease surveillance, ecological modeling
Future Directions
Expand to county-level analysis with higher spatial resolution
Incorporate vegetation indices (NDVI) from satellite imagery
Test machine learning approaches (Random Forest, Lasso)
Include socioeconomic and land use variables
Develop real-time forecasting dashboard
References
CDC. (2023). Hantavirus Pulmonary Syndrome Surveillance Data
NOAA National Centers for Environmental Information. (2023). Climate Data Online
Mills, J. N., et al. (1999). "Hantavirus reservoirs and the ecology of hantavirus pulmonary syndrome." Emerging Infectious Diseases
License
Public domain data from U.S. Government agencies (CDC, NOAA). Code available for educational and research purposes.

Note: This research is for educational purposes and does not constitute medical advice.
```