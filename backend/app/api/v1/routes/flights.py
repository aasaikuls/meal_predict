import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import Customer, Meal
from app.services.meal_planning import _segment_from_flight_number

router = APIRouter()
logger = logging.getLogger("meal.routes.flights")

# Simple in-process cache (warm on first request, cleared on restart)
_flights_cache: dict | None = None
_customer_summary_cache: dict[str, Any] = {}
_available_meals_cache: dict[str, Any] = {}


@router.get("/flights")
async def get_flights(db: AsyncSession = Depends(get_db)):
    """Get all available flights, destination categories, and available dates."""
    global _flights_cache
    if _flights_cache is not None:
        return _flights_cache

    result = await db.execute(
        select(
            Customer.operating_flight_number,
            Customer.departure_airport,
            Customer.arrival_airport,
            Customer.destination_region,
            Customer.segment_local_departure_datetime,
        ).distinct()
    )
    rows = result.all()

    flight_map: dict[str, dict] = {}
    categories: set[str] = set()

    for row in rows:
        fn = str(row.operating_flight_number).strip()
        if fn not in flight_map:
            flight_map[fn] = {
                "flightNumber": fn,
                "origin": row.departure_airport,
                "destination": row.arrival_airport,
                "route": f"{row.departure_airport}-{row.arrival_airport}",
                "category": row.destination_region or "Unknown",
                "dates": set(),
            }
        if row.destination_region:
            categories.add(row.destination_region)
        if row.segment_local_departure_datetime:
            dt_str = str(row.segment_local_departure_datetime).strip().split(" ")[0]
            for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(dt_str, fmt).strftime("%Y-%m-%d")
                    flight_map[fn]["dates"].add(parsed)
                    break
                except ValueError:
                    continue

    flights = [
        {
            "flightNumber": v["flightNumber"],
            "origin": v["origin"],
            "destination": v["destination"],
            "route": v["route"],
            "category": v["category"],
            "availableDates": sorted(v["dates"]),
        }
        for v in flight_map.values()
    ]

    _flights_cache = {"flights": flights, "categories": sorted(categories)}
    return _flights_cache


@router.get("/customer-summary")
async def get_customer_summary(
    flight_number: str,
    flight_date: str,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"{flight_number}|{flight_date}"
    if cache_key in _customer_summary_cache:
        return _customer_summary_cache[cache_key]

    try:
        target_date_str = datetime.strptime(flight_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        day_of_week = datetime.strptime(flight_date, "%Y-%m-%d").strftime("%A")
        actual_fn = flight_number.split("(")[0].strip()

        result = await db.execute(
            select(Customer).where(
                Customer.operating_flight_number == actual_fn
            )
        )
        all_rows = result.scalars().all()

        # Filter by date
        from app.services.meal_planning import _parse_date_flexible
        customers = [r for r in all_rows if _parse_date_flexible(r.segment_local_departure_datetime or "") == datetime.strptime(flight_date, "%Y-%m-%d").date()]

        if not customers:
            return {"error": f"No customers found for flight {flight_number} on {flight_date}"}

        # Deduplicate by customer_number
        seen: set[str] = set()
        unique = []
        for r in customers:
            cid = r.customer_number or f"{r.nationality_code}_{r.age_group}_{r.cabin_class}"
            if cid not in seen:
                seen.add(cid)
                unique.append(r)

        # Cabin distribution
        cabin_dist: dict[str, int] = {}
        for r in unique:
            cabin_dist[r.cabin_class] = cabin_dist.get(r.cabin_class, 0) + 1

        # Destination
        dest_airport = unique[0].arrival_airport if unique else "Unknown"

        # Meal times (from all rows, not deduplicated)
        meal_times = sorted({r.meal_time for r in customers if r.meal_time})

        # Analysis cabin
        analysis_cabin = "Y" if "Y" in cabin_dist else ("S" if "S" in cabin_dist else None)

        nat_breakdown: dict[str, int] = {}
        age_breakdown: dict[str, int] = {}
        if analysis_cabin:
            cabin_pax = [r for r in unique if r.cabin_class == analysis_cabin]
            for r in cabin_pax:
                if r.nationality_code:
                    nat_breakdown[r.nationality_code] = nat_breakdown.get(r.nationality_code, 0) + 1
                if r.age_group:
                    age_breakdown[r.age_group] = age_breakdown.get(r.age_group, 0) + 1

        pre_booked = sum(1 for r in unique if r.pre_booked_meal)
        needs_prediction = len(unique) - pre_booked

        result_data = {
            "flight_number": flight_number,
            "flight_date": flight_date,
            "day_of_week": day_of_week,
            "total_customers": len(unique),
            "pre_booked_passengers": pre_booked,
            "passengers_needing_prediction": needs_prediction,
            "cabin_distribution": cabin_dist,
            "destination_airport": dest_airport,
            "meal_times": meal_times,
            "analysis_cabin": analysis_cabin,
            "nationality_breakdown": nat_breakdown,
            "age_breakdown": age_breakdown,
        }
        _customer_summary_cache[cache_key] = result_data
        return result_data

    except Exception as exc:
        logger.exception("Error in customer summary")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/available-meals")
async def get_available_meals(
    flight_number: str,
    flight_date: str,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"{flight_number}|{flight_date}"
    if cache_key in _available_meals_cache:
        return _available_meals_cache[cache_key]

    try:
        segment = _segment_from_flight_number(flight_number)

        result = await db.execute(
            select(Meal).where(
                Meal.segment == segment,
                Meal.segment_local_departure_date == flight_date,
            )
        )
        meals = result.scalars().all()

        if not meals:
            return {"meals_by_time": {}, "message": "No meal data found"}

        # Group by meal_time, prefer Y cabin
        by_time: dict[str, dict[str, list]] = {}
        for m in meals:
            by_time.setdefault(m.meal_time, {}).setdefault(m.cabin_class, []).append(m)

        meals_by_time: dict[str, list] = {}
        for meal_time, cabin_map in by_time.items():
            display = cabin_map.get("Y") or cabin_map.get("S") or []
            meals_by_time[meal_time] = [
                {"cabin_class": m.cabin_class, "meal_name": m.meal_name, "meal_pref": m.meal_pref}
                for m in display
            ]

        data = {
            "flight_number": flight_number,
            "flight_date": flight_date,
            "segment": segment,
            "meals_by_time": meals_by_time,
        }
        _available_meals_cache[cache_key] = data
        return data

    except Exception as exc:
        logger.exception("Error in available meals")
        raise HTTPException(status_code=500, detail=str(exc))
