"""
Unit tests for query_books portmanteau tool.

Tests all operations: search, list, recent, by_author, by_series
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.book_management.query_books import query_books


@pytest.fixture
def mock_query_helpers():
    """Mock the helper functions."""
    from unittest.mock import MagicMock

    with (
        patch("calibre_mcp.tools.book_management.query_books._search_books_helper") as search,
        patch("calibre_mcp.tools.book_management.query_books._list_books_helper") as list_books,
        patch("calibre_mcp.tools.book_management.query_books._get_books_by_author_helper") as by_author,
        patch("calibre_mcp.tools.book_management.query_books._get_books_by_series_helper") as by_series,
        patch("calibre_mcp.services.book_service.book_service") as book_service,
    ):
        search.return_value = {
            "results": [
                {"id": 1, "title": "Book 1", "authors": ["Author 1"]},
                {"id": 2, "title": "Book 2", "authors": ["Author 2"]},
            ],
            "total": 2,
            "page": 1,
            "per_page": 50,
        }

        list_books.return_value = {"items": [{"id": 1, "title": "Book 1"}, {"id": 2, "title": "Book 2"}], "total": 2}

        by_author.return_value = {"items": [{"id": 1, "title": "Book 1", "authors": ["Author 1"]}], "total": 1}

        by_series.return_value = {"items": [{"id": 1, "title": "Book 1", "series": "Series 1"}], "total": 1}

        # Mock book_service.get_recent_books for recent operation
        mock_book = MagicMock()
        mock_book.dict.return_value = {"id": 1, "title": "Recent Book 1", "authors": ["Author 1"]}
        book_service.get_recent_books.return_value = [mock_book]

        yield {
            "search": search,
            "list": list_books,
            "by_author": by_author,
            "by_series": by_series,
            "book_service": book_service,
        }


@pytest.mark.asyncio
async def test_query_books_search(mock_query_helpers):
    """Test query_books search operation."""
    result = await query_books(operation="search", text="python", limit=10)

    assert "results" in result
    assert result["total"] == 2
    assert len(result["results"]) == 2
    mock_query_helpers["search"].assert_called_once()


@pytest.mark.asyncio
async def test_query_books_search_by_author(mock_query_helpers):
    """Test query_books search by author."""
    result = await query_books(operation="search", author="Conan Doyle", limit=10)

    assert "results" in result
    mock_query_helpers["search"].assert_called_once()


@pytest.mark.asyncio
async def test_query_books_list(mock_query_helpers):
    """Test query_books list operation."""
    result = await query_books(operation="list", limit=50)

    assert "items" in result
    assert result["total"] == 2
    mock_query_helpers["list"].assert_called_once()


@pytest.mark.asyncio
async def test_query_books_by_author(mock_query_helpers):
    """Test query_books by_author operation."""
    result = await query_books(operation="by_author", author_id=1, limit=10)

    assert "items" in result
    assert result["total"] == 1
    mock_query_helpers["by_author"].assert_called_once()


@pytest.mark.asyncio
async def test_query_books_by_series(mock_query_helpers):
    """Test query_books by_series operation."""
    result = await query_books(operation="by_series", series_id=1, limit=10)

    assert "items" in result
    assert result["total"] == 1
    mock_query_helpers["by_series"].assert_called_once()


@pytest.mark.asyncio
async def test_query_books_recent(mock_query_helpers):
    """Test query_books recent operation."""
    result = await query_books(operation="recent", limit=10)

    assert "success" in result
    assert result["success"] is True
    assert "books" in result
    assert result["total"] == 1
    assert len(result["books"]) == 1
    # Verify book_service.get_recent_books was called
    assert mock_query_helpers["book_service"].get_recent_books.called
    mock_query_helpers["book_service"].get_recent_books.assert_called_once_with(limit=10)


@pytest.mark.asyncio
async def test_query_books_invalid_operation():
    """Test query_books with invalid operation."""
    result = await query_books(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_query_books_missing_required_params():
    """Test query_books with missing required parameters."""
    # by_author requires author_id
    result = await query_books(operation="by_author")

    assert "error" in result
    assert "author_id is required" in result["error"]

    # by_series requires series_id
    result = await query_books(operation="by_series")

    assert "error" in result
    assert "series_id is required" in result["error"]


@pytest.mark.asyncio
async def test_query_books_recent_with_custom_limit(mock_query_helpers):
    """Test query_books recent operation with custom limit."""
    result = await query_books(operation="recent", limit=5)

    assert "success" in result
    assert result["success"] is True
    assert result["limit"] == 5
    mock_query_helpers["book_service"].get_recent_books.assert_called_once_with(limit=5)
