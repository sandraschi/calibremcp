"""
Unit tests for manage_libraries portmanteau tool.

Tests all operations: list, switch, stats, search
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.library.manage_libraries import manage_libraries


@pytest.fixture
def mock_library_operations():
    """Mock library operations."""
    from unittest.mock import MagicMock

    with (
        patch("calibre_mcp.tools.library.library_management.list_libraries_helper") as list_libs,
        patch("calibre_mcp.tools.library.library_management.switch_library_helper") as switch,
        patch("calibre_mcp.tools.library.library_management.get_library_stats_helper") as stats,
        patch("calibre_mcp.tools.library.library_management.cross_library_search_helper") as search,
    ):
        # Mock Pydantic model response for list_libraries
        mock_list_response = MagicMock()
        mock_list_response.model_dump.return_value = {
            "libraries": [
                {"name": "Main Library", "path": "/path/to/main", "book_count": 100, "is_active": True},
                {"name": "Secondary Library", "path": "/path/to/secondary", "book_count": 50, "is_active": False},
            ],
            "current_library": "Main Library",
            "total_libraries": 2,
        }
        list_libs.return_value = mock_list_response

        switch.return_value = {
            "success": True,
            "library_name": "Secondary Library",
            "library_path": "/path/to/secondary",
            "message": "Switched to Secondary Library",
        }

        # Mock Pydantic model response for stats
        mock_stats_response = MagicMock()
        mock_stats_response.model_dump.return_value = {
            "library_name": "Main Library",
            "total_books": 100,
            "total_authors": 50,
            "total_series": 10,
            "format_distribution": {"EPUB": 80, "PDF": 20},
        }
        stats.return_value = mock_stats_response

        # Mock Pydantic model response for search
        mock_search_response = MagicMock()
        mock_search_response.model_dump.return_value = {
            "results": [
                {"id": 1, "title": "Book 1", "library_name": "Main Library"},
                {"id": 2, "title": "Book 2", "library_name": "Secondary Library"},
            ],
            "total_found": 2,
            "query_used": "python",
        }
        search.return_value = mock_search_response

        yield {
            "list": list_libs,
            "switch": switch,
            "stats": stats,
            "search": search,
            "list_response": mock_list_response,
            "stats_response": mock_stats_response,
            "search_response": mock_search_response,
        }


@pytest.mark.asyncio
async def test_manage_libraries_list(mock_library_operations):
    """Test manage_libraries list operation."""
    result = await manage_libraries(operation="list")

    assert "libraries" in result
    assert result["total_libraries"] == 2
    assert len(result["libraries"]) == 2
    mock_library_operations["list"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_libraries_switch(mock_library_operations):
    """Test manage_libraries switch operation."""
    result = await manage_libraries(operation="switch", library_name="Secondary Library")

    assert result["success"] is True
    assert result["library_name"] == "Secondary Library"
    mock_library_operations["switch"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_libraries_stats(mock_library_operations):
    """Test manage_libraries stats operation."""
    result = await manage_libraries(operation="stats", library_name="Main Library")

    assert result["library_name"] == "Main Library"
    assert result["total_books"] == 100
    mock_library_operations["stats"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_libraries_search(mock_library_operations):
    """Test manage_libraries search operation."""
    result = await manage_libraries(operation="search", query="python")

    assert "results" in result
    assert result["total_found"] == 2
    mock_library_operations["search"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_libraries_invalid_operation():
    """Test manage_libraries with invalid operation."""
    result = await manage_libraries(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_libraries_missing_required_params():
    """Test manage_libraries with missing required parameters."""
    # switch requires library_name
    result = await manage_libraries(operation="switch")

    assert "error" in result
    assert "library_name is required" in result["error"]

    # search requires query
    result = await manage_libraries(operation="search")

    assert "error" in result
    assert "query is required" in result["error"]
