"""Test the open_book_file tool with fixture books."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from calibre_mcp.tools.viewer_tools import ViewerTools
from calibre_mcp.server import mcp


@pytest.fixture
def mock_book_file(tmp_path):
    """Create a mock book file for testing."""
    # Create a test PDF file
    test_file = tmp_path / "test_book.pdf"
    test_file.write_bytes(b"fake pdf content")
    return str(test_file)


@pytest.fixture
def viewer_tools():
    """Create ViewerTools instance."""
    return ViewerTools(mcp)


@pytest.mark.asyncio
async def test_open_book_file_success(viewer_tools, mock_book_file):
    """Test open_book_file with existing file."""
    result = await viewer_tools.open_book_file(book_id=123, file_path=mock_book_file)

    assert result["success"] is True
    assert "message" in result
    assert result["file_path"] == mock_book_file


@pytest.mark.asyncio
async def test_open_book_file_not_found(viewer_tools):
    """Test open_book_file with non-existent file."""
    non_existent = "/nonexistent/path/book.epub"

    result = await viewer_tools.open_book_file(book_id=123, file_path=non_existent)

    assert result["success"] is False
    assert "error" in result or "message" in result


@pytest.mark.asyncio
async def test_open_book_file_with_formats(viewer_tools, mock_book_file):
    """Test open_book_file when file_path is missing but formats are available."""
    # Mock book_service to return formats
    with patch("calibre_mcp.tools.viewer_tools.book_service") as mock_service:
        mock_service.get_by_id.return_value = {
            "formats": [
                {"format": "PDF", "path": mock_book_file},
                {"format": "EPUB", "path": str(Path(mock_book_file).with_suffix(".epub"))},
            ]
        }

        # Test with no file_path
        result = await viewer_tools.open_book_file(book_id=123, file_path="")

        # Should find PDF format
        assert result["success"] is True


@pytest.mark.asyncio
async def test_open_book_file_platform_macos(viewer_tools, mock_book_file):
    """Test open_book_file uses correct platform command on macOS."""
    with patch("platform.system", return_value="Darwin"):
        with patch("subprocess.run") as mock_subprocess:
            result = await viewer_tools.open_book_file(book_id=123, file_path=mock_book_file)

            assert result["success"] is True
            mock_subprocess.assert_called_once()
            # Should call with "open" command
            assert mock_subprocess.call_args[0][0][0] == "open"
