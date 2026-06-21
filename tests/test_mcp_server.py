"""
Tests for the Calibre MCP server implementation.

Tests verify FastMCP 3.x server initialization, lifespan, and tool registration.
"""

import inspect
import os

import pytest
from fastmcp import FastMCP

# Import the actual server
from calibre_mcp.server import mcp, server_lifespan


def test_server_initialization():
    """Test that the MCP server is properly initialized."""
    assert mcp is not None
    assert isinstance(mcp, FastMCP)
    # The FastMCP instance name is "CalibreMCP"; "CalibreMCP Phase 2" is the
    # run_server_async server_name override used at runtime.
    assert mcp.name == "CalibreMCP"


def test_server_has_tool_decorator():
    """Test that the server has the tool decorator."""
    assert hasattr(mcp, "tool")
    assert callable(mcp.tool)


@pytest.mark.asyncio
async def test_server_lifespan_starts_in_degraded_mode():
    """Server lifespan must start without error when no Calibre source is configured.

    When neither CALIBRE_BASE_PATH nor CALIBRE_SERVER_URL are set, the probe
    logs a warning but does NOT raise, allowing the server to start in
    degraded mode.  This is the typical test-environment state.
    """
    test_mcp = FastMCP("test")

    # Strip any stray env vars so the probe takes the "nothing configured" branch
    saved = {}
    for key in ("CALIBRE_BASE_PATH", "CALIBRE_SERVER_URL"):
        saved[key] = os.environ.pop(key, None)
    try:
        async with server_lifespan(test_mcp):
            pass  # entered and exited without exception
    finally:
        for key, val in saved.items():
            if val is not None:
                os.environ[key] = val


@pytest.mark.asyncio
async def test_server_lifespan_fails_on_bad_configured_source():
    """Lifespan raises RuntimeError when a source is configured but unreachable."""
    test_mcp = FastMCP("test")

    # Point at a non-existent path so the probe hard-fails
    saved = os.environ.pop("CALIBRE_BASE_PATH", None)
    os.environ["CALIBRE_BASE_PATH"] = "/nonexistent/calibre/path"
    try:
        with pytest.raises(RuntimeError, match="CalibreMCP startup failed"):
            async with server_lifespan(test_mcp):
                pass
    finally:
        del os.environ["CALIBRE_BASE_PATH"]
        if saved is not None:
            os.environ["CALIBRE_BASE_PATH"] = saved


def test_tools_are_registered():
    """Test that tools can be registered with the server without errors."""
    from calibre_mcp.tools import register_tools

    try:
        register_tools(mcp)
    except Exception as e:
        pytest.fail(f"Tool registration failed: {e}")


def test_query_books_tool_exists():
    """query_books portmanteau tool is accessible and is a coroutine function."""
    from calibre_mcp.tools.book_management.query_books import query_books

    assert inspect.iscoroutinefunction(query_books)
    sig = inspect.signature(query_books)
    assert "operation" in sig.parameters


def test_manage_libraries_tool_exists():
    """manage_libraries portmanteau tool is accessible and is a coroutine function."""
    from calibre_mcp.tools.library.manage_libraries import manage_libraries

    assert inspect.iscoroutinefunction(manage_libraries)
    sig = inspect.signature(manage_libraries)
    assert "operation" in sig.parameters


@pytest.mark.asyncio
async def test_library_discovery_returns_dict():
    """discover_libraries returns a dict (possibly empty in test env)."""
    from calibre_mcp.server import discover_libraries

    # Strip env so discovery doesn't try to scan a real L: drive
    saved = {}
    for key in ("CALIBRE_BASE_PATH", "CALIBRE_LOCAL_LIBRARY_PATH"):
        saved[key] = os.environ.pop(key, None)
    try:
        result = await discover_libraries()
        assert isinstance(result, dict)
    finally:
        for key, val in saved.items():
            if val is not None:
                os.environ[key] = val
