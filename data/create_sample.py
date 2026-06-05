import pandas as pd

# Create a small sample from your existing medicare data
# Run this once to generate sample_data.csv

df = pd.read_csv(
    '../healthcare-claims-project/data/medicare_data.csv',
    low_memory=False,
    dtype={'Rndrng_Prvdr_State_FIPS': str, 'Rndrng_Prvdr_Zip5': str}
)

# Take 100k rows as sample
sample = df.head(100000)
sample.to_csv('data/sample_data.csv', index=False)
print(f"✅ Sample created: {len(sample):,} rows")