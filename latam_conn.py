import pandas as pd

# Predefined list of Latin American countries (rows of our matrix)
latam_countries = [
    "Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Mexico",
    "Nicaragua", "Panama", "Argentina", "Bolivia", "Brazil", "Chile", "Colombia",
    "Ecuador", "French Guiana", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay",
    "Venezuela", "Cuba", "Dominican Republic", "Haiti", "Guadeloupe", "Martinique",
    "Puerto Rico", "Saint-Barthélemy", "Saint-Martin"
]

# Load the deduped Excel file (assuming sheet name 'Countries')
df = pd.read_excel('deduped_output_no_empty_rows.xlsx', sheet_name='Countries')

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
