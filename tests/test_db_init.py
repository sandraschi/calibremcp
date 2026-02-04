"""Test database init with actual library."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from calibre_mcp.db.database import init_database
from calibre_mcp.services.tag_service import tag_service

# Initialize with L: library
library_path = r"L:\Multimedia Files\Written Word\Calibre-Bibliothek"
db_path = library_path + r"\metadata.db"

print(f"Initializing database: {db_path}")
init_database(db_path)

print("Getting tag statistics...")
stats = tag_service.get_tag_statistics()
print(f"Total tags: {stats['total_tags']}")
print(f"Used tags: {stats['used_tags_count']}")
print(f"Unused tags: {stats['unused_tags_count']}")
