#!/usr/bin/env python3
"""
Direct test of Calibre MCP functionality without MCP tools.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def test_direct():
    """Test Calibre MCP functionality directly."""


    try:
        # Test 1: Basic imports
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import get_database, init_database
        from calibre_mcp.services.book_service import BookService


        # Test 2: Config
        config = CalibreConfig()

        # Test 3: Database initialization
        if config.local_library_path and (config.local_library_path / "metadata.db").exists():
            init_database(str(config.local_library_path / "metadata.db"), echo=False)
            db_available = True
        else:
            db_available = False

        if db_available:
            # Test 4: Book service
            db = get_database()
            book_service = BookService(db)

            # Test basic query
            result = book_service.get_all(limit=5)
            books = result.get("items", [])
            if books:
                for book in books[:3]:
                    book.get("title", "Unknown")
                    ", ".join(book.get("authors", []))

            # Test search
            result = book_service.get_all(search="the", limit=3)
            books = result.get("items", [])

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_direct()
    sys.exit(0 if success else 1)
