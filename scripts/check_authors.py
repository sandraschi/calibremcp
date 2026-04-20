"""Check how many authors exist."""

import sqlite3

conn = sqlite3.connect(r"L:\Multimedia Files\Written Word\Calibre-Bibliothek\metadata.db")
cur = conn.cursor()

# Count authors
cur.execute("SELECT COUNT(*) FROM authors")
author_count = cur.fetchone()[0]

# Get some sample authors
cur.execute("SELECT id, name FROM authors LIMIT 20")
authors = cur.fetchall()
for _author_id, _author_name in authors:
    pass

conn.close()
