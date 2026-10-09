"""
Unit tests for manage_viewer portmanteau tool.

Tests all operations: open_book, get_page, get_metadata, get_state, update_state, close_viewer, open_book_file
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.viewer.manage_viewer import manage_viewer


@pytest.fixture
def mock_viewer_helpers():
    """Mock the viewer helper functions."""
    with (
        patch("calibre_mcp.tools.viewer.manage_viewer.open_book_helper") as open_book,
        patch("calibre_mcp.tools.viewer.manage_viewer.get_page_helper") as get_page,
        patch("calibre_mcp.tools.viewer.manage_viewer.get_metadata_helper") as get_metadata,
        patch("calibre_mcp.tools.viewer.manage_viewer.get_state_helper") as get_state,
        patch("calibre_mcp.tools.viewer.manage_viewer.update_state_helper") as update_state,
        patch("calibre_mcp.tools.viewer.manage_viewer.close_viewer_helper") as close_viewer,
        patch("calibre_mcp.tools.viewer.manage_viewer.open_book_file_helper") as open_file,
    ):
        open_book.return_value = {
            "success": True,
            "file_path": "/path/to/book.epub",
            "metadata": {"title": "Test Book"},
        }

        get_page.return_value = {"page_number": 1, "content": "Page content here", "total_pages": 100}

        get_metadata.return_value = {"title": "Test Book", "author": "Test Author", "format": "EPUB"}

        get_state.return_value = {"current_page": 1, "total_pages": 100, "reading_direction": "ltr"}

        update_state.return_value = {"success": True, "current_page": 2}

        close_viewer.return_value = {"success": True, "message": "Viewer closed"}

        open_file.return_value = {"success": True, "file_path": "/path/to/book.epub"}

        yield {
            "open_book": open_book,
            "get_page": get_page,
            "get_metadata": get_metadata,
            "get_state": get_state,
            "update_state": update_state,
            "close_viewer": close_viewer,
            "open_file": open_file,
        }


@pytest.mark.asyncio
async def test_manage_viewer_open_book(mock_viewer_helpers):
    """Test manage_viewer open_book operation."""
    result = await manage_viewer(operation="open_book", file_path="/path/to/book.epub")

    assert result["success"] is True
    assert "file_path" in result
    mock_viewer_helpers["open_book"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_viewer_get_page(mock_viewer_helpers):
    """Test manage_viewer get_page operation."""
    result = await manage_viewer(operation="get_page", file_path="/path/to/book.epub", page_number=1)

    assert "page_number" in result
    assert result["page_number"] == 1
    mock_viewer_helpers["get_page"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_viewer_get_metadata(mock_viewer_helpers):
    """Test manage_viewer get_metadata operation."""
    result = await manage_viewer(operation="get_metadata", file_path="/path/to/book.epub")

    assert "title" in result
    mock_viewer_helpers["get_metadata"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_viewer_get_state(mock_viewer_helpers):
    """Test manage_viewer get_state operation."""
    result = await manage_viewer(operation="get_state", file_path="/path/to/book.epub")

    assert "current_page" in result
    mock_viewer_helpers["get_state"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_viewer_update_state(mock_viewer_helpers):
    """Test manage_viewer update_state operation."""
    result = await manage_viewer(operation="update_state", file_path="/path/to/book.epub", current_page=2)

    assert result["success"] is True
    mock_viewer_helpers["update_state"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_viewer_close_viewer(mock_viewer_helpers):
    """Test manage_viewer close_viewer operation."""
    result = await manage_viewer(operation="close_viewer", file_path="/path/to/book.epub")

    assert result["success"] is True
    mock_viewer_helpers["close_viewer"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_viewer_open_book_file(mock_viewer_helpers):
    """Test manage_viewer open_book_file operation."""
    result = await manage_viewer(operation="open_book_file", file_path="/path/to/book.epub")

    assert result["success"] is True
    mock_viewer_helpers["open_file"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_viewer_invalid_operation():
    """Test manage_viewer with invalid operation."""
    result = await manage_viewer(operation="invalid", book_id=123, file_path="/path/to/book.epub")

    assert "error" in result
    assert "Invalid operation" in result["error"]
