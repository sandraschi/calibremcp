"""Check how many authors exist."""

import sqlite3

conn = sqlite3.connect(r"L:\Multimedia Files\Written Word\Calibre-Bibliothek\metadata.db")
cur = conn.cursor()

# Count authors
cur.execute("SELECT COUNT(*) FROM authors")
author_count = cur.fetchone()[0]
print(f"Total authors in database: {author_count}")

# Get some sample authors
cur.execute("SELECT id, name FROM authors LIMIT 20")
authors = cur.fetchall()
print("\nSample authors (first 20):")
for author_id, author_name in authors:
    print(f"  {author_id}: {author_name}")

conn.close()
