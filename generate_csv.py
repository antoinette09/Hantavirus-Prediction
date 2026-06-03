import pandas as pd
import re

def generate_cdc_csv():
    print("Reading raw_cdc_data.txt...")
    with open('raw_cdc_data.txt', 'r') as f:
        text = f.read()
    
    # Split the text by the table headers
    tables = re.split(r'Table of U\.S\. Hantavirus Cases by (\d{4}) \(All States\)', text)
    
    data = []
    for i in range(1, len(tables), 2):
        year = int(tables[i])
        content = tables[i+1]
        
        lines = content.strip().split('\n')
        for line in lines:
            # Find all numbers in the line
            nums = re.findall(r'\d+', line)
            if len(nums) >= 4:
                total_cases = int(nums[-1]) # The last number is always the Total
                
                # The state name is everything before the first number
                state_name = re.split(r'\d+', line)[0].strip()
                
                # Filter out headers and the "Total" summary row
                if state_name and state_name not in ['State', 'Total', 'Year', 'Month']:
                    data.append({
                        'year': year,
                        'state': state_name,
                        'cases': total_cases
                    })
                    
    # Create a DataFrame and save it as a clean CSV
    df = pd.DataFrame(data)
    df.to_csv('cdc_hantavirus_1993_2023.csv', index=False)
    print(f"✅ SUCCESS! Created 'cdc_hantavirus_1993_2023.csv' with {len(df)} records.")

if __name__ == "__main__":
    generate_cdc_csv()