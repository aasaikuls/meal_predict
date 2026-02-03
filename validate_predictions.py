"""
Validation script to compare main.py predictions with PredictionResults (Original Results comaprision)CSV files.
Tests whether the current prediction algorithm matches the original meal_planning.py results.
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def load_prediction_results():
    """Load all PredictionResults CSV files"""
    results_dir = 'PredictionResults'
    prediction_files = {
        'SIN JFK': 'SIN_JFK_PredictionResults.csv',
        'SIN CDG': 'SIN_CDG_PredictionResults.csv',
        'SIN MAA': 'SIN_MAA_PredictionResults.csv',
        'PEK SIN': 'PEK_SIN_PredictionResults.csv',
        'AKL SIN': 'AKL_SIN_PredictionResults.csv'
    }
    
    all_results = {}
    for segment, filename in prediction_files.items():
        filepath = os.path.join(results_dir, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            all_results[segment] = df
            print(f"[OK] Loaded {filename}: {len(df)} rows")
        else:
            print(f"[MISSING] {filename}")
    
    return all_results

def simulate_main_py_prediction(segment, date_str, cabin_class, meal_time, customers_df, 
                                nationality_probs, age_probs, dest_probs, meal_probs,
                                available_proteins):
    """
    Simulate the prediction logic from main.py
    Returns: dict of {protein: count}
    """
    # Parse date
    target_date = pd.to_datetime(date_str).date()
    
    # Filter customers
    flight_data = customers_df[customers_df['segment'] == segment].copy()
    
    # Parse dates
    flight_data['parsed_date'] = pd.to_datetime(
        flight_data['segment_local_departure_datetime'].str.split().str[0],
        format='%d/%m/%Y',
        dayfirst=True,
        errors='coerce'
    ).dt.date
    
    flight_data = flight_data[flight_data['parsed_date'] == target_date]
    
    # Remove Under 2
    flight_data = flight_data[flight_data['age_group'] != 'Under 2']
    
    # Select cabin based on segment (matching meal_planning.py logic)
    segment_value = flight_data['segment'].iloc[0] if not flight_data.empty else ""
    if segment_value == "SIN JFK":
        cabin_data = flight_data[flight_data['cabin_class'] == 'S']
    else:
        cabin_data = flight_data[flight_data['cabin_class'] == 'Y']
    
    if cabin_data.empty:
        return {}
    
    # Filter by meal_time
    cabin_data = cabin_data[cabin_data['meal_time'] == meal_time]
    if cabin_data.empty:
        return {}
    
    # Add weekday
    cabin_data['weekday'] = pd.to_datetime(
        cabin_data['segment_local_departure_datetime'],
        format='%d/%m/%Y %H:%M',
        dayfirst=True
    ).dt.day_name()
    
    # Create feature_set (matching meal_planning.py)
    cabin_data['feature_set'] = (
        cabin_data['nationality_code'].astype(str) + '_' +
        cabin_data['age_group'].astype(str) + '_' +
        cabin_data['destination_region'].astype(str) + '_' +
        cabin_data['meal_time'].astype(str)
    )
    
    # Group passengers (matching meal_planning.py exactly - include segment, cabin_class, parsed_date)
    grouped = cabin_data.groupby([
        'segment', 'cabin_class', 'parsed_date', 'weekday', 'feature_set'
    ]).size().reset_index(name='passenger_count')
    
    # Get feature details
    feature_details = cabin_data.groupby('feature_set').agg({
        'nationality_code': 'first',
        'age_group': 'first',
        'destination_region': 'first',
        'meal_time': 'first'
    }).reset_index()
    
    grouped = grouped.merge(feature_details, on='feature_set', how='left')
    
    # Default weights (as in main.py)
    W1 = 0.40  # Nationality
    W2 = 0.20  # Age
    W3 = 0.25  # Destination
    W4 = 0.15  # Meal time
    
    results_by_protein = {p: 0 for p in available_proteins}
    
    for _, group in grouped.iterrows():
        nationality = group['nationality_code']
        age_group = group['age_group']
        destination = group['destination_region']
        weekday = group['weekday']
        passenger_count = group['passenger_count']
        
        # Get probabilities
        nat_key = f"{nationality}_{weekday}"
        nat_prob_dict = nationality_probs.get(nat_key, {})
        age_prob_dict = age_probs.get(age_group, {})
        dest_prob_dict = dest_probs.get(destination, {})
        meal_prob_dict = meal_probs.get(meal_time, {})
        
        # Calculate weighted probabilities
        weighted_probs = {}
        for protein in available_proteins:
            weighted_prob = (
                nat_prob_dict.get(protein, 0) * W1 +
                age_prob_dict.get(protein, 0) * W2 +
                dest_prob_dict.get(protein, 0) * W3 +
                meal_prob_dict.get(protein, 0) * W4
            )
            weighted_probs[protein] = weighted_prob
        
        # Normalize
        total = sum(weighted_probs.values())
        if total > 0:
            final_probs = {p: v/total for p, v in weighted_probs.items()}
        else:
            final_probs = {p: 1.0/len(available_proteins) for p in available_proteins}
        
        # Calculate counts using largest remainder method
        protein_counts = {}
        remainders = {}
        
        for protein in available_proteins:
            exact = passenger_count * final_probs[protein]
            floor_count = int(exact)
            protein_counts[protein] = floor_count
            remainders[protein] = exact - floor_count
        
        # Distribute remaining
        total_allocated = sum(protein_counts.values())
        remaining = passenger_count - total_allocated
        
        if remaining > 0:
            # Use stable sort (preserves input order on ties) - matches meal_planning.py
            sorted_proteins = sorted(available_proteins, key=lambda p: remainders[p], reverse=True)
            for i in range(remaining):
                protein_counts[sorted_proteins[i]] += 1
        
        # Add to results
        for protein, count in protein_counts.items():
            results_by_protein[protein] += count
    
    return results_by_protein

def load_csv_probabilities():
    """Load probability CSVs (same as main.py uses)"""
    nationality_df = pd.read_csv('Nationality.csv')
    age_df = pd.read_csv('Age.csv')
    dest_df = pd.read_csv('Destination.csv')
    meal_df = pd.read_csv('MealTime.csv')
    
    # Build probability dicts
    nationality_probs = {}
    for _, row in nationality_df.iterrows():
        key = f"{row['nationality_code']}_{row['day_of_week']}"
        nationality_probs[key] = {
            'Pork': row['Pork'],
            'Chicken': row['Chicken'],
            'Beef': row['Beef'],
            'Seafood': row['Seafood'],
            'Lamb': row['Lamb'],
            'Vegetarian': row['Vegetarian']
        }
    
    age_probs = {}
    for _, row in age_df.iterrows():
        age_probs[row['age_group']] = {
            'Pork': row['Pork'],
            'Chicken': row['Chicken'],
            'Beef': row['Beef'],
            'Seafood': row['Seafood'],
            'Lamb': row['Lamb'],
            'Vegetarian': row['Vegetarian']
        }
    
    dest_probs = {}
    for _, row in dest_df.iterrows():
        dest_probs[row['destination_region']] = {
            'Pork': row['Pork'],
            'Chicken': row['Chicken'],
            'Beef': row['Beef'],
            'Seafood': row['Seafood'],
            'Lamb': row['Lamb'],
            'Vegetarian': row['Vegetarian']
        }
    
    meal_probs = {}
    for _, row in meal_df.iterrows():
        meal_probs[row['meal_time']] = {
            'Pork': row['Pork'],
            'Chicken': row['Chicken'],
            'Beef': row['Beef'],
            'Seafood': row['Seafood'],
            'Lamb': row['Lamb'],
            'Vegetarian': row['Vegetarian']
        }
    
    return nationality_probs, age_probs, dest_probs, meal_probs

def get_available_proteins_for_meal(segment, date, cabin_class, meal_time, meal_df):
    """Get available proteins for a specific meal time"""
    target_date = pd.to_datetime(date).date()
    meal_df['parsed_date'] = pd.to_datetime(meal_df['segment_local_departure_date'], errors='coerce').dt.date
    
    filtered = meal_df[
        (meal_df['segment'] == segment) &
        (meal_df['parsed_date'] == target_date) &
        (meal_df['cabin_class'] == cabin_class) &
        (meal_df['meal_time'] == meal_time)
    ]
    
    if filtered.empty:
        return []
    
    # IMPORTANT: Preserve order from meal_df (DO NOT SORT)
    # Order affects tie-breaking in largest remainder method
    return filtered['meal_pref'].unique().tolist()

def normalize_probs_for_available_proteins(probs_dict, available_proteins):
    """Normalize probabilities to only include available proteins"""
    available_probs = {p: probs_dict.get(p, 0) for p in available_proteins}
    total = sum(available_probs.values())
    if total > 0:
        return {p: v/total for p, v in available_probs.items()}
    else:
        equal_prob = 1.0 / len(available_proteins)
        return {p: equal_prob for p in available_proteins}

def run_validation():
    """Run validation comparing main.py logic to PredictionResults"""
    print("="*80)
    print("MEAL PREDICTION VALIDATION")
    print("Comparing main.py algorithm with PredictionResults CSV files")
    print("="*80)
    print()
    
    # Load data
    print("[*] Loading data...")
    prediction_results = load_prediction_results()
    customers_df = pd.read_csv('customers.csv', dtype={'age_group': str}, low_memory=False)
    customers_df['age_group'] = customers_df['age_group'].replace('Feb-18', '2-18')
    meal_df = pd.read_csv('meal_df_new.csv')
    
    print(f"[OK] Loaded customers.csv: {len(customers_df)} rows")
    print(f"[OK] Loaded meal_df_new.csv: {len(meal_df)} rows")
    print()
    
    # Load probability data
    print("[*] Loading probability data...")
    nationality_probs, age_probs, dest_probs, meal_probs = load_csv_probabilities()
    print(f"[OK] Nationality probabilities: {len(nationality_probs)} entries")
    print(f"[OK] Age probabilities: {len(age_probs)} entries")
    print(f"[OK] Destination probabilities: {len(dest_probs)} entries")
    print(f"[OK] Meal time probabilities: {len(meal_probs)} entries")
    print()
    
    # Test cases from PredictionResults
    test_cases = []
    
    # Sample a few dates from each segment
    for segment, df in prediction_results.items():
        # Filter rows with predicted_meal_count (not NaN)
        valid_rows = df[df['predicted_meal_count'].notna()]
        
        # Get unique date/cabin/meal_time combinations
        unique_combos = valid_rows.groupby([
            'segment_local_departure_date', 'cabin_class', 'meal_time'
        ]).first().reset_index()
        
        # Sample up to 3 dates per segment
        for _, combo in unique_combos.head(3).iterrows():
            test_cases.append({
                'segment': segment,
                'date': combo['segment_local_departure_date'],
                'cabin_class': combo['cabin_class'],
                'meal_time': combo['meal_time'],
                'weekday': combo['weekday'] if 'weekday' in combo else None
            })
    
    print(f"[*] Running {len(test_cases)} test cases...")
    print()
    
    # Run tests
    mismatches = []
    matches = []
    
    for i, test in enumerate(test_cases):
        segment = test['segment']
        date = test['date']
        cabin = test['cabin_class']
        meal_time = test['meal_time']
        
        print(f"\n{'='*80}")
        print(f"Test {i+1}/{len(test_cases)}: {segment} | {date} | {cabin} | {meal_time}")
        print(f"{'='*80}")
        
        # Get available proteins
        available_proteins = get_available_proteins_for_meal(segment, date, cabin, meal_time, meal_df)
        if not available_proteins:
            print(f"[WARN] No available proteins found in meal_df_new.csv - SKIP")
            continue
        
        print(f"Available proteins: {available_proteins}")
        
        # Normalize probabilities for available proteins
        normalized_nat_probs = {}
        for key, probs in nationality_probs.items():
            normalized_nat_probs[key] = normalize_probs_for_available_proteins(probs, available_proteins)
        
        normalized_age_probs = {}
        for key, probs in age_probs.items():
            normalized_age_probs[key] = normalize_probs_for_available_proteins(probs, available_proteins)
        
        normalized_dest_probs = {}
        for key, probs in dest_probs.items():
            normalized_dest_probs[key] = normalize_probs_for_available_proteins(probs, available_proteins)
        
        normalized_meal_probs = {}
        for key, probs in meal_probs.items():
            normalized_meal_probs[key] = normalize_probs_for_available_proteins(probs, available_proteins)
        
        # Run main.py simulation
        predicted = simulate_main_py_prediction(
            segment, date, cabin, meal_time, customers_df,
            normalized_nat_probs, normalized_age_probs, normalized_dest_probs, normalized_meal_probs,
            available_proteins
        )
        
        # Get expected from PredictionResults
        expected_df = prediction_results[segment]
        expected_rows = expected_df[
            (expected_df['segment_local_departure_date'] == date) &
            (expected_df['cabin_class'] == cabin) &
            (expected_df['meal_time'] == meal_time) &
            (expected_df['predicted_meal_count'].notna())
        ]
        
        expected = {}
        for _, row in expected_rows.iterrows():
            protein = row['protein_type']
            count = int(row['predicted_meal_count'])
            expected[protein] = count
        
        # Compare
        print(f"\n{'Protein':<15} {'Expected':<12} {'Predicted':<12} {'Diff':<12} {'Match'}")
        print("-"*65)
        
        all_proteins = set(list(expected.keys()) + list(predicted.keys()))
        test_passed = True
        
        for protein in sorted(all_proteins):
            exp_count = expected.get(protein, 0)
            pred_count = predicted.get(protein, 0)
            diff = pred_count - exp_count
            match = "[OK]" if diff == 0 else "[X]"
            
            if diff != 0:
                test_passed = False
            
            print(f"{protein:<15} {exp_count:<12} {pred_count:<12} {diff:<12} {match}")
        
        if test_passed:
            print("\n[PASS] All proteins match!")
            matches.append(test)
        else:
            print("\n[FAIL] Mismatches detected")
            mismatches.append({
                'test': test,
                'expected': expected,
                'predicted': predicted
            })
    
    # Summary
    print("\n\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {len(matches)} [OK]")
    print(f"Failed: {len(mismatches)} [FAIL]")
    print()
    
    if mismatches:
        print("[!] FAILED TESTS:")
        for i, mismatch in enumerate(mismatches):
            test = mismatch['test']
            print(f"\n  {i+1}. {test['segment']} | {test['date']} | {test['cabin_class']} | {test['meal_time']}")
            print(f"     Expected: {mismatch['expected']}")
            print(f"     Predicted: {mismatch['predicted']}")
    
    return len(mismatches) == 0

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
