"""Check how many tags exist."""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

conn = sqlite3.connect(r"L:\Multimedia Files\Written Word\Calibre-Bibliothek\metadata.db")
cur = conn.cursor()

# Count tags
cur.execute("SELECT COUNT(*) FROM tags")
tag_count = cur.fetchone()[0]
print(f"Total tags in database: {tag_count}")

# Get some sample tags
cur.execute("SELECT id, name FROM tags LIMIT 20")
tags = cur.fetchall()
print("\nSample tags (first 20):")
for tag_id, tag_name in tags:
    print(f"  {tag_id}: {tag_name}")

conn.close()
