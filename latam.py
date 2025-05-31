import pandas as pd

def extract_countries(address_str):
    if pd.isna(address_str):
        return []
    # Split addresses by semicolon if multiple addresses exist
    addresses = address_str.split(";")
    countries = []
    for addr in addresses:
        addr = addr.strip()
        if addr:
            # Assume the country is the text after the last comma
            parts = addr.split(",")
            if parts:
                countries.append(parts[-1].strip())
    return countries

# Read the CSV file (adjust the file name as needed)
df = pd.read_csv('WoS_records_LatAm_Addresses_only_CSV.csv')

# Extract a list of countries from the 'addresses' column for each row
df['country_list'] = df['addresses'].apply(extract_countries)

# Determine the maximum number of countries in any row
max_countries = df['country_list'].apply(len).max()

# Create separate columns for each country in the list
for i in range(max_countries):
    df[f'Country_{i+1}'] = df['country_list'].apply(lambda x: x[i] if i < len(x) else None)

# Optionally, create a new DataFrame with only the country columns
country_cols = [f'Country_{i+1}' for i in range(max_countries)]
df_countries = df[country_cols]

# Write to an Excel file with two sheets: one for the original data and one for the countries
with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Original', index=False)
    df_countries.to_excel(writer, sheet_name='Countries', index=False)
