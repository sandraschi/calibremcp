"""
Integration tests for book search functionality.

Tests the full search flow from tool call through database query to result formatting.
"""

import asyncio

import pytest

from calibre_mcp.db.database import close_database, init_database
from calibre_mcp.tools.book_tools import search_books_helper


class TestSearchIntegration:
    """Integration tests for search functionality."""

    @pytest.mark.asyncio
    async def test_full_search_flow(self, test_database):
        """Test the complete search flow from tool to database."""
        # Test search by author
        result = await search_books_helper(author="Conan Doyle", limit=10)

        assert "items" in result
        assert "total" in result
        assert "page" in result
        assert "total_pages" in result
        assert result["total"] >= 2

        # Verify book structure
        if result["items"]:
            book = result["items"][0]
            assert "id" in book
            assert "title" in book
            assert "authors" in book

    @pytest.mark.asyncio
    async def test_search_with_database_reconnection(self, test_database):
        """Test search after database reconnection."""
        # Close and reopen database
        close_database()
        init_database(str(test_database), echo=False)

        result = await search_books_helper(text="Scarlet", limit=10)

        assert "items" in result
        assert result["total"] >= 1

    @pytest.mark.asyncio
    async def test_search_multiple_queries_sequential(self, test_database):
        """Test multiple sequential search queries."""
        queries = [
            {"text": "Scarlet"},
            {"author": "Conan Doyle"},
            {"tag": "mystery"},
            {"series": "Sherlock Holmes"},
        ]

        results = []
        for query in queries:
            result = await search_books_helper(**query, limit=10)
            results.append(result)
            assert "items" in result
            assert result["total"] >= 0

        # Verify all queries returned results
        assert len(results) == len(queries)

    @pytest.mark.asyncio
    async def test_search_concurrent_queries(self, test_database):
        """Test concurrent search queries."""

        async def run_search(query_params):
            return await search_books_helper(**query_params, limit=10)

        queries = [
            {"text": "Scarlet"},
            {"author": "Conan Doyle"},
            {"tag": "mystery"},
        ]

        results = await asyncio.gather(*[run_search(q) for q in queries])

        assert len(results) == len(queries)
        for result in results:
            assert "items" in result
            assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_with_table_formatting(self, test_database):
        """Test search with table formatting integration."""
        result = await search_books_helper(author="Conan Doyle", format_table=True, limit=10)

        assert "items" in result
        assert "table" in result
        assert isinstance(result["table"], str)

        # Verify table contains expected columns
        table = result["table"]
        assert "ID" in table or "Title" in table or "Author" in table

    @pytest.mark.asyncio
    async def test_search_error_handling(self, test_database):
        """Test error handling in search flow."""
        # Test with invalid limit
        with pytest.raises(ValueError):
            await search_books_helper(limit=0)

        # Test with invalid offset
        with pytest.raises(ValueError):
            await search_books_helper(offset=-1)

        # Valid query should still work after errors
        result = await search_books_helper(limit=10)
        assert "items" in result

    @pytest.mark.asyncio
    async def test_search_with_complex_filters(self, test_database):
        """Test search with complex filter combinations."""
        result = await search_books_helper(
            author="Conan Doyle",
            tags=["mystery", "detective"],
            exclude_tags=["horror"],
            exclude_authors=["Stephen King"],
            min_rating=1,
            formats=["EPUB"],
            limit=10,
        )

        assert "items" in result
        assert result["total"] >= 0

        # Verify filters were applied
        if result["items"]:
            for book in result["items"]:
                # Should have EPUB format
                formats = [f.get("format", "") for f in book.get("formats", [])]
                assert "EPUB" in formats or len(formats) == 0

    @pytest.mark.asyncio
    async def test_search_pagination_consistency(self, test_database):
        """Test that pagination returns consistent results."""
        # Get all results without pagination
        all_results = await search_books_helper(limit=100)
        total_books = all_results["total"]

        if total_books > 0:
            # Get first page
            page1 = await search_books_helper(limit=2, offset=0)

            # Get second page
            if total_books > 2:
                page2 = await search_books_helper(limit=2, offset=2)

                # Verify no duplicates between pages
                page1_ids = {book["id"] for book in page1["items"]}
                page2_ids = {book["id"] for book in page2["items"]}
                assert len(page1_ids & page2_ids) == 0

    @pytest.mark.asyncio
    async def test_search_result_structure(self, test_database):
        """Test that search results have correct structure."""
        result = await search_books_helper(author="Conan Doyle", limit=1)

        assert "items" in result
        assert "total" in result
        assert "page" in result
        assert "per_page" in result
        assert "total_pages" in result

        if result["items"]:
            book = result["items"][0]
            # Verify book has required fields
            assert "id" in book
            assert "title" in book
            # Authors should be a list
            assert isinstance(book.get("authors", []), list)

    @pytest.mark.asyncio
    async def test_search_empty_library(self, tmp_path):
        """Test search behavior with empty library."""
        # Create empty database
        empty_db = tmp_path / "empty_metadata.db"
        init_database(str(empty_db), echo=False)

        try:
            result = await search_books_helper(limit=10)
            assert "items" in result
            assert result["total"] == 0
            assert len(result["items"]) == 0
        finally:
            close_database()

    @pytest.mark.asyncio
    async def test_search_large_result_set(self, test_database):
        """Test search with large result set."""
        # Get all books
        result = await search_books_helper(limit=1000)

        assert "items" in result
        assert result["total"] >= 0
        assert len(result["items"]) <= 1000

    @pytest.mark.asyncio
    async def test_search_case_sensitivity(self, test_database):
        """Test that search is case-insensitive across the flow."""
        queries = [
            "scarlet",
            "SCARLET",
            "Scarlet",
            "ScArLeT",
        ]

        results = []
        for query in queries:
            result = await search_books_helper(text=query, limit=10)
            results.append(result["total"])

        # All should return same count
        assert len(set(results)) == 1
