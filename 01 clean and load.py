"""
01_clean_and_load.py
RevP/Optimize — clean the Hotel Booking Demand dataset and load it into SQLite.

Prereqs:
    pip install pandas
    Download hotel_bookings.csv from Kaggle ("Hotel Booking Demand") into this folder.

Run:
    python 01_clean_and_load.py

Outputs:
    hotel.db                 (SQLite database with a `bookings` table)
    exports/bookings.csv     (cleaned data, for Power BI CSV import if you skip ODBC)
"""

import sqlite3
import os
import pandas as pd

SRC = "hotel_bookings.csv"
DB = "hotel.db"
EXPORT_DIR = "exports"

def main():
    if not os.path.exists(SRC):
        raise SystemExit(
            f"Can't find {SRC}. Download 'Hotel Booking Demand' from Kaggle "
            "and put hotel_bookings.csv in this folder."
        )

    df = pd.read_csv(SRC)
    start_rows = len(df)
    print(f"Loaded {start_rows:,} rows.")

    # --- Known data-quality fixes (document these in your README) ---

    # 1. Missing values in a few columns per the dataset's documentation.
    df["children"] = df["children"].fillna(0)
    df["country"] = df["country"].fillna("UNK")
    df["agent"] = df["agent"].fillna(0)
    df["company"] = df["company"].fillna(0)

    # 2. ADR (average daily rate) has a small number of bad values:
    #    one negative rate and at least one extreme outlier (~5400).
    #    Cap to a sane range and drop non-positive rates.
    before = len(df)
    df = df[df["adr"] > 0]
    df = df[df["adr"] < 1000]  # 1000/night cap; note this in README
    print(f"Dropped {before - len(df):,} rows with non-positive or extreme ADR.")

    # 3. Rows with zero guests are not real bookings.
    df["total_guests"] = df["adults"] + df["children"] + df["babies"]
    before = len(df)
    df = df[df["total_guests"] > 0]
    print(f"Dropped {before - len(df):,} rows with zero guests.")

    # --- Derived fields used by the analysis ---
    df["total_nights"] = df["stays_in_week_nights"] + df["stays_in_weekend_nights"]
    df = df[df["total_nights"] > 0]  # drop 0-night rows

    # Potential room revenue = rate * nights (what the booking is worth if honored)
    df["potential_revenue"] = (df["adr"] * df["total_nights"]).round(2)
    # Realized revenue = 0 if canceled, else potential
    df["realized_revenue"] = df.apply(
        lambda r: 0.0 if r["is_canceled"] == 1 else r["potential_revenue"], axis=1
    ).round(2)

    # Arrival date as a real date, for time-series in Power BI
    month_map = {m: i for i, m in enumerate(
        ["January","February","March","April","May","June",
         "July","August","September","October","November","December"], start=1)}
    df["arrival_month_num"] = df["arrival_date_month"].map(month_map)
    df["arrival_date"] = pd.to_datetime(dict(
        year=df["arrival_date_year"],
        month=df["arrival_month_num"],
        day=df["arrival_date_day_of_month"],
    ), errors="coerce")

    # --- Modeled cost layer (TRANSPARENT ASSUMPTION — say so in README) ---
    # Public data has no supplier cost. We model a cost-of-sale % by distribution
    # channel to demonstrate margin analysis. Swap for real costs when available.
    channel_cost_rate = {
        "Direct": 0.55,      # lowest cost-of-sale (no intermediary)
        "Corporate": 0.60,
        "TA/TO": 0.72,       # travel agent / tour operator — higher commission
        "GDS": 0.70,
        "Undefined": 0.68,
    }
    df["cost_rate"] = df["distribution_channel"].map(channel_cost_rate).fillna(0.68)
    df["modeled_margin"] = (df["realized_revenue"] * (1 - df["cost_rate"])).round(2)

    print(f"Final clean rows: {len(df):,} (removed {start_rows - len(df):,} total).")

    # --- Write outputs ---
    os.makedirs(EXPORT_DIR, exist_ok=True)
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    df.to_sql("bookings", conn, index=False)
    conn.close()
    df.to_csv(os.path.join(EXPORT_DIR, "bookings.csv"), index=False)

    print(f"\nWrote {DB} (table: bookings) and {EXPORT_DIR}/bookings.csv")
    print("Next: run the queries in 02_build_views.sql and 03_analysis_queries.sql")

if __name__ == "__main__":
    main()
