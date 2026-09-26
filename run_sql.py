"""
run_sql.py — run a .sql file against a SQLite database.

Put this file in the same folder as hotel.db and 02_build_views.sql, then run:

    python run_sql.py

It runs 02_build_views.sql against hotel.db and then confirms the views exist.
"""

import sqlite3
import os
import sys

DB = "hotel.db"
SQL_FILE = "02_build_views.sql"

def main():
    # Allow an optional custom sql file: python run_sql.py some_other.sql
    sql_file = sys.argv[1] if len(sys.argv) > 1 else SQL_FILE

    if not os.path.exists(DB):
        raise SystemExit(f"Can't find {DB}. Run 01_clean_and_load.py first.")
    if not os.path.exists(sql_file):
        raise SystemExit(f"Can't find {sql_file}. Make sure it's in this folder.")

    conn = sqlite3.connect(DB)
    conn.executescript(open(sql_file).read())   # executescript runs multiple statements
    conn.commit()

    # Confirm the views were created
    views = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name"
    ).fetchall()
    conn.close()

    print(f"Ran {sql_file} against {DB}.")
    if views:
        print("Views now in the database:")
        for (name,) in views:
            print("  -", name)
    else:
        print("No views found — check the SQL file ran correctly.")

if __name__ == "__main__":
    main()