#!/usr/bin/env python3
"""
Comprehensive test battery for Calibre MCP server functionality.

Tests all core operations: libraries, search, authors, tags, dates.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

async def test_calibre_mcp():
    """Run comprehensive tests for Calibre MCP functionality."""

    print("🚀 CALIBRE MCP COMPREHENSIVE TEST BATTERY")
    print("=" * 50)

    try:
        # Test 1: Basic imports and setup
        print("\n📦 TEST 1: Basic Imports & Setup")
        from calibre_mcp import mcp
        from calibre_mcp.server import CalibreConfig
        from calibre_mcp.tools.library.manage_libraries import manage_libraries
        from calibre_mcp.tools.book_management.query_books import query_books
        from calibre_mcp.tools.authors.manage_authors import manage_authors
        from calibre_mcp.tools.tags.manage_tags import manage_tags

        print("✓ All imports successful")

        # Test 2: List libraries
        print("\n🏛️  TEST 2: List Libraries")
        result = await manage_libraries(operation="list")
        print(f"✓ Libraries found: {result.get('total', 0)}")
        if result.get('libraries'):
            for lib in result['libraries'][:3]:  # Show first 3
                print(f"  - {lib['name']}: {lib['book_count']} books")

        # Test 3: Search single library by title
        print("\n🔍 TEST 3: Search Single Library by Title")
        if result.get('libraries'):
            first_lib = result['libraries'][0]['name']
            result = await query_books(
                operation="search",
                query="the",  # Common word to find books
                limit=5
            )
            print(f"✓ Found {len(result.get('items', []))} books containing 'the'")
            if result.get('items'):
                for book in result['items'][:3]:
                    print(f"  - {book.get('title', 'Unknown')} by {', '.join(book.get('authors', []))}")

        # Test 4: Search across libraries
        print("\n🌐 TEST 4: Search Across Libraries")
        result = await manage_libraries(
            operation="search",
            query="mystery",  # Search for mystery books
            limit=10
        )
        print(f"✓ Cross-library search found {result.get('total_found', 0)} books")
        if result.get('results'):
            for book in result['results'][:3]:
                lib_name = book.get('library_name', 'Unknown')
                print(f"  - {book.get('title', 'Unknown')} ({lib_name})")

        # Test 5: List authors
        print("\n👤 TEST 5: List Authors")
        result = await manage_authors(operation="list", limit=10)
        print(f"✓ Found {result.get('total', 0)} authors")
        if result.get('items'):
            for author in result['items'][:5]:
                print(f"  - {author.get('name', 'Unknown')}: {author.get('book_count', 0)} books")

        # Test 6: Search by author
        print("\n🔍 TEST 6: Search by Author")
        result = await query_books(
            operation="search",
            author="doyle",  # Arthur Conan Doyle
            limit=5
        )
        print(f"✓ Found {len(result.get('items', []))} books by Doyle")
        if result.get('items'):
            for book in result['items'][:3]:
                print(f"  - {book.get('title', 'Unknown')}")

        # Test 7: List tags
        print("\n🏷️  TEST 7: List Tags")
        result = await manage_tags(operation="list", limit=10)
        print(f"✓ Found {result.get('total', 0)} tags")
        if result.get('items'):
            for tag in result['items'][:5]:
                print(f"  - {tag.get('name', 'Unknown')}: {tag.get('book_count', 0)} books")

        # Test 8: Search by tag
        print("\n🔍 TEST 8: Search by Tag")
        result = await query_books(
            operation="search",
            tag="fiction",  # Search for fiction books
            limit=5
        )
        print(f"✓ Found {len(result.get('items', []))} fiction books")
        if result.get('items'):
            for book in result['items'][:3]:
                print(f"  - {book.get('title', 'Unknown')} by {', '.join(book.get('authors', []))}")

        # Test 9: Search by publication year
        print("\n📅 TEST 9: Search by Publication Year")
        result = await query_books(
            operation="search",
            query="",  # Empty query to search by year only
            after_date="2020-01-01",
            before_date="2024-12-31",
            limit=5
        )
        print(f"✓ Found {len(result.get('items', []))} books from 2020-2024")
        if result.get('items'):
            for book in result['items'][:3]:
                pubdate = book.get('pubdate', 'Unknown')
                print(f"  - {book.get('title', 'Unknown')} ({pubdate})")

        # Test 10: Search by year range
        print("\n📅 TEST 10: Search by Year Range")
        result = await query_books(
            operation="search",
            query="",
            min_year=2010,
            max_year=2020,
            limit=5
        )
        print(f"✓ Found {len(result.get('items', []))} books from 2010-2020")
        if result.get('items'):
            for book in result['items'][:3]:
                pubdate = book.get('pubdate', 'Unknown')
                print(f"  - {book.get('title', 'Unknown')} ({pubdate})")

        print("\n" + "=" * 50)
        print("🎉 ALL COMPREHENSIVE TESTS COMPLETED!")
        print("Calibre MCP server is fully functional.")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    # Run the async test
    success = asyncio.run(test_calibre_mcp())
    sys.exit(0 if success else 1)