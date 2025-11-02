"""Inspect Calibre FTS database structure to understand tokenizer usage."""
import sqlite3
from pathlib import Path

fts_path = Path(r"L:\Multimedia Files\Written Word\Calibre-Bibliothek\full-text-search.db")

if not fts_path.exists():
    print(f"FTS database not found: {fts_path}")
    exit(1)

conn = sqlite3.connect(str(fts_path))
cursor = conn.cursor()

# Get all tables
print("=== TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# Get CREATE TABLE statements for FTS tables
print("\n=== FTS TABLE STRUCTURE ===")
cursor.execute("""
    SELECT name, sql FROM sqlite_master 
    WHERE type='table' AND sql LIKE '%USING fts%'
""")
fts_tables = cursor.fetchall()

for name, sql in fts_tables:
    print(f"\nTable: {name}")
    print(f"SQL: {sql}")

# Check if content table exists
print("\n=== CONTENT TABLE STRUCTURE ===")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='books_text'")
content_table = cursor.fetchone()
if content_table:
    print(f"Content table SQL: {content_table[0]}")
    
    # Check columns
    cursor.execute("PRAGMA table_info(books_text)")
    columns = cursor.fetchall()
    print(f"\nColumns in books_text:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Try searching content table directly
    print("\n=== DIRECT CONTENT TABLE SEARCH ===")
    try:
        cursor.execute("""
            SELECT id FROM books_text 
            WHERE searchable_text LIKE '%worst of times%' 
            LIMIT 5
        """)
        results = cursor.fetchall()
        print(f"✓ Direct search succeeded! Found {len(results)} results")
        print(f"  Book IDs: {[r[0] for r in results]}")
    except sqlite3.Error as e:
        print(f"✗ Direct search failed: {e}")
else:
    print("Content table 'books_text' not found")

conn.close()
