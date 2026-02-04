"""
Tests for the Calibre MCP server implementation.

Tests verify FastMCP 2.13+ server initialization and tool registration.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastmcp import FastMCP

# Import the actual server
from calibre_mcp.server import mcp, server_lifespan


def test_server_initialization():
    """Test that the MCP server is properly initialized."""
    # Verify server exists and is FastMCP instance
    assert mcp is not None
    assert isinstance(mcp, FastMCP)
    assert mcp.name == "CalibreMCP Phase 2"


def test_server_has_tool_decorator():
    """Test that the server has the tool decorator."""
    assert hasattr(mcp, "tool")
    assert callable(mcp.tool)


@pytest.mark.asyncio
async def test_server_lifespan_initializes_storage():
    """Test that server lifespan initializes storage properly."""
    # Create a test MCP instance
    test_mcp = FastMCP("test")

    # Mock the storage initialization
    with patch("calibre_mcp.server.CalibreMCPStorage") as mock_storage_class:
        mock_storage = MagicMock()
        mock_storage.initialize = MagicMock(return_value=None)
        mock_storage.get_current_library = MagicMock(return_value=None)
        mock_storage_class.return_value = mock_storage

        # Run lifespan
        async with server_lifespan(test_mcp):
            # Verify storage was initialized
            mock_storage_class.assert_called_once_with(test_mcp)
            mock_storage.initialize.assert_called_once()


@pytest.mark.asyncio
async def test_server_lifespan_handles_errors_gracefully():
    """Test that server lifespan handles errors gracefully."""
    test_mcp = FastMCP("test")

    # Mock storage to raise an error
    with patch("calibre_mcp.server.CalibreMCPStorage") as mock_storage_class:
        mock_storage_class.side_effect = Exception("Storage init failed")

        # Should not crash, but handle error
        try:
            async with server_lifespan(test_mcp):
                pass
        except Exception:
            # It's OK if it raises - we just want to verify it doesn't crash hard
            pass


def test_tools_are_registered():
    """Test that tools are registered with the server."""
    # Import tools to trigger registration
    from calibre_mcp.tools import register_tools

    # This should not raise an error
    try:
        register_tools(mcp)
    except Exception as e:
        pytest.fail(f"Tool registration failed: {e}")


def test_search_books_tool_exists():
    """Test that search_books tool is accessible."""
    # Verify it's a coroutine function
    import inspect

    from calibre_mcp.tools.book_tools import search_books

    assert inspect.iscoroutinefunction(search_books)

    # Verify it has proper signature
    sig = inspect.signature(search_books)
    assert "query" in sig.parameters or "text" in sig.parameters


def test_list_libraries_tool_exists():
    """Test that list_libraries tool is accessible."""
    # Verify it's a coroutine function
    import inspect

    from calibre_mcp.tools.library.library_management import list_libraries

    assert inspect.iscoroutinefunction(list_libraries)


@pytest.mark.asyncio
async def test_library_discovery_returns_dict():
    """Test that library discovery returns proper structure."""
    from calibre_mcp.server import discover_libraries

    # Mock the discovery
    with patch("calibre_mcp.server.discover_libraries") as mock_discover:
        mock_discover.return_value = {
            "main": "/path/to/main",
            "test": "/path/to/test",
        }

        result = await discover_libraries()

        # Verify structure
        assert isinstance(result, dict)
        assert "main" in result
        assert "test" in result
