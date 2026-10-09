"""
Unit tests for manage_smart_collections portmanteau tool.

Tests key operations: create, get, update, delete, list, query
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.advanced_features.manage_smart_collections import (
        manage_smart_collections,
    )


@pytest.fixture
def mock_collection_storage():
    """Mock the collection storage."""
    with patch("calibre_mcp.tools.advanced_features.manage_smart_collections._collections_storage", {}):
        yield


@pytest.mark.asyncio
async def test_manage_smart_collections_create(mock_collection_storage):
    """Test manage_smart_collections create operation."""
    collection_data = {
        "name": "Test Collection",
        "rules": [{"field": "tags", "operator": "contains", "value": "scifi"}],
    }
    result = await manage_smart_collections(operation="create", collection_data=collection_data)

    assert "collection_id" in result
    assert result["name"] == "Test Collection"


@pytest.mark.asyncio
async def test_manage_smart_collections_get(mock_collection_storage):
    """Test manage_smart_collections get operation."""
    # First create a collection
    collection_data = {
        "name": "Test Collection",
        "rules": [{"field": "tags", "operator": "contains", "value": "scifi"}],
    }
    create_result = await manage_smart_collections(operation="create", collection_data=collection_data)
    collection_id = create_result["collection_id"]

    # Then get it
    result = await manage_smart_collections(operation="get", collection_id=collection_id)

    assert result["name"] == "Test Collection"


@pytest.mark.asyncio
async def test_manage_smart_collections_list(mock_collection_storage):
    """Test manage_smart_collections list operation."""
    result = await manage_smart_collections(operation="list")

    assert "collections" in result
    assert isinstance(result["collections"], list)


@pytest.mark.asyncio
async def test_manage_smart_collections_invalid_operation():
    """Test manage_smart_collections with invalid operation."""
    result = await manage_smart_collections(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_smart_collections_missing_required_params():
    """Test manage_smart_collections with missing required parameters."""
    # Get operation requires collection_id
    result = await manage_smart_collections(operation="get")

    assert "error" in result
    assert "collection_id is required" in result["error"]

    # Create operation requires collection_data
    result = await manage_smart_collections(operation="create")

    assert "error" in result
    assert "collection_data is required" in result["error"]
