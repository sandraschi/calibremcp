#!/usr/bin/env python3
"""
Comprehensive test battery for Calibre MCP server functionality.

Tests all core operations: libraries, search, authors, tags, dates.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def test_calibre_mcp():
    """Run comprehensive tests for Calibre MCP functionality."""


    try:
        # Test 1: Basic imports and setup
        from calibre_mcp.tools.authors.manage_authors import manage_authors
        from calibre_mcp.tools.book_management.query_books import query_books
        from calibre_mcp.tools.library.manage_libraries import manage_libraries
        from calibre_mcp.tools.tags.manage_tags import manage_tags


        # Test 2: List libraries
        result = await manage_libraries(operation="list")
        if result.get("libraries"):
            for _lib in result["libraries"][:3]:  # Show first 3
                pass

        # Test 3: Search single library by title
        if result.get("libraries"):
            result["libraries"][0]["name"]
            result = await query_books(
                operation="search",
                query="the",  # Common word to find books
                limit=5,
            )
            if result.get("items"):
                for book in result["items"][:3]:
                    pass

        # Test 4: Search across libraries
        result = await manage_libraries(
            operation="search",
            query="mystery",  # Search for mystery books
            limit=10,
        )
        if result.get("results"):
            for book in result["results"][:3]:
                book.get("library_name", "Unknown")

        # Test 5: List authors
        result = await manage_authors(operation="list", limit=10)
        if result.get("items"):
            for _author in result["items"][:5]:
                pass

        # Test 6: Search by author
        result = await query_books(
            operation="search",
            author="doyle",  # Arthur Conan Doyle
            limit=5,
        )
        if result.get("items"):
            for book in result["items"][:3]:
                pass

        # Test 7: List tags
        result = await manage_tags(operation="list", limit=10)
        if result.get("items"):
            for _tag in result["items"][:5]:
                pass

        # Test 8: Search by tag
        result = await query_books(
            operation="search",
            tag="fiction",  # Search for fiction books
            limit=5,
        )
        if result.get("items"):
            for book in result["items"][:3]:
                pass

        # Test 9: Search by publication year
        result = await query_books(
            operation="search",
            query="",  # Empty query to search by year only
            after_date="2020-01-01",
            before_date="2024-12-31",
            limit=5,
        )
        if result.get("items"):
            for book in result["items"][:3]:
                book.get("pubdate", "Unknown")

        # Test 10: Search by year range
        result = await query_books(
            operation="search", query="", min_year=2010, max_year=2020, limit=5
        )
        if result.get("items"):
            for book in result["items"][:3]:
                book.get("pubdate", "Unknown")


    except Exception:
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    # Run the async test
    success = asyncio.run(test_calibre_mcp())
    sys.exit(0 if success else 1)
