import pandas as pd
import pycountry


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



# Build a set of valid country names including both common and official names
valid_countries = set()
for country in pycountry.countries:
    valid_countries.add(country.name.strip())
    if hasattr(country, 'official_name'):
        valid_countries.add(country.official_name.strip())

# Read the Excel file (adjust the file name and sheet name as needed)
df = pd.read_excel('output.xlsx', sheet_name='Countries')

# Identify columns that contain country names (assuming they start with "Country_")
country_cols = [col for col in df.columns if col.startswith('Country_')]

# For each cell in the identified columns, clear the cell if it is not a valid country name
for col in country_cols:
    df[col] = df[col].apply(lambda x: x.strip() if pd.notnull(x) and x.strip() in valid_countries else None)

# Save the cleaned data to a new Excel file
df.to_excel('cleaned_output.xlsx', index=False, sheet_name='Countries')




# Read the Excel file containing country columns (assumed to start with "Country_")
df = pd.read_excel('cleaned_output.xlsx', sheet_name='Countries')
country_cols = [col for col in df.columns if col.startswith('Country_')]

def dedup_row(row):
    seen = set()
    deduped = []
    for col in country_cols:
        value = row[col]
        if pd.notnull(value):
            value_str = str(value).strip()  # Remove extra whitespace
            if value_str and value_str not in seen:
                seen.add(value_str)
                deduped.append(value_str)
    # Pad with None to maintain the same number of columns
    deduped += [None] * (len(country_cols) - len(deduped))
    return pd.Series(deduped, index=country_cols)

df[country_cols] = df.apply(dedup_row, axis=1)
df.to_excel('deduped_output.xlsx', index=False, sheet_name='Countries')



# Predefined list of Latin American countries (rows of our matrix)
latam_countries = [
    "Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Mexico",
    "Nicaragua", "Panama", "Argentina", "Bolivia", "Brazil", "Chile", "Colombia",
    "Ecuador", "French Guiana", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay",
    "Venezuela", "Cuba", "Dominican Republic", "Haiti", "Guadeloupe", "Martinique",
    "Puerto Rico", "Saint-Barthélemy", "Saint-Martin"
]

# Load the deduped Excel file (assuming sheet name 'Countries')
df = pd.read_excel('deduped_output.xlsx', sheet_name='Countries')

# Identify the country columns (assuming they start with "Country_")
country_cols = [col for col in df.columns if col.startswith("Country_")]

# Create a set of all countries mentioned in the file
all_countries = set()
for idx, row in df.iterrows():
    for col in country_cols:
        if pd.notnull(row[col]):
            country = row[col].strip()
            all_countries.add(country)
all_countries = sorted(all_countries)

# Initialize connectivity matrix with row headers as latam_countries and columns as all_countries
conn_matrix = pd.DataFrame(0, index=latam_countries, columns=all_countries)

# Process each row to update the connectivity matrix
for idx, row in df.iterrows():
    # Extract unique countries from the row
    row_countries = {row[col].strip() for col in country_cols if pd.notnull(row[col])}
    # Find Latin American countries in the row (they will be our row indices)
    latam_in_row = row_countries.intersection(latam_countries)
    if not latam_in_row:
        continue  # Skip rows that do not involve any Latin American country
    # If there's only one country, count a self-connection
    if len(row_countries) == 1:
        for latam in latam_in_row:
            conn_matrix.loc[latam, latam] += 1
    # For rows with multiple countries, add connection for each pair
    else:
        for latam in latam_in_row:
            for country in row_countries:
                conn_matrix.loc[latam, country] += 1

# Save the connectivity matrix as a CSV file
conn_matrix.to_csv('latam_conn.csv')
