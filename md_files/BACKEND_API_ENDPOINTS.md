# Backend API Endpoints Documentation

## Quick Reference - All Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Health check |
| GET | `/api/flights` | Get available flights with dates |
| GET | `/api/customer-summary` | Get passenger details for a flight |
| GET | `/api/available-meals` | Get meal options for a flight |
| POST | `/api/initialize-session` | Initialize session memory with defaults |
| POST | `/api/update-session-probability` | Update a single probability row |
| GET | `/api/get-modified-rows` | Get all user-modified rows |
| GET | `/api/master-metrics` | Get probability tables for Master Metrics page |
| POST | `/api/predict` | Run meal prediction calculation |
| POST | `/api/clear-session` | Clear session memory |
| GET | `/api/workflow-steps` | Get prediction workflow steps for UI |
| POST | `/api/save-custom-metrics` | Save custom metrics to JSON (not used) |

---

## Endpoint Details

### `GET /`
**Health check** - Returns API status and confirms server is running.

---

### `GET /api/flights`
**Get available flights** - Loads `customers.csv` and returns:
- List of unique flights with origin/destination
- Available dates for each flight
- Destination region categories

Used by: Flight selection screen

---

### `GET /api/customer-summary`
**Get passenger summary** - For a specific flight and date, returns:
- Total passenger count
- Cabin class distribution (Y/S)
- Nationality breakdown
- Age group breakdown
- Available meal times

Parameters: `flight_number`, `flight_date`

Used by: Master Metrics screen (summary card at top)

---

### `GET /api/available-meals`
**Get meal options** - For a specific flight and date, returns:
- Meals grouped by meal time (Lunch, Dinner, etc.)
- Protein types available (Chicken, Beef, etc.)
- Prioritizes Y cabin, falls back to S cabin

Parameters: `flight_number`, `flight_date`

Used by: Master Metrics screen (to determine available proteins)

---

### `POST /api/initialize-session`
**Initialize session memory** - Sets up session with default probabilities:
- Loads all 4 CSV files (Nationality, Age, Destination, MealTime)
- Normalizes probabilities for available proteins per meal time
- Creates session key: `"flight_number|flight_date"`
- Each row marked as `'no_change'`

Body: `{ flight_number, flight_date }`

Used by: Master Metrics screen on page load

---

### `POST /api/update-session-probability`
**Update probability row** - When user validates a row:
- Updates `current_probabilities` in session memory
- Changes marker from `'no_change'` to `'user_modified'`
- Keeps `default_probabilities` for comparison

Body: `{ session_key, metric_type, row_key, probabilities }`

Used by: Master Metrics screen when "Validate and Save Below" clicked

---

### `GET /api/get-modified-rows`
**Get user modifications** - Returns all rows where user changed values:
- Filters by `marker == 'user_modified'`
- Includes both default and current probabilities
- Used to display "Modified Rows" table

Parameters: `session_key`

Used by: Master Metrics screen (Modified Rows section)

---

### `GET /api/master-metrics`
**Get probability tables** - Returns all CSV data structured by meal time:
- Loads Nationality, Age, Destination, MealTime CSVs
- Normalizes for available proteins per meal time
- Returns data organized as: `{ meal_time: [rows] }`

Parameters: `flight_number`, `flight_date`

Used by: Master Metrics screen (populates probability tables)

---

### `POST /api/predict`
**Run prediction calculation** - Core prediction endpoint:
1. Checks if session memory exists for this flight
2. Extracts weights from request body (W1, W2, W3, W4)
3. For each passenger group:
   - Gets probabilities (Session Memory → CSV fallback)
   - Calculates: `Final = (Nat × W1) + (Age × W2) + (Dest × W3) + (Meal × W4)`
   - Normalizes to 100%
   - Allocates meals using largest remainder method
4. Returns meal counts per protein per meal time

Body: `{ flight_number, flight_date, master_metrics }`

Used by: Prediction screen

---

### `POST /api/clear-session`
**Clear session memory** - Removes all session data from memory.

Used by: When user navigates back to flight selection

---

### `GET /api/workflow-steps`
**Get workflow steps** - Returns list of 8 prediction steps for UI animation.

Used by: Prediction screen (progress display)

---

### `POST /api/save-custom-metrics`
**Save to JSON** (Legacy/Unused) - Originally intended to save custom metrics to persistent JSON files. Currently not actively used since session memory handles modifications.

---

## Data Sources

### CSV Files (Read-Only)
- `customers.csv` - Passenger data
- `Nationality.csv` - Nationality probabilities by weekday
- `Age.csv` - Age group probabilities
- `Destination.csv` - Destination region probabilities
- `MealTime.csv` - Meal time probabilities
- `meal_df_new.csv` - Available meals per flight
- `PredictionResults/*.csv` - Historical predictions for comparison

### In-Memory Storage
- `SESSION_MEMORY` - Dictionary storing user modifications per flight+date
- `CSV_DEFAULTS_CACHE` - Cached CSV data (loaded once per server start)

---

## Key Concepts

**Session Key Format**: `"flight_number|flight_date"` (e.g., `"SQ 0286 (AKL → SIN)|2024-06-01"`)

**Probability Priority**: Session Memory (user modified) → CSV Defaults (baseline)

**Weights vs Probabilities**:
- Weights = Importance percentages (sent in request)
- Probabilities = Protein percentages (stored in session memory)
