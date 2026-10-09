"""
Unit tests for manage_files portmanteau tool.

Tests all 3 operations: convert, download, bulk
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.files.manage_files import manage_files


@pytest.fixture
def mock_file_helpers():
    """Mock the file helper functions."""
    with (
        patch("calibre_mcp.tools.files.file_operations.convert_book_format_helper") as convert,
        patch("calibre_mcp.tools.files.file_operations.download_book_helper") as download,
        patch("calibre_mcp.tools.files.file_operations.bulk_format_operations_helper") as bulk,
    ):
        convert.return_value = [{"book_id": 1, "format": "EPUB", "success": True}]

        download.return_value = {"book_id": 1, "format": "EPUB", "file_path": "/path/to/book.epub", "size": 1000000}

        bulk.return_value = {"processed": 10, "successful": 8, "failed": 2}

        yield {
            "convert": convert,
            "download": download,
            "bulk": bulk,
        }


@pytest.mark.asyncio
async def test_manage_files_convert(mock_file_helpers):
    """Test manage_files convert operation."""
    conversion_requests = [{"book_id": 1, "source_format": "PDF", "target_format": "EPUB"}]
    result = await manage_files(operation="convert", conversion_requests=conversion_requests)

    assert isinstance(result, list)
    assert result[0]["success"] is True
    mock_file_helpers["convert"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_files_download(mock_file_helpers):
    """Test manage_files download operation."""
    result = await manage_files(operation="download", book_id=1, format_preference="EPUB")

    assert result["book_id"] == 1
    assert result["format"] == "EPUB"
    assert "file_path" in result
    mock_file_helpers["download"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_files_bulk(mock_file_helpers):
    """Test manage_files bulk operation."""
    result = await manage_files(operation="bulk", operation_type="convert", target_format="EPUB", book_ids=[1, 2, 3])

    assert result["processed"] == 10
    assert result["successful"] == 8
    mock_file_helpers["bulk"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_files_invalid_operation():
    """Test manage_files with invalid operation."""
    result = await manage_files(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_files_missing_required_params():
    """Test manage_files with missing required parameters."""
    # Download operation requires book_id
    result = await manage_files(operation="download")

    assert "error" in result
    assert "book_id is required" in result["error"]

    # Convert operation requires conversion_requests
    result = await manage_files(operation="convert")

    assert "error" in result
    assert "conversion_requests is required" in result["error"]

    # Bulk operation requires operation_type
    result = await manage_files(operation="bulk")

    assert "error" in result
    assert "operation_type is required" in result["error"]
