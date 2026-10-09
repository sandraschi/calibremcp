"""
Unit tests for manage_books portmanteau tool.

Tests all operations: add, get, details, update, delete
"""

from unittest.mock import MagicMock, patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.book_management.manage_books import manage_books


@pytest.fixture
def mock_book_helpers():
    """Mock the helper functions."""
    with (
        patch("calibre_mcp.tools.book_management.manage_books.add_book_helper") as add,
        patch("calibre_mcp.tools.book_management.manage_books.get_book_helper") as get,
        patch("calibre_mcp.tools.book_management.manage_books.update_book_helper") as update,
        patch("calibre_mcp.tools.book_management.manage_books.delete_book_helper") as delete,
        patch("calibre_mcp.server.get_api_client") as get_client,
    ):
        add.return_value = {
            "id": "123",
            "title": "Test Book",
            "authors": [{"name": "Test Author"}],
            "formats": ["EPUB"],
        }

        get.return_value = {"id": "123", "title": "Test Book", "authors": [{"name": "Test Author"}], "has_cover": True}

        update.return_value = {"success": True, "book_id": "123", "updated_fields": ["title", "rating"]}

        delete.return_value = {"success": True, "book_id": "123", "message": "Book deleted successfully"}

        # Mock client for details operation
        from unittest.mock import AsyncMock

        mock_client = AsyncMock()
        mock_client.get_book_details.return_value = {
            "title": "Test Book",
            "authors": ["Test Author"],
            "formats": ["EPUB", "PDF"],
            "tags": ["fiction"],
            "series": "Test Series",
            "series_index": 1.0,
            "rating": 5,
            "comments": "Test comments",
            "published": "2024-01-01",
            "languages": ["en"],
            "identifiers": {"isbn": "1234567890"},
            "last_modified": "2024-01-01T00:00:00",
            "cover_url": "http://example.com/cover.jpg",
            "download_links": {"epub": "http://example.com/book.epub"},
        }
        get_client.return_value = mock_client

        yield {
            "add": add,
            "get": get,
            "update": update,
            "delete": delete,
            "get_client": get_client,
            "client": mock_client,
        }


@pytest.mark.asyncio
async def test_manage_books_add(mock_book_helpers):
    """Test manage_books add operation."""
    result = await manage_books(operation="add", file_path="/path/to/book.epub", metadata={"title": "Test Book"})

    assert result["id"] == "123"
    assert result["title"] == "Test Book"
    mock_book_helpers["add"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_books_get(mock_book_helpers):
    """Test manage_books get operation."""
    result = await manage_books(operation="get", book_id="123", include_metadata=True)

    assert result["id"] == "123"
    assert result["title"] == "Test Book"
    mock_book_helpers["get"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_books_details(mock_book_helpers):
    """Test manage_books details operation."""
    with (
        patch("calibre_mcp.server.current_library", return_value="test_library"),
        patch("calibre_mcp.server.BookDetailResponse") as BookDetailResponse,
    ):
        # Mock BookDetailResponse
        mock_response = MagicMock()
        mock_response.dict.return_value = {
            "book_id": 123,
            "title": "Test Book",
            "authors": ["Test Author"],
            "formats": ["EPUB", "PDF"],
        }
        BookDetailResponse.return_value = mock_response

        result = await manage_books(operation="details", book_id="123")

        assert result["success"] is True
        assert "book" in result
        # Verify get_api_client was called
        assert mock_book_helpers["get_client"].called
        # Verify client.get_book_details was called
        assert mock_book_helpers["client"].get_book_details.called


@pytest.mark.asyncio
async def test_manage_books_update(mock_book_helpers):
    """Test manage_books update operation."""
    result = await manage_books(operation="update", book_id="123", metadata={"title": "Updated Title", "rating": 5})

    assert result["success"] is True
    assert result["book_id"] == "123"
    mock_book_helpers["update"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_books_delete(mock_book_helpers):
    """Test manage_books delete operation."""
    result = await manage_books(operation="delete", book_id="123", delete_files=True)

    assert result["success"] is True
    assert result["book_id"] == "123"
    mock_book_helpers["delete"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_books_invalid_operation():
    """Test manage_books with invalid operation."""
    result = await manage_books(operation="invalid")

    assert result.get("success") is False
    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_books_missing_required_params():
    """Test manage_books with missing required parameters."""
    # Add operation requires file_path
    result = await manage_books(operation="add")

    assert result.get("success") is False
    assert "error" in result
    assert "file_path is required" in result["error"]

    # Get operation requires book_id
    result = await manage_books(operation="get")

    assert result.get("success") is False
    assert "error" in result
    assert "book_id is required" in result["error"]

    # Details operation requires book_id
    result = await manage_books(operation="details")

    assert result.get("success") is False
    assert "error" in result
    assert "book_id is required" in result["error"]
