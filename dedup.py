import pandas as pd

# Read the Excel file containing country columns (assumed to start with "Country_")
df = pd.read_excel('cleaned_output.xlsx', sheet_name='Countries')
country_cols = [col for col in df.columns if col.startswith('Country_')]

def dedup_row(row):
    seen = set()
    deduped = []
    for col in country_cols:
        value = row[col]
        if pd.notnull(value) and value not in seen:
            seen.add(value)
            deduped.append(value)
    # Pad with None to maintain the same number of columns
    deduped += [None] * (len(country_cols) - len(deduped))
    return pd.Series(deduped, index=country_cols)

df[country_cols] = df.apply(dedup_row, axis=1)
df.to_excel('deduped_output.xlsx', index=False, sheet_name='Countries')
