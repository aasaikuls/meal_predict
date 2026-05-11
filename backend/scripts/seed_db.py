"""
Database seeder — populates MySQL tables from the project CSV files.

Usage (from the backend/ directory):
    python scripts/seed_db.py

Requires: pymysql, sqlalchemy (both already in requirements.txt)
Set env vars or create a .env file before running.
"""

import csv
import os
import sys
from pathlib import Path

# Allow importing from app/
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import Base
import app.models.models  # registers all ORM models  # noqa: F401
from app.models.models import (
    Customer,
    Meal,
    NationalityPref,
    AgePref,
    DestinationPref,
    MealtimePref,
    PredictionHistory,
)

PROTEIN_COLS = ["Pork", "Chicken", "Beef", "Seafood", "Lamb", "Vegetarian"]

# In Docker the CSVs are mounted at /data/; locally they live at the project root
_DOCKER_DATA = Path("/data")
_LOCAL_DATA = Path(__file__).parent.parent.parent
DATA_DIR = _DOCKER_DATA if _DOCKER_DATA.exists() else _LOCAL_DATA


def _float(val: str) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def seed_nationality(session: Session):
    path = DATA_DIR / "Nationality.csv"
    if not path.exists():
        print(f"  SKIP — {path} not found")
        return
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    session.execute(text("DELETE FROM nationality_prefs"))
    for row in rows:
        session.add(NationalityPref(
            nationality_code=row["nationality_code"],
            day_of_week=row["day_of_week"],
            pork=_float(row.get("Pork", 0)),
            chicken=_float(row.get("Chicken", 0)),
            beef=_float(row.get("Beef", 0)),
            seafood=_float(row.get("Seafood", 0)),
            lamb=_float(row.get("Lamb", 0)),
            vegetarian=_float(row.get("Vegetarian", 0)),
            reasoning=row.get("reasoning"),
            sources=row.get("sources"),
        ))
    session.flush()
    print(f"  nationality_prefs: {len(rows)} rows")


def seed_age(session: Session):
    path = DATA_DIR / "Age.csv"
    if not path.exists():
        print(f"  SKIP — {path} not found")
        return
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    session.execute(text("DELETE FROM age_prefs"))
    for row in rows:
        session.add(AgePref(
            age_group=row["age_group"],
            pork=_float(row.get("Pork", 0)),
            chicken=_float(row.get("Chicken", 0)),
            beef=_float(row.get("Beef", 0)),
            seafood=_float(row.get("Seafood", 0)),
            lamb=_float(row.get("Lamb", 0)),
            vegetarian=_float(row.get("Vegetarian", 0)),
            reasoning=row.get("Reasoning"),
            sources=row.get("Sources"),
        ))
    session.flush()
    print(f"  age_prefs: {len(rows)} rows")


def seed_destination(session: Session):
    path = DATA_DIR / "Destination.csv"
    if not path.exists():
        print(f"  SKIP — {path} not found")
        return
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    session.execute(text("DELETE FROM destination_prefs"))
    seen = set()
    inserted = 0
    for row in rows:
        code = row["airport_code"]
        if code in seen:
            continue
        seen.add(code)
        session.add(DestinationPref(
            airport_code=code,
            destination_region=row.get("destination_region", ""),
            pork=_float(row.get("Pork", 0)),
            chicken=_float(row.get("Chicken", 0)),
            beef=_float(row.get("Beef", 0)),
            seafood=_float(row.get("Seafood", 0)),
            lamb=_float(row.get("Lamb", 0)),
            vegetarian=_float(row.get("Vegetarian", 0)),
            reasoning=row.get("Reasoning"),
            sources=row.get("Sources"),
        ))
        inserted += 1
    session.flush()
    print(f"  destination_prefs: {inserted} rows")


def seed_mealtime(session: Session):
    path = DATA_DIR / "MealTime.csv"
    if not path.exists():
        print(f"  SKIP — {path} not found")
        return
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    session.execute(text("DELETE FROM mealtime_prefs"))
    seen = set()
    inserted = 0
    for row in rows:
        mt = row["meal_time"]
        if mt in seen:
            continue
        seen.add(mt)
        session.add(MealtimePref(
            meal_time=mt,
            pork=_float(row.get("Pork", 0)),
            chicken=_float(row.get("Chicken", 0)),
            beef=_float(row.get("Beef", 0)),
            seafood=_float(row.get("Seafood", 0)),
            lamb=_float(row.get("Lamb", 0)),
            vegetarian=_float(row.get("Vegetarian", 0)),
            reasoning=row.get("Reasoning"),
        ))
        inserted += 1
    session.flush()
    print(f"  mealtime_prefs: {inserted} rows")


def seed_customers(session: Session):
    path = DATA_DIR / "customers.csv"
    if not path.exists():
        print(f"  SKIP — {path} not found")
        return
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    session.execute(text("DELETE FROM customers"))
    for row in rows:
        session.add(Customer(
            operating_flight_number=row.get("operating_flight_number", ""),
            segment=row.get("segment", ""),
            cabin_class=row.get("cabin_class", ""),
            departure_airport=row.get("departure_airport", ""),
            arrival_airport=row.get("arrival_airport", ""),
            destination_region=row.get("destination_region"),
            nationality_code=row.get("nationality_code"),
            age_group=row.get("age_group"),
            meal_time=row.get("meal_time"),
            customer_number=row.get("customer_number"),
            segment_local_departure_datetime=row.get("segment_local_departure_datetime"),
        ))
    session.flush()
    print(f"  customers: {len(rows)} rows")


def seed_meals(session: Session):
    path = DATA_DIR / "meal_df_new.csv"
    if not path.exists():
        print(f"  SKIP — {path} not found")
        return
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    session.execute(text("DELETE FROM meals"))
    for row in rows:
        # date column may be "2024-06-01 00:00:00" — strip time
        date_raw = row.get("segment_local_departure_date", "")
        date_val = date_raw.split(" ")[0] if date_raw else ""
        session.add(Meal(
            segment=row.get("segment", ""),
            segment_local_departure_date=date_val,
            cabin_class=row.get("cabin_class", ""),
            meal_time=row.get("meal_time", ""),
            meal_name=row.get("meal_name"),
            meal_pref=row.get("meal_pref"),
        ))
    session.flush()
    print(f"  meals: {len(rows)} rows")


def seed_prediction_history(session: Session):
    """Load all PredictionResults/*.csv files into prediction_history table."""
    # Check Docker mount first, then local project path
    pred_dir = Path("/data/PredictionResults")
    if not pred_dir.exists():
        pred_dir = Path(__file__).parent.parent.parent / "PredictionResults"
    if not pred_dir.exists():
        print(f"  SKIP — PredictionResults not found")
        return
    session.execute(text("DELETE FROM prediction_history"))
    total = 0
    for csv_path in sorted(pred_dir.glob("*_PredictionResults.csv")):
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            date_raw = row.get("segment_local_departure_date", "")
            date_val = date_raw.split(" ")[0] if date_raw else ""
            session.add(PredictionHistory(
                segment=row.get("segment", ""),
                segment_local_departure_date=date_val,
                cabin_class=row.get("cabin_class", ""),
                meal_time=row.get("meal_time", ""),
                protein_type=row.get("protein_type", ""),
                original_meal_count=int(float(row.get("original_meal_count") or 0)),
            ))
            total += 1
        print(f"    {csv_path.name}: {len(rows)} rows")
    session.flush()
    print(f"  prediction_history: {total} rows total")


SEEDERS = {
    "nationality":          seed_nationality,
    "age":                  seed_age,
    "destination":          seed_destination,
    "mealtime":             seed_mealtime,
    "customers":            seed_customers,
    "meals":                seed_meals,
    "prediction_history":   seed_prediction_history,
}


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed MySQL tables from CSV files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Available tables: " + ", ".join(SEEDERS),
    )
    parser.add_argument(
        "tables",
        nargs="*",
        metavar="TABLE",
        help="Tables to seed (default: all). E.g. customers meals",
    )
    args = parser.parse_args()

    targets = args.tables if args.tables else list(SEEDERS)

    unknown = [t for t in targets if t not in SEEDERS]
    if unknown:
        parser.error(f"Unknown table(s): {', '.join(unknown)}. Available: {', '.join(SEEDERS)}")

    settings = get_settings()
    engine = create_engine(settings.sync_database_url, echo=False)

    print("Creating tables if not exist...")
    Base.metadata.create_all(engine)

    print(f"Seeding: {', '.join(targets)}")
    with Session(engine) as session:
        for table in targets:
            print(f"\n[{table}]")
            SEEDERS[table](session)
        session.commit()

    print("\nDone.")


if __name__ == "__main__":
    main()
