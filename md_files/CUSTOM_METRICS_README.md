# Custom Metrics Storage Architecture

## Important: CSV Files Are Never Modified

The meal prediction system maintains data integrity by following these principles:

### Read-Only CSV Files
The following CSV files contain the baseline probability data and are **NEVER modified** by the application:
- `Nationality.csv`
- `Age.csv`
- `Destination.csv`
- `MealTime.csv`
- `customers.csv`
- All files in `PredictionResults/`

These files represent the trained model's default probabilities and should only be updated through model retraining, not through the UI.

---

## API Endpoints & Flow

### 1. **Session Initialization** (When user lands on Master Metrics page)
```
POST /api/initialize-session
Body: { flight_number, flight_date }
```
- Loads CSV defaults for all 4 metrics (Nationality, Age, Destination, MealTime)
- Normalizes probabilities for available proteins per meal time
- Stores in `SESSION_MEMORY` dictionary with key: `"flight_number|flight_date"`
- Each row gets `marker: 'no_change'` (tracks user modifications)

### 2. **Update Probability** (When user validates a row)
```
POST /api/update-session-probability
Body: { session_key, metric_type, row_key, probabilities }
```
- Updates `current_probabilities` in session memory
- Changes `marker` from `'no_change'` → `'user_modified'`
- Keeps `default_probabilities` unchanged (for comparison)

### 3. **Get Modified Rows** (Display "Modified Rows" table)
```
GET /api/get-modified-rows?session_key=...
```
- Returns all rows where `marker == 'user_modified'`
- Shows both default and current probabilities for comparison

### 4. **Run Prediction** (When user clicks "Run Prediction")
```
POST /api/predict
Body: { flight_number, flight_date, master_metrics }
```
- **Weights**: Sent in request body (from frontend state)
- **Probabilities Priority**:
  1. Session Memory (user modifications) ← **First choice**
  2. CSV defaults (if not in session) ← **Fallback**
- Calculation: `Final = (Nat × W1) + (Age × W2) + (Dest × W3) + (Meal × W4)`

### 5. **Clear Session** (When user returns to flight selection)
```
POST /api/clear-session
```
- Clears `SESSION_MEMORY` dictionary
- User modifications lost unless saved to JSON

---

## Data Flow Diagram

```
User Action                 Frontend                Backend               Storage
────────────────────────────────────────────────────────────────────────────────
1. Select Flight    →   Load Master Metrics   →   Initialize Session  →  SESSION_MEMORY
                                                    (Load CSV defaults)

2. Edit Table Row   →   Update local state    →   (No backend call)   →  Frontend state
                        (masterData)

3. Validate Row     →   Send to backend       →   Update Session      →  SESSION_MEMORY
                        (clicked button)          (marker: modified)      (current_probs)

4. Run Prediction   →   Collect weights +     →   Check Session       →  Read SESSION_MEMORY
                        validated rows            Memory first            OR CSV defaults
                                                  Calculate results

5. Navigate Away    →   Call clear-session    →   Clear SESSION_MEMORY →  Memory cleared
```

---

## Key Concepts

**Session Memory vs Persistent Storage:**
- **Session Memory** = Temporary (cleared on navigation)
- **JSON Files** = Persistent (saved custom metrics - currently not implemented)

**Weights vs Probabilities:**
- **Weights** (Importance %) = Stored in frontend state, passed in API request
- **Probabilities** (Protein %) = Stored in session memory (backend)

**Priority System:**
```python
if session_key_exists and row_key in session:
    use session['current_probabilities']  # User's custom values
else:
    use csv_defaults                      # Original baseline
```

---

