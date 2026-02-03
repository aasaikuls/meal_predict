import pandas as pd
import os

prediction_dir = ''

# Files to update
prediction_files = [
    'AKL_SIN_PredictionResults.csv',
    'PEK_SIN_PredictionResults.csv',
    'SIN_CDG_PredictionResults.csv',
    'SIN_JFK_PredictionResults.csv',
    'SIN_MAA_PredictionResults.csv'
]

for file in prediction_files:
    file_path = os.path.join(prediction_dir, file)
    
    if os.path.exists(file_path):
        print(f"Processing {file}...")
        
        # Read the file
        df = pd.read_csv(file_path)
        
        # Replace SIN with BKK in all columns
        for col in df.columns:
            if df[col].dtype == 'object':  # Only process string columns
                df[col] = df[col].astype(str).str.replace('SIN', 'BKK', regex=False)
        
        # Also update the filename
        new_filename = file.replace('SIN', 'BKK')
        new_file_path = os.path.join(prediction_dir, new_filename)
        
        # Save with new filename
        df.to_csv(new_file_path, index=False)
        print(f"✓ Saved as {new_filename}")
    else:
        print(f"✗ File not found: {file}")

print("\n✓ All prediction files updated!")