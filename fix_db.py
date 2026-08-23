import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print("No db.sqlite3 found")
    exit(0)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Drop corrupted tables
tables_to_drop = ['bookings_booking', 'bookings_bookingevent', 'payments_wallet']
for table in tables_to_drop:
    try:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"Dropped {table}")
    except Exception as e:
        print(f"Error dropping {table}: {e}")

# Delete from migrations
try:
    cur.execute("DELETE FROM django_migrations WHERE app IN ('bookings', 'payments')")
    print("Cleared migration history for bookings and payments")
except Exception as e:
    print(f"Error clearing migrations: {e}")

conn.commit()
conn.close()
print("Database cleanup complete.")
