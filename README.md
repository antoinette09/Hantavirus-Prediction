# Hantavirus Prediction Using Climate Data (1993-2023)

## Project Overview
This research investigates whether historical weather data can predict Hantavirus Pulmonary Syndrome (HPS) outbreaks in the Four Corners region of the American Southwest. By analyzing 31 years of CDC surveillance data alongside NOAA climate records, this project tests the "bottom-up ecological cascade" hypothesis—the theory that increased precipitation promotes vegetation growth, leading to larger deer mouse populations and increased human exposure risk.

## Key Findings
✅ **Precipitation is a better predictor than temperature** (AIC: 499.87 vs 503.19)  
✅ **12-month lag shows strongest correlation** (r = 0.162)  
✅ **Statistically significant relationship** between antecedent rainfall and HPS cases  
✅ **Supports ecological cascade theory**: Wetter conditions → more vegetation → larger rodent populations → increased human risk

## Data Sources
- **Hantavirus Cases**: CDC National Notifiable Diseases Surveillance System (NNDSS), 1993-2023
  - 867 total cases across Four Corners states (AZ, CO, NM, UT, NV)
  - Peak outbreak: 1993 (48 cases)
  
- **Climate Data**: NOAA Climate Data Online, Cortez, CO weather station (USC00051886)
  - Monthly precipitation (inches) and temperature (°F)
  - 32 years of records (1992-2023)

## Methodology
1. **Data Cleaning**: Parsed raw CDC tables and NOAA monthly summaries
2. **Feature Engineering**: Created 12-month and 18-month lag variables for climate data
3. **Statistical Modeling**: Negative Binomial Regression (appropriate for overdispersed count data)
4. **Model Evaluation**: Akaike Information Criterion (AIC) for model selection

## Results Summary
| Model | Predictor | AIC Score | Correlation (r) |
|-------|-----------|-----------|-----------------|
| Best | Precipitation (12-month lag) | 499.87 | 0.162 |
| Alternative | Temperature (12-month lag) | 503.19 | -0.013 |

**Interpretation**: Each additional inch of precipitation is associated with a 3.9% increase in expected HPS cases one year later.

## Public Health Implications
This research demonstrates the feasibility of climate-based early warning systems for hantavirus. Public health officials could:
- Monitor precipitation patterns to identify high-risk periods 12 months in advance
- Target prevention campaigns to high-risk counties following wet years
- Allocate resources more effectively for surveillance and education

## Repository Structure
hantavirus-prediction/
├── hantavirus_prediction.py # Main analysis script
├── make_tables.py # Data alignment table generator
├── cdc_hantavirus_1993_2023.csv # Processed CDC case data
├── 4328282.csv # NOAA weather data (Cortez, CO)
├── raw_cdc_data.txt # Original CDC tables (1993-2023)
├── correlation_heatmap.png # Visualization: variable correlations
├── model_comparison.png # Visualization: AIC comparison
└── README.md # This file


## How to Run
1. **Install dependencies**:
```bash
pip install pandas numpy statsmodels matplotlib seaborn

Run the analysis:
python hantavirus_prediction.py

Generate data tables (for paper appendices):
python make_tables.py

Skills Demonstrated
📊 Data Science: Data cleaning, feature engineering, statistical modeling
🐍 Python Programming: pandas, NumPy, statsmodels, matplotlib
📈 Statistical Analysis: Negative Binomial Regression, AIC model selection
Epidemiology: Disease surveillance, ecological modeling
📝 Research: Scientific writing, data visualization, reproducibility
Future Directions
Expand to county-level analysis with higher spatial resolution
Incorporate vegetation indices (NDVI) from satellite imagery
Test machine learning approaches (Random Forest, Lasso regression)
Include socioeconomic and land use variables
Develop real-time forecasting dashboard
References
CDC. (2023). Hantavirus Pulmonary Syndrome Surveillance Data
NOAA National Centers for Environmental Information. (2023). Climate Data Online
Mills, J. N., et al. (1999). "Hantavirus reservoirs and the ecology of hantavirus pulmonary syndrome." Emerging Infectious Diseases
Author
[Your Name]
Rising High School Senior | Aspiring Data Scientist & Public Health Researcher
This project was completed independently as part of advanced scientific research.
License
This project uses public domain data from U.S. Government agencies (CDC, NOAA). Code is available for educational and research purposes.

Note: All data sources are publicly available. This research is for educational purposes and does not constitute medical advice.