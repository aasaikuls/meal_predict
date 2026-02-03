from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import pandas as pd
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from ai_summary import router as ai_summary_router, call_kariba_llm, PassengerGroup, TopNationality

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Airline Meal Prediction API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the AI summary router
app.include_router(ai_summary_router)

# In-memory cache for CSV default probabilities (loaded once per server start)
CSV_DEFAULTS_CACHE = {
    'nationality': None,
    'age': None,
    'destination': None,
    'mealtime': None,
    'loaded': False
}

# In-memory cache for flights data (loaded once per server start)
FLIGHTS_CACHE = {
    'flights': None,
    'categories': None,
    'loaded': False,
    'error': None
}

# In-memory cache for customer summary (keyed by flight_number|flight_date)
CUSTOMER_SUMMARY_CACHE = {}

# In-memory cache for available meals (keyed by flight_number|flight_date)
AVAILABLE_MEALS_CACHE = {}

def load_csv_defaults_once():
    """Load CSV defaults into memory cache (only once per server session)"""
    if CSV_DEFAULTS_CACHE['loaded']:
        print("✅ load_csv_defaults_once()---------- Using cached CSV defaults from memory")
        return CSV_DEFAULTS_CACHE
    
    print("📂load_csv_defaults_once()----------- Loading CSV defaults into memory cache (one-time operation)...")
    
    # Load Nationality CSV
    csv_nationality_probs = {}
    csv_nationality_reasoning = {}
    nationality_file = os.path.join(DATA_DIR, 'Nationality.csv')
    if os.path.exists(nationality_file):
        nat_df = pd.read_csv(nationality_file)
        for _, row in nat_df.iterrows():
            key = f"{row['nationality_code']}_{row['day_of_week']}"
            csv_nationality_probs[key] = {
                'Pork': row['Pork'],
                'Chicken': row['Chicken'],
                'Beef': row['Beef'],
                'Seafood': row['Seafood'],
                'Lamb': row['Lamb'],
                'Vegetarian': row['Vegetarian']
            }
            # Store reasoning if available
            if 'reasoning' in row and pd.notna(row['reasoning']):
                csv_nationality_reasoning[key] = str(row['reasoning'])
        print(f"load_csv_defaults_once()--------  ✓ Loaded {len(csv_nationality_probs)} nationality defaults")
    
    # Load Age CSV
    csv_age_probs = {}
    csv_age_reasoning = {}
    age_file = os.path.join(DATA_DIR, 'Age.csv')
    if os.path.exists(age_file):
        age_df = pd.read_csv(age_file)
        for _, row in age_df.iterrows():
            age_group = row['age_group']
            csv_age_probs[age_group] = {
                'Pork': row['Pork'],
                'Chicken': row['Chicken'],
                'Beef': row['Beef'],
                'Seafood': row['Seafood'],
                'Lamb': row['Lamb'],
                'Vegetarian': row['Vegetarian']
            }
            # Store reasoning if available
            if 'reasoning' in row and pd.notna(row['reasoning']):
                csv_age_reasoning[age_group] = str(row['reasoning'])
        print(f"load_csv_defaults_once()-------------  ✓ Loaded {len(csv_age_probs)} age defaults")
    
    # Load Destination CSV
    csv_destination_probs = {}
    csv_destination_reasoning = {}
    destination_file = os.path.join(DATA_DIR, 'Destination.csv')
    if os.path.exists(destination_file):
        dest_df = pd.read_csv(destination_file)
        for _, row in dest_df.iterrows():
            dest_region = row['destination_region']
            csv_destination_probs[dest_region] = {
                'Pork': row['Pork'],
                'Chicken': row['Chicken'],
                'Beef': row['Beef'],
                'Seafood': row['Seafood'],
                'Lamb': row['Lamb'],
                'Vegetarian': row['Vegetarian']
            }
            # Store reasoning if available
            if 'reasoning' in row and pd.notna(row['reasoning']):
                csv_destination_reasoning[dest_region] = str(row['reasoning'])
        print(f"load_csv_defaults_once() --------  ✓ Loaded {len(csv_destination_probs)} destination defaults")
    
    # Load MealTime CSV
    csv_mealtime_probs = {}
    csv_mealtime_reasoning = {}
    mealtime_file = os.path.join(DATA_DIR, 'MealTime.csv')
    if os.path.exists(mealtime_file):
        meal_df = pd.read_csv(mealtime_file)
        for _, row in meal_df.iterrows():
            meal_time = row['meal_time']
            csv_mealtime_probs[meal_time] = {
                'Pork': row['Pork'],
                'Chicken': row['Chicken'],
                'Beef': row['Beef'],
                'Seafood': row['Seafood'],
                'Lamb': row['Lamb'],
                'Vegetarian': row['Vegetarian']
            }
            # Store reasoning if available
            if 'reasoning' in row and pd.notna(row['reasoning']):
                csv_mealtime_reasoning[meal_time] = str(row['reasoning'])
        print(f"load_csv_defaults_once() -----------  ✓ Loaded {len(csv_mealtime_probs)} mealtime defaults")
    
    # Store in cache
    CSV_DEFAULTS_CACHE['nationality'] = csv_nationality_probs
    CSV_DEFAULTS_CACHE['age'] = csv_age_probs
    CSV_DEFAULTS_CACHE['destination'] = csv_destination_probs
    CSV_DEFAULTS_CACHE['mealtime'] = csv_mealtime_probs
    CSV_DEFAULTS_CACHE['nationality_reasoning'] = csv_nationality_reasoning
    CSV_DEFAULTS_CACHE['age_reasoning'] = csv_age_reasoning
    CSV_DEFAULTS_CACHE['destination_reasoning'] = csv_destination_reasoning
    CSV_DEFAULTS_CACHE['mealtime_reasoning'] = csv_mealtime_reasoning
    CSV_DEFAULTS_CACHE['loaded'] = True
    
    print("✅ CSV defaults cached in memory\n")
    return CSV_DEFAULTS_CACHE

# Data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "..")
PREDICTION_RESULTS_DIR = os.path.join(DATA_DIR, 'PredictionResults')


# TEMPORARY SESSION MEMORY - Cache for current flight+date session only
# This is NOT persistent storage - it gets cleared when user returns to flight selection
# Structure: {session_key: {metric_type: {row_key: {probabilities, marker, default_probabilities}}}}
# session_key format: "flight_number|flight_date"
SESSION_MEMORY = {}

def clear_session_memory():
    """Clear all session memory (called when returning to flight selection page)"""
    global SESSION_MEMORY
    SESSION_MEMORY = {}
    print("🗑️  Session memory cleared")

def normalize_probabilities_for_proteins(row_dict: dict, available_proteins: list) -> dict:
    """
    Normalize probabilities to sum to 1.0 for only the available proteins.
    Returns normalized probabilities for available proteins only.
    """
    protein_columns = ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian']
    
    # Extract probabilities for available proteins
    available_probs = {}
    total = 0.0
    for protein in available_proteins:
        if protein in protein_columns:
            prob = float(row_dict.get(protein, 0))
            available_probs[protein] = prob
            total += prob
    
    # Normalize to sum to 1.0
    if total > 0:
        normalized = {protein: prob/total for protein, prob in available_probs.items()}
    else:
        # Equal distribution if all are zero
        equal_prob = 1.0 / len(available_proteins)
        normalized = {protein: equal_prob for protein in available_proteins}
    
    return normalized

# Load prediction results for comparison
def load_prediction_results(segment, date, cabin_class, meal_time):
    """
    Load historical prediction results for comparison.
    Returns dict with protein_type as key and original_meal_count as value.
    """
    try:
        # Convert segment format: "SQ 0024 (AKL → SIN)" or "AKL SIN" to "AKL_SIN"
        if '→' in segment:
            parts = segment.split('(')[1].split(')')[0].split('→')
            origin = parts[0].strip()
            destination = parts[1].strip()
            segment_key = f"{origin}_{destination}"
        else:
            # Already in "AKL SIN" format
            segment_key = segment.replace(' ', '_')
        
        csv_file = os.path.join(PREDICTION_RESULTS_DIR, f"{segment_key}_PredictionResults.csv")
        
        if not os.path.exists(csv_file):
            print(f"Prediction results file not found: {csv_file}")
            return None
        
        df = pd.read_csv(csv_file)
        
        # Filter by date, cabin_class, and meal_time
        # Convert date format from YYYY-MM-DD to match CSV format
        filtered_df = df[
            (df['segment_local_departure_date'] == date) &
            (df['cabin_class'] == cabin_class) &
            (df['meal_time'] == meal_time)
        ]
        
        if filtered_df.empty:
            return None
        
        # Get the first occurrence of each protein type and return original_meal_count
        results = {}
        for protein_type in filtered_df['protein_type'].unique():
            protein_df = filtered_df[filtered_df['protein_type'] == protein_type]
            if not protein_df.empty:
                results[protein_type] = int(protein_df.iloc[0]['original_meal_count'])
        
        return results
        
    except Exception as e:
        print(f"Error loading prediction results: {e}")
        return None

# Models
class MasterMetrics(BaseModel):
    nationality_importance: float = 40.0
    age_importance: float = 20.0
    destination_importance: float = 25.0
    mealtime_importance: float = 15.0
    nationality_data: Optional[Dict] = None
    age_data: Optional[Dict] = None
    destination_data: Optional[Dict] = None
    mealtime_data: Optional[Dict] = None

class PredictionRequest(BaseModel):
    flight_number: str
    flight_date: str
    master_metrics: Optional[MasterMetrics] = None

class WorkflowStep(BaseModel):
    step: int
    total_steps: int
    message: str
    progress: int
    timestamp: str

class PredictionResult(BaseModel):
    flight_number: str
    flight_date: str
    total_passengers: int
    meal_predictions: List[Dict]
    protein_distribution: Dict[str, float]
    workflow_completed: bool

# Default master metrics
default_metrics = MasterMetrics()

@app.get("/")
def read_root():
    return {"message": "Airline Meal Prediction API", "status": "running"}

@app.get("/api/flights")
def get_flights():
    """Get available flights with categories and dates from customers.csv (cached)"""
    global FLIGHTS_CACHE
    
    # Return cached data if available
    if FLIGHTS_CACHE['loaded']:
        print("✅ Returning cached flights data")
        if FLIGHTS_CACHE['error']:
            return {"flights": [], "categories": [], "error": FLIGHTS_CACHE['error']}
        return {"flights": FLIGHTS_CACHE['flights'], "categories": FLIGHTS_CACHE['categories']}
    
    # Load flights data for the first time
    print("📂 Loading flights data from customers.csv (one-time operation)...")
    try:
        customers_file = os.path.join(DATA_DIR, 'customers.csv')
        if not os.path.exists(customers_file):
            FLIGHTS_CACHE['loaded'] = True
            FLIGHTS_CACHE['error'] = "customers.csv not found"
            return {"flights": [], "categories": [], "error": "customers.csv not found"}
        
        df = pd.read_csv(customers_file, low_memory=False)
        
        # Get unique destination regions (categories)
        categories = sorted(df['destination_region'].dropna().unique().tolist())
        
        # Get unique flights with their details
        flight_groups = df.groupby('operating_flight_number').agg({
            'departure_airport': 'first',
            'arrival_airport': 'first',
            'destination_region': 'first',
            'segment_local_departure_datetime': lambda x: sorted(x.dropna().unique().tolist())
        }).reset_index()
        
        flights = []
        for _, row in flight_groups.iterrows():
            flight_num = str(row['operating_flight_number']).strip()
            origin = str(row['departure_airport'])
            destination = str(row['arrival_airport'])
            category = str(row['destination_region']) if pd.notna(row['destination_region']) else 'Unknown'
            
            # Extract dates
            dates = []
            for dt_str in row['segment_local_departure_datetime']:
                try:
                    if pd.notna(dt_str) and str(dt_str).strip() != '':
                        # Extract date part (before time if present)
                        date_part = str(dt_str).split()[0] if ' ' in str(dt_str) else str(dt_str)
                        # Parse the date as DD/MM/YYYY format and convert to YYYY-MM-DD format
                        parsed_date = pd.to_datetime(date_part, format='%d/%m/%Y', dayfirst=True)
                        date_str = parsed_date.strftime('%Y-%m-%d')
                        if date_str not in dates:
                            dates.append(date_str)
                except Exception as e:
                    pass
            
            print(f"DEBUG: Flight {flight_num} has {len(dates)} valid dates")
            
            flights.append({
                'flightNumber': flight_num,
                'origin': origin,
                'destination': destination,
                'route': f"{origin}-{destination}",
                'category': category,
                'availableDates': sorted(dates)
            })
        
        # Cache the results
        FLIGHTS_CACHE['flights'] = flights
        FLIGHTS_CACHE['categories'] = categories
        FLIGHTS_CACHE['loaded'] = True
        print(f"✅ Cached {len(flights)} flights and {len(categories)} categories")
        
        return {"flights": flights, "categories": categories}
    except Exception as e:
        print(f"Error loading flights: {e}")
        import traceback
        traceback.print_exc()
        FLIGHTS_CACHE['loaded'] = True
        FLIGHTS_CACHE['error'] = str(e)
        return {"flights": [], "categories": [], "error": str(e)}

@app.get("/api/customer-summary")
def get_customer_summary(flight_number: str, flight_date: str):
    """Get customer summary for selected flight and date (cached)"""
    global CUSTOMER_SUMMARY_CACHE
    
    # Create cache key
    cache_key = f"{flight_number}|{flight_date}"
    
    # Return cached data if available
    if cache_key in CUSTOMER_SUMMARY_CACHE:
        print(f"✅ Returning cached customer summary for {cache_key}")
        return CUSTOMER_SUMMARY_CACHE[cache_key]
    
    print(f"📂 Loading customer summary for {cache_key}...")
    try:
        customers_file = os.path.join(DATA_DIR, 'customers.csv')
        
        if not os.path.exists(customers_file):
            result = {"error": "customers.csv not found"}
            CUSTOMER_SUMMARY_CACHE[cache_key] = result
            return result
        
        # Read CSV with age_group as string to prevent Excel date conversion
        df = pd.read_csv(customers_file, dtype={'age_group': str}, low_memory=False)
        
        # Fix Excel's auto-conversion of "2-18" to "Feb-18"
        if 'age_group' in df.columns:
            df['age_group'] = df['age_group'].replace('Feb-18', '2-18')
        
        # Parse the flight date
        target_date = pd.to_datetime(flight_date).date()
        
        # Filter by flight number
        flight_data = df[df['operating_flight_number'].astype(str).str.strip() == flight_number.strip()]
        
        if flight_data.empty:
            return {"error": f"No data found for flight {flight_number}"}
        
        # Filter by date
        flight_data['parsed_date'] = pd.to_datetime(
            flight_data['segment_local_departure_datetime'].str.split().str[0],
            format='%d/%m/%Y',
            dayfirst=True,
            errors='coerce'
        ).dt.date
        
        flight_data = flight_data[flight_data['parsed_date'] == target_date]
        
        if flight_data.empty:
            return {"error": f"No customers found for flight {flight_number} on {flight_date}"}
        
        # Get unique passengers using customer_number if available
        # Each customer can have multiple meal_times, so we deduplicate by customer_number
        if 'customer_number' in flight_data.columns:
            unique_passengers = flight_data.drop_duplicates(subset=['customer_number'], keep='first')
        else:
            # Fallback: drop duplicates on all columns except meal_time
            passenger_id_cols = [col for col in flight_data.columns if col not in ['meal_time', 'parsed_date']]
            unique_passengers = flight_data.drop_duplicates(subset=passenger_id_cols, keep='first')
        
        # Total customers (unique passengers)
        total_customers = len(unique_passengers)
        
        # Cabin class distribution (using unique passengers)
        cabin_distribution = {}
        if 'cabin_class' in unique_passengers.columns:
            cabin_distribution = unique_passengers['cabin_class'].value_counts().to_dict()
        
        # Destination airport code (extract from segment or arrival_airport)
        destination_airport = 'Unknown'
        if 'arrival_airport' in unique_passengers.columns and len(unique_passengers) > 0:
            destination_airport = unique_passengers['arrival_airport'].iloc[0]
        elif 'segment' in unique_passengers.columns and len(unique_passengers) > 0:
            # Extract destination from segment (e.g., "AKL SIN" -> "SIN")
            segment = unique_passengers['segment'].iloc[0]
            if isinstance(segment, str) and ' ' in segment:
                destination_airport = segment.split()[-1]
        
        # Unique meal times (from original flight_data)
        meal_times = []
        if 'meal_time' in flight_data.columns:
            meal_times = sorted(flight_data['meal_time'].dropna().unique().tolist())
        
        # Determine cabin class for detailed analysis (Y first, then S)
        analysis_cabin = None
        if 'Y' in cabin_distribution:
            analysis_cabin = 'Y'
        elif 'S' in cabin_distribution:
            analysis_cabin = 'S'
        
        # Nationality and Age breakdown for selected cabin (using unique passengers)
        nationality_breakdown = {}
        age_breakdown = {}
        
        if analysis_cabin:
            cabin_data = unique_passengers[unique_passengers['cabin_class'] == analysis_cabin]
            
            # Nationality breakdown
            if 'nationality_code' in cabin_data.columns:
                nationality_breakdown = cabin_data['nationality_code'].value_counts().to_dict()
            
            # Age group breakdown
            if 'age_group' in cabin_data.columns:
                age_breakdown = cabin_data['age_group'].value_counts().to_dict()
        
        # Get day of week from flight_date
        parsed_date = pd.to_datetime(flight_date)
        day_of_week = parsed_date.strftime('%A')  # Full weekday name (e.g., "Monday")
        
        result = {
            "flight_number": flight_number,
            "flight_date": flight_date,
            "day_of_week": day_of_week,
            "total_customers": int(total_customers),
            "cabin_distribution": {k: int(v) for k, v in cabin_distribution.items()},
            "destination_airport": destination_airport,
            "meal_times": meal_times,
            "analysis_cabin": analysis_cabin,
            "nationality_breakdown": {k: int(v) for k, v in nationality_breakdown.items()},
            "age_breakdown": {k: int(v) for k, v in age_breakdown.items()}
        }
        
        # Cache the result
        CUSTOMER_SUMMARY_CACHE[cache_key] = result
        print(f"✅ Cached customer summary for {cache_key}")
        
        return result
    except Exception as e:
        print(f"Error loading customer summary: {e}")
        import traceback
        traceback.print_exc()
        error_result = {"error": str(e)}
        CUSTOMER_SUMMARY_CACHE[cache_key] = error_result
        return error_result

@app.get("/api/available-meals")
def get_available_meals(flight_number: str, flight_date: str):
    """Get available meals for a specific flight and date from meal_df_new.csv (cached)"""
    global AVAILABLE_MEALS_CACHE
    
    # Create cache key
    cache_key = f"{flight_number}|{flight_date}"
    
    # Return cached data if available
    if cache_key in AVAILABLE_MEALS_CACHE:
        print(f"✅ Returning cached available meals for {cache_key}")
        return AVAILABLE_MEALS_CACHE[cache_key]
    
    print(f"📂 Loading available meals for {cache_key}...")
    try:
        # Load meal data
        meal_file = os.path.join(DATA_DIR, 'meal_df_new.csv')
        if not os.path.exists(meal_file):
            result = {"error": "Meal data file not found"}
            AVAILABLE_MEALS_CACHE[cache_key] = result
            return result
        
        df = pd.read_csv(meal_file)
        
        # Parse the date from the request (YYYY-MM-DD format)
        target_date = pd.to_datetime(flight_date).date()
        
        # Parse segment_local_departure_date column (already in datetime format)
        df['parsed_date'] = pd.to_datetime(df['segment_local_departure_date'], errors='coerce').dt.date
        
        # Extract flight route from segment column (e.g., "AKL SIN")
        # Match the flight route from the flight_number
        # flight_number format is like "SQ286 (AKL → SIN)"
        if '(' in flight_number and '→' in flight_number:
            route_part = flight_number.split('(')[1].split(')')[0]  # "AKL → SIN"
            origin, destination = route_part.split('→')
            origin = origin.strip()
            destination = destination.strip()
            segment_filter = f"{origin} {destination}"
        else:
            return {"error": "Invalid flight number format"}
        
        # Filter by segment and date
        meal_data = df[(df['segment'] == segment_filter) & (df['parsed_date'] == target_date)]
        
        if meal_data.empty:
            return {"meals_by_time": {}, "message": "No meal data found for this flight and date"}
        
        # Group meals by meal_time, prioritizing Y cabin, then S cabin
        meals_by_time = {}
        for meal_time in meal_data['meal_time'].unique():
            time_meals = meal_data[meal_data['meal_time'] == meal_time]
            
            # Check if Y cabin exists for this meal time
            y_cabin_meals = time_meals[time_meals['cabin_class'] == 'Y']
            
            if not y_cabin_meals.empty:
                # Use Y cabin meals
                display_meals = y_cabin_meals
            else:
                # Use S cabin meals if Y cabin not present
                s_cabin_meals = time_meals[time_meals['cabin_class'] == 'S']
                display_meals = s_cabin_meals
            
            meals_list = []
            for _, row in display_meals.iterrows():
                meals_list.append({
                    "cabin_class": row['cabin_class'],
                    "meal_name": row['meal_name'],
                    "meal_pref": row['meal_pref']
                })
            
            meals_by_time[meal_time] = meals_list
        
        result = {
            "flight_number": flight_number,
            "flight_date": flight_date,
            "segment": segment_filter,
            "meals_by_time": meals_by_time
        }
        
        # Cache the result
        AVAILABLE_MEALS_CACHE[cache_key] = result
        print(f"✅ Cached available meals for {cache_key}")
        
        return result
    except Exception as e:
        print(f"Error loading available meals: {e}")
        import traceback
        traceback.print_exc()
        error_result = {"error": str(e)}
        AVAILABLE_MEALS_CACHE[cache_key] = error_result
        return error_result

@app.post("/api/clear-session")
def clear_session():
    """
    Clear temporary session memory.
    Called when user returns to flight selection page.
    """
    try:
        clear_session_memory()
        return {"success": True, "message": "Session memory cleared"}
    except Exception as e:
        print(f"Error clearing session: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/initialize-session")
async def initialize_session(request: dict):
    """
    Initialize session memory with normalized and restricted probabilities for a flight+date.
    This loads all CSV defaults, normalizes them for available proteins per meal time.
    Each row gets a marker to track if user has modified it.
    """
    try:
        flight_number = request.get("flight_number")
        flight_date = request.get("flight_date")
        
        if not flight_number or not flight_date:
            raise HTTPException(status_code=400, detail="flight_number and flight_date required")
        
        session_key = f"{flight_number}|{flight_date}"
        
        print(f"\n🔄 initialize_session(request: dict) ----------- Session Init: {session_key}")
        
        # Get available proteins by meal time for this flight+date
        meal_file = os.path.join(DATA_DIR, 'meal_df_new.csv')
        if not os.path.exists(meal_file):
            raise HTTPException(status_code=404, detail="Meal data file not found")
        
        meal_df = pd.read_csv(meal_file)
        
        # Parse flight to get segment
        if '(' in flight_number and '→' in flight_number:
            route_part = flight_number.split('(')[1].split(')')[0]
            origin, destination = route_part.split('→')
            segment_filter = f"{origin.strip()} {destination.strip()}"
        else:
            raise HTTPException(status_code=400, detail="Invalid flight number format")
        
        # Parse date and get weekday
        target_date = pd.to_datetime(flight_date).date()
        weekday = pd.to_datetime(flight_date).day_name()
        meal_df['parsed_date'] = pd.to_datetime(meal_df['segment_local_departure_date'], errors='coerce').dt.date
        
        # Filter meals for this flight+date
        filtered_meals = meal_df[
            (meal_df['segment'] == segment_filter) & 
            (meal_df['parsed_date'] == target_date)
        ]
        
        if filtered_meals.empty:
            raise HTTPException(status_code=404, detail=f"No meals found for {segment_filter} on {flight_date}")
        
        # Get proteins per meal time (prioritize Y cabin, fallback to S)
        available_proteins_by_mealtime = {}
        for meal_time in filtered_meals['meal_time'].unique():
            time_meals = filtered_meals[filtered_meals['meal_time'] == meal_time]
            y_cabin = time_meals[time_meals['cabin_class'] == 'Y']
            cabin_data = y_cabin if not y_cabin.empty else time_meals[time_meals['cabin_class'] == 'S']
            
            if not cabin_data.empty:
                proteins = sorted(cabin_data['meal_pref'].unique().tolist())
                available_proteins_by_mealtime[meal_time] = proteins
        
        if not available_proteins_by_mealtime:
            raise HTTPException(status_code=404, detail=f"No meals found for {segment_filter} on {flight_date}")
        
        # Initialize session memory structure
        SESSION_MEMORY[session_key] = {
            'flight_number': flight_number,
            'flight_date': flight_date,
            'weekday': weekday,
            'segment': segment_filter,
            'available_proteins_by_mealtime': available_proteins_by_mealtime,
            'nationality': {},
            'age': {},
            'destination': {},
            'mealtime': {}
        }
        
        # Load and normalize NATIONALITY probabilities
        nat_df = pd.read_csv(os.path.join(DATA_DIR, 'Nationality.csv'))
        nat_count = 0
        for _, row in nat_df.iterrows():
            nat_code = row['nationality_code']
            day_of_week = row['day_of_week']
            
            # Create entries for each meal time with restricted proteins
            for meal_time, proteins in available_proteins_by_mealtime.items():
                row_key = f"{nat_code}_{day_of_week}_{meal_time}"
                normalized_probs = normalize_probabilities_for_proteins(row.to_dict(), proteins)
                
                SESSION_MEMORY[session_key]['nationality'][row_key] = {
                    'nationality_code': nat_code,
                    'day_of_week': day_of_week,
                    'meal_time': meal_time,
                    'current_probabilities': normalized_probs.copy(),
                    'default_probabilities': normalized_probs.copy(),
                    'marker': 'no_change',
                    'available_proteins': proteins
                }
                nat_count += 1
        
        # Load and normalize AGE probabilities
        age_df = pd.read_csv(os.path.join(DATA_DIR, 'Age.csv'))
        age_count = 0
        for _, row in age_df.iterrows():
            age_group = row['age_group']
            
            for meal_time, proteins in available_proteins_by_mealtime.items():
                row_key = f"{age_group}_{meal_time}"
                normalized_probs = normalize_probabilities_for_proteins(row.to_dict(), proteins)
                
                SESSION_MEMORY[session_key]['age'][row_key] = {
                    'age_group': age_group,
                    'meal_time': meal_time,
                    'current_probabilities': normalized_probs.copy(),
                    'default_probabilities': normalized_probs.copy(),
                    'marker': 'no_change',
                    'available_proteins': proteins
                }
                age_count += 1
        
        # Load and normalize DESTINATION probabilities
        dest_df = pd.read_csv(os.path.join(DATA_DIR, 'Destination.csv'))
        dest_count = 0
        for _, row in dest_df.iterrows():
            dest_region = row['destination_region']
            
            for meal_time, proteins in available_proteins_by_mealtime.items():
                row_key = f"{dest_region}_{meal_time}"
                normalized_probs = normalize_probabilities_for_proteins(row.to_dict(), proteins)
                
                SESSION_MEMORY[session_key]['destination'][row_key] = {
                    'destination_region': dest_region,
                    'meal_time': meal_time,
                    'current_probabilities': normalized_probs.copy(),
                    'default_probabilities': normalized_probs.copy(),
                    'marker': 'no_change',
                    'available_proteins': proteins
                }
                dest_count += 1
        
        # Load and normalize MEALTIME probabilities
        meal_df_probs = pd.read_csv(os.path.join(DATA_DIR, 'MealTime.csv'))
        meal_count = 0
        for _, row in meal_df_probs.iterrows():
            meal_time = row['meal_time']
            
            if meal_time in available_proteins_by_mealtime:
                proteins = available_proteins_by_mealtime[meal_time]
                row_key = meal_time
                normalized_probs = normalize_probabilities_for_proteins(row.to_dict(), proteins)
                
                SESSION_MEMORY[session_key]['mealtime'][row_key] = {
                    'meal_time': meal_time,
                    'current_probabilities': normalized_probs.copy(),
                    'default_probabilities': normalized_probs.copy(),
                    'marker': 'no_change',
                    'available_proteins': proteins
                }
                meal_count += 1
        
        total_rows = nat_count + age_count + dest_count + meal_count
        print(f"Initialize_session(request: dict) --------------- ✅  Initialized {total_rows} rows (nat:{nat_count}, age:{age_count}, dest:{dest_count}, meal:{meal_count})\n")
        
        return {
            "success": True,
            "session_key": session_key,
            "summary": {
                "nationality_rows": nat_count,
                "age_rows": age_count,
                "destination_rows": dest_count,
                "mealtime_rows": meal_count,
                "total_rows": nat_count + age_count + dest_count + meal_count
            },
            "available_proteins_by_mealtime": available_proteins_by_mealtime
        }
        
    except Exception as e:
        print(f"❌ Error initializing session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-session-probability")
async def update_session_probability(request: dict):
    """
    Update a single probability row in session memory.
    Turns marker from 'no_change' to 'user_modified' and updates current_probabilities.
    """
    try:
        session_key = request.get("session_key")
        metric_type = request.get("metric_type")  # 'nationality', 'age', 'destination', 'mealtime'
        row_key = request.get("row_key")
        new_probabilities = request.get("probabilities")  # {protein: probability}
        
        if not session_key or session_key not in SESSION_MEMORY:
            raise HTTPException(status_code=404, detail="Session not found. Please reinitialize.")
        
        if metric_type not in SESSION_MEMORY[session_key]:
            raise HTTPException(status_code=400, detail=f"Invalid metric_type: {metric_type}")
        
        if row_key not in SESSION_MEMORY[session_key][metric_type]:
            raise HTTPException(status_code=404, detail=f"Row key not found: {row_key}")
        
        # Update the row
        row = SESSION_MEMORY[session_key][metric_type][row_key]
        row['current_probabilities'] = new_probabilities
        
        # Check if different from default to set marker
        is_different = False
        for protein, prob in new_probabilities.items():
            default_prob = row['default_probabilities'].get(protein, 0)
            if abs(prob - default_prob) > 0.001:  # Tolerance for floating point
                is_different = True
                break
        
        row['marker'] = 'user_modified' if is_different else 'no_change'
        
        if is_different:
            print(f"📝update_session_probability() --------------- Modified: {metric_type}/{row_key}")
        
        return {
            "success": True,
            "marker": row['marker'],
            "message": f"Row updated: {row_key}"
        }
        
    except Exception as e:
        print(f"❌ Error updating session probability: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get-modified-rows")
async def get_modified_rows(session_key: str):
    """
    Get all rows with marker='user_modified' for display in frontend.
    Shows both default and current probabilities for comparison.
    In frontend it is a table.
    """
    try:
        if not session_key or session_key not in SESSION_MEMORY:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = SESSION_MEMORY[session_key]
        modified_rows = []
        
        # Check all metric types
        for metric_type in ['nationality', 'age', 'destination', 'mealtime']:
            for row_key, row_data in session.get(metric_type, {}).items():
                if row_data['marker'] == 'user_modified':
                    modified_rows.append({
                        'metric_type': metric_type,
                        'row_key': row_key,
                        'default_probabilities': row_data['default_probabilities'],
                        'current_probabilities': row_data['current_probabilities'],
                        'available_proteins': row_data['available_proteins'],
                        'row_details': {k: v for k, v in row_data.items() 
                                      if k not in ['current_probabilities', 'default_probabilities', 
                                                   'marker', 'available_proteins']}
                    })
        
        return {
            "success": True,
            "modified_rows": modified_rows,
            "count": len(modified_rows)
        }
        
    except Exception as e:
        print(f"❌ Error getting modified rows: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/master-metrics")
def get_master_metrics(flight_number: Optional[str] = None, flight_date: Optional[str] = None):
    """Get current master metrics configuration from CSV files, with meal-time-specific protein availability"""
    try:
        response = {
            "nationality_importance": default_metrics.nationality_importance,
            "age_importance": default_metrics.age_importance,
            "destination_importance": default_metrics.destination_importance,
            "mealtime_importance": default_metrics.mealtime_importance,
            "nationality_sample": [],
            "age_sample": [],
            "destination_sample": [],
            "mealtime_sample": [],
            "available_proteins": ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian'],
            "available_proteins_by_mealtime": {}  # NEW: Meal-time-specific proteins
        }
        
        # Determine available proteins BY MEAL TIME from meal data if flight info provided
        available_proteins_by_mealtime = {}
        if flight_number and flight_date:
            try:
                meal_file = os.path.join(DATA_DIR, 'meal_df_new.csv')
                if os.path.exists(meal_file):
                    meal_df = pd.read_csv(meal_file)
                    
                    # Parse flight_number to extract origin and destination
                    if '(' in flight_number and '→' in flight_number:
                        route_part = flight_number.split('(')[1].split(')')[0]  # "AKL → SIN"
                        origin, destination = route_part.split('→')
                        origin = origin.strip()
                        destination = destination.strip()
                        segment_filter = f"{origin} {destination}"
                        
                        # Parse date
                        target_date = pd.to_datetime(flight_date).date()
                        meal_df['parsed_date'] = pd.to_datetime(meal_df['segment_local_departure_date'], errors='coerce').dt.date
                        
                        # Filter by segment and date
                        filtered_meals = meal_df[
                            (meal_df['segment'] == segment_filter) & 
                            (meal_df['parsed_date'] == target_date)
                        ]
                        
                        if not filtered_meals.empty:
                            # Get proteins PER MEAL TIME from Y cabin, or S cabin if Y not available
                            for meal_time in filtered_meals['meal_time'].unique():
                                time_meals = filtered_meals[filtered_meals['meal_time'] == meal_time]
                                
                                y_cabin_meals = time_meals[time_meals['cabin_class'] == 'Y']
                                if not y_cabin_meals.empty:
                                    proteins = sorted(y_cabin_meals['meal_pref'].unique().tolist())
                                else:
                                    s_cabin_meals = time_meals[time_meals['cabin_class'] == 'S']
                                    if not s_cabin_meals.empty:
                                        proteins = sorted(s_cabin_meals['meal_pref'].unique().tolist())
                                    else:
                                        proteins = []
                                
                                if proteins:
                                    available_proteins_by_mealtime[meal_time] = proteins
                            
                            print(f"\n=== MEAL-TIME-SPECIFIC PROTEINS ===")
                            print(f"Flight: {segment_filter} on {flight_date}")
                            for meal_time, proteins in available_proteins_by_mealtime.items():
                                print(f"  {meal_time}: {proteins}")
                            print("=" * 50 + "\n")
                            
                            response['available_proteins_by_mealtime'] = available_proteins_by_mealtime
                            # Also set global available_proteins to union of all meal times
                            all_proteins = set()
                            for proteins in available_proteins_by_mealtime.values():
                                all_proteins.update(proteins)
                            response['available_proteins'] = sorted(list(all_proteins))
            except Exception as e:
                print(f"Error extracting available proteins: {e}")
                import traceback
                traceback.print_exc()
        
        # Load CSV data and structure it BY MEAL TIME
        # Each metric will be organized as: {meal_time: [rows filtered for that meal time]}
        
        # Define all protein columns for normalization
        all_protein_columns = ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian']
        
        def normalize_probabilities_for_available_proteins(df, available_proteins_list):
            """
            Normalize protein probabilities to sum to 1.0 for each row,
            considering only the proteins available for that specific meal time
            """
            df = df.copy()
            for idx in range(len(df)):
                # Only sum the available proteins for this meal time
                row_total = sum(df.loc[idx, protein] for protein in available_proteins_list if protein in df.columns)
                # Normalize only the available proteins
                if row_total > 0:
                    for protein in available_proteins_list:
                        if protein in df.columns:
                            df.loc[idx, protein] = df.loc[idx, protein] / row_total
                # Zero out unavailable proteins
                for protein in all_protein_columns:
                    if protein not in available_proteins_list and protein in df.columns:
                        df.loc[idx, protein] = 0.0
            return df
        
        # Structure: response[metric_sample][meal_time] = normalized rows for that meal time
        response_structure = {
            'nationality_sample': {},
            'age_sample': {},
            'destination_sample': {},
            'mealtime_sample': {}
        }
        
        # Load Nationality.csv and split by meal time
        nationality_file = os.path.join(DATA_DIR, 'Nationality.csv')
        if os.path.exists(nationality_file):
            nat_df = pd.read_csv(nationality_file)
            for meal_time, proteins in available_proteins_by_mealtime.items():
                # Normalize for this meal time's proteins
                meal_time_df = normalize_probabilities_for_available_proteins(nat_df.copy(), proteins)
                response_structure['nationality_sample'][meal_time] = meal_time_df.to_dict('records')
        
        # Load Age.csv and split by meal time
        age_file = os.path.join(DATA_DIR, 'Age.csv')
        if os.path.exists(age_file):
            age_df = pd.read_csv(age_file)
            for meal_time, proteins in available_proteins_by_mealtime.items():
                meal_time_df = normalize_probabilities_for_available_proteins(age_df.copy(), proteins)
                response_structure['age_sample'][meal_time] = meal_time_df.to_dict('records')
        
        # Load Destination.csv and split by meal time
        destination_file = os.path.join(DATA_DIR, 'Destination.csv')
        if os.path.exists(destination_file):
            dest_df = pd.read_csv(destination_file)
            for meal_time, proteins in available_proteins_by_mealtime.items():
                meal_time_df = normalize_probabilities_for_available_proteins(dest_df.copy(), proteins)
                response_structure['destination_sample'][meal_time] = meal_time_df.to_dict('records')
        
        # Load MealTime.csv and split by meal time (same structure for consistency)
        mealtime_file = os.path.join(DATA_DIR, 'MealTime.csv')
        if os.path.exists(mealtime_file):
            meal_df = pd.read_csv(mealtime_file)
            for meal_time, proteins in available_proteins_by_mealtime.items():
                meal_time_df = normalize_probabilities_for_available_proteins(meal_df.copy(), proteins)
                response_structure['mealtime_sample'][meal_time] = meal_time_df.to_dict('records')
        
        # Update response with the meal-time-structured data
        response.update(response_structure)
        
        return response
    except Exception as e:
        print(f"Error loading master metrics: {e}")
        import traceback
        traceback.print_exc()
        return response

@app.post("/api/predict")
async def predict_meals(request: dict):
    """
    Predict meal distribution based on master metrics
    """
    try:
        print("\n=== PREDICTION REQUEST RECEIVED ===")
        print(f"Request keys: {request.keys()}")
        
        flight_number = request.get("flight_number")
        flight_date = request.get("flight_date")
        master_metrics = request.get("master_metrics", {})
        
        print(f"Flight: {flight_number}, Date: {flight_date}")
        print(f"Master metrics keys: {master_metrics.keys() if master_metrics else 'None'}")
        
        # Check if session memory exists for this flight+date
        session_key = f"{flight_number}|{flight_date}"
        use_session_memory = session_key in SESSION_MEMORY
        
        if use_session_memory:
            print(f"\n{'='*60}")
            print(f"✅ USING SESSION MEMORY")
            print(f"Session Key: {session_key}")
            session = SESSION_MEMORY[session_key]
            modified_count = sum(1 for metric_type in ['nationality', 'age', 'destination', 'mealtime']
                               for row in session.get(metric_type, {}).values()
                               if row['marker'] == 'user_modified')
            print(f"Modified rows in session: {modified_count}")
            print(f"{'='*60}\n")
        else:
            print(f"\n{'='*60}")
            print(f"⚠️  WARNING: No session memory found for {session_key}")
            print(f"Using CSV defaults as fallback")
            print(f"{'='*60}\n")
        
        # Get weights (convert from percentage to decimal)
        nat_weight = master_metrics.get('nationality_importance', 40.0)
        age_weight = master_metrics.get('age_importance', 20.0)
        dest_weight = master_metrics.get('destination_importance', 25.0)
        meal_weight = master_metrics.get('mealtime_importance', 15.0)
        
        W1 = nat_weight / 100.0
        W2 = age_weight / 100.0
        W3 = dest_weight / 100.0
        W4 = meal_weight / 100.0
        
        # Check if using default weights
        is_default = (nat_weight == 40.0 and age_weight == 20.0 and 
                     dest_weight == 25.0 and meal_weight == 15.0)
        
        print(f"\n=== IMPORTANCE WEIGHTS USED IN PREDICTION ===")
        if is_default:
            print("🔄 Using DEFAULT WEIGHTS")
        else:
            print("✏️ Using CUSTOM WEIGHTS")
        print(f"  Nationality: {nat_weight}% (W1 = {W1:.3f})")
        print(f"  Age:         {age_weight}% (W2 = {W2:.3f})")
        print(f"  Destination: {dest_weight}% (W3 = {W3:.3f})")
        print(f"  Meal Time:   {meal_weight}% (W4 = {W4:.3f})")
        print(f"  Total: {nat_weight + age_weight + dest_weight + meal_weight}%")
        print(f"  Formula: Final = (Nat × {W1:.2f}) + (Age × {W2:.2f}) + (Dest × {W3:.2f}) + (Meal × {W4:.2f})")
        print("=" * 50 + "\n")
        
        # Load CSV defaults from cache (loaded once per server start)
        csv_cache = load_csv_defaults_once()
        csv_nationality_probs = csv_cache['nationality']
        csv_age_probs = csv_cache['age']
        csv_destination_probs = csv_cache['destination']
        csv_mealtime_probs = csv_cache['mealtime']
        csv_nationality_reasoning = csv_cache.get('nationality_reasoning', {})
        csv_age_reasoning = csv_cache.get('age_reasoning', {})
        csv_destination_reasoning = csv_cache.get('destination_reasoning', {})
        csv_mealtime_reasoning = csv_cache.get('mealtime_reasoning', {})
        
        # Get probability data from master_metrics (may be empty if no custom probs)
        nationality_probs = master_metrics.get("nationality_data", {})
        age_probs = master_metrics.get("age_data", {})
        destination_probs = master_metrics.get("destination_data", {})
        mealtime_probs = master_metrics.get("mealtime_data", {})
        has_custom_probs = master_metrics.get("has_custom_probabilities", False)
        
        # If no custom probabilities, use CSV defaults for everything
        if not has_custom_probs or len(nationality_probs) == 0:
            nationality_probs = csv_nationality_probs
            age_probs = csv_age_probs
            destination_probs = csv_destination_probs
            mealtime_probs = csv_mealtime_probs
            print(f"🔄 Using CSV defaults for all probability lookups")
        
        print(f"\n=== PROBABILITY DATA SOURCE ===")
        if has_custom_probs:
            print(f"✏️  CUSTOM PROBABILITIES DETECTED")
            print(f"   Custom nationality entries: {len(nationality_probs)}")
            print(f"   Custom age entries: {len(age_probs)}")
            print(f"   Custom destination entries: {len(destination_probs)}")
            print(f"   Custom mealtime entries: {len(mealtime_probs)}")
            print(f"   Backend will use: CUSTOM for these entries + CSV DEFAULTS for all others")
        else:
            print(f"🔄 Using CSV defaults - {len(nationality_probs)} nationality entries loaded")
        print("=" * 50 + "\n")
        
        # Load Destination.csv for airport code to region mapping
        destination_file = os.path.join(DATA_DIR, 'Destination.csv')
        destination_df = pd.read_csv(destination_file)
        airport_to_region = dict(zip(destination_df['airport_code'], destination_df['destination_region']))
        
        # Load customer data
        customers_file = os.path.join(DATA_DIR, 'customers.csv')
        df = pd.read_csv(customers_file, dtype={'age_group': str}, low_memory=False)
        
        # Fix age group
        if 'age_group' in df.columns:
            df['age_group'] = df['age_group'].replace('Feb-18', '2-18')
        
        # Parse date
        target_date = pd.to_datetime(flight_date).date()
        
        # Extract just the flight number from format "SQ 0024 (SIN → JFK)"
        # The CSV contains just "SQ 0024" in operating_flight_number column
        if '(' in flight_number:
            actual_flight_number = flight_number.split('(')[0].strip()
        else:
            actual_flight_number = flight_number.strip()
        
        print(f"Target date: {target_date}")
        print(f"Looking for flight: '{actual_flight_number}'")
        
        # Filter by flight - just strip whitespace
        flight_data = df[df['operating_flight_number'].astype(str).str.strip() == actual_flight_number]
        
        print(f"Found {len(flight_data)} rows before date filter")
        
        # Parse and filter by date
        flight_data['parsed_date'] = pd.to_datetime(
            flight_data['segment_local_departure_datetime'].str.split().str[0],
            format='%d/%m/%Y',
            dayfirst=True,
            errors='coerce'
        ).dt.date
        
        print(f"Sample dates from CSV: {flight_data['parsed_date'].head(5).tolist()}")
        print(f"Looking for target date: {target_date}")
        
        flight_data = flight_data[flight_data['parsed_date'] == target_date]
        
        # Remove Under 2 age group
        flight_data = flight_data[flight_data['age_group'] != 'Under 2']
        
        # Select cabin class based on segment (matching meal_planning.py logic)
        # SIN JFK uses S (business) class, all others use Y (economy) class
        segment = flight_data['segment'].iloc[0] if not flight_data.empty else ""
        if segment == "SIN JFK":
            flight_data = flight_data[flight_data['cabin_class'] == 'S']
        else:
            flight_data = flight_data[flight_data['cabin_class'] == 'Y']
        
        if flight_data.empty:
            return {"error": "No passenger data found"}
        
        # Extract destination airport code from segment (e.g., "SIN MAA" → "MAA")
        destination_airport = segment.split()[-1] if ' ' in segment else segment
        destination_region = airport_to_region.get(destination_airport, destination_airport)
        
        print(f"\n=== DESTINATION LOOKUP ===")
        print(f"Segment: {segment}")
        print(f"Destination Airport: {destination_airport}")
        print(f"Destination Region: {destination_region}")
        print("=" * 50 + "\n")
        
        # Add weekday
        flight_data['weekday'] = pd.to_datetime(
            flight_data['segment_local_departure_datetime'],
            format='%d/%m/%Y %H:%M',
            dayfirst=True
        ).dt.day_name()
        
        print(f"\n=== FLIGHT DATE & WEEKDAY CALCULATION ===")
        print(f"Selected Date: {target_date}")
        print(f"Calculated Weekday: {flight_data['weekday'].iloc[0] if not flight_data.empty else 'N/A'}")
        print(f"This weekday will be used for nationality-based probability lookup")
        print("=" * 50 + "\n")
        
        # Get available meals for this flight
        meal_file = os.path.join(DATA_DIR, 'meal_df_new.csv')
        meal_df = pd.read_csv(meal_file)
        meal_df['parsed_date'] = pd.to_datetime(meal_df['segment_local_departure_date'], errors='coerce').dt.date
        
        # Get segment and cabin from flight (segment already extracted above)
        cabin = flight_data['cabin_class'].iloc[0]
        
        # Get meals for this flight
        flight_meals = meal_df[(meal_df['segment'] == segment) & 
                               (meal_df['parsed_date'] == target_date) &
                               (meal_df['cabin_class'] == cabin)]
        
        print(f"\n=== AVAILABLE MEALS FOR THIS FLIGHT ===")
        print(f"Segment: {segment}, Date: {target_date}, Cabin: {cabin}")
        print(f"Total meal records found: {len(flight_meals)}")
        if not flight_meals.empty:
            for meal_time in flight_meals['meal_time'].unique():
                time_meals = flight_meals[flight_meals['meal_time'] == meal_time]
                proteins = time_meals['meal_pref'].unique().tolist()
                print(f"  {meal_time}: {proteins}")
        print("=" * 50 + "\n")
        
        # Create feature_set column (matching meal_planning.py line 218-222)
        flight_data['feature_set'] = (
            flight_data['nationality_code'].astype(str) + '_' +
            flight_data['age_group'].astype(str) + '_' +
            flight_data['destination_region'].astype(str) + '_' +
            flight_data['meal_time'].astype(str)
        )
        
        # Group passengers (matching meal_planning.py line 211-213 exactly)
        # IMPORTANT: Order of groupby columns affects iteration order!
        grouped = flight_data.groupby([
            'segment', 'cabin_class', 'parsed_date', 'weekday', 'feature_set'
        ]).size().reset_index(name='passenger_count')
        
        # Get feature details for each feature_set
        feature_details = flight_data.groupby('feature_set').agg({
            'nationality_code': 'first',
            'age_group': 'first',
            'destination_region': 'first',
            'meal_time': 'first'
        }).reset_index()
        
        grouped = grouped.merge(feature_details, on='feature_set', how='left')
        
        # Process each group
        results_by_mealtime = {}
        print(f"🔄 Processing {len(grouped)} passenger groups...")
        
        # Track unique nationality+weekday combinations for logging
        nat_weekday_combinations = set()
        
        # Track meal-time-specific proteins for logging
        mealtime_proteins_used = {}
        
        for _, group in grouped.iterrows():
            meal_time = group['meal_time']
            nationality = group['nationality_code']
            age_group = group['age_group']
            # Use destination_region from segment lookup instead of customer CSV
            destination = destination_region
            weekday = group['weekday']
            passenger_count = group['passenger_count']
            
            # Track for logging
            nat_weekday_combinations.add(f"{nationality}_{weekday}")
            
            # Get available proteins for this meal time
            time_meals = flight_meals[flight_meals['meal_time'] == meal_time]
            if time_meals.empty:
                continue
            
            # IMPORTANT: Sort alphabetically for deterministic ordering
            # .unique().tolist() can have non-deterministic order in some pandas versions
            # Alphabetical sort ensures consistent tie-breaking in largest remainder method
            available_proteins = sorted(time_meals['meal_pref'].unique().tolist())
            
            # Track meal-time-specific proteins
            if meal_time not in mealtime_proteins_used:
                mealtime_proteins_used[meal_time] = sorted(available_proteins)
            
            # Get probabilities for each metric
            # PRIORITY: Session Memory > CSV Cache
            
            # Nationality (with weekday and meal_time)
            nat_key = f"{nationality}_{weekday}_{meal_time}"
            if use_session_memory and nat_key in session['nationality']:
                nat_prob_dict = session['nationality'][nat_key]['current_probabilities']
            else:
                # Fallback to CSV cache (old format without meal_time)
                csv_key = f"{nationality}_{weekday}"
                nat_prob_dict = csv_nationality_probs.get(csv_key, {})
                # Normalize for available proteins
                if nat_prob_dict:
                    nat_prob_dict = normalize_probabilities_for_proteins(nat_prob_dict, available_proteins)
                if not nat_prob_dict:
                    print(f"⚠️  WARNING: No probability data found for {nat_key}")
            
            # Age (meal-time-specific)
            age_key = f"{age_group}_{meal_time}"
            if use_session_memory and age_key in session['age']:
                age_prob_dict = session['age'][age_key]['current_probabilities']
            else:
                # Fallback to CSV cache
                age_prob_dict = csv_age_probs.get(age_group, {})
                # Normalize for available proteins
                if age_prob_dict:
                    age_prob_dict = normalize_probabilities_for_proteins(age_prob_dict, available_proteins)
                if not age_prob_dict:
                    print(f"⚠️  WARNING: No probability data found for age {age_group}")
            
            # Destination (meal-time-specific)
            dest_key = f"{destination}_{meal_time}"
            if use_session_memory and dest_key in session['destination']:
                dest_prob_dict = session['destination'][dest_key]['current_probabilities']
            else:
                # Fallback to CSV cache
                dest_prob_dict = csv_destination_probs.get(destination, {})
                # Normalize for available proteins
                if dest_prob_dict:
                    dest_prob_dict = normalize_probabilities_for_proteins(dest_prob_dict, available_proteins)
                if not dest_prob_dict:
                    print(f"⚠️  WARNING: No probability data found for destination {destination}")
            
            # Meal time
            if use_session_memory and meal_time in session['mealtime']:
                meal_prob_dict = session['mealtime'][meal_time]['current_probabilities']
            else:
                # Fallback to CSV cache
                meal_prob_dict = csv_mealtime_probs.get(meal_time, {})
                # Normalize for available proteins
                if meal_prob_dict:
                    meal_prob_dict = normalize_probabilities_for_proteins(meal_prob_dict, available_proteins)
                if not meal_prob_dict:
                    print(f"⚠️  WARNING: No probability data found for meal time {meal_time}")
            
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
            exact_counts = {}
            
            for protein in available_proteins:
                exact = passenger_count * final_probs[protein]
                exact_counts[protein] = exact
                floor_count = int(exact)
                protein_counts[protein] = floor_count
                remainders[protein] = exact - floor_count
            
            # Distribute remaining passengers using largest remainder method
            total_allocated = sum(protein_counts.values())
            remaining = passenger_count - total_allocated
            
            if remaining > 0:
                # Use stable sort (preserves input order on ties)
                sorted_proteins = sorted(available_proteins, key=lambda p: remainders[p], reverse=True)
                for i in range(remaining):
                    protein_counts[sorted_proteins[i]] += 1
            
            # Add to results
            if meal_time not in results_by_mealtime:
                results_by_mealtime[meal_time] = {}
            
            for protein, count in protein_counts.items():
                if protein not in results_by_mealtime[meal_time]:
                    results_by_mealtime[meal_time][protein] = 0
                results_by_mealtime[meal_time][protein] += count
        
        print(f"✅ Finished processing all passenger groups")
        
        # Load historical/original counts for comparison
        original_counts_by_mealtime = {}
        if not flight_data.empty and 'segment' in flight_data.columns:
            segment = flight_data['segment'].iloc[0]
            for meal_time in results_by_mealtime.keys():
                original_counts = load_prediction_results(segment, flight_date, cabin, meal_time)
                if original_counts:
                    original_counts_by_mealtime[meal_time] = original_counts
        
        # Get cabin-specific passenger count
        if 'customer_number' in flight_data.columns:
            cabin_passengers_for_prediction = int(flight_data['customer_number'].nunique())
        else:
            cabin_passengers_for_prediction = int(flight_data.shape[0])
        
        # Sort proteins alphabetically within each meal time
        sorted_meal_times = {meal_time: dict(sorted(proteins.items())) for meal_time, proteins in results_by_mealtime.items()}
        sorted_original_counts = {meal_time: dict(sorted(proteins.items())) for meal_time, proteins in original_counts_by_mealtime.items()}
        
        # Calculate top nationalities with reasoning for AI summary
        nationality_counts = flight_data.groupby('nationality_code').size().reset_index(name='count')
        nationality_counts = nationality_counts.sort_values('count', ascending=False).head(5)
        total_passengers_count = len(flight_data)
        
        # Get weekday for this flight
        flight_weekday = flight_data['weekday'].iloc[0] if not flight_data.empty else ""
        
        top_nationalities = []
        for _, nat_row in nationality_counts.iterrows():
            nat_code = nat_row['nationality_code']
            nat_count = nat_row['count']
            nat_percentage = (nat_count / total_passengers_count) * 100
            
            # Get reasoning from CSV
            nat_key = f"{nat_code}_{flight_weekday}"
            reasoning = csv_nationality_reasoning.get(nat_key, "")
            
            # Get sources if available (from Nationality.csv)
            sources = ""
            if nat_key in nationality_probs:
                # Try to get sources from original CSV
                nationality_file = os.path.join(DATA_DIR, 'Nationality.csv')
                if os.path.exists(nationality_file):
                    nat_df = pd.read_csv(nationality_file)
                    nat_record = nat_df[(nat_df['nationality_code'] == nat_code) & 
                                       (nat_df['day_of_week'] == flight_weekday)]
                    if not nat_record.empty and 'sources' in nat_record.columns:
                        sources = str(nat_record.iloc[0]['sources']) if pd.notna(nat_record.iloc[0]['sources']) else ""
            
            top_nationalities.append({
                'nationality_code': nat_code,
                'count': int(nat_count),
                'percentage': float(nat_percentage),
                'reasoning': reasoning,
                'sources': sources
            })
        
        print(f"\n=== TOP 5 NATIONALITIES ===")
        for nat in top_nationalities:
            print(f"  {nat['nationality_code']}: {nat['count']} passengers ({nat['percentage']:.1f}%)")
            if nat['reasoning']:
                print(f"    Reasoning: {nat['reasoning'][:100]}...")
        print("=" * 50 + "\n")
        
        # Format passenger details for AI summary
        passenger_details_list = []
        for _, group in grouped.iterrows():
            meal_time = group['meal_time']
            nationality = group['nationality_code']
            age_group = group['age_group']
            # Use destination_region from segment lookup instead of customer CSV
            destination = destination_region
            weekday = group['weekday']
            passenger_count = group['passenger_count']
            
            # Get available proteins for this meal time
            time_meals = flight_meals[flight_meals['meal_time'] == meal_time]
            if time_meals.empty:
                continue
            
            available_proteins = time_meals['meal_pref'].unique().tolist()
            
            # Get probabilities for each metric
            nat_key = f"{nationality}_{weekday}"
            nat_prob_dict = nationality_probs.get(nat_key, {})
            # Normalize for available proteins if using CSV defaults
            if nat_prob_dict and not has_custom_probs:
                nat_prob_dict = normalize_probabilities_for_proteins(nat_prob_dict, available_proteins)
            
            age_key = f"{age_group}_{meal_time}"
            age_prob_dict = age_probs.get(age_key, {})
            if not age_prob_dict:
                age_prob_dict = age_probs.get(age_group, {})
            # Normalize for available proteins if using CSV defaults
            if age_prob_dict and not has_custom_probs:
                age_prob_dict = normalize_probabilities_for_proteins(age_prob_dict, available_proteins)
            
            dest_key = f"{destination}_{meal_time}"
            dest_prob_dict = destination_probs.get(dest_key, {})
            if not dest_prob_dict:
                dest_prob_dict = destination_probs.get(destination, {})
            # Normalize for available proteins if using CSV defaults
            if dest_prob_dict and not has_custom_probs:
                dest_prob_dict = normalize_probabilities_for_proteins(dest_prob_dict, available_proteins)
            
            meal_prob_dict = mealtime_probs.get(meal_time, {})
            # Normalize for available proteins if using CSV defaults
            if meal_prob_dict and not has_custom_probs:
                meal_prob_dict = normalize_probabilities_for_proteins(meal_prob_dict, available_proteins)
            
            # DEBUG: Log first group's probabilities
            if len(passenger_details_list) == 0:  # Log only for the very first group
                print(f"\n🔍 DEBUG: Probabilities for FIRST passenger group:")
                print(f"   Nationality: {nationality}, Weekday: {weekday}")
                print(f"   Nationality key: {nat_key}")
                print(f"   Nationality probs: {nat_prob_dict}")
                print(f"   Age: {age_group}, Meal time: {meal_time}")
                print(f"   Age key: {age_key}")
                print(f"   Age probs: {age_prob_dict}")
                print(f"   Destination: {destination}")
                print(f"   Dest key: {dest_key}")
                print(f"   Dest probs: {dest_prob_dict}")
                print(f"   Meal time: {meal_time}")
                print(f"   Meal probs: {meal_prob_dict}")
                print(f"   Available proteins: {available_proteins}")
                print(f"   Weights: W1={W1}, W2={W2}, W3={W3}, W4={W4}\n")
            
            # Calculate weighted probabilities for this group
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
            
            passenger_details_list.append({
                'nationality': nationality,
                'age_group': age_group,
                'destination': f"{destination_airport} ({destination})",  # e.g., "MAA (South Asia)"
                'meal_time': meal_time,
                'weekday': weekday,
                'count': int(passenger_count),
                'probabilities': final_probs,
                'metric_probabilities': {  # NEW: Individual metric probabilities for AI analysis
                    'nationality': {protein: nat_prob_dict.get(protein, 0) for protein in available_proteins},
                    'age': {protein: age_prob_dict.get(protein, 0) for protein in available_proteins},
                    'destination': {protein: dest_prob_dict.get(protein, 0) for protein in available_proteins},
                    'meal_time': {protein: meal_prob_dict.get(protein, 0) for protein in available_proteins}
                },
                'reasoning': {  # NEW: Cultural/behavioral insights from CSV reasoning columns
                    'nationality': csv_nationality_reasoning.get(nat_key, ''),
                    'age': csv_age_reasoning.get(age_group, ''),
                    'destination': csv_destination_reasoning.get(destination, ''),
                    'meal_time': csv_mealtime_reasoning.get(meal_time, '')
                }
            })
        
        # Generate AI summaries for each meal time (do this during prediction for faster UX)
        print(f"🤖 Generating AI summaries for each meal time...")
        ai_summaries = {}
        for mealTime in sorted_meal_times.keys():
            try:
                # Build passenger groups for this meal time - convert dicts to Pydantic models
                passengerGroups = [
                    PassengerGroup(
                        nationality=p['nationality'],
                        age_group=p['age_group'],
                        destination=p['destination'],
                        meal_time=p['meal_time'],
                        weekday=p.get('weekday', ''),
                        count=p['count'],
                        probabilities=p.get('probabilities', {}),
                        metric_probabilities=p.get('metric_probabilities', {}),
                        reasoning=p.get('reasoning', {})
                    )
                    for p in passenger_details_list if p['meal_time'] == mealTime
                ]
                
                # Convert top nationalities to Pydantic models
                topNationalitiesModels = [
                    TopNationality(
                        nationality_code=nat['nationality_code'],
                        count=nat['count'],
                        percentage=nat['percentage'],
                        reasoning=nat.get('reasoning', ''),
                        sources=nat.get('sources', '')
                    )
                    for nat in top_nationalities
                ]
                
                # Get prediction results for this meal time
                predictionResults = sorted_meal_times[mealTime]
                
                # Get original counts for this meal time
                originalCountsForMealTime = sorted_original_counts.get(mealTime, {})
                
                # Call AI summary generation
                summary = call_kariba_llm(
                    passengerGroups,
                    {
                        "nationality_importance": nat_weight,
                        "age_importance": age_weight,
                        "destination_importance": dest_weight,
                        "mealtime_importance": meal_weight
                    },
                    predictionResults,
                    originalCountsForMealTime,
                    topNationalitiesModels
                )
                ai_summaries[mealTime] = summary
                print(f"   ✓ Generated AI summary for {mealTime} ({len(summary)} chars)")
            except Exception as e:
                print(f"   ✗ Error generating AI summary for {mealTime}: {str(e)}")
                ai_summaries[mealTime] = "AI summary not available due to an error."
        
        # Format results
        print(f"📊 Formatting final results...")
        results = {
            "flight_number": flight_number,
            "flight_date": flight_date,
            "cabin_class": cabin,
            "total_passengers": cabin_passengers_for_prediction,
            "cabin_passengers_for_prediction": cabin_passengers_for_prediction,
            "meal_times": sorted_meal_times,
            "original_counts": sorted_original_counts,  # Add original counts
            "passenger_details": passenger_details_list,  # Add passenger details for AI summary
            "weights_used": {  # Add weights used for AI summary
                "nationality_importance": nat_weight,
                "age_importance": age_weight,
                "destination_importance": dest_weight,
                "mealtime_importance": meal_weight
            },
            "top_nationalities": top_nationalities,  # Add top nationalities with reasoning
            "ai_summaries": ai_summaries  # Add pre-generated AI summaries
        }
        
        print(f"✅ Step 8/8: Prediction complete!")
        print(f"   → {results['total_passengers']} passengers, {len(results['meal_times'])} meal times")
        print(f"   → Returning results to frontend...")
        
        return results
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflow-steps")
async def get_workflow_steps():
    """Get the workflow steps for the prediction process"""
    return {
        "steps": [
            "Loading passenger booking data...",
            "Analyzing nationality distribution...",
            "Processing age demographics...",
            "Evaluating destination preferences...",
            "Calculating meal time factors...",
            "Running LLM prediction model...",
            "Optimizing meal proportions...",
            "Generating recommendations..."
        ]
    }

@app.post("/api/save-custom-metrics")
async def save_custom_metrics(request: dict):
    """
    Save user-customized probability metrics to persistent storage.
    NOTE: This NEVER modifies the original CSV files - only saves to JSON.
    """
    try:
        metrics = request.get('metrics', {})
        weights = request.get('weights', {})
        flight_number = request.get('flight_number', 'default')
        
        print(f"\n=== SAVING CUSTOM METRICS ===")
        print(f"Flight number: {flight_number}")
        print(f"Metrics keys: {metrics.keys() if metrics else 'None'}")
        print(f"Weights: {weights}")
        
        # Validate that all protein probabilities sum to 100%
        validation_errors = []
        tolerance = 0.001  # 0.1% tolerance for rounding
        
        # First, validate weights sum to 100%
        if weights:
            total_weight = (
                weights.get('nationality_importance', 0) +
                weights.get('age_importance', 0) +
                weights.get('destination_importance', 0) +
                weights.get('mealtime_importance', 0)
            )
            
            if abs(total_weight - 100) > 0.1:  # 0.1% tolerance
                validation_errors.append(
                    f"Total importance weights: {total_weight:.1f}% (must equal 100%)"
                )
                print(f"\n WEIGHT VALIDATION FAILED: Total = {total_weight:.1f}%")
        
        # Validate protein probabilities
        
        categories = ['nationality', 'age', 'destination', 'mealtime']
        proteins = ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian']
        
        for category in categories:
            sample_key = f'{category}_sample'
            if sample_key not in metrics:
                continue
            
            sample_data = metrics[sample_key]
            if not isinstance(sample_data, dict):
                continue
            
            # Data is structured by meal time: {Lunch: [...], Dinner: [...]}
            for meal_time, meal_data in sample_data.items():
                if not isinstance(meal_data, list):
                    continue
                
                for idx, row in enumerate(meal_data):
                    # Get available proteins for this meal time from metrics if provided
                    available_proteins = proteins
                    if 'available_proteins_by_mealtime' in metrics and meal_time in metrics['available_proteins_by_mealtime']:
                        available_proteins = metrics['available_proteins_by_mealtime'][meal_time]
                    
                    total = sum(row.get(protein, 0) for protein in available_proteins)
                    
                    if abs(total - 1.0) > tolerance:  # Check if total is ~1.0 (100%)
                        identifier = ''
                        if category == 'nationality':
                            identifier = f"{row.get('nationality_code', '')} ({row.get('day_of_week', '')}) - {meal_time}"
                        elif category == 'age':
                            identifier = f"{row.get('age_group', '')} - {meal_time}"
                        elif category == 'destination':
                            identifier = f"{row.get('airport_code', row.get('destination_region', ''))} - {meal_time}"
                        elif category == 'mealtime':
                            identifier = f"{row.get('meal_time', '')} - {meal_time}"
                        
                        validation_errors.append(
                            f"{category.capitalize()} - {identifier}: Total is {total*100:.1f}% (must be 100%)"
                        )
        
        if validation_errors:
            print(f"\n❌ VALIDATION FAILED: {len(validation_errors)} errors found")
            for error in validation_errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(validation_errors) > 10:
                print(f"   ... and {len(validation_errors) - 10} more errors")
            
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "Validation failed: Some protein probabilities do not sum to 100%",
                    "errors": validation_errors[:20]  # Return first 20 errors
                }
            )
        
        print("✅ Validation passed: All protein probabilities sum to 100%")
        
        # Log detailed probability data being saved
        print(f"\n DETAILED PROBABILITY DATA BEING SAVED:")
        
        # Show all probability values being saved (simpler approach - just show what's being saved)
        total_entries = 0
        
        # Show nationality data
        if 'nationality_sample' in metrics and metrics['nationality_sample']:
            nat_entries = []
            for meal_time, meal_data in metrics['nationality_sample'].items():
                if isinstance(meal_data, list):
                    for row in meal_data:
                        nat_code = row.get('nationality_code', '')
                        weekday = row.get('day_of_week', '')
                        # Show any non-zero probabilities
                        proteins_str = []
                        for protein in ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian']:
                            val = row.get(protein, 0)
                            if val > 0.01:  # Only show if > 1%
                                proteins_str.append(f"{protein}={val*100:.1f}%")
                        if proteins_str:
                            nat_entries.append(f"      {nat_code} ({weekday}) - {meal_time}: {', '.join(proteins_str)}")
                            total_entries += 1
            if nat_entries:
                print(f"\n    Nationality Data ({len(nat_entries)} entries):")
                for entry in nat_entries[:5]:  # Show first 5
                    print(entry)
                if len(nat_entries) > 5:
                    print(f"      ... and {len(nat_entries) - 5} more entries")
        
        # Show age data
        if 'age_sample' in metrics and metrics['age_sample']:
            age_entries = []
            for meal_time, meal_data in metrics['age_sample'].items():
                if isinstance(meal_data, list):
                    for row in meal_data:
                        age_group = row.get('age_group', '')
                        proteins_str = []
                        for protein in ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian']:
                            val = row.get(protein, 0)
                            if val > 0.01:  # Only show if > 1%
                                proteins_str.append(f"{protein}={val*100:.1f}%")
                        if proteins_str:
                            age_entries.append(f"      {age_group} - {meal_time}: {', '.join(proteins_str)}")
                            total_entries += 1
            if age_entries:
                print(f"\n   👥 Age Data ({len(age_entries)} entries):")
                for entry in age_entries:  # Show all age entries (usually small)
                    print(entry)
        
        # Show destination data
        if 'destination_sample' in metrics and metrics['destination_sample']:
            dest_entries = []
            for meal_time, meal_data in metrics['destination_sample'].items():
                if isinstance(meal_data, list):
                    for row in meal_data:
                        dest = row.get('destination_region', '')
                        proteins_str = []
                        for protein in ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian']:
                            val = row.get(protein, 0)
                            if val > 0.01:  # Only show if > 1%
                                proteins_str.append(f"{protein}={val*100:.1f}%")
                        if proteins_str:
                            dest_entries.append(f"      {dest} - {meal_time}: {', '.join(proteins_str)}")
                            total_entries += 1
            if dest_entries:
                print(f"\n   ✈️  Destination Data ({len(dest_entries)} entries):")
                for entry in dest_entries[:5]:  # Show first 5
                    print(entry)
                if len(dest_entries) > 5:
                    print(f"      ... and {len(dest_entries) - 5} more entries")
        
        # Show mealtime data
        if 'mealtime_sample' in metrics and metrics['mealtime_sample']:
            meal_entries = []
            for meal_time, meal_data in metrics['mealtime_sample'].items():
                if isinstance(meal_data, list):
                    for row in meal_data:
                        meal = row.get('meal_time', '')
                        proteins_str = []
                        for protein in ['Pork', 'Chicken', 'Beef', 'Seafood', 'Lamb', 'Vegetarian']:
                            val = row.get(protein, 0)
                            if val > 0.01:  # Only show if > 1%
                                proteins_str.append(f"{protein}={val*100:.1f}%")
                        if proteins_str:
                            meal_entries.append(f"      {meal}: {', '.join(proteins_str)}")
                            total_entries += 1
            if meal_entries:
                print(f"\n   🍽️  Meal Time Data ({len(meal_entries)} entries):")
                for entry in meal_entries:  # Show all mealtime entries
                    print(entry)
        
        if total_entries > 0:
            print(f"\n   ✅ TOTAL ENTRIES SAVED: {total_entries}")
        else:
            print("   ℹ️  No probability data to save")
        
        print("=" * 50 + "\n")
        
        return {
            "success": True, 
            "message": "Metrics validated successfully"
        }
    except Exception as e:
        print(f"Error validating custom metrics: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
