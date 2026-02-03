import pandas as pd

# Read just the first 1000 rows to check structure
df = pd.read_csv('customers.csv', dtype={'age_group': str}, nrows=1000)

print("Column names:")
for col in df.columns:
    print(f"  - {col}")

# Check for ID-like columns
print("\n\nSample of first 3 rows:")
print(df.head(3).T)  # Transpose for better readability
