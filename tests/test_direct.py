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

    print("🧪 DIRECT CALIBRE MCP TEST")
    print("=" * 40)

    try:
        # Test 1: Basic imports
        print("\n📦 TEST 1: Basic Imports")
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import get_database, init_database
        from calibre_mcp.services.book_service import BookService

        print("✓ Imports successful")

        # Test 2: Config
        print("\n⚙️  TEST 2: Configuration")
        config = CalibreConfig()
        print(f"✓ Config loaded: {config.library_name}")

        # Test 3: Database initialization
        print("\n💾 TEST 3: Database Initialization")
        if config.local_library_path and (config.local_library_path / "metadata.db").exists():
            init_database(str(config.local_library_path / "metadata.db"), echo=False)
            print("✓ Database initialized")
            db_available = True
        else:
            print("⚠️  No database available")
            db_available = False

        if db_available:
            # Test 4: Book service
            print("\n📚 TEST 4: Book Service")
            db = get_database()
            book_service = BookService(db)

            # Test basic query
            result = book_service.get_all(limit=5)
            books = result.get("items", [])
            print(f"✓ Found {len(books)} books")
            if books:
                for book in books[:3]:
                    title = book.get("title", "Unknown")
                    authors = ", ".join(book.get("authors", []))
                    print(f"  - {title} by {authors}")

            # Test search
            result = book_service.get_all(search="the", limit=3)
            books = result.get("items", [])
            print(f"✓ Search 'the' found {len(books)} books")

        print("\n" + "=" * 40)
        print("✅ DIRECT TESTS COMPLETED!")
        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_direct()
    sys.exit(0 if success else 1)
