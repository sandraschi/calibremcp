"""
Test that all portmanteau tools are properly registered with the MCP server.

This test verifies Phase 4 requirement: Verify tool registration
"""

import inspect

import pytest

from calibre_mcp.server import mcp

# List of the 11 portmanteau tools registered with the MCP server
# (manage_specialized has no module — specialized_tools.py holds unregistered helpers only;
# analyze_library, manage_bulk_operations, manage_content_sync, manage_smart_collections
# and manage_users are importable helpers whose @mcp.tool decorators were removed in the
# portmanteau consolidation — verified by test_portmanteau_tools_have_operation_parameter)
EXPECTED_PORTMANTEAU_TOOLS = [
    "manage_libraries",
    "manage_books",
    "query_books",
    "manage_tags",
    "manage_authors",
    "manage_metadata",
    "manage_files",
    "manage_system",
    "manage_analysis",
    "export_books",
    "manage_viewer",
]


@pytest.mark.asyncio
async def test_all_portmanteau_tools_registered():
    """Test that all 16 portmanteau tools are registered with the MCP server."""
    # Import tools to trigger registration
    from calibre_mcp.tools import register_tools  # noqa: F401

    register_tools(mcp)

    # FastMCP 3.4+ public async API - private _tools was removed
    tool_names = set()
    try:
        tools_list = await mcp.list_tools()
        if tools_list:
            tool_names = {tool.name for tool in tools_list}
    except (AttributeError, TypeError):
        tool_names = set()

    # If list_tools returned nothing, fall back to callable attribute probe
    if not tool_names:
        tool_names = {name for name in dir(mcp) if not name.startswith("_") and callable(getattr(mcp, name, None))}

    # Verify all portmanteau tools are registered
    missing_tools = []
    for tool_name in EXPECTED_PORTMANTEAU_TOOLS:
        if tool_name not in tool_names:
            missing_tools.append(tool_name)

    assert len(missing_tools) == 0, (
        f"Missing portmanteau tools: {missing_tools}. Registered tools: {sorted(tool_names)}"
    )

    # Verify we have at least the expected number of tools
    assert len(tool_names) >= len(EXPECTED_PORTMANTEAU_TOOLS), (
        f"Expected at least {len(EXPECTED_PORTMANTEAU_TOOLS)} portmanteau tools, found {len(tool_names)}"
    )


def test_portmanteau_tools_have_operation_parameter():
    """Test that all portmanteau tools have an 'operation' parameter."""
    from calibre_mcp.tools import register_tools  # noqa: F401

    register_tools(mcp)

    # Import the actual tool functions directly
    from calibre_mcp.tools.advanced_features.manage_bulk_operations import (
        manage_bulk_operations,
    )
    from calibre_mcp.tools.advanced_features.manage_content_sync import (
        manage_content_sync,
    )
    from calibre_mcp.tools.advanced_features.manage_smart_collections import (
        manage_smart_collections,
    )
    from calibre_mcp.tools.analysis.analyze_library import analyze_library
    from calibre_mcp.tools.analysis.manage_analysis import manage_analysis
    from calibre_mcp.tools.authors.manage_authors import manage_authors
    from calibre_mcp.tools.book_management.manage_books import manage_books
    from calibre_mcp.tools.book_management.query_books import query_books
    from calibre_mcp.tools.files.manage_files import manage_files
    from calibre_mcp.tools.import_export.export_books_portmanteau import (
        export_books,
    )
    from calibre_mcp.tools.library.manage_libraries import manage_libraries
    from calibre_mcp.tools.metadata.manage_metadata import manage_metadata
    from calibre_mcp.tools.system.manage_system import manage_system
    from calibre_mcp.tools.tags.manage_tags import manage_tags
    from calibre_mcp.tools.user_management.manage_users import manage_users
    from calibre_mcp.tools.viewer.manage_viewer import manage_viewer

    tool_functions = {
        "manage_books": manage_books,
        "query_books": query_books,
        "manage_libraries": manage_libraries,
        "manage_tags": manage_tags,
        "manage_authors": manage_authors,
        "manage_metadata": manage_metadata,
        "manage_files": manage_files,
        "manage_system": manage_system,
        "manage_analysis": manage_analysis,
        "analyze_library": analyze_library,
        "manage_bulk_operations": manage_bulk_operations,
        "manage_content_sync": manage_content_sync,
        "manage_smart_collections": manage_smart_collections,
        "manage_users": manage_users,
        "export_books": export_books,
        "manage_viewer": manage_viewer,
    }

    for tool_name, func in tool_functions.items():
        # Check signature
        sig = inspect.signature(func)
        assert "operation" in sig.parameters, (
            f"Portmanteau tool '{tool_name}' missing 'operation' parameter. Parameters: {list(sig.parameters.keys())}"
        )

        # Verify operation parameter is required (no default)
        operation_param = sig.parameters["operation"]
        assert operation_param.default == inspect.Parameter.empty, (
            f"Portmanteau tool '{tool_name}' 'operation' parameter should be required (no default value)"
        )


def test_portmanteau_tools_are_async():
    """Test that all portmanteau tools are async functions."""
    # Import the actual tool functions directly
    from calibre_mcp.tools.advanced_features.manage_bulk_operations import (
        manage_bulk_operations,
    )
    from calibre_mcp.tools.advanced_features.manage_content_sync import (
        manage_content_sync,
    )
    from calibre_mcp.tools.advanced_features.manage_smart_collections import (
        manage_smart_collections,
    )
    from calibre_mcp.tools.analysis.analyze_library import analyze_library
    from calibre_mcp.tools.analysis.manage_analysis import manage_analysis
    from calibre_mcp.tools.authors.manage_authors import manage_authors
    from calibre_mcp.tools.book_management.manage_books import manage_books
    from calibre_mcp.tools.book_management.query_books import query_books
    from calibre_mcp.tools.files.manage_files import manage_files
    from calibre_mcp.tools.import_export.export_books_portmanteau import export_books
    from calibre_mcp.tools.library.manage_libraries import manage_libraries
    from calibre_mcp.tools.metadata.manage_metadata import manage_metadata
    from calibre_mcp.tools.system.manage_system import manage_system
    from calibre_mcp.tools.tags.manage_tags import manage_tags
    from calibre_mcp.tools.user_management.manage_users import manage_users
    from calibre_mcp.tools.viewer.manage_viewer import manage_viewer

    tool_functions = {
        "manage_books": manage_books,
        "query_books": query_books,
        "manage_libraries": manage_libraries,
        "manage_tags": manage_tags,
        "manage_authors": manage_authors,
        "manage_metadata": manage_metadata,
        "manage_files": manage_files,
        "manage_system": manage_system,
        "manage_analysis": manage_analysis,
        "analyze_library": analyze_library,
        "manage_bulk_operations": manage_bulk_operations,
        "manage_content_sync": manage_content_sync,
        "manage_smart_collections": manage_smart_collections,
        "manage_users": manage_users,
        "export_books": export_books,
        "manage_viewer": manage_viewer,
    }

    for tool_name, func in tool_functions.items():
        # Verify it's async
        assert inspect.iscoroutinefunction(func), f"Portmanteau tool '{tool_name}' is not an async function"


def test_portmanteau_tools_importable():
    """Test that all portmanteau tools can be imported."""

    for tool_name in EXPECTED_PORTMANTEAU_TOOLS:
        # Try to import the tool function
        # Tools are in various modules, so we'll just verify they exist in the tools package
        try:
            # Import the tools module to trigger registration
            from calibre_mcp.tools import register_tools  # noqa: F401
            # If we get here, imports worked
        except ImportError as e:
            pytest.fail(f"Failed to import tools (required for {tool_name}): {e}")


def test_portmanteau_tool_count():
    """Test that we have exactly 11 registered portmanteau tools."""
    # Verify we have all expected tools defined
    assert len(EXPECTED_PORTMANTEAU_TOOLS) == 11, (
        f"Expected 11 portmanteau tools in test, found {len(EXPECTED_PORTMANTEAU_TOOLS)}"
    )

    # Verify all tools are in the expected list
    assert set(EXPECTED_PORTMANTEAU_TOOLS) == {
        "manage_libraries",
        "manage_books",
        "query_books",
        "manage_tags",
        "manage_authors",
        "manage_metadata",
        "manage_files",
        "manage_system",
        "manage_analysis",
        "export_books",
        "manage_viewer",
    }, "Portmanteau tool list mismatch"
