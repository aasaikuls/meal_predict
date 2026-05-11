"""
Filter MAG data to 5 realistic flights only:
  MH 0180  KUL→MAA  3.5h  Dinner            (single meal, short-medium haul)
  MH 0088  KUL→NRT  7h    Lunch             (single meal, medium haul)
  MH 0002  KUL→SYD  8h    Lunch + Dinner    (2 meals, long haul)
  MH 0070  KUL→LHR  13h   Dinner+Supper+Breakfast (ultra long haul)
  MH 0609  KUL→SIN  1h    Refreshments      (very short haul)
"""
import csv
from collections import Counter
from pathlib import Path

DATA_DIR = Path("/data")

KEEP_FLIGHTS = {"MH 0180", "MH 0088", "MH 0002", "MH 0070", "MH 0609"}
KEEP_SEGMENTS = {"KUL MAA", "KUL NRT", "KUL SYD", "KUL LHR", "KUL SIN"}

# ── mag_bookings.csv ──────────────────────────────────────────────────────────
src_b = DATA_DIR / "mag_bookings.csv"
with open(src_b, newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = [r for r in reader if r["operating_flight_number"] in KEEP_FLIGHTS]

out_b = Path("/tmp/mag_bookings.csv")
with open(out_b, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

c = Counter(r["operating_flight_number"] for r in rows)
print("Bookings kept:", dict(c), "| Total:", len(rows))

# ── mag_meal.csv ─────────────────────────────────────────────────────────────
src_m = DATA_DIR / "mag_meal.csv"
with open(src_m, newline="") as f:
    reader = csv.DictReader(f)
    mfields = reader.fieldnames
    mrows = []
    for r in reader:
        if r["segment"] not in KEEP_SEGMENTS:
            continue
        # MH0180 serves Dinner only on KUL→MAA; drop Lunch rows from old MH0192
        if r["segment"] == "KUL MAA" and r["meal_time"] != "Dinner":
            continue
        mrows.append(r)

out_m = Path("/tmp/mag_meal.csv")
with open(out_m, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=mfields)
    writer.writeheader()
    writer.writerows(mrows)

mc = Counter(r["segment"] for r in mrows)
print("Meal rows kept:", dict(mc), "| Total:", len(mrows))
print("Done. Files written to /tmp/")
