"""
Unit tests for manage_tags portmanteau tool.

Tests all 10 operations: list, get, create, update, delete, find_duplicates,
merge, get_unused, delete_unused, statistics
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.tags.manage_tags import manage_tags


@pytest.fixture
def mock_tag_helpers():
    """Mock the tag helper functions."""
    with (
        patch("calibre_mcp.tools.tags.manage_tags.list_tags_helper") as list_tags,
        patch("calibre_mcp.tools.tags.manage_tags.get_tag_helper") as get_tag,
        patch("calibre_mcp.tools.tags.manage_tags.create_tag_helper") as create_tag,
        patch("calibre_mcp.tools.tags.manage_tags.update_tag_helper") as update_tag,
        patch("calibre_mcp.tools.tags.manage_tags.delete_tag_helper") as delete_tag,
        patch("calibre_mcp.tools.tags.manage_tags.find_duplicate_tags_helper") as find_dups,
        patch("calibre_mcp.tools.tags.manage_tags.merge_tags_helper") as merge_tags,
        patch("calibre_mcp.tools.tags.manage_tags.get_unused_tags_helper") as get_unused,
        patch("calibre_mcp.tools.tags.manage_tags.delete_unused_tags_helper") as delete_unused,
        patch("calibre_mcp.tools.tags.manage_tags.get_tag_statistics_helper") as stats,
    ):
        list_tags.return_value = {"items": [{"id": 1, "name": "mystery", "book_count": 10}], "total": 1}

        get_tag.return_value = {"id": 1, "name": "mystery", "book_count": 10}

        create_tag.return_value = {"id": 2, "name": "New Tag", "book_count": 0}

        update_tag.return_value = {"id": 1, "name": "Updated Tag", "book_count": 10}

        delete_tag.return_value = {"success": True}

        find_dups.return_value = {"duplicate_groups": [], "total_duplicates": 0}

        merge_tags.return_value = {"success": True, "target_tag": {"id": 1, "name": "merged", "book_count": 20}}

        get_unused.return_value = {"unused_tags": [{"id": 3, "name": "unused", "book_count": 0}], "count": 1}

        delete_unused.return_value = {"success": True, "deleted_count": 1}

        stats.return_value = {"total_tags": 100, "unused_tags_count": 5}

        yield {
            "list": list_tags,
            "get": get_tag,
            "create": create_tag,
            "update": update_tag,
            "delete": delete_tag,
            "find_duplicates": find_dups,
            "merge": merge_tags,
            "get_unused": get_unused,
            "delete_unused": delete_unused,
            "statistics": stats,
        }


@pytest.mark.asyncio
async def test_manage_tags_list(mock_tag_helpers):
    """Test manage_tags list operation."""
    result = await manage_tags(operation="list", limit=10)

    assert "items" in result
    assert result["total"] == 1
    mock_tag_helpers["list"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_tags_get(mock_tag_helpers):
    """Test manage_tags get operation."""
    result = await manage_tags(operation="get", tag_id=1)

    assert result["id"] == 1
    assert result["name"] == "mystery"
    mock_tag_helpers["get"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_tags_create(mock_tag_helpers):
    """Test manage_tags create operation."""
    result = await manage_tags(operation="create", name="New Tag")

    assert result["id"] == 2
    assert result["name"] == "New Tag"
    mock_tag_helpers["create"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_tags_update(mock_tag_helpers):
    """Test manage_tags update operation."""
    result = await manage_tags(operation="update", tag_id=1, new_name="Updated Tag")

    assert result["name"] == "Updated Tag"
    mock_tag_helpers["update"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_tags_delete(mock_tag_helpers):
    """Test manage_tags delete operation."""
    result = await manage_tags(operation="delete", tag_id=1)

    assert result["success"] is True
    mock_tag_helpers["delete"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_tags_find_duplicates(mock_tag_helpers):
    """Test manage_tags find_duplicates operation."""
    result = await manage_tags(operation="find_duplicates", similarity_threshold=0.8)

    assert "duplicate_groups" in result
    mock_tag_helpers["find_duplicates"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_tags_merge(mock_tag_helpers):
    """Test manage_tags merge operation."""
    result = await manage_tags(operation="merge", source_tag_ids=[2, 3], target_tag_id=1)

    assert result["success"] is True
    mock_tag_helpers["merge"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_tags_get_unused(mock_tag_helpers):
    """Test manage_tags get_unused operation."""
    result = await manage_tags(operation="get_unused")

    assert "unused_tags" in result
    assert result["count"] == 1
    mock_tag_helpers["get_unused"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_tags_delete_unused(mock_tag_helpers):
    """Test manage_tags delete_unused operation."""
    result = await manage_tags(operation="delete_unused")

    assert result["success"] is True
    assert result["deleted_count"] == 1
    mock_tag_helpers["delete_unused"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_tags_statistics(mock_tag_helpers):
    """Test manage_tags statistics operation."""
    result = await manage_tags(operation="statistics")

    assert result["total_tags"] == 100
    mock_tag_helpers["statistics"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_tags_invalid_operation():
    """Test manage_tags with invalid operation."""
    result = await manage_tags(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_tags_missing_required_params():
    """Test manage_tags with missing required parameters."""
    # Get operation requires tag_id or tag_name
    result = await manage_tags(operation="get")

    assert "error" in result
    assert "tag_id or tag_name is required" in result["error"]

    # Create operation requires name
    result = await manage_tags(operation="create")

    assert "error" in result
    assert "name is required" in result["error"]
