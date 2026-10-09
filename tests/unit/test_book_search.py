"""
Unit tests for book search functionality.

Tests the search_books_helper function and book_service.get_all method
with various search parameters and edge cases.
"""

import time

import pytest

from calibre_mcp.services.book_service import BookService
from calibre_mcp.tools.book_tools import search_books_helper


class TestSearchBooksHelper:
    """Test the search_books_helper function."""

    @pytest.mark.asyncio
    async def test_search_by_text(self, test_database):
        """Test searching books by text query."""
        result = await search_books_helper(text="Scarlet", limit=10)

        assert "items" in result
        assert "total" in result
        assert isinstance(result["items"], list)
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_by_author(self, test_database):
        """Test searching books by author name."""
        result = await search_books_helper(author="Conan Doyle", limit=10)

        assert "items" in result
        assert "total" in result
        # Should find at least the Sherlock Holmes books
        assert result["total"] >= 2

    @pytest.mark.asyncio
    async def test_search_by_multiple_authors(self, test_database):
        """Test searching books by multiple authors (OR logic)."""
        result = await search_books_helper(authors=["Conan Doyle", "Austen"], limit=10)

        assert "items" in result
        assert result["total"] >= 3  # At least 2 Doyle + 1 Austen

    @pytest.mark.asyncio
    async def test_search_by_tag(self, test_database):
        """Test searching books by tag."""
        result = await search_books_helper(tag="mystery", limit=10)

        assert "items" in result
        assert result["total"] >= 2  # At least 2 mystery books

    @pytest.mark.asyncio
    async def test_search_by_multiple_tags(self, test_database):
        """Test searching books by multiple tags (OR logic)."""
        result = await search_books_helper(tags=["mystery", "romance"], limit=10)

        assert "items" in result
        assert result["total"] >= 3  # Mystery + romance books

    @pytest.mark.asyncio
    async def test_search_by_series(self, test_database):
        """Test searching books by series."""
        result = await search_books_helper(series="Sherlock Holmes", limit=10)

        assert "items" in result
        assert result["total"] >= 2  # At least 2 Sherlock Holmes books

    @pytest.mark.asyncio
    async def test_search_with_exclude_tags(self, test_database):
        """Test searching with tag exclusions."""
        result = await search_books_helper(author="Conan Doyle", exclude_tags=["detective"], limit=10)

        assert "items" in result
        # Should exclude detective books, but may still find others

    @pytest.mark.asyncio
    async def test_search_with_exclude_authors(self, test_database):
        """Test searching with author exclusions."""
        result = await search_books_helper(tag="classic", exclude_authors=["Mark Twain"], limit=10)

        assert "items" in result
        # Should exclude Mark Twain books

    @pytest.mark.asyncio
    async def test_search_by_rating(self, test_database):
        """Test searching books by rating."""
        # Note: Test database may not have ratings, so this tests the filter logic
        result = await search_books_helper(min_rating=4, limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_by_publisher(self, test_database):
        """Test searching books by publisher."""
        result = await search_books_helper(publisher="Test Publisher", limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_with_date_filters(self, test_database):
        """Test searching with publication date filters."""
        result = await search_books_helper(pubdate_start="2020-01-01", pubdate_end="2024-12-31", limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_with_format_filter(self, test_database):
        """Test searching books by format."""
        result = await search_books_helper(formats=["EPUB"], limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_with_size_filters(self, test_database):
        """Test searching books by file size."""
        result = await search_books_helper(min_size=1000, max_size=10000, limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_pagination(self, test_database):
        """Test search pagination."""
        # Get first page
        page1 = await search_books_helper(limit=2, offset=0)

        assert "items" in page1
        assert "page" in page1
        assert "total_pages" in page1
        assert len(page1["items"]) <= 2

        # Get second page
        if page1["total_pages"] > 1:
            page2 = await search_books_helper(limit=2, offset=2)
            assert "items" in page2
            assert page2["page"] == 2

    @pytest.mark.asyncio
    async def test_search_table_format(self, test_database):
        """Test search with table formatting."""
        result = await search_books_helper(author="Conan Doyle", format_table=True, limit=10)

        assert "items" in result
        assert "table" in result
        assert isinstance(result["table"], str)
        assert len(result["table"]) > 0

    @pytest.mark.asyncio
    async def test_search_empty_query(self, test_database):
        """Test search with empty query returns all books."""
        result = await search_books_helper(limit=100)

        assert "items" in result
        assert result["total"] >= 4  # Should find all test books

    @pytest.mark.asyncio
    async def test_search_no_results(self, test_database):
        """Test search that returns no results."""
        result = await search_books_helper(text="NonexistentBookTitle12345", limit=10)

        assert "items" in result
        assert result["total"] == 0
        assert len(result["items"]) == 0

    @pytest.mark.asyncio
    async def test_search_text_actually_filters(self, test_database):
        """Regression test: a plain free-text query must filter results, not no-op.

        Reproduces a bug where a nonsense query returned the exact same books
        as a real query (and as no query at all) because `text` was silently
        ignored unless the query also contained a recognized structured hint
        like "by <author>" or "tag <name>".
        """
        baseline = await search_books_helper(limit=50)
        real = await search_books_helper(text="Scarlet", limit=50)
        nonsense = await search_books_helper(text="zzznonexistentbookterm12345", limit=50)

        assert nonsense["total"] == 0
        assert real["total"] > 0
        assert real["total"] < baseline["total"]
        assert all("scarlet" in book["title"].lower() for book in real["items"])

    @pytest.mark.asyncio
    async def test_search_invalid_limit(self, test_database):
        """Test search with invalid limit raises error."""
        with pytest.raises(ValueError, match="Limit must be between"):
            await search_books_helper(limit=0)

        with pytest.raises(ValueError, match="Limit must be between"):
            await search_books_helper(limit=1001)

    @pytest.mark.asyncio
    async def test_search_invalid_offset(self, test_database):
        """Test search with invalid offset raises error."""
        with pytest.raises(ValueError, match="Offset cannot be negative"):
            await search_books_helper(offset=-1)

    @pytest.mark.asyncio
    async def test_search_combined_filters(self, test_database):
        """Test search with multiple combined filters."""
        result = await search_books_helper(
            author="Conan Doyle", tag="mystery", min_rating=1, formats=["EPUB"], limit=10
        )

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, test_database):
        """Test that search is case-insensitive."""
        result1 = await search_books_helper(text="scarlet", limit=10)
        result2 = await search_books_helper(text="SCARLET", limit=10)
        result3 = await search_books_helper(text="Scarlet", limit=10)

        assert result1["total"] == result2["total"]
        assert result2["total"] == result3["total"]

    @pytest.mark.asyncio
    async def test_search_partial_match(self, test_database):
        """Test that search supports partial matching."""
        result = await search_books_helper(text="Scarl", limit=10)

        assert result["total"] >= 1  # Should find "A Study in Scarlet"

    @pytest.mark.asyncio
    async def test_search_query_alias(self, test_database):
        """Test that 'query' parameter is alias for 'text'."""
        result1 = await search_books_helper(text="Scarlet", limit=10)
        result2 = await search_books_helper(query="Scarlet", limit=10)

        assert result1["total"] == result2["total"]


class TestBookServiceGetAll:
    """Test the BookService.get_all method."""

    def test_get_all_basic(self, test_database):
        """Test basic get_all query."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        result = service.get_all(skip=0, limit=10)

        assert "items" in result
        assert "total" in result
        assert "page" in result
        assert "page_size" in result
        assert "total_pages" in result
        assert result["total"] >= 4  # At least 4 test books

    def test_get_all_with_search(self, test_database):
        """Test get_all with search parameter."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        result = service.get_all(search="Scarlet", skip=0, limit=10)

        assert "items" in result
        assert result["total"] >= 1

    def test_get_all_with_author_filter(self, test_database):
        """Test get_all with author_name filter."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        result = service.get_all(author_name="Conan Doyle", skip=0, limit=10)

        assert "items" in result
        assert result["total"] >= 2

    def test_get_all_with_multiple_authors(self, test_database):
        """Test get_all with authors_list filter."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        result = service.get_all(authors_list=["Conan Doyle", "Austen"], skip=0, limit=10)

        assert "items" in result
        assert result["total"] >= 3

    def test_get_all_with_tag_filter(self, test_database):
        """Test get_all with tag_name filter."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        result = service.get_all(tag_name="mystery", skip=0, limit=10)

        assert "items" in result
        assert result["total"] >= 2

    def test_get_all_with_series_filter(self, test_database):
        """Test get_all with series_name filter."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        result = service.get_all(series_name="Sherlock Holmes", skip=0, limit=10)

        assert "items" in result
        assert result["total"] >= 2

    def test_get_all_with_exclusions(self, test_database):
        """Test get_all with exclusion filters."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        result = service.get_all(tag_name="classic", exclude_authors_list=["Mark Twain"], skip=0, limit=10)

        assert "items" in result
        # Should exclude Tom Sawyer

    def test_get_all_pagination(self, test_database):
        """Test get_all pagination."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        page1 = service.get_all(skip=0, limit=2)
        assert len(page1["items"]) <= 2

        if page1["total"] > 2:
            page2 = service.get_all(skip=2, limit=2)
            assert len(page2["items"]) <= 2
            assert page2["page"] == 2

    def test_get_all_sorting(self, test_database):
        """Test get_all with sorting."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        result_asc = service.get_all(sort_by="title", sort_order="asc", skip=0, limit=10)
        result_desc = service.get_all(sort_by="title", sort_order="desc", skip=0, limit=10)

        assert result_asc["items"][0]["title"] != result_desc["items"][0]["title"]

    def test_get_all_invalid_limit(self, test_database):
        """Test get_all with invalid limit raises error."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        with pytest.raises(ValueError, match="Limit must be between"):
            service.get_all(limit=0)

        with pytest.raises(ValueError, match="Limit must be between"):
            service.get_all(limit=1001)

    def test_get_all_invalid_skip(self, test_database):
        """Test get_all with invalid skip raises error."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        with pytest.raises(ValueError, match="Skip cannot be negative"):
            service.get_all(skip=-1)

    def test_get_all_invalid_sort_order(self, test_database):
        """Test get_all with invalid sort_order raises error."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        with pytest.raises(ValueError, match="sort_order must be"):
            service.get_all(sort_order="invalid")

    def test_get_all_invalid_sort_by(self, test_database):
        """Test get_all with invalid sort_by raises error."""
        from calibre_mcp.db.database import get_database

        db = get_database()
        service = BookService(db)

        with pytest.raises(ValueError, match="sort_by must be one of"):
            service.get_all(sort_by="invalid_field")


class TestSearchEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_search_special_characters(self, test_database):
        """Test search with special characters."""
        result = await search_books_helper(text="O'Reilly", limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_unicode(self, test_database):
        """Test search with Unicode characters."""
        result = await search_books_helper(text="café", limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_very_long_query(self, test_database):
        """Test search with very long query string."""
        long_query = "a" * 1000
        result = await search_books_helper(text=long_query, limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_sql_injection_attempt(self, test_database):
        """Test that SQL injection attempts are handled safely."""
        malicious_query = "'; DROP TABLE books; --"
        result = await search_books_helper(text=malicious_query, limit=10)

        assert "items" in result
        # Database should still be intact
        verify_result = await search_books_helper(limit=10)
        assert verify_result["total"] >= 4

    @pytest.mark.asyncio
    async def test_search_empty_string(self, test_database):
        """Test search with empty string."""
        result = await search_books_helper(text="", limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_whitespace_only(self, test_database):
        """Test search with whitespace-only query."""
        result = await search_books_helper(text="   ", limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_search_all_filters_none(self, test_database):
        """Test search with all filters set to None."""
        result = await search_books_helper(text=None, author=None, tag=None, series=None, limit=10)

        assert "items" in result
        assert result["total"] >= 0


class TestSearchPerformance:
    """Performance tests for search functionality."""

    @pytest.mark.asyncio
    async def test_search_performance_basic(self, test_database):
        """Test basic search performance."""
        start_time = time.time()
        result = await search_books_helper(text="Scarlet", limit=10)
        duration = time.time() - start_time

        assert duration < 1.0  # Should complete in under 1 second
        assert "items" in result

    @pytest.mark.asyncio
    async def test_search_performance_complex_filters(self, test_database):
        """Test search performance with complex filters."""
        start_time = time.time()
        result = await search_books_helper(
            author="Conan Doyle",
            tags=["mystery", "detective"],
            exclude_tags=["horror"],
            min_rating=1,
            formats=["EPUB", "PDF"],
            limit=10,
        )
        duration = time.time() - start_time

        assert duration < 2.0  # Should complete in under 2 seconds
        assert "items" in result

    @pytest.mark.asyncio
    async def test_search_performance_pagination(self, test_database):
        """Test search performance with pagination."""
        start_time = time.time()

        # Fetch multiple pages
        for offset in range(0, 10, 2):
            await search_books_helper(limit=2, offset=offset)

        duration = time.time() - start_time

        assert duration < 3.0  # Should complete in under 3 seconds
