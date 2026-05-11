"""
MAG (Malaysia Airlines) database seeder.

Ingests data from:
  - mag_bookings.csv  → customers table
  - mag_meal.csv      → meals + prediction_history tables

Preference tables (nationality_prefs, age_prefs, destination_prefs,
mealtime_prefs) are derived from the overall protein distribution in
mag_meal.csv, since no passenger-level meal-choice data is available.

Usage:
    # From backend/ directory, seed all MAG tables:
    python scripts/seed_mag.py

    # Seed specific tables only:
    python scripts/seed_mag.py customers meals prediction_history

Available table names:
    customers  meals  prediction_history
    nationality  age  destination  mealtime

Data files are resolved in this order:
    1. /data/mag_bookings.csv  /data/mag_meal.csv   (Docker mount)
    2. <project_root>/.docs/mag_data_files/          (local dev)
"""

import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import Base
import app.models.models  # noqa: F401  registers all ORM models
from app.models.models import (
    AgePref,
    Customer,
    DestinationPref,
    Meal,
    MealtimePref,
    NationalityPref,
    PredictionHistory,
)

# ---------------------------------------------------------------------------
# Data-file resolution
# ---------------------------------------------------------------------------

_DOCKER_DATA = Path("/data")
_DOCKER_TMP  = Path("/tmp")
_LOCAL_DATA = Path(__file__).parent.parent.parent / ".docs" / "mag_data_files"

def _data_dir() -> Path:
    # Docker: files copied to /data (via volume mount)
    if (_DOCKER_DATA / "mag_bookings.csv").exists():
        return _DOCKER_DATA
    # Docker: files copied manually to /tmp
    if (_DOCKER_TMP / "mag_bookings.csv").exists():
        return _DOCKER_TMP
    # Local dev
    if _LOCAL_DATA.exists() and (_LOCAL_DATA / "mag_bookings.csv").exists():
        return _LOCAL_DATA
    raise FileNotFoundError(
        "Cannot find MAG data files. Expected one of:\n"
        "  /data/mag_bookings.csv      (Docker volume)\n"
        "  /tmp/mag_bookings.csv       (Docker manual copy)\n"
        f"  {_LOCAL_DATA}/mag_bookings.csv  (local)"
    )


def _open(data_dir: Path, filename: str):
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return open(path, newline="", encoding="utf-8-sig")


# ---------------------------------------------------------------------------
# Protein type normalisation
# ---------------------------------------------------------------------------

# MAG meal prefs → app standard protein types
# Malaysia Airlines is halal so no Pork/Beef standalone options.
PROTEIN_MAP = {
    "CHICKEN":    "Chicken",
    "Chicken":    "Chicken",
    "FISH":       "Seafood",
    "SEAFOOD":    "Seafood",
    "Seafood":    "Seafood",
    "LAMB":       "Lamb",
    "Lamb":       "Lamb",
    "GRAIN":      "Vegetarian",   # grain/rice-based dishes
    "PASTA":      "Vegetarian",   # pasta dishes
    "VEGETARIAN": "Vegetarian",
    "Vegetarian": "Vegetarian",
}

CABIN_MAP = {
    "YCL": "Y",
    "JCL": "J",
    "Y":   "Y",
    "J":   "J",
}

AGE_FIX = {
    "18-Feb": "2-18",   # Excel corrupted "2-18" → "18-Feb"
    "Feb-18": "2-18",
}

DAYS_OF_WEEK = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


def _fix_age(val: str) -> str:
    return AGE_FIX.get(val, val)


def _parse_date(dt_str: str) -> str:
    """Return 'YYYY-MM-DD' from '6/1/2026 0:00' or '6/1/2026 21:30'."""
    dt_str = dt_str.strip().split(" ")[0]
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(dt_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return dt_str


def _weekday(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    except ValueError:
        return "Monday"


# ---------------------------------------------------------------------------
# Derive overall protein distribution from mag_meal.csv
# (used as a flat prior for all preference tables)
# ---------------------------------------------------------------------------

def _protein_distribution(data_dir: Path) -> dict[str, float]:
    """Return normalised {ProteinType: probability} from mag_meal.csv."""
    counts: dict[str, int] = defaultdict(int)
    with _open(data_dir, "mag_meal.csv") as f:
        for row in csv.DictReader(f):
            raw = row.get("meal_pref", "").strip()
            protein = PROTEIN_MAP.get(raw)
            if protein:
                counts[protein] += 1
    total = sum(counts.values())
    if not total:
        return {"Chicken": 0.4, "Vegetarian": 0.35, "Seafood": 0.15, "Lamb": 0.1}
    return {p: c / total for p, c in sorted(counts.items())}


# ---------------------------------------------------------------------------
# Seeders
# ---------------------------------------------------------------------------

def seed_customers(session: Session, data_dir: Path):
    with _open(data_dir, "mag_bookings.csv") as f:
        rows = list(csv.DictReader(f))
    session.execute(text("DELETE FROM customers"))
    for row in rows:
        session.add(Customer(
            operating_flight_number=row["operating_flight_number"].strip(),
            segment=row["segment"].strip(),
            cabin_class=CABIN_MAP.get(row["cabin_class"].strip(), row["cabin_class"].strip()),
            departure_airport=row["departure_airport"].strip(),
            arrival_airport=row["arrival_airport"].strip(),
            destination_region=row.get("destination_region", "").strip() or None,
            nationality_code=row.get("nationality_code", "").strip() or None,
            age_group=_fix_age(row.get("age_group", "").strip()) or None,
            meal_time=row.get("meal_time", "").strip() or None,
            customer_number=row.get("customer_number", "").strip() or None,
            segment_local_departure_datetime=_parse_date(row.get("segment_local_departure_datetime", "").strip()) or None,
            pre_booked_meal=row.get("available_meals", "").strip() or None,
        ))
    session.flush()
    print(f"  customers: {len(rows)} rows")


def seed_meals(session: Session, data_dir: Path):
    with _open(data_dir, "mag_meal.csv") as f:
        rows = list(csv.DictReader(f))
    session.execute(text("DELETE FROM meals"))
    inserted = 0
    for row in rows:
        raw_pref = row.get("meal_pref", "").strip()
        protein = PROTEIN_MAP.get(raw_pref, raw_pref)  # keep original if unknown
        cabin_raw = row.get("cabin_class", "").strip()
        cabin = CABIN_MAP.get(cabin_raw, cabin_raw)
        date_raw = row.get("segment_local_departure_date", "").strip()
        date_val = _parse_date(date_raw) if date_raw else ""
        session.add(Meal(
            segment=row.get("segment", "").strip(),
            segment_local_departure_date=date_val,
            cabin_class=cabin,
            meal_time=row.get("meal_time", "").strip(),
            meal_name=row.get("meal_name", "").strip() or None,
            meal_pref=protein,
        ))
        inserted += 1
    session.flush()
    print(f"  meals: {inserted} rows")


def seed_prediction_history(session: Session, data_dir: Path):
    """
    Estimate planned meal counts per protein by:
      1. Counting passengers per segment/date/cabin from mag_bookings.csv
      2. Getting protein types available per segment/date/cabin/mealtime from mag_meal.csv
      3. Distributing passenger count across available proteins (equal share + largest-remainder rounding)
    """
    # Step 1: passenger counts
    pax: dict[tuple, int] = defaultdict(int)   # (segment, date, cabin, meal_time) → count
    with _open(data_dir, "mag_bookings.csv") as f:
        for row in csv.DictReader(f):
            seg = row["segment"].strip()
            date = _parse_date(row["segment_local_departure_datetime"].strip())
            cabin = CABIN_MAP.get(row["cabin_class"].strip(), row["cabin_class"].strip())
            mt = row.get("meal_time", "Dinner").strip()
            pax[(seg, date, cabin, mt)] += 1

    # Step 2: available proteins per combo from mag_meal
    available: dict[tuple, set] = defaultdict(set)   # (segment, date, cabin, meal_time) → {proteins}
    with _open(data_dir, "mag_meal.csv") as f:
        for row in csv.DictReader(f):
            seg = row["segment"].strip()
            date = _parse_date(row["segment_local_departure_date"].strip())
            cabin_raw = row.get("cabin_class", "").strip()
            cabin = CABIN_MAP.get(cabin_raw, cabin_raw)
            mt = row.get("meal_time", "Dinner").strip()
            raw_pref = row.get("meal_pref", "").strip()
            protein = PROTEIN_MAP.get(raw_pref)
            if protein:
                available[(seg, date, cabin, mt)].add(protein)

    # Step 3: distribute & insert
    session.execute(text("DELETE FROM prediction_history"))
    total_rows = 0
    for key, total_pax in pax.items():
        seg, date, cabin, mt = key
        proteins = sorted(available.get(key, set()))
        if not proteins:
            continue
        n = len(proteins)
        base = total_pax // n
        remainder = total_pax % n
        # Largest-remainder: first `remainder` proteins get base+1
        for i, protein in enumerate(proteins):
            count = base + (1 if i < remainder else 0)
            session.add(PredictionHistory(
                segment=seg,
                segment_local_departure_date=date,
                cabin_class=cabin,
                meal_time=mt,
                protein_type=protein,
                original_meal_count=count,
            ))
            total_rows += 1
    session.flush()
    print(f"  prediction_history: {total_rows} rows (estimated from passenger counts)")


def seed_nationality(session: Session, data_dir: Path):
    """
    Build nationality_prefs from all nationalities in mag_bookings.csv.
    Probabilities = overall protein distribution from mag_meal.csv.
    One row per nationality × day_of_week (all days same probability).
    """
    dist = _protein_distribution(data_dir)
    chicken   = dist.get("Chicken",    0.0)
    seafood   = dist.get("Seafood",    0.0)
    lamb      = dist.get("Lamb",       0.0)
    vegetarian= dist.get("Vegetarian", 0.0)
    # MAG: no Pork/Beef
    pork = 0.0
    beef = 0.0

    nationalities: set[str] = set()
    with _open(data_dir, "mag_bookings.csv") as f:
        for row in csv.DictReader(f):
            code = row.get("nationality_code", "").strip()
            if code:
                nationalities.add(code)

    session.execute(text("DELETE FROM nationality_prefs"))
    inserted = 0
    for code in sorted(nationalities):
        for day in DAYS_OF_WEEK:
            session.add(NationalityPref(
                nationality_code=code,
                day_of_week=day,
                pork=pork,
                chicken=chicken,
                beef=beef,
                seafood=seafood,
                lamb=lamb,
                vegetarian=vegetarian,
                reasoning=f"Derived from MAG meal distribution for {code} passengers.",
                sources="mag_meal.csv aggregate",
            ))
            inserted += 1
    session.flush()
    print(f"  nationality_prefs: {inserted} rows ({len(nationalities)} nationalities × 7 days)")


def seed_age(session: Session, data_dir: Path):
    """
    Build age_prefs from all age groups in mag_bookings.csv.
    Probabilities = overall protein distribution from mag_meal.csv.
    """
    dist = _protein_distribution(data_dir)
    chicken    = dist.get("Chicken",    0.0)
    seafood    = dist.get("Seafood",    0.0)
    lamb       = dist.get("Lamb",       0.0)
    vegetarian = dist.get("Vegetarian", 0.0)
    pork = 0.0
    beef = 0.0

    age_groups: set[str] = set()
    with _open(data_dir, "mag_bookings.csv") as f:
        for row in csv.DictReader(f):
            ag = _fix_age(row.get("age_group", "").strip())
            if ag:
                age_groups.add(ag)

    session.execute(text("DELETE FROM age_prefs"))
    for ag in sorted(age_groups):
        session.add(AgePref(
            age_group=ag,
            pork=pork,
            chicken=chicken,
            beef=beef,
            seafood=seafood,
            lamb=lamb,
            vegetarian=vegetarian,
            reasoning=f"Derived from MAG meal distribution for age group {ag}.",
            sources="mag_meal.csv aggregate",
        ))
    session.flush()
    print(f"  age_prefs: {len(age_groups)} rows")


def seed_destination(session: Session, data_dir: Path):
    """
    Build destination_prefs from departure/arrival airports in mag_bookings.csv.
    """
    dist = _protein_distribution(data_dir)
    chicken    = dist.get("Chicken",    0.0)
    seafood    = dist.get("Seafood",    0.0)
    lamb       = dist.get("Lamb",       0.0)
    vegetarian = dist.get("Vegetarian", 0.0)
    pork = 0.0
    beef = 0.0

    airports: dict[str, str] = {}   # airport_code → destination_region
    with _open(data_dir, "mag_bookings.csv") as f:
        for row in csv.DictReader(f):
            for col, region_col in [("departure_airport", "destination_region"),
                                     ("arrival_airport",   "destination_region")]:
                code = row.get(col, "").strip()
                region = row.get(region_col, "").strip()
                if code:
                    airports[code] = region

    session.execute(text("DELETE FROM destination_prefs"))
    for code, region in sorted(airports.items()):
        session.add(DestinationPref(
            airport_code=code,
            destination_region=region,
            pork=pork,
            chicken=chicken,
            beef=beef,
            seafood=seafood,
            lamb=lamb,
            vegetarian=vegetarian,
            reasoning=f"Derived from MAG meal distribution for {code} ({region}).",
            sources="mag_meal.csv aggregate",
        ))
    session.flush()
    print(f"  destination_prefs: {len(airports)} rows")


def seed_mealtime(session: Session, data_dir: Path):
    """
    Build mealtime_prefs from meal times in mag_bookings.csv.
    """
    dist = _protein_distribution(data_dir)
    chicken    = dist.get("Chicken",    0.0)
    seafood    = dist.get("Seafood",    0.0)
    lamb       = dist.get("Lamb",       0.0)
    vegetarian = dist.get("Vegetarian", 0.0)
    pork = 0.0
    beef = 0.0

    meal_times: set[str] = set()
    with _open(data_dir, "mag_bookings.csv") as f:
        for row in csv.DictReader(f):
            mt = row.get("meal_time", "").strip()
            if mt:
                meal_times.add(mt)

    session.execute(text("DELETE FROM mealtime_prefs"))
    for mt in sorted(meal_times):
        session.add(MealtimePref(
            meal_time=mt,
            pork=pork,
            chicken=chicken,
            beef=beef,
            seafood=seafood,
            lamb=lamb,
            vegetarian=vegetarian,
            reasoning=f"Derived from MAG meal distribution for {mt} service.",
        ))
    session.flush()
    print(f"  mealtime_prefs: {len(meal_times)} rows")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

SEEDERS = {
    "customers":           seed_customers,
    "meals":               seed_meals,
    "prediction_history":  seed_prediction_history,
}

# Preference tables (nationality/age/destination/mealtime) are intentionally
# excluded — they contain research-backed data seeded via seed_db.py and must
# not be overwritten with MAG-derived estimates.

ALL_ORDER = [
    "customers", "meals", "prediction_history",
]


def main():
    parser = argparse.ArgumentParser(
        description="Seed MySQL with MAG (Malaysia Airlines) data.",
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

    targets = args.tables if args.tables else ALL_ORDER
    unknown = [t for t in targets if t not in SEEDERS]
    if unknown:
        parser.error(f"Unknown table(s): {', '.join(unknown)}. Available: {', '.join(SEEDERS)}")

    data_dir = _data_dir()
    print(f"Using data from: {data_dir}\n")

    settings = get_settings()
    engine = create_engine(settings.sync_database_url, echo=False)
    Base.metadata.create_all(engine)

    print(f"Seeding: {', '.join(targets)}")
    with Session(engine) as session:
        for table in targets:
            print(f"\n[{table}]")
            SEEDERS[table](session, data_dir)
        session.commit()

    print("\nDone. MAG data seeded successfully.")


if __name__ == "__main__":
    main()
