"""
Tests for search functionality in Calibre MCP.

Tests the actual search_books tool via FastMCP interface.
"""

import pytest
from unittest.mock import MagicMock, patch

# Import tools to trigger registration
from calibre_mcp.tools import book_tools  # noqa: F401

from calibre_mcp.server import mcp
from calibre_mcp.services.book_service import BookService
from tests.fixtures.test_data import SAMPLE_BOOKS


@pytest.fixture
def mock_book_service():
    """Create a properly configured mock book service."""
    service = MagicMock(spec=BookService)

    # Setup mock responses with actual data structure
    service.get_all.return_value = {
        "items": [
            {
                "id": book["id"],
                "title": book["title"],
                "authors": book["authors"],
                "tags": book.get("tags", []),
                "series": book.get("series"),
                "comments": book.get("comments", ""),
                "publisher": book.get("publisher"),
            }
            for book in SAMPLE_BOOKS
        ],
        "total": len(SAMPLE_BOOKS),
        "page": 1,
        "per_page": 50,
        "total_pages": 1,
    }

    return service


@pytest.mark.asyncio
async def test_search_by_title(mock_book_service):
    """Test searching books by title."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        result = await tool.run(arguments={"text": "Python Programming"})
        data = result.data

        # Verify the service was called with the correct parameters
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert "search" in call_kwargs or "query" in str(call_kwargs)

        # Verify the results
        assert len(data["items"]) > 0
        assert any("Python" in item.get("title", "") for item in data["items"])


@pytest.mark.asyncio
async def test_search_by_author(mock_book_service):
    """Test searching books by author."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        result = await tool.run(arguments={"author": "John Doe"})
        data = result.data

        # Verify the service was called with the correct parameters
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert "author_name" in call_kwargs
        assert call_kwargs["author_name"] == "John Doe"

        # Verify the results
        assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_search_by_tag(mock_book_service):
    """Test searching books by tag."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        result = await tool.run(arguments={"tag": "python"})
        data = result.data

        # Verify the service was called with the correct parameters
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert "tag_name" in call_kwargs
        assert call_kwargs["tag_name"] == "python"

        # Verify the results
        assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_search_by_comment(mock_book_service):
    """Test searching books by comment content."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        result = await tool.run(arguments={"comment": "comprehensive guide"})
        data = result.data

        # Verify the service was called with the correct parameters
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert "comment" in call_kwargs
        assert "comprehensive guide" in call_kwargs["comment"]

        # Verify the results
        assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_search_combined_filters(mock_book_service):
    """Test searching with multiple filters."""
    from datetime import datetime, timedelta

    # Define date ranges
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        await tool.run(
            arguments={
                "text": "Python",
                "author": "John Doe",
                "tag": "programming",
                "pubdate_start": start_date,
                "pubdate_end": end_date,
                "added_after": start_date,
                "added_before": end_date,
                "min_size": 1024,
                "max_size": 10485760,
                "formats": ["EPUB", "PDF"],
            }
        )

        # Verify the service was called with the correct parameters
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert "search" in call_kwargs or "Python" in str(call_kwargs)
        assert call_kwargs["author_name"] == "John Doe"
        assert call_kwargs["tag_name"] == "programming"
        assert "pubdate_start" in call_kwargs
        assert "min_size" in call_kwargs


@pytest.mark.asyncio
async def test_search_by_date_ranges(mock_book_service):
    """Test searching by publication date and entry date ranges."""
    from datetime import datetime, timedelta

    # Define date ranges
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        # Test publication date range
        await tool.run(arguments={"pubdate_start": start_date, "pubdate_end": end_date})

        # Verify publication date filter
        mock_book_service.get_all.assert_called()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert "pubdate_start" in call_kwargs
        assert "pubdate_end" in call_kwargs


@pytest.mark.asyncio
async def test_search_by_size_range(mock_book_service):
    """Test searching by file size range."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        # Test minimum size
        await tool.run(arguments={"min_size": 1048576})
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert call_kwargs["min_size"] == 1048576

        # Test maximum size
        await tool.run(arguments={"max_size": 5242880})
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert call_kwargs["max_size"] == 5242880


@pytest.mark.asyncio
async def test_search_by_file_type(mock_book_service):
    """Test searching by file format."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        # Test single format
        await tool.run(arguments={"formats": ["EPUB"]})
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert call_kwargs["formats"] == ["EPUB"]

        # Test multiple formats
        await tool.run(arguments={"formats": ["EPUB", "PDF", "MOBI"]})
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert "EPUB" in call_kwargs["formats"]
        assert "PDF" in call_kwargs["formats"]


@pytest.mark.asyncio
async def test_search_by_rating(mock_book_service):
    """Test filtering books by star rating."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        # Test exact rating
        await tool.run(arguments={"rating": 5})
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert call_kwargs["rating"] == 5

        # Test minimum rating
        await tool.run(arguments={"min_rating": 4})
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert call_kwargs["min_rating"] == 4


@pytest.mark.asyncio
async def test_search_pagination(mock_book_service):
    """Test search results pagination."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        result = await tool.run(arguments={"text": "Python", "limit": 1, "offset": 1})
        data = result.data

        # Verify the service was called with the correct pagination parameters
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert call_kwargs["limit"] == 1
        assert call_kwargs["skip"] == 1

        # Verify pagination metadata
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data


@pytest.mark.asyncio
async def test_search_empty_results():
    """Test search with no results."""
    empty_service = MagicMock(spec=BookService)
    empty_service.get_all.return_value = {
        "items": [],
        "total": 0,
        "page": 1,
        "per_page": 50,
        "total_pages": 0,
    }

    with patch("calibre_mcp.services.book_service.book_service", empty_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        result = await tool.run(arguments={"text": "Nonexistent Book"})
        data = result.data

        # Verify the results
        assert len(data["items"]) == 0
        assert data["total"] == 0
