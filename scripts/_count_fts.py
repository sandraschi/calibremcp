import sqlite3
db = r'C:\Users\hackb\OneDrive\Calibre Library\full-text-search.db'
conn = sqlite3.connect(db)
rows, chars = conn.execute(
    "SELECT COUNT(*), SUM(LENGTH(searchable_text)) FROM books_text "
    "WHERE searchable_text IS NOT NULL AND trim(searchable_text) != ''"
).fetchone()
conn.close()
chars = chars or 0
chunks = chars // 1000
print(f"Book-format rows: {rows}")
print(f"Total chars: {chars:,}")
print(f"Estimated total chunks (~1000 char stride): {chunks:,}")
print(f"At current rate (~7 chunks/sec), remaining from 3200: {max(0, chunks - 3200) / 7 / 3600:.1f}h")
