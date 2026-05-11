from pydantic import BaseModel
from typing import Dict, List, Optional, Any


# ── Flight / Customer schemas ──────────────────────────────────────────────────

class FlightInfo(BaseModel):
    flightNumber: str
    origin: str
    destination: str
    route: str
    category: str
    availableDates: List[str]


class FlightsResponse(BaseModel):
    flights: List[FlightInfo]
    categories: List[str]


class CustomerSummaryResponse(BaseModel):
    flight_number: str
    flight_date: str
    day_of_week: str
    total_customers: int
    cabin_distribution: Dict[str, int]
    destination_airport: str
    meal_times: List[str]
    analysis_cabin: Optional[str]
    nationality_breakdown: Dict[str, int]
    age_breakdown: Dict[str, int]


class MealItem(BaseModel):
    cabin_class: str
    meal_name: str
    meal_pref: str


class AvailableMealsResponse(BaseModel):
    flight_number: str
    flight_date: str
    segment: str
    meals_by_time: Dict[str, List[MealItem]]


# ── Session schemas ────────────────────────────────────────────────────────────

class InitSessionRequest(BaseModel):
    flight_number: str
    flight_date: str


class UpdateSessionProbabilityRequest(BaseModel):
    session_key: str
    metric_type: str
    row_key: str
    probabilities: Dict[str, float]


# ── Metrics schemas ────────────────────────────────────────────────────────────

class MasterMetrics(BaseModel):
    nationality_importance: float = 40.0
    age_importance: float = 20.0
    destination_importance: float = 25.0
    mealtime_importance: float = 15.0
    nationality_data: Optional[Dict[str, Any]] = None
    age_data: Optional[Dict[str, Any]] = None
    destination_data: Optional[Dict[str, Any]] = None
    mealtime_data: Optional[Dict[str, Any]] = None
    has_custom_probabilities: bool = False


# ── Prediction schemas ─────────────────────────────────────────────────────────

class PredictionRequest(BaseModel):
    flight_number: str
    flight_date: str
    master_metrics: Optional[MasterMetrics] = None


class PassengerGroup(BaseModel):
    nationality: str
    age_group: str
    destination: str
    meal_time: str
    weekday: str = ""
    count: int
    probabilities: Dict[str, float]
    metric_probabilities: Dict[str, Dict[str, float]] = {}
    reasoning: Dict[str, str] = {}


class TopNationality(BaseModel):
    nationality_code: str
    count: int
    percentage: float
    reasoning: str = ""
    sources: str = ""


class PredictionSummaryRequest(BaseModel):
    flight_number: str
    flight_date: str
    passenger_groups: List[PassengerGroup]
    weights: Dict[str, float]
    prediction_results: Dict[str, float]
    original_counts: Dict[str, int]
    top_nationalities: List[TopNationality] = []


# ── Save-metrics validation schema ────────────────────────────────────────────

class SaveCustomMetricsRequest(BaseModel):
    metrics: Dict[str, Any] = {}
    weights: Dict[str, float] = {}
    flight_number: str = "default"
