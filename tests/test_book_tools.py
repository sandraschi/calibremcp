"""
Tests for book-related tools in Calibre MCP.

Tests actual tool functions via FastMCP tool interface.
"""

import pytest
from unittest.mock import patch, MagicMock

# Import tools to trigger registration
from calibre_mcp.tools import book_tools  # noqa: F401

from calibre_mcp.server import mcp
from calibre_mcp.services.book_service import BookService

from tests.fixtures.test_data import SAMPLE_BOOKS


@pytest.fixture
def mock_book_service():
    """Create a properly configured mock book service."""
    service = MagicMock(spec=BookService)

    # Setup realistic return values matching actual service structure
    service.get_all.return_value = {
        "items": [
            {
                "id": book["id"],
                "title": book["title"],
                "authors": book["authors"],
                "tags": book.get("tags", []),
                "series": book.get("series"),
                "description": book.get("description", ""),
            }
            for book in SAMPLE_BOOKS
        ],
        "total": len(SAMPLE_BOOKS),
        "page": 1,
        "per_page": 50,
        "total_pages": 1,
    }

    service.get_by_id.return_value = {
        "id": SAMPLE_BOOKS[0]["id"],
        "title": SAMPLE_BOOKS[0]["title"],
        "authors": SAMPLE_BOOKS[0]["authors"],
    }

    return service


@pytest.mark.asyncio
async def test_search_books_tool_registered():
    """Test that search_books tool is registered with MCP server."""
    tools = await mcp.get_tools()

    # Verify tool exists
    assert "search_books" in tools, (
        f"search_books not found. Available tools: {list(tools.keys())[:10]}"
    )

    tool = tools["search_books"]
    assert tool is not None
    assert hasattr(tool, "run")


@pytest.mark.asyncio
async def test_search_books_basic(mock_book_service):
    """Test basic search_books functionality with mocked service."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        # Call the tool
        tool_result = await tool.run(arguments={"query": "Test Book"})
        result = tool_result.data

        # Verify structure
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "items" in result, f"Missing 'items' key. Keys: {list(result.keys())}"
        assert "total" in result
        assert "page" in result
        assert "per_page" in result
        assert "total_pages" in result

        # Verify service was called
        mock_book_service.get_all.assert_called_once()


@pytest.mark.asyncio
async def test_search_books_with_author_filter(mock_book_service):
    """Test search_books with author filter."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        result = await tool.run(arguments={"author": "Author 1"})
        data = result.data

        # Verify results structure
        assert "items" in data
        assert isinstance(data["items"], list)

        # Verify service was called with author filter
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert "author_name" in call_kwargs, (
            f"author_name not in call. Keys: {list(call_kwargs.keys())}"
        )
        assert call_kwargs["author_name"] == "Author 1"


@pytest.mark.asyncio
async def test_search_books_with_tag_filter(mock_book_service):
    """Test search_books with tag filter."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        await tool.run(arguments={"tag": "fiction"})

        # Verify service was called with tag filter
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert "tag_name" in call_kwargs
        assert call_kwargs["tag_name"] == "fiction"


@pytest.mark.asyncio
async def test_search_books_with_series_filter(mock_book_service):
    """Test search_books with series filter."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        await tool.run(arguments={"series": "Test Series 1"})

        # Verify service was called with series filter
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert "series_name" in call_kwargs
        assert call_kwargs["series_name"] == "Test Series 1"


@pytest.mark.asyncio
async def test_search_books_pagination_parameters(mock_book_service):
    """Test search_books pagination parameters are passed correctly."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        await tool.run(arguments={"query": "test", "limit": 10, "offset": 20})

        # Verify pagination parameters
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert call_kwargs["limit"] == 10
        assert call_kwargs["skip"] == 20


@pytest.mark.asyncio
async def test_search_books_combines_filters(mock_book_service):
    """Test search_books correctly combines multiple filters."""
    with patch("calibre_mcp.services.book_service.book_service", mock_book_service):
        tools = await mcp.get_tools()
        tool = tools["search_books"]

        await tool.run(
            arguments={
                "author": "Author 1",
                "tag": "fiction",
                "series": "Test Series 1",
                "min_rating": 4,
                "limit": 5,
            }
        )

        # Verify all filters were passed
        mock_book_service.get_all.assert_called_once()
        call_kwargs = mock_book_service.get_all.call_args[1]
        assert call_kwargs["author_name"] == "Author 1"
        assert call_kwargs["tag_name"] == "fiction"
        assert call_kwargs["series_name"] == "Test Series 1"
        assert call_kwargs["min_rating"] == 4
        assert call_kwargs["limit"] == 5


@pytest.mark.asyncio
async def test_search_books_empty_results():
    """Test search_books returns proper structure for empty results."""
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

        result = await tool.run(arguments={"query": "nonexistent"})
        data = result.data

        # Verify empty result structure
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["total_pages"] == 0
