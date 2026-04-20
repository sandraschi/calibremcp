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

# Get some sample tags
cur.execute("SELECT id, name FROM tags LIMIT 20")
tags = cur.fetchall()
for _tag_id, _tag_name in tags:
    pass

conn.close()
