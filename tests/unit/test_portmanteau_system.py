"""
Unit tests for manage_system portmanteau tool.

Tests all 6 operations: help, status, tool_help, list_tools, hello_world, health_check
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.system.manage_system import manage_system


@pytest.fixture
def mock_system_helpers():
    """Mock the system helper functions."""
    with (
        patch("calibre_mcp.tools.system.manage_system.system_tools.help_helper") as help_func,
        patch("calibre_mcp.tools.system.manage_system.system_tools.status_helper") as status_func,
        patch("calibre_mcp.tools.system.manage_system.system_tools.tool_help_helper") as tool_help,
        patch("calibre_mcp.tools.system.manage_system.system_tools.list_tools_helper") as list_tools,
        patch("calibre_mcp.tools.system.manage_system.system_tools.hello_world_helper") as hello,
        patch("calibre_mcp.tools.system.manage_system.system_tools.health_check_helper") as health,
    ):
        help_func.return_value = {"content": "Help content here", "level": "basic"}

        status_func.return_value = {"status": "healthy", "tools_count": 17}

        tool_help.return_value = {"tool_name": "manage_books", "help": "Tool help content"}

        list_tools.return_value = {"tools": [{"name": "manage_books", "description": "..."}], "total": 17}

        hello.return_value = {"message": "Hello, World! The CalibreMCP server is working correctly."}

        health.return_value = {"status": "healthy", "checks": {"calibre": True, "library": True}}

        yield {
            "help": help_func,
            "status": status_func,
            "tool_help": tool_help,
            "list_tools": list_tools,
            "hello": hello,
            "health": health,
        }


@pytest.mark.asyncio
async def test_manage_system_help(mock_system_helpers):
    """Test manage_system help operation."""
    result = await manage_system(operation="help", level="basic")

    assert "content" in result
    mock_system_helpers["help"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_system_status(mock_system_helpers):
    """Test manage_system status operation."""
    result = await manage_system(operation="status", status_level="basic")

    assert result["content"]["status"] == "healthy"
    mock_system_helpers["status"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_system_tool_help(mock_system_helpers):
    """Test manage_system tool_help operation."""
    result = await manage_system(operation="tool_help", tool_name="manage_books")

    assert result["tool_name"] == "manage_books"
    mock_system_helpers["tool_help"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_system_list_tools(mock_system_helpers):
    """Test manage_system list_tools operation."""
    result = await manage_system(operation="list_tools")

    assert "tools" in result
    assert result["total"] == 17
    mock_system_helpers["list_tools"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_system_hello_world(mock_system_helpers):
    """Test manage_system hello_world operation."""
    result = await manage_system(operation="hello_world")

    assert "message" in result
    assert "Hello" in result["message"]
    mock_system_helpers["hello"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_system_health_check(mock_system_helpers):
    """Test manage_system health_check operation."""
    result = await manage_system(operation="health_check")

    assert result["status"] == "healthy"
    assert "checks" in result
    mock_system_helpers["health"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_system_invalid_operation():
    """Test manage_system with invalid operation."""
    result = await manage_system(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_system_missing_required_params():
    """Test manage_system with missing required parameters."""
    # Tool_help operation requires tool_name
    result = await manage_system(operation="tool_help")

    assert "error" in result
    assert "tool_name is required" in result["error"]
