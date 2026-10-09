"""
Unit tests for manage_bulk_operations portmanteau tool.

Tests all 4 operations: update_metadata, export, delete, convert
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.advanced_features.manage_bulk_operations import (
        manage_bulk_operations,
    )


@pytest.fixture
def mock_bulk_helpers():
    """Mock the bulk operations helper functions."""
    with (
        patch("calibre_mcp.tools.advanced_features.manage_bulk_operations.update_metadata_helper") as update,
        patch("calibre_mcp.tools.advanced_features.manage_bulk_operations.export_helper") as export,
        patch("calibre_mcp.tools.advanced_features.manage_bulk_operations.delete_helper") as delete,
        patch("calibre_mcp.tools.advanced_features.manage_bulk_operations.convert_helper") as convert,
    ):
        update.return_value = {"updated_books": [1, 2, 3], "success_count": 3}

        export.return_value = {"exported_books": 5, "export_path": "/path/to/export"}

        delete.return_value = {"deleted_books": [1, 2], "success_count": 2}

        convert.return_value = {"converted_books": [1, 2, 3], "success_count": 3}

        yield {
            "update": update,
            "export": export,
            "delete": delete,
            "convert": convert,
        }


@pytest.mark.asyncio
async def test_manage_bulk_operations_update_metadata(mock_bulk_helpers):
    """Test manage_bulk_operations update_metadata operation."""
    result = await manage_bulk_operations(operation="update_metadata", book_ids=[1, 2, 3], updates={"rating": 5})

    assert result["success_count"] == 3
    mock_bulk_helpers["update"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_bulk_operations_export(mock_bulk_helpers):
    """Test manage_bulk_operations export operation."""
    result = await manage_bulk_operations(operation="export", book_ids=[1, 2, 3], export_path="/path/to/export")

    assert result["exported_books"] == 5
    mock_bulk_helpers["export"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_bulk_operations_delete(mock_bulk_helpers):
    """Test manage_bulk_operations delete operation."""
    result = await manage_bulk_operations(operation="delete", book_ids=[1, 2])

    assert result["success_count"] == 2
    mock_bulk_helpers["delete"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_bulk_operations_convert(mock_bulk_helpers):
    """Test manage_bulk_operations convert operation."""
    result = await manage_bulk_operations(operation="convert", book_ids=[1, 2, 3], target_format="EPUB")

    assert result["success_count"] == 3
    mock_bulk_helpers["convert"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_bulk_operations_invalid_operation():
    """Test manage_bulk_operations with invalid operation."""
    result = await manage_bulk_operations(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_bulk_operations_missing_required_params():
    """Test manage_bulk_operations with missing required parameters."""
    # All operations require book_ids
    result = await manage_bulk_operations(operation="update_metadata")

    assert "error" in result
    assert "book_ids is required" in result["error"]
