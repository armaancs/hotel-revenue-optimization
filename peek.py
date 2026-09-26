import sqlite3, pandas as pd
conn = sqlite3.connect("hotel.db")
print(pd.read_sql("SELECT * FROM bookings LIMIT 10", conn))
print(pd.read_sql("SELECT COUNT(*) AS n FROM bookings", conn))
conn.close()