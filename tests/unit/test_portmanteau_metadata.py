"""
Unit tests for manage_metadata portmanteau tool.

Tests all 3 operations: update, organize_tags, fix_issues
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.metadata.manage_metadata import manage_metadata


@pytest.fixture
def mock_metadata_helpers():
    """Mock the metadata helper functions."""
    with (
        patch("calibre_mcp.tools.metadata.metadata_management.update_book_metadata_helper") as update,
        patch("calibre_mcp.tools.metadata.metadata_management.auto_organize_tags_helper") as organize,
        patch("calibre_mcp.tools.metadata.metadata_management.fix_metadata_issues_helper") as fix,
    ):
        update.return_value = {"updated_books": [1, 2], "failed_updates": [], "success_count": 2}

        organize.return_value = {"total_tags": 100, "duplicate_groups": []}

        fix.return_value = {"updated_books": [1, 2, 3], "success_count": 3}

        yield {
            "update": update,
            "organize": organize,
            "fix": fix,
        }


@pytest.mark.asyncio
async def test_manage_metadata_update(mock_metadata_helpers):
    """Test manage_metadata update operation."""
    updates = [{"book_id": 1, "field": "title", "value": "New Title"}]
    result = await manage_metadata(operation="update", updates=updates)

    assert result["success_count"] == 2
    assert len(result["updated_books"]) == 2
    mock_metadata_helpers["update"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_metadata_organize_tags(mock_metadata_helpers):
    """Test manage_metadata organize_tags operation."""
    result = await manage_metadata(operation="organize_tags")

    assert result["total_tags"] == 100
    mock_metadata_helpers["organize"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_metadata_fix_issues(mock_metadata_helpers):
    """Test manage_metadata fix_issues operation."""
    result = await manage_metadata(operation="fix_issues")

    assert result["success_count"] == 3
    mock_metadata_helpers["fix"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_metadata_invalid_operation():
    """Test manage_metadata with invalid operation."""
    result = await manage_metadata(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_metadata_missing_required_params():
    """Test manage_metadata with missing required parameters."""
    # Update operation requires updates
    result = await manage_metadata(operation="update")

    assert "error" in result
    assert "updates is required" in result["error"]
