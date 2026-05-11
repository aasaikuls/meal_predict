import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core import redis_client
from app.schemas.schemas import InitSessionRequest, UpdateSessionProbabilityRequest
from app.services.meal_planning import (
    get_available_proteins_by_mealtime,
    load_prob_defaults,
    normalize_probs,
    _segment_from_flight_number,
)

router = APIRouter()
logger = logging.getLogger("meal.routes.sessions")


@router.post("/clear-session")
async def clear_session():
    """Clear all session memory when user returns to flight selection."""
    await redis_client.clear_all_sessions()
    return {"success": True, "message": "Session memory cleared"}


@router.post("/initialize-session")
async def initialize_session(
    request: InitSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Initialize session in Redis with normalized probabilities for a flight+date.
    Each row gets a marker to track if user has modified it.
    """
    flight_number = request.flight_number
    flight_date = request.flight_date
    segment = _segment_from_flight_number(flight_number)
    weekday = datetime.strptime(flight_date, "%Y-%m-%d").strftime("%A")

    try:
        proteins_by_mealtime = await get_available_proteins_by_mealtime(db, segment, flight_date)
        if not proteins_by_mealtime:
            raise HTTPException(status_code=404, detail=f"No meals found for {segment} on {flight_date}")

        defaults = await load_prob_defaults(db)

        session: dict = {
            "flight_number": flight_number,
            "flight_date": flight_date,
            "weekday": weekday,
            "segment": segment,
            "available_proteins_by_mealtime": proteins_by_mealtime,
            "nationality": {},
            "age": {},
            "destination": {},
            "mealtime": {},
        }

        nat_count = age_count = dest_count = meal_count = 0

        # Nationality
        for key, probs in defaults["nationality"].items():
            nat_code, day = key.rsplit("_", 1)
            for meal_time, proteins in proteins_by_mealtime.items():
                row_key = f"{nat_code}_{day}_{meal_time}"
                norm = normalize_probs(probs, proteins)
                session["nationality"][row_key] = {
                    "nationality_code": nat_code,
                    "day_of_week": day,
                    "meal_time": meal_time,
                    "current_probabilities": norm,
                    "default_probabilities": norm.copy(),
                    "marker": "no_change",
                    "available_proteins": proteins,
                }
                nat_count += 1

        # Age
        for age_group, probs in defaults["age"].items():
            for meal_time, proteins in proteins_by_mealtime.items():
                row_key = f"{age_group}_{meal_time}"
                norm = normalize_probs(probs, proteins)
                session["age"][row_key] = {
                    "age_group": age_group,
                    "meal_time": meal_time,
                    "current_probabilities": norm,
                    "default_probabilities": norm.copy(),
                    "marker": "no_change",
                    "available_proteins": proteins,
                }
                age_count += 1

        # Destination
        for dest_region, probs in defaults["destination"].items():
            for meal_time, proteins in proteins_by_mealtime.items():
                row_key = f"{dest_region}_{meal_time}"
                norm = normalize_probs(probs, proteins)
                session["destination"][row_key] = {
                    "destination_region": dest_region,
                    "meal_time": meal_time,
                    "current_probabilities": norm,
                    "default_probabilities": norm.copy(),
                    "marker": "no_change",
                    "available_proteins": proteins,
                }
                dest_count += 1

        # Mealtime
        for meal_time, probs in defaults["mealtime"].items():
            if meal_time in proteins_by_mealtime:
                proteins = proteins_by_mealtime[meal_time]
                norm = normalize_probs(probs, proteins)
                session["mealtime"][meal_time] = {
                    "meal_time": meal_time,
                    "current_probabilities": norm,
                    "default_probabilities": norm.copy(),
                    "marker": "no_change",
                    "available_proteins": proteins,
                }
                meal_count += 1

        await redis_client.set_session(flight_number, flight_date, session)
        total = nat_count + age_count + dest_count + meal_count
        logger.info(f"Session initialized: {flight_number}|{flight_date} — {total} rows")

        return {
            "success": True,
            "session_key": f"{flight_number}|{flight_date}",
            "summary": {
                "nationality_rows": nat_count,
                "age_rows": age_count,
                "destination_rows": dest_count,
                "mealtime_rows": meal_count,
                "total_rows": total,
            },
            "available_proteins_by_mealtime": proteins_by_mealtime,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error initializing session")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/update-session-probability")
async def update_session_probability(request: UpdateSessionProbabilityRequest):
    """Update a single probability row in the Redis session."""
    session_key_parts = request.session_key.split("|")
    if len(session_key_parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid session_key format")

    flight_number, flight_date = session_key_parts
    session = await redis_client.get_session(flight_number, flight_date)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please reinitialize.")

    metric_type = request.metric_type
    row_key = request.row_key
    new_probs = request.probabilities

    if metric_type not in session:
        raise HTTPException(status_code=400, detail=f"Invalid metric_type: {metric_type}")
    if row_key not in session[metric_type]:
        raise HTTPException(status_code=404, detail=f"Row key not found: {row_key}")

    row = session[metric_type][row_key]
    row["current_probabilities"] = new_probs

    # Check if changed from default
    is_different = any(
        abs(new_probs.get(p, 0) - row["default_probabilities"].get(p, 0)) > 0.001
        for p in new_probs
    )
    row["marker"] = "user_modified" if is_different else "no_change"

    await redis_client.update_session(flight_number, flight_date, session)
    return {"success": True, "marker": row["marker"], "message": f"Row updated: {row_key}"}


@router.get("/get-modified-rows")
async def get_modified_rows(session_key: str):
    """Return all rows with marker='user_modified' from the Redis session."""
    parts = session_key.split("|")
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid session_key format")

    flight_number, flight_date = parts
    session = await redis_client.get_session(flight_number, flight_date)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    modified = []
    for metric_type in ["nationality", "age", "destination", "mealtime"]:
        for row_key, row_data in session.get(metric_type, {}).items():
            if row_data["marker"] == "user_modified":
                modified.append({
                    "metric_type": metric_type,
                    "row_key": row_key,
                    "default_probabilities": row_data["default_probabilities"],
                    "current_probabilities": row_data["current_probabilities"],
                    "available_proteins": row_data["available_proteins"],
                    "row_details": {
                        k: v for k, v in row_data.items()
                        if k not in ("current_probabilities", "default_probabilities", "marker", "available_proteins")
                    },
                })

    return {"success": True, "modified_rows": modified, "count": len(modified)}
