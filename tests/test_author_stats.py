"""Test author stats."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from calibre_mcp.db.database import init_database
from calibre_mcp.services.author_service import author_service

# Initialize with L: library
library_path = r"L:\Multimedia Files\Written Word\Calibre-Bibliothek"
db_path = library_path + r"\metadata.db"

print(f"Initializing database: {db_path}")
init_database(db_path)

print("Getting author statistics...")
stats = author_service.get_author_stats()
print(f"Total authors: {stats['total_authors']}")
print("\nTop 10 authors by book count:")
for idx, author in enumerate(stats["top_authors"][:10], 1):
    print(f"  {idx}. {author['name']}: {author['book_count']} books")
