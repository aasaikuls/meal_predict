"""
Trim mag_meal.csv to realistic per-date meal counts per route.

Realistic meal service sizes:
  KUL SIN  (1h,  Refreshments) : Y=2  J=3
  KUL MAA  (3.5h, Dinner)      : Y=4  J=5
  KUL NRT  (7h,  Lunch)        : Y=4  J=5
  KUL SYD  (8h,  each service) : Y=4  J=5
  KUL LHR  (13h, each service) : Y=5  J=6

Strategy per group: deduplicate by meal_name, then pick diverse set
by cycling through protein preferences.
"""
from pathlib import Path
from collections import defaultdict
import csv, re

DATA = Path("/data/mag_meal.csv")
OUT  = Path("/tmp/mag_meal_trimmed.csv")

# Max meals per (segment, cabin_class, meal_time) per date
LIMITS = {
    # (segment, cabin_class, meal_time) -> max
    ("KUL SIN", "YCL", "Refreshments"): 2,
    ("KUL SIN", "JCL", "Refreshments"): 3,
    ("KUL MAA", "YCL", "Dinner"):       4,
    ("KUL MAA", "JCL", "Dinner"):       5,
    ("KUL NRT", "YCL", "Lunch"):        4,
    ("KUL NRT", "JCL", "Lunch"):        5,
    ("KUL SYD", "YCL", "Lunch"):        4,
    ("KUL SYD", "JCL", "Lunch"):        5,
    ("KUL SYD", "YCL", "Dinner"):       4,
    ("KUL SYD", "JCL", "Dinner"):       5,
    ("KUL LHR", "YCL", "Dinner"):       5,
    ("KUL LHR", "JCL", "Dinner"):       6,
    ("KUL LHR", "YCL", "Supper"):       3,
    ("KUL LHR", "JCL", "Supper"):       4,
    ("KUL LHR", "YCL", "Breakfast"):    3,
    ("KUL LHR", "JCL", "Breakfast"):    4,
}
DEFAULT_LIMIT = 5

PREF_NORM = {
    "CHICKEN": "Chicken", "Chicken": "Chicken",
    "FISH": "Seafood", "SEAFOOD": "Seafood", "Seafood": "Seafood",
    "GRAIN": "Vegetarian", "PASTA": "Vegetarian",
    "VEGETARIAN": "Vegetarian", "Vegetarian": "Vegetarian",
    "LAMB": "Lamb", "Lamb": "Lamb",
    "BEEF": "Beef", "Beef": "Beef",
    "PORK": "Pork", "Pork": "Pork",
}
PREF_ORDER = ["Chicken", "Seafood", "Vegetarian", "Lamb", "Beef", "Pork"]

def diverse_select(rows, limit):
    """Deduplicate by meal_name, then pick a diverse set by normalised meal_pref."""
    seen_names = set()
    unique = []
    for r in rows:
        if r["meal_name"] not in seen_names:
            seen_names.add(r["meal_name"])
            unique.append(r)

    if len(unique) <= limit:
        return unique

    # Group by normalised pref
    by_pref = defaultdict(list)
    for r in unique:
        norm = PREF_NORM.get(r["meal_pref"].strip(), "Other")
        by_pref[norm].append(r)

    # Build ordered list of pref queues (priority order, then anything else)
    ordered_prefs = [p for p in PREF_ORDER if by_pref.get(p)]
    ordered_prefs += [p for p in by_pref if p not in PREF_ORDER and by_pref[p]]
    queues = {p: list(by_pref[p]) for p in ordered_prefs}

    result = []
    while len(result) < limit:
        found_any = False
        for p in ordered_prefs:
            if queues[p] and len(result) < limit:
                result.append(queues[p].pop(0))
                found_any = True
        if not found_any:
            break

    return result[:limit]

# Read all rows
with open(DATA, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    all_rows = list(reader)

date_col = fieldnames[0]  # segment_local_departure_date

# Group by (segment, cabin_class, meal_time, date)
groups = defaultdict(list)
for r in all_rows:
    key = (r["segment"], r["cabin_class"], r["meal_time"], r[date_col])
    groups[key].append(r)

# Apply limits
kept = []
for (seg, cab, mt, dt), rows in sorted(groups.items()):
    limit = LIMITS.get((seg, cab, mt), DEFAULT_LIMIT)
    selected = diverse_select(rows, limit)
    kept.extend(selected)

with open(OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(kept)

# Report
from collections import Counter
summary = Counter((r["segment"], r["cabin_class"], r["meal_time"]) for r in kept)
per_day = {}
dates_count = Counter((r["segment"], r["cabin_class"], r["meal_time"], r[date_col]) for r in kept)
dates_per_group = Counter((r["segment"], r["cabin_class"], r["meal_time"]) for r in kept)

print(f"Total rows: {len(all_rows)} → {len(kept)}")
print()
for (seg, cab, mt), total in sorted(summary.items()):
    num_dates = len(set(r[date_col] for r in groups[(seg,cab,mt,)] if False) or
                    [r[date_col] for r in kept if r["segment"]==seg and r["cabin_class"]==cab and r["meal_time"]==mt])
    dates = len(set(r[date_col] for r in kept if r["segment"]==seg and r["cabin_class"]==cab and r["meal_time"]==mt))
    print(f"  {seg} | {cab} | {mt}: {total//dates if dates else 0} meals/day × {dates} days = {total} rows")
print(f"\nWritten to {OUT}")
