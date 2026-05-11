import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.models import NationalityPref, AgePref, DestinationPref, MealtimePref
from app.services.meal_planning import (
    get_available_proteins_by_mealtime,
    normalize_probs,
    _segment_from_flight_number,
)

router = APIRouter()
logger = logging.getLogger("meal.routes.metrics")

PROTEIN_COLUMNS = ["Pork", "Chicken", "Beef", "Seafood", "Lamb", "Vegetarian"]

DEFAULT_WEIGHTS = {
    "nationality_importance": 40.0,
    "age_importance": 20.0,
    "destination_importance": 25.0,
    "mealtime_importance": 15.0,
}


def _model_to_dict(row, extra_keys: list[str]) -> dict:
    d: dict = {}
    for k in extra_keys:
        d[k] = getattr(row, k, None)
    for p in PROTEIN_COLUMNS:
        d[p] = getattr(row, p.lower(), 0.0)
    if hasattr(row, "reasoning"):
        d["reasoning"] = row.reasoning
    if hasattr(row, "sources"):
        d["sources"] = row.sources
    return d


def _normalize_row_dict(row_dict: dict, proteins: list[str]) -> dict:
    total = sum(float(row_dict.get(p, 0)) for p in proteins)
    out = dict(row_dict)
    for p in PROTEIN_COLUMNS:
        if p in proteins and total > 0:
            out[p] = float(row_dict.get(p, 0)) / total
        else:
            out[p] = 0.0
    return out


@router.get("/master-metrics")
async def get_master_metrics(
    flight_number: Optional[str] = None,
    flight_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Return metric importance weights + probability tables structured by meal time.
    When flight_number + flight_date are provided the tables are normalized
    to the proteins actually available for that flight.
    """
    response: dict = {
        **DEFAULT_WEIGHTS,
        "nationality_sample": {},
        "age_sample": {},
        "destination_sample": {},
        "mealtime_sample": {},
        "available_proteins": PROTEIN_COLUMNS,
        "available_proteins_by_mealtime": {},
    }

    proteins_by_mealtime: dict[str, list[str]] = {}
    if flight_number and flight_date:
        try:
            segment = _segment_from_flight_number(flight_number)
            proteins_by_mealtime = await get_available_proteins_by_mealtime(db, segment, flight_date)
            response["available_proteins_by_mealtime"] = proteins_by_mealtime
            all_proteins: set[str] = set()
            for pl in proteins_by_mealtime.values():
                all_proteins.update(pl)
            if all_proteins:
                response["available_proteins"] = sorted(all_proteins)
        except Exception as exc:
            logger.warning(f"Could not extract proteins by mealtime: {exc}")

    # Load all pref tables
    nat_rows = (await db.execute(select(NationalityPref))).scalars().all()
    age_rows = (await db.execute(select(AgePref))).scalars().all()
    dest_rows = (await db.execute(select(DestinationPref))).scalars().all()
    meal_rows = (await db.execute(select(MealtimePref))).scalars().all()

    if proteins_by_mealtime:
        for meal_time, proteins in proteins_by_mealtime.items():
            response["nationality_sample"][meal_time] = [
                _normalize_row_dict(
                    _model_to_dict(r, ["nationality_code", "day_of_week"]), proteins
                )
                for r in nat_rows
            ]
            response["age_sample"][meal_time] = [
                _normalize_row_dict(_model_to_dict(r, ["age_group"]), proteins)
                for r in age_rows
            ]
            response["destination_sample"][meal_time] = [
                _normalize_row_dict(_model_to_dict(r, ["airport_code", "destination_region"]), proteins)
                for r in dest_rows
            ]
            response["mealtime_sample"][meal_time] = [
                _normalize_row_dict(_model_to_dict(r, ["meal_time"]), proteins)
                for r in meal_rows
            ]
    else:
        # No meal-time filter — return all with all proteins
        response["nationality_sample"]["all"] = [_model_to_dict(r, ["nationality_code", "day_of_week"]) for r in nat_rows]
        response["age_sample"]["all"] = [_model_to_dict(r, ["age_group"]) for r in age_rows]
        response["destination_sample"]["all"] = [_model_to_dict(r, ["airport_code", "destination_region"]) for r in dest_rows]
        response["mealtime_sample"]["all"] = [_model_to_dict(r, ["meal_time"]) for r in meal_rows]

    return response


@router.post("/save-custom-metrics")
async def save_custom_metrics(request: dict):
    """
    Validate user-customized probability metrics.
    Does NOT persist to DB — validation only; session memory is the authoritative store.
    """
    metrics = request.get("metrics", {})
    weights = request.get("weights", {})
    tolerance = 0.001
    errors: list[str] = []

    # Validate weight sum
    if weights:
        total = sum([
            weights.get("nationality_importance", 0),
            weights.get("age_importance", 0),
            weights.get("destination_importance", 0),
            weights.get("mealtime_importance", 0),
        ])
        if abs(total - 100) > 0.1:
            errors.append(f"Total importance weights: {total:.1f}% (must equal 100%)")

    # Validate protein probabilities
    proteins_all = ["Pork", "Chicken", "Beef", "Seafood", "Lamb", "Vegetarian"]
    for category in ["nationality", "age", "destination", "mealtime"]:
        sample_key = f"{category}_sample"
        sample_data = metrics.get(sample_key, {})
        if not isinstance(sample_data, dict):
            continue
        for meal_time, meal_data in sample_data.items():
            if not isinstance(meal_data, list):
                continue
            proteins = metrics.get("available_proteins_by_mealtime", {}).get(meal_time, proteins_all)
            for row in meal_data:
                total = sum(row.get(p, 0) for p in proteins)
                if abs(total - 1.0) > tolerance:
                    identifier = row.get("nationality_code") or row.get("age_group") or row.get("airport_code") or row.get("meal_time", "")
                    errors.append(f"{category} - {identifier} ({meal_time}): Total is {total * 100:.1f}% (must be 100%)")

    if errors:
        raise HTTPException(
            status_code=400,
            detail={"message": "Validation failed: probabilities do not sum to 100%", "errors": errors[:20]},
        )

    return {"success": True, "message": "Validation passed"}
