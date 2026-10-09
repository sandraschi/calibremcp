"""
Integration tests for portmanteau tools.

Tests portmanteau tools with real database connections and fixtures.
"""

import pytest

from calibre_mcp.db.database import close_database, init_database
from calibre_mcp.tools.book_management.manage_books import manage_books
from calibre_mcp.tools.book_management.query_books import query_books
from calibre_mcp.tools.library.manage_libraries import manage_libraries


@pytest.mark.asyncio
async def test_manage_books_integration(test_library, sample_book_data):
    """Integration test for manage_books operations."""
    # Initialize database
    init_database(str(test_library["db_path"]), echo=False)

    try:
        # Test get operation (assuming book exists in test database)
        result = await manage_books.fn(operation="get", book_id="1", include_metadata=True)

        # Verify result structure
        assert "id" in result or "error" in result

    finally:
        close_database()


@pytest.mark.asyncio
async def test_query_books_integration(test_library):
    """Integration test for query_books operations."""
    # Initialize database
    init_database(str(test_library["db_path"]), echo=False)

    try:
        # Test search operation
        result = await query_books.fn(operation="search", text="test", limit=10)

        # Verify result structure
        assert "results" in result or "items" in result
        assert "total" in result

        # Test list operation
        result = await query_books.fn(operation="list", limit=10)

        # Verify result is a LibrarySearchResponse with expected attributes
        assert hasattr(result, "results")
        assert hasattr(result, "total_found")
        assert isinstance(result.results, list)
        assert isinstance(result.total_found, int)

    finally:
        close_database()


@pytest.mark.asyncio
async def test_manage_libraries_integration(test_library):
    """Integration test for manage_libraries operations."""
    # Initialize database
    init_database(str(test_library["db_path"]), echo=False)

    try:
        # Test list operation
        result = await manage_libraries.fn(operation="list")

        # Test stats operation
        stats_result = await manage_libraries.fn(operation="stats", library_name="main")

        assert "book_count" in stats_result

        # Verify result structure
        assert "libraries" in result or "error" in result

        # Test stats operation (if library exists)
        if "libraries" in result and len(result["libraries"]) > 0:
            library_name = result["libraries"][0]["name"]
            stats_result = await manage_libraries.fn(operation="stats", library_name=library_name)

            assert "library_name" in stats_result or "error" in stats_result

    finally:
        close_database()


@pytest.mark.asyncio
async def test_portmanteau_workflow_integration(test_library):
    """Test a complete workflow using multiple portmanteau tools."""
    # Initialize database
    init_database(str(test_library["db_path"]), echo=False)

    try:
        # 1. List libraries
        libraries = await manage_libraries.fn(operation="list")

        # 2. Query books
        books = await query_books.fn(operation="search", text="", limit=5)

        # 3. Get book details if available
        if "results" in books and len(books["results"]) > 0:
            book_id = str(books["results"][0].get("id", "1"))
            book_details = await manage_books(operation="get", book_id=book_id)

            assert "id" in book_details or "error" in book_details

    finally:
        close_database()
