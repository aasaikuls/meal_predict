# AI Summary Explanation

## Overview

The `ai_summary.py` module generates executive summaries explaining **why** the meal predictions look the way they do. It uses an LLM (Large Language Model) via the Kariba API to analyze passenger groups, feature weights, and prediction results.

---

## What Are Passenger Groups?

**Passenger groups** are clusters of passengers who share the same characteristics (features):

- **Nationality** (e.g., SG, IN, US)
- **Age Group** (e.g., 19-30, 31-50, 51-65)
- **Destination Region** (e.g., Southeast Asia, South Asia, Europe)
- **Meal Time** (e.g., Breakfast, Lunch, Dinner)
- **Weekday** (e.g., Monday, Tuesday)

### Example Passenger Groups

For flight **SIN-MAA on June 1, 2024 (Saturday)**:

```
Group 1: 15 passengers
- Profile: Nationality=SG, Age=19-30, Destination=South Asia, Meal Time=Lunch, Weekday=Saturday
- Count: 15 passengers

Group 2: 8 passengers
- Profile: Nationality=IN, Age=31-50, Destination=South Asia, Meal Time=Lunch, Weekday=Saturday
- Count: 8 passengers

Group 3: 22 passengers
- Profile: Nationality=US, Age=51-65, Destination=South Asia, Meal Time=Dinner, Weekday=Saturday
- Count: 22 passengers

... (many more groups)
```

Each group gets **different meal probabilities** based on their unique feature combination.

---

## How It Works

### Step 1: Predict Meals (from `main.py`)

1. **Group passengers** by features (nationality, age, destination, meal_time)
2. **Calculate probabilities** for each protein type using weighted LLM probabilities
3. **Apply largest remainder method** to distribute whole meals to each group
4. **Sum up all groups** to get final meal counts

### Step 2: Generate AI Summary (from `ai_summary.py`)

The backend calls the `/api/ai-summary` endpoint with:
- **Passenger groups** (with their probabilities)
- **Feature weights** (importance percentages)
- **Final predicted meal counts**

The LLM analyzes this data and generates a 2-bullet executive summary.

---

## Input to the LLM

### Example Input Structure

```json
{
  "flight_number": "SQ402",
  "flight_date": "2024-06-01",
  "weights": {
    "nationality_importance": 40,
    "age_importance": 20,
    "destination_importance": 25,
    "meal_time_importance": 15
  },
  "passenger_groups": [
    {
      "nationality": "SG",
      "age_group": "19-30",
      "destination": "South Asia",
      "meal_time": "Lunch",
      "weekday": "Saturday",
      "count": 15,
      "probabilities": {
        "Chicken": 0.445,
        "Seafood": 0.234,
        "Vegetarian": 0.321
      },
      "metric_probabilities": {
        "nationality": {
          "Chicken": 0.40,
          "Seafood": 0.25,
          "Vegetarian": 0.35
        },
        "age": {
          "Chicken": 0.50,
          "Seafood": 0.20,
          "Vegetarian": 0.30
        },
        "destination": {
          "Chicken": 0.45,
          "Seafood": 0.25,
          "Vegetarian": 0.30
        },
        "meal_time": {
          "Chicken": 0.45,
          "Seafood": 0.20,
          "Vegetarian": 0.35
        }
      }
    },
    {
      "nationality": "IN",
      "age_group": "31-50",
      "destination": "South Asia",
      "meal_time": "Lunch",
      "weekday": "Saturday",
      "count": 8,
      "probabilities": {
        "Chicken": 0.356,
        "Seafood": 0.189,
        "Vegetarian": 0.455
      },
      "metric_probabilities": {
        "nationality": {
          "Chicken": 0.30,
          "Seafood": 0.15,
          "Vegetarian": 0.55
        },
        "age": {
          "Chicken": 0.40,
          "Seafood": 0.20,
          "Vegetarian": 0.40
        },
        "destination": {
          "Chicken": 0.38,
          "Seafood": 0.20,
          "Vegetarian": 0.42
        },
        "meal_time": {
          "Chicken": 0.35,
          "Seafood": 0.18,
          "Vegetarian": 0.47
        }
      }
    }
  ],
  "prediction_results": {
    "Chicken": 94,
    "Seafood": 49,
    "Vegetarian": 68
  },
  "original_counts": {
    "Chicken": 90,
    "Seafood": 55,
    "Vegetarian": 66
  }
}
```

---

## LLM Prompt Format

The system constructs a prompt like this:

```
You are generating an executive summary for airline meal planning leadership. 
The results below are from taking LLM Probabilities for each feature and giving each feature some weights (importance).
The resultant Final Weighted Probabilities for each group determines the number of meals of each protein type allocated in the passenger group.

Inputs provided:
- Feature weights
- Passenger group breakdown (counts + final weighted protein probabilities)
- Final predicted meal counts

FEATURE WEIGHTS:
- Nationality Importance: 40%
- Age Importance: 20%
- Destination Importance: 25%
- Meal Time Importance: 15%

PASSENGER GROUPS:
Passenger Group: 15 passengers
- Profile: Nationality=SG, Age Group=19-30, Destination=South Asia, Meal Time=Lunch, Weekday=Saturday
- Final Weighted Probabilities: Chicken: 44.5%, Seafood: 23.4%, Vegetarian: 32.1%
- Feature-Specific Probabilities:
  * Nationality: Chicken: 40.0%, Seafood: 25.0%, Vegetarian: 35.0%
  * Age: Chicken: 50.0%, Seafood: 20.0%, Vegetarian: 30.0%
  * Destination: Chicken: 45.0%, Seafood: 25.0%, Vegetarian: 30.0%
  * Meal Time: Chicken: 45.0%, Seafood: 20.0%, Vegetarian: 35.0%

Passenger Group: 8 passengers
- Profile: Nationality=IN, Age Group=31-50, Destination=South Asia, Meal Time=Lunch, Weekday=Saturday
- Final Weighted Probabilities: Chicken: 35.6%, Seafood: 18.9%, Vegetarian: 45.5%
- Feature-Specific Probabilities:
  * Nationality: Chicken: 30.0%, Seafood: 15.0%, Vegetarian: 55.0%
  * Age: Chicken: 40.0%, Seafood: 20.0%, Vegetarian: 40.0%
  * Destination: Chicken: 38.0%, Seafood: 20.0%, Vegetarian: 42.0%
  * Meal Time: Chicken: 35.0%, Seafood: 18.0%, Vegetarian: 47.0%

... (more groups)

FINAL PREDICTED MEAL COUNTS:
- Chicken: 94 meals
- Seafood: 49 meals
- Vegetarian: 68 meals

TASK:
Provide a VERY SHORT executive summary explaining why the predicted meal mix looks this way.

STRICT RULES (must follow):
- Output ONLY 2 bullets maximum
- Each bullet MUST be one sentence only
- Max 25 words per bullet
- No parentheses, no examples, no sub-clauses
- Focus on scale and impact, not explanation
- Use business language, not data science language

FORMAT (exactly): Please name the bullet point as key driver and not trend.
- Key driver 1: <one short sentence>
- Key driver 2: <one short sentence or omit if not needed>
```

---

## Example LLM Output

```
- Key driver 1: Indian passengers with high vegetarian preference dominate the flight composition
- Key driver 2: Lunch service attracts mixed protein demand across young and middle-aged travelers
```

---

## Key Components

### 1. **PassengerGroup Class**
Defines the structure of each passenger group:
- Demographics (nationality, age, destination)
- Context (meal_time, weekday)
- Count (number of passengers)
- Probabilities (final weighted + individual feature probabilities)

### 2. **call_kariba_llm Function**
- Formats passenger groups, weights, and predictions into a prompt
- Calls Kariba API with GPT-5-mini model
- Returns a 2-bullet executive summary

### 3. **/api/ai-summary Endpoint**
- Receives prediction data from frontend
- Calls LLM to generate summary
- Returns summary text for display

---

## Why This Is Useful

Instead of showing users:
> "94 Chicken, 49 Seafood, 68 Vegetarian"

The AI explains **why**:
> "Indian passengers with high vegetarian preference dominate the flight composition"

This helps airline planners understand the **business reasons** behind the predictions, not just the numbers.

---

## Configuration

- **API URL**: `KARIBA_API_URL` environment variable
- **Model**: `GPT5-mini` (default)
- **User Token**: `LLM_USER_TOKEN` environment variable (required for authentication)

### Setting User Token

```bash
# In .env file or environment
LLM_USER_TOKEN=your_actual_token_here
```

⚠️ **Note**: Current code has a hardcoded test token - replace with your actual token for production!

---

## Error Handling

The system handles:
- **403 Forbidden**: Invalid/expired user token
- **Network errors**: Connection timeouts, SSL issues
- **API failures**: Returns user-friendly error messages

If LLM fails, it shows:
> "AI summary not available due to connection error. Please check network connectivity."

---

## Technical Flow

```
Frontend (ResultsDisplay.jsx)
    ↓
POST /api/ai-summary
    ↓
ai_summary.py → call_kariba_llm()
    ↓
Kariba API (GPT-5-mini)
    ↓
2-bullet executive summary
    ↓
Display in UI
```

---

## Data Privacy

- Uses `pii_type: ["no_pii"]` to indicate no personally identifiable information
- Only aggregated passenger group data is sent (no individual passenger details)
- SSL verification disabled for internal API calls (controlled environment)
