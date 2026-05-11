"""
ANALYSIS: Differences between meal_planning.py and main.py

KEY FINDINGS:
=============

1. GROUPING LOGIC:
   - meal_planning.py: Groups by 'feature_set' (nat + age + dest + meal_time concatenated)
   - main.py: Groups by ['nationality_code', 'age_group', 'destination_region', 'meal_time', 'weekday']
   - ✅ SAME LOGIC (weekday is part of nationality lookup anyway)

2. CABIN CLASS SELECTION:
   - meal_planning.py (lines 193-196):
     ```python
     flights_4 =  df[(df.segment != 'SIN JFK') & (df.cabin_class == 'Y')]
     flight_jfk = df[(df.segment == "SIN JFK")&(df.cabin_class == 'S')]
     df = pd.concat([flights_4, flight_jfk], axis = 0, ignore_index = True)
     ```
   - main.py (lines 662-670):
     ```python
     # Select Y class or S class
     y_data = flight_data[flight_data['cabin_class'] == 'Y']
     if not y_data.empty:
         flight_data = y_data
     else:
         s_data = flight_data[flight_data['cabin_class'] == 'S']
         flight_data = s_data
     ```
   - ❌ DIFFERENT LOGIC!
     meal_planning.py treats SIN JFK specially (uses S class for SIN JFK, Y for others)
     main.py uses Y if available, otherwise S (for all flights)

3. WEIGHTS:
   - meal_planning.py (lines 30-33): W1=0.40, W2=0.20, W3=0.25, W4=0.15
   - main.py (lines 570-573): Same default values
   - ✅ SAME

4. PROBABILITY NORMALIZATION:
   - meal_planning.py (lines 37-65): Normalizes probabilities for available proteins
   - main.py: Uses pre-normalized probabilities from frontend
   - ✅ SAME (frontend normalizes)

5. LARGEST REMAINDER METHOD:
   - meal_planning.py (lines 138-173):
     - Floors all counts
     - Calculates remainders
     - Sorts proteins by remainder (largest first)
     - Distributes remaining passengers one by one to proteins with largest remainders
   - main.py (lines 840-875):
     - Same logic
   - ✅ SAME

6. AGGREGATION:
   - meal_planning.py (lines 333-347): Aggregates by summing protein counts across all feature groups
   - main.py (lines 904-916): Aggregates by summing protein counts per meal_time
   - ✅ SAME

ROOT CAUSE:
===========
The cabin class selection logic is DIFFERENT!

meal_planning.py:
- SIN JFK uses ONLY S (business) class
- All other flights use ONLY Y (economy) class

main.py:
- Uses Y if available for ANY flight
- Falls back to S only if Y is empty

IMPACT:
=======
For SIN JFK flights:
- meal_planning.py processes S class passengers
- main.py might process Y class passengers if Y exists
- This causes different passenger counts and distributions

For other flights:
- Both should process Y class
- But main.py has a fallback to S which meal_planning.py doesn't have

FIX REQUIRED:
=============
Update main.py to match meal_planning.py's cabin selection logic:
- If segment == "SIN JFK", use cabin_class == 'S'
- If segment != "SIN JFK", use cabin_class == 'Y'
- No fallback logic
"""

print(__doc__)
