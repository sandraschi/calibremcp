"""Check database schema."""

import sqlite3

conn = sqlite3.connect(r"L:\Multimedia Files\Written Word\Calibre-Bibliothek\metadata.db")
cur = conn.cursor()

# Get all table schemas
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cur.fetchall()

for (table_name,) in tables:
    pass

# Check books table schema
cur.execute("PRAGMA table_info(books)")
columns = cur.fetchall()
for _col in columns:
    pass

# Check if there's a publishers table
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%publish%'")
publisher_tables = cur.fetchall()
for (table_name,) in publisher_tables:
    cur.execute(f"PRAGMA table_info({table_name})")
    cols = cur.fetchall()
    for _col in cols:
        pass

conn.close()
