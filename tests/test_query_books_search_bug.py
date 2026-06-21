"""
Test for query_books search functionality — author and series search.

Bug Summary (now fixed):
- query_books(operation="search") failed to match books by author name or series name.
- Text search returned noise from descriptions instead of actual metadata matches.

These tests use the auto-generated test fixture library (Arthur Conan Doyle, Jane Austen,
Mark Twain; Sherlock Holmes series) and do NOT need a live Calibre installation.

The return structure of search_books_helper (which query_books delegates to) is:
    {"items": [...], "total": N, "page": P, "per_page": L, "total_pages": T}
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
async def initialized_server(ensure_test_db):
    """Initialize the calibre-mcp database with the test fixture data."""
    scripts_dir = Path(__file__).parent.parent / "scripts"
    sys.path.insert(0, str(scripts_dir))
    try:
        from create_test_db import create_test_database  # type: ignore[import]
    finally:
        sys.path.pop(0)

    from calibre_mcp.db.database import close_database, get_database, init_database

    db_path = Path(__file__).parent / "fixtures" / "test_library" / "metadata.db"

    # Always rebuild for a known-clean state
    create_test_database()
    init_database(str(db_path), echo=False, force=True)

    yield get_database()

    close_database()


# ---------------------------------------------------------------------------
# Author search tests
# ---------------------------------------------------------------------------

class TestAuthorSearch:
    """Test author search functionality."""

    @pytest.mark.asyncio
    async def test_search_by_author_name_full(self, initialized_server):
        """Search by full author name returns books by that author."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", author="Arthur Conan Doyle", limit=50)

        assert "items" in result, f"Expected 'items' key, got: {list(result.keys())}"
        assert result["total"] > 0, "Expected at least one match for Arthur Conan Doyle"

        for book in result["items"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            assert "doyle" in author_str, (
                f"Book '{book.get('title')}' should be by Conan Doyle, "
                f"but authors are: {author_names}"
            )

    @pytest.mark.asyncio
    async def test_search_by_author_partial(self, initialized_server):
        """Search by partial author name (last name only) returns books."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", author="Doyle", limit=50)

        assert "items" in result
        assert result["total"] > 0, "Expected matches for 'Doyle'"
        for book in result["items"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            assert "doyle" in author_str

    @pytest.mark.asyncio
    async def test_search_by_two_part_name(self, initialized_server):
        """Search by two-part author name matches correctly."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", author="Conan Doyle", limit=50)

        assert "items" in result
        assert result["total"] > 0
        for book in result["items"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            assert "conan" in author_str and "doyle" in author_str

    @pytest.mark.asyncio
    async def test_author_search_no_noise_from_description(self, initialized_server):
        """Author search does not return books that merely mention the author in comments."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", author="Conan Doyle", limit=50)

        assert "items" in result
        for book in result["items"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            assert "conan" in author_str and "doyle" in author_str


# ---------------------------------------------------------------------------
# Series search tests
# ---------------------------------------------------------------------------

class TestSeriesSearch:
    """Test series search functionality."""

    @pytest.mark.asyncio
    async def test_search_by_series_name(self, initialized_server):
        """Search by series name returns books in that series."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", series="Sherlock Holmes", limit=50)

        assert "items" in result
        if result["total"] > 0:
            for book in result["items"]:
                series_data = book.get("series")
                if series_data:
                    series_str = (
                        series_data.get("name", "") if isinstance(series_data, dict)
                        else str(series_data)
                    ).lower()
                    assert "sherlock" in series_str or "holmes" in series_str, (
                        f"Book '{book.get('title')}' series is '{series_data}'"
                    )


# ---------------------------------------------------------------------------
# Combined-filter tests
# ---------------------------------------------------------------------------

class TestCombinedSearch:
    """Test combination of author/series with other filters."""

    @pytest.mark.asyncio
    async def test_author_and_tag_search(self, initialized_server):
        """Author search combined with tag filter returns the intersection."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(
            operation="search", author="Conan Doyle", tag="mystery", limit=50
        )

        assert "items" in result
        for book in result["items"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            assert "doyle" in author_str, f"Expected Doyle book, got: {author_names}"

    @pytest.mark.asyncio
    async def test_author_and_rating_search(self, initialized_server):
        """Author search combined with min_rating filter returns correct books."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", author="Conan Doyle", min_rating=3, limit=50)

        assert "items" in result
        for book in result["items"]:
            author_names = [
                a["name"] if isinstance(a, dict) else a for a in book.get("authors", [])
            ]
            author_str = " ".join(author_names).lower()
            assert "doyle" in author_str


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_author_search_no_matches(self, initialized_server):
        """Author search with no matching authors returns empty results."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(
            operation="search", author="Nonexistent Author Name Xyz", limit=50
        )

        assert "items" in result
        assert result["total"] == 0
        assert len(result["items"]) == 0

    @pytest.mark.asyncio
    async def test_series_search_no_matches(self, initialized_server):
        """Series search with no matching series returns empty results."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(
            operation="search", series="Nonexistent Series Name Xyz", limit=50
        )

        assert "items" in result
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_case_insensitive_author_search(self, initialized_server):
        """Author search is case-insensitive."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result_upper = await query_books(operation="search", author="CONAN DOYLE", limit=50)
        result_lower = await query_books(operation="search", author="conan doyle", limit=50)

        assert result_upper["total"] == result_lower["total"], (
            "Case-insensitive search should return the same count; "
            f"upper={result_upper['total']}, lower={result_lower['total']}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
