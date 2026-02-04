"""Test the path fix."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from calibre_mcp.db.database import init_database
from calibre_mcp.services.book_service import book_service

# Initialize with the L: drive library
init_database(r"L:\Multimedia Files\Written Word\Calibre-Bibliothek\metadata.db")

# Get book 6696
book = book_service.get_by_id(6696)
print(f"Book: {book['title']}")
print("\nFormats:")
for fmt in book.get("formats", []):
    print(f"  {fmt.get('format')}: {fmt.get('path')}")
    # Check if file exists
    path = Path(fmt.get("path"))
    exists = path.exists()
    print(f"    File exists: {exists}")
