import pandas as pd
import pycountry

# Build a set of valid country names using pycountry
valid_countries = {country.name for country in pycountry.countries}

# Read the Excel file (adjust the file name and sheet name as needed)
df = pd.read_excel('output.xlsx', sheet_name='Countries')

# Identify columns that contain country names (assuming they start with "Country_")
country_cols = [col for col in df.columns if col.startswith('Country_')]

# For each cell in the identified columns, clear the cell if it is not a valid country name
for col in country_cols:
    df[col] = df[col].apply(lambda x: x if pd.notnull(x) and x in valid_countries else None)

# Save the cleaned data to a new Excel file
df.to_excel('cleaned_output.xlsx', index=False, sheet_name='Countries')
