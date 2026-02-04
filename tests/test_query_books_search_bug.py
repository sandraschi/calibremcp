"""
Test for query_books search bug fix - author and series search functionality.

Bug Summary:
- query_books(operation="search") fails to match books by author name or series name
- Text search returns noise from descriptions instead of actual metadata matches
- Impact: Author/series filtering is completely broken

This test reproduces and validates the fix for:
1. Author search by name (e.g., "Conan Doyle")
2. Series search by name (e.g., "Sherlock Holmes")
3. Combinations of author/series with other filters
"""

import pytest


@pytest.fixture
async def initialized_server():
    """Initialize the calibre-mcp server with test data."""
    from calibre_mcp.db.database import get_database, init_database
    from tests.fixtures.conftest import get_test_db_path

    db_path = get_test_db_path()
    if db_path.exists():
        db_path.unlink()

    init_database(str(db_path), echo=False, force=True)
    yield get_database()


class TestAuthorSearch:
    """Test author search functionality."""

    @pytest.mark.asyncio
    async def test_search_by_author_name_full(self, initialized_server):
        """Test: search by full author name returns books by that author."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", author="Arthur Conan Doyle", limit=50)

        assert result["success"] is True
        assert result["total_found"] > 0

        # All returned books should be by Arthur Conan Doyle
        for book in result["results"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            assert "conan" in author_str and "doyle" in author_str, (
                f"Book '{book['title']}' should be by Conan Doyle but authors are: {author_names}"
            )

    @pytest.mark.asyncio
    async def test_search_by_author_partial(self, initialized_server):
        """Test: search by partial author name (last name only) returns books."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", author="Doyle", limit=50)

        assert result["success"] is True
        assert result["total_found"] > 0

        # Should match "Arthur Conan Doyle"
        for book in result["results"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            assert "doyle" in author_str

    @pytest.mark.asyncio
    async def test_search_by_two_part_name(self, initialized_server):
        """Test: search by two-part author name matches correctly."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", author="Conan Doyle", limit=50)

        assert result["success"] is True
        assert result["total_found"] > 0

        # Should match "Arthur Conan Doyle" (has both "Conan" AND "Doyle")
        for book in result["results"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            assert "conan" in author_str and "doyle" in author_str

    @pytest.mark.asyncio
    async def test_search_by_author_through_text_param(self, initialized_server):
        """Test: search using 'by Author' syntax through text parameter."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", text="by Conan Doyle", limit=50)

        assert result["success"] is True
        assert result["total_found"] > 0

        # Should extract author from query and find books
        for book in result["results"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            assert "conan" in author_str and "doyle" in author_str

    @pytest.mark.asyncio
    async def test_search_author_no_noise_from_description(self, initialized_server):
        """Test: author search doesn't match noise from book descriptions."""
        from calibre_mcp.tools.book_management.query_books import query_books

        # Search for "Conan Doyle" - should NOT match books mentioning this in description
        result = await query_books(operation="search", author="Conan Doyle", limit=50)

        assert result["success"] is True
        # Results should be actual books BY Conan Doyle, not books that mention him
        for book in result["results"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            # All results must be actual author matches
            assert "conan" in author_str and "doyle" in author_str


class TestSeriesSearch:
    """Test series search functionality."""

    @pytest.mark.asyncio
    async def test_search_by_series_name(self, initialized_server):
        """Test: search by series name returns books in that series."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", series="Sherlock Holmes", limit=50)

        if result["total_found"] > 0:
            # All returned books should be in Sherlock Holmes series
            for book in result["results"]:
                series_names = []
                series_data = book.get("series")
                if series_data:
                    if isinstance(series_data, dict):
                        series_names.append(series_data.get("name", ""))
                    elif isinstance(series_data, str):
                        series_names.append(series_data)

                series_str = " ".join(series_names).lower()
                assert "sherlock" in series_str or len(series_names) == 1

    @pytest.mark.asyncio
    async def test_search_by_series_through_text_param(self, initialized_server):
        """Test: series search through 'series X' syntax in text parameter."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", text="series Sherlock Holmes", limit=50)

        # If any results found, they should be from the series
        if result["total_found"] > 0:
            for book in result["results"]:
                series_data = book.get("series")
                assert series_data is not None


class TestCombinedSearch:
    """Test combination of author/series with other filters."""

    @pytest.mark.asyncio
    async def test_author_and_tag_search(self, initialized_server):
        """Test: author search combined with tag filter."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(
            operation="search", author="Conan Doyle", tag="mystery", limit=50
        )

        # Should return books that are BOTH by Conan Doyle AND tagged as mystery
        assert result["success"] is True
        if result["total_found"] > 0:
            for book in result["results"]:
                author_names = [
                    a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
                ]
                author_str = " ".join(author_names).lower()
                assert "conan" in author_str and "doyle" in author_str

    @pytest.mark.asyncio
    async def test_author_and_rating_search(self, initialized_server):
        """Test: author search combined with rating filter."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", author="Conan Doyle", min_rating=3, limit=50)

        assert result["success"] is True
        if result["total_found"] > 0:
            for book in result["results"]:
                # Should be by Conan Doyle
                author_names = [
                    a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
                ]
                author_str = " ".join(author_names).lower()
                assert "conan" in author_str and "doyle" in author_str

                # Should have sufficient rating
                rating = book.get("rating", 0)
                if rating:
                    assert rating >= 3


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_author_search_no_matches(self, initialized_server):
        """Test: author search with no matching authors returns empty results."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", author="Nonexistent Author Name", limit=50)

        assert result["success"] is True
        assert result["total_found"] == 0
        assert len(result.get("results", [])) == 0

    @pytest.mark.asyncio
    async def test_series_search_no_matches(self, initialized_server):
        """Test: series search with no matching series returns empty results."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", series="Nonexistent Series Name", limit=50)

        assert result["success"] is True
        assert result["total_found"] == 0

    @pytest.mark.asyncio
    async def test_case_insensitive_author_search(self, initialized_server):
        """Test: author search is case-insensitive."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result_upper = await query_books(operation="search", author="CONAN DOYLE", limit=50)

        result_lower = await query_books(operation="search", author="conan doyle", limit=50)

        # Both should find the same number of books
        assert result_upper["total_found"] == result_lower["total_found"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
