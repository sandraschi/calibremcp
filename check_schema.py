"""Check database schema."""

import sqlite3

conn = sqlite3.connect(r"L:\Multimedia Files\Written Word\Calibre-Bibliothek\metadata.db")
cur = conn.cursor()

# Get all table schemas
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cur.fetchall()

print("Tables in database:")
for (table_name,) in tables:
    print(f"  {table_name}")

# Check books table schema
print("\nBooks table schema:")
cur.execute("PRAGMA table_info(books)")
columns = cur.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check if there's a publishers table
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%publish%'")
publisher_tables = cur.fetchall()
print("\nPublisher-related tables:")
for (table_name,) in publisher_tables:
    print(f"  {table_name}")
    cur.execute(f"PRAGMA table_info({table_name})")
    cols = cur.fetchall()
    for col in cols:
        print(f"    {col[1]} ({col[2]})")

conn.close()
