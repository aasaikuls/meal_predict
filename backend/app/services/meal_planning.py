"""
Core meal planning business logic.
Replaces the CSV-based calculations in the old main.py.
All data comes from MySQL via SQLAlchemy async sessions.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Customer,
    Meal,
    NationalityPref,
    AgePref,
    DestinationPref,
    MealtimePref,
    PredictionHistory,
)

logger = logging.getLogger("meal.service")

PROTEIN_COLUMNS = ["Pork", "Chicken", "Beef", "Seafood", "Lamb", "Vegetarian"]


# ── helpers ───────────────────────────────────────────────────────────────────

def normalize_probs(raw: dict[str, float], available: list[str]) -> dict[str, float]:
    """Normalize probabilities for the subset of available proteins."""
    subset = {p: float(raw.get(p, 0.0)) for p in available}
    total = sum(subset.values())
    if total > 0:
        return {p: v / total for p, v in subset.items()}
    equal = 1.0 / len(available)
    return {p: equal for p in available}


def _model_to_prob_dict(row) -> dict[str, float]:
    """Convert an ORM pref row to a protein → probability dict."""
    return {
        "Pork": row.pork,
        "Chicken": row.chicken,
        "Beef": row.beef,
        "Seafood": row.seafood,
        "Lamb": row.lamb,
        "Vegetarian": row.vegetarian,
    }


def largest_remainder(passenger_count: int, probs: dict[str, float]) -> dict[str, int]:
    """Allocate integer meal counts using the largest remainder method."""
    exact = {p: passenger_count * v for p, v in probs.items()}
    counts = {p: int(v) for p, v in exact.items()}
    remainders = {p: exact[p] - counts[p] for p in probs}
    remaining = passenger_count - sum(counts.values())
    for protein in sorted(probs.keys(), key=lambda p: remainders[p], reverse=True)[:remaining]:
        counts[protein] += 1
    return counts


def _parse_date(date_str: str):
    """Parse YYYY-MM-DD date string to date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def _segment_from_flight_number(flight_number: str) -> str:
    """Extract 'AKL SIN' from 'SQ 0286 (AKL → SIN)'."""
    if "(" in flight_number and "→" in flight_number:
        route = flight_number.split("(")[1].split(")")[0]
        origin, destination = route.split("→")
        return f"{origin.strip()} {destination.strip()}"
    raise ValueError(f"Cannot parse segment from flight_number: {flight_number!r}")


# ── DB query helpers ───────────────────────────────────────────────────────────

async def get_available_proteins_by_mealtime(
    db: AsyncSession, segment: str, date_str: str
) -> dict[str, list[str]]:
    """Return {meal_time: [sorted protein list]} for the given segment & date.
    Falls back to segment-only lookup when no date-exact rows exist."""
    for query in [
        select(Meal.meal_time, Meal.meal_pref, Meal.cabin_class).where(
            and_(Meal.segment == segment, Meal.segment_local_departure_date == date_str)
        ),
        select(Meal.meal_time, Meal.meal_pref, Meal.cabin_class).where(
            Meal.segment == segment
        ),
    ]:
        result = await db.execute(query)
        rows = result.all()
        if rows:
            break
    if not rows:
        return {}

    # Prefer Y cabin; fall back to S
    by_time: dict[str, dict[str, list]] = {}
    for meal_time, meal_pref, cabin_class in rows:
        by_time.setdefault(meal_time, {}).setdefault(cabin_class, []).append(meal_pref)

    result_map: dict[str, list[str]] = {}
    for meal_time, cabin_map in by_time.items():
        proteins = cabin_map.get("Y") or cabin_map.get("S") or []
        if proteins:
            result_map[meal_time] = sorted(set(proteins))
    return result_map


async def load_prob_defaults(db: AsyncSession) -> dict[str, Any]:
    """
    Load all four preference tables into dicts for fast in-memory lookup.
    Returns:
      {
        "nationality": { "IN_Saturday": {Pork: 0.03, ...}, ... },
        "age":         { "31-50": {Pork: 0.16, ...}, ... },
        "destination": { "South Asia": {Pork: 0.03, ...}, ... },
        "mealtime":    { "Dinner": {Pork: 0.20, ...}, ... },
        "nationality_reasoning": { "IN_Saturday": "...", ... },
        "age_reasoning":         { "31-50": "...", ... },
        "destination_reasoning": { "South Asia": "...", ... },
        "mealtime_reasoning":    { "Dinner": "...", ... },
        "airport_to_region":     { "MAA": "South Asia", ... },
      }
    """
    cache: dict[str, Any] = {
        "nationality": {},
        "age": {},
        "destination": {},
        "mealtime": {},
        "nationality_reasoning": {},
        "age_reasoning": {},
        "destination_reasoning": {},
        "mealtime_reasoning": {},
        "airport_to_region": {},
    }

    # Nationality
    for row in (await db.execute(select(NationalityPref))).scalars():
        key = f"{row.nationality_code}_{row.day_of_week}"
        cache["nationality"][key] = _model_to_prob_dict(row)
        if row.reasoning:
            cache["nationality_reasoning"][key] = row.reasoning

    # Age
    for row in (await db.execute(select(AgePref))).scalars():
        cache["age"][row.age_group] = _model_to_prob_dict(row)
        if row.reasoning:
            cache["age_reasoning"][row.age_group] = row.reasoning

    # Destination
    for row in (await db.execute(select(DestinationPref))).scalars():
        cache["destination"][row.destination_region] = _model_to_prob_dict(row)
        cache["airport_to_region"][row.airport_code] = row.destination_region
        if row.reasoning:
            cache["destination_reasoning"][row.destination_region] = row.reasoning

    # Mealtime
    for row in (await db.execute(select(MealtimePref))).scalars():
        cache["mealtime"][row.meal_time] = _model_to_prob_dict(row)
        if row.reasoning:
            cache["mealtime_reasoning"][row.meal_time] = row.reasoning

    return cache


async def get_prediction_history(
    db: AsyncSession, segment: str, date_str: str, cabin_class: str, meal_time: str
) -> dict[str, int]:
    """Load historical meal counts for the Planned vs Recommended chart.
    Tries progressively looser conditions until data is found."""
    conditions = [
        # Exact: segment + date + cabin + mealtime
        and_(PredictionHistory.segment == segment,
             PredictionHistory.segment_local_departure_date == date_str,
             PredictionHistory.cabin_class == cabin_class,
             PredictionHistory.meal_time == meal_time),
        # Any cabin for this segment + date + mealtime
        and_(PredictionHistory.segment == segment,
             PredictionHistory.segment_local_departure_date == date_str,
             PredictionHistory.meal_time == meal_time),
        # Any date for this segment + cabin + mealtime
        and_(PredictionHistory.segment == segment,
             PredictionHistory.cabin_class == cabin_class,
             PredictionHistory.meal_time == meal_time),
        # Any date + any cabin for this segment + mealtime
        and_(PredictionHistory.segment == segment,
             PredictionHistory.meal_time == meal_time),
    ]
    for cond in conditions:
        result = await db.execute(
            select(PredictionHistory.protein_type, PredictionHistory.original_meal_count)
            .where(cond)
            .limit(20)
        )
        rows = result.all()
        if rows:
            return {row.protein_type: row.original_meal_count for row in rows}
    return {}


# ── Main prediction engine ────────────────────────────────────────────────────

async def run_prediction(
    db: AsyncSession,
    flight_number: str,
    flight_date: str,
    master_metrics: dict,
    session_data: dict | None,
) -> dict:
    """
    Core prediction algorithm.
    Returns the full results dict expected by the frontend.
    """
    segment = _segment_from_flight_number(flight_number)
    target_date = _parse_date(flight_date)
    weekday = datetime.strptime(flight_date, "%Y-%m-%d").strftime("%A")

    # Weights
    nat_w = master_metrics.get("nationality_importance", 40.0) / 100.0
    age_w = master_metrics.get("age_importance", 20.0) / 100.0
    dest_w = master_metrics.get("destination_importance", 25.0) / 100.0
    meal_w = master_metrics.get("mealtime_importance", 15.0) / 100.0

    # Load probability defaults from DB
    defaults = await load_prob_defaults(db)
    airport_to_region = defaults["airport_to_region"]

    # Available proteins per meal time
    proteins_by_mealtime = await get_available_proteins_by_mealtime(db, segment, flight_date)
    if not proteins_by_mealtime:
        return {"error": f"No meal data found for {segment} on {flight_date}"}

    # Determine destination region
    dest_airport = segment.split()[-1]
    destination_region = airport_to_region.get(dest_airport, dest_airport)

    # Derive cabin class from the dominant class on this flight
    cabin_result = await db.execute(
        select(Customer.cabin_class)
        .where(Customer.operating_flight_number == flight_number.split("(")[0].strip())
    )
    cabin_counts: dict[str, int] = {}
    for (cc,) in cabin_result.all():
        cabin_counts[cc] = cabin_counts.get(cc, 0) + 1
    # Prefer J > Y > S based on data; fall back to Y
    cabin_class = max(cabin_counts, key=cabin_counts.get) if cabin_counts else "Y"

    # Fetch customers
    result = await db.execute(
        select(
            Customer.nationality_code,
            Customer.age_group,
            Customer.meal_time,
            Customer.customer_number,
            Customer.segment_local_departure_datetime,
            Customer.pre_booked_meal,
        )
        .where(
            and_(
                Customer.operating_flight_number == flight_number.split("(")[0].strip(),
                Customer.cabin_class == cabin_class,
                Customer.age_group != "Under 2",
            )
        )
    )
    all_customers = result.all()

    # Filter by date
    customers = [
        row for row in all_customers
        if row.segment_local_departure_datetime
        and _parse_date_flexible(row.segment_local_departure_datetime) == target_date
    ]

    if not customers:
        return {"error": "No passenger data found"}

    # Split pre-booked vs needs-prediction
    pre_booked_customers = [r for r in customers if r.pre_booked_meal]
    prediction_customers = [r for r in customers if not r.pre_booked_meal]

    # Tally pre-booked meals by SPML code → protein mapping
    SPML_TO_PROTEIN = {
        "MOML": "Chicken", "HNML": "Vegetarian", "VGML": "Vegetarian",
        "CHML": "Chicken", "SFML": "Seafood", "AVML": "Vegetarian",
        "KSML": "Chicken", "NLML": "Vegetarian",
    }
    pre_booked_counts: dict[str, dict[str, int]] = {}  # meal_time → protein → count
    for row in pre_booked_customers:
        mt = row.meal_time or "Dinner"
        protein = SPML_TO_PROTEIN.get(row.pre_booked_meal, "Chicken")
        pre_booked_counts.setdefault(mt, {})
        pre_booked_counts[mt][protein] = pre_booked_counts[mt].get(protein, 0) + 1

    # Build feature groups: (nationality, age_group, meal_time, weekday) → count
    # Only for passengers who need prediction (no pre-booked meal)
    feature_groups: dict[tuple, int] = {}
    seen_customers: set[str] = set()
    for row in prediction_customers:
        cid = row.customer_number or f"{row.nationality_code}_{row.age_group}_{row.meal_time}"
        seen_customers.add(cid)
        key = (row.nationality_code, row.age_group, row.meal_time, weekday)
        feature_groups[key] = feature_groups.get(key, 0) + 1

    # ── Per-group probability calculation ────────────────────────────────────
    results_by_mealtime: dict[str, dict[str, int]] = {}
    passenger_details: list[dict] = []

    for (nationality, age_group, meal_time, wday), pcount in feature_groups.items():
        if meal_time not in proteins_by_mealtime:
            continue
        available_proteins = proteins_by_mealtime[meal_time]

        # Resolve probabilities: session memory overrides defaults
        def _get_probs(metric_type: str, key: str, available: list[str]) -> dict[str, float]:
            if session_data and key in session_data.get(metric_type, {}):
                return session_data[metric_type][key]["current_probabilities"]
            raw = defaults[metric_type].get(key, {})
            return normalize_probs(raw, available)

        nat_probs = _get_probs("nationality", f"{nationality}_{wday}_{meal_time}", available_proteins)
        if not nat_probs:
            nat_probs = normalize_probs(defaults["nationality"].get(f"{nationality}_{wday}", {}), available_proteins)

        age_probs = _get_probs("age", f"{age_group}_{meal_time}", available_proteins)
        if not age_probs:
            age_probs = normalize_probs(defaults["age"].get(age_group, {}), available_proteins)

        dest_probs = _get_probs("destination", f"{destination_region}_{meal_time}", available_proteins)
        if not dest_probs:
            dest_probs = normalize_probs(defaults["destination"].get(destination_region, {}), available_proteins)

        mt_probs = _get_probs("mealtime", meal_time, available_proteins)
        if not mt_probs:
            mt_probs = normalize_probs(defaults["mealtime"].get(meal_time, {}), available_proteins)

        # Weighted combination
        weighted = {
            p: (
                nat_probs.get(p, 0) * nat_w
                + age_probs.get(p, 0) * age_w
                + dest_probs.get(p, 0) * dest_w
                + mt_probs.get(p, 0) * meal_w
            )
            for p in available_proteins
        }
        total = sum(weighted.values())
        final_probs = {p: v / total for p, v in weighted.items()} if total > 0 else {p: 1 / len(available_proteins) for p in available_proteins}

        counts = largest_remainder(pcount, final_probs)

        # Accumulate
        if meal_time not in results_by_mealtime:
            results_by_mealtime[meal_time] = {}
        for protein, cnt in counts.items():
            results_by_mealtime[meal_time][protein] = results_by_mealtime[meal_time].get(protein, 0) + cnt

        passenger_details.append({
            "nationality": nationality,
            "age_group": age_group,
            "destination": f"{dest_airport} ({destination_region})",
            "meal_time": meal_time,
            "weekday": wday,
            "count": pcount,
            "probabilities": final_probs,
            "metric_probabilities": {
                "nationality": {p: nat_probs.get(p, 0) for p in available_proteins},
                "age": {p: age_probs.get(p, 0) for p in available_proteins},
                "destination": {p: dest_probs.get(p, 0) for p in available_proteins},
                "meal_time": {p: mt_probs.get(p, 0) for p in available_proteins},
            },
            "reasoning": {
                "nationality": defaults["nationality_reasoning"].get(f"{nationality}_{wday}", ""),
                "age": defaults["age_reasoning"].get(age_group, ""),
                "destination": defaults["destination_reasoning"].get(destination_region, ""),
                "meal_time": defaults["mealtime_reasoning"].get(meal_time, ""),
            },
        })

    # Historical counts
    original_counts_by_mealtime: dict[str, dict[str, int]] = {}
    for mt in results_by_mealtime:
        hist = await get_prediction_history(db, segment, flight_date, cabin_class, mt)
        if hist:
            original_counts_by_mealtime[mt] = hist

    # Top nationalities
    nat_counter: dict[str, int] = {}
    for row in customers:
        nat_counter[row.nationality_code] = nat_counter.get(row.nationality_code, 0) + 1
    total_pax = len(customers)
    top_nationalities = [
        {
            "nationality_code": code,
            "count": cnt,
            "percentage": cnt / total_pax * 100,
            "reasoning": defaults["nationality_reasoning"].get(f"{code}_{weekday}", ""),
            "sources": "",
        }
        for code, cnt in sorted(nat_counter.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    # Sort proteins alphabetically within each meal time
    sorted_results = {mt: dict(sorted(v.items())) for mt, v in results_by_mealtime.items()}
    sorted_original = {mt: dict(sorted(v.items())) for mt, v in original_counts_by_mealtime.items()}

    return {
        "flight_number": flight_number,
        "flight_date": flight_date,
        "cabin_class": cabin_class,
        "total_passengers": len(customers),
        "pre_booked_passengers": len(pre_booked_customers),
        "cabin_passengers_for_prediction": len(prediction_customers),
        "pre_booked_counts": pre_booked_counts,
        "meal_times": sorted_results,
        "original_counts": sorted_original,
        "passenger_details": passenger_details,
        "weights_used": {
            "nationality_importance": master_metrics.get("nationality_importance", 40.0),
            "age_importance": master_metrics.get("age_importance", 20.0),
            "destination_importance": master_metrics.get("destination_importance", 25.0),
            "mealtime_importance": master_metrics.get("mealtime_importance", 15.0),
        },
        "top_nationalities": top_nationalities,
        "ai_summaries": {},  # populated by prediction route after calling LLM
    }


def _parse_date_flexible(dt_str: str):
    """Parse dates in 'M/D/YYYY', 'DD/MM/YYYY', or 'YYYY-MM-DD' formats."""
    dt_str = str(dt_str).strip().split(" ")[0]
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(dt_str, fmt).date()
        except ValueError:
            continue
    return None
