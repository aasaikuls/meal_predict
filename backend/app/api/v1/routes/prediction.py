import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core import redis_client
from app.schemas.schemas import PassengerGroup, TopNationality
from app.services.meal_planning import run_prediction
from app.services.llm.factory import get_llm_provider

router = APIRouter()
logger = logging.getLogger("meal.routes.prediction")


@router.post("/predict")
async def predict_meals(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    Run meal prediction for a flight+date with given master metrics.
    Calls LLM provider (kariba or bedrock) to generate AI summaries.
    """
    flight_number = request.get("flight_number")
    flight_date = request.get("flight_date")
    master_metrics = request.get("master_metrics") or {}

    if not flight_number or not flight_date:
        raise HTTPException(status_code=400, detail="flight_number and flight_date are required")

    # Load session from Redis
    session_data = await redis_client.get_session(flight_number, flight_date)

    try:
        results = await run_prediction(db, flight_number, flight_date, master_metrics, session_data)
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(exc))

    if "error" in results:
        raise HTTPException(status_code=404, detail=results["error"])

    # Generate AI summaries per meal time
    weights = results.get("weights_used", {})
    passenger_details = results.get("passenger_details", [])
    top_nationalities_raw = results.get("top_nationalities", [])
    top_nat_models = [TopNationality(**n) for n in top_nationalities_raw]

    llm = get_llm_provider()
    ai_summaries: dict[str, str] = {}

    for meal_time, protein_counts in results["meal_times"].items():
        groups = [
            PassengerGroup(**p)
            for p in passenger_details
            if p["meal_time"] == meal_time
        ]
        original_counts = results.get("original_counts", {}).get(meal_time, {})
        try:
            summary = llm.call(
                passenger_groups=groups,
                weights=weights,
                prediction_results={k: float(v) for k, v in protein_counts.items()},
                original_counts=original_counts,
                top_nationalities=top_nat_models,
            )
            ai_summaries[meal_time] = summary
            logger.info(f"AI summary generated for {meal_time} ({len(summary)} chars)")
        except Exception as exc:
            logger.error(f"AI summary failed for {meal_time}: {exc}")
            ai_summaries[meal_time] = "AI summary not available due to an error."

    results["ai_summaries"] = ai_summaries
    return results


@router.get("/workflow-steps")
async def get_workflow_steps():
    """Return the 8-step workflow step messages for the prediction progress UI."""
    return {
        "steps": [
            "Loading passenger booking data...",
            "Analyzing nationality distribution...",
            "Processing age demographics...",
            "Evaluating destination preferences...",
            "Calculating meal time factors...",
            "Running LLM prediction model...",
            "Optimizing meal proportions...",
            "Generating recommendations...",
        ]
    }
