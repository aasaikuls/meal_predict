import pandas as pd

# Read the customers CSV
df = pd.read_csv('customers.csv', dtype={'age_group': str}, low_memory=False)

# Fix Excel's auto-conversion
if 'age_group' in df.columns:
    df['age_group'] = df['age_group'].replace('Feb-18', '2-18')

# Filter for AKL SIN flight
flight_number = 'SQ 0024'
target_date = pd.to_datetime('1/6/2024', dayfirst=True).date()

# Filter by flight number
flight_data = df[df['operating_flight_number'].astype(str).str.strip() == flight_number.strip()]

print(f"Total rows for {flight_number}: {len(flight_data)}")

# Parse and filter by date
flight_data['parsed_date'] = pd.to_datetime(
    flight_data['segment_local_departure_datetime'].str.split().str[0],
    format='%d/%m/%Y',
    dayfirst=True,
    errors='coerce'
).dt.date

flight_data = flight_data[flight_data['parsed_date'] == target_date]

print(f"Total rows after date filter: {len(flight_data)}")

# Check meal_time distribution
if 'meal_time' in flight_data.columns:
    print(f"\nMeal time distribution:")
    print(flight_data['meal_time'].value_counts())

# Method 1: Current approach - exclude meal_time and parsed_date
passenger_id_cols = [col for col in flight_data.columns if col not in ['meal_time', 'parsed_date']]
unique_passengers_method1 = flight_data.drop_duplicates(subset=passenger_id_cols, keep='first')
print(f"\nMethod 1 (current): {len(unique_passengers_method1)} unique passengers")

# Method 2: Use customer_number only
unique_passengers_method2 = flight_data.drop_duplicates(subset=['customer_number'], keep='first')
print(f"Method 2 (customer_number only): {len(unique_passengers_method2)} unique passengers")

# Check if there are duplicates by customer_number
duplicate_check = flight_data.groupby('customer_number').size()
print(f"\nCustomers appearing more than once: {(duplicate_check > 1).sum()}")
print(f"Max appearances per customer: {duplicate_check.max()}")
print(f"Average appearances per customer: {duplicate_check.mean():.2f}")

# Show distribution
print(f"\nAppearances distribution:")
print(duplicate_check.value_counts().sort_index())
