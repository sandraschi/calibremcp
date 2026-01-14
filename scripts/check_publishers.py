"""Check how many publishers exist."""

import sqlite3

conn = sqlite3.connect(r"L:\Multimedia Files\Written Word\Calibre-Bibliothek\metadata.db")
cur = conn.cursor()

# Count publishers
cur.execute("SELECT COUNT(*) FROM publishers")
publisher_count = cur.fetchone()[0]
print(f"Total unique publishers in database: {publisher_count}")

# Get some sample publishers
cur.execute("""
    SELECT p.name, COUNT(*) as count 
    FROM publishers p
    JOIN books_publishers_link bpl ON p.id = bpl.publisher
    GROUP BY p.id, p.name 
    ORDER BY count DESC 
    LIMIT 20
""")
publishers = cur.fetchall()
print("\nTop 20 publishers by book count:")
for idx, (publisher, count) in enumerate(publishers, 1):
    print(f"  {idx}. {publisher}: {count} books")

conn.close()
