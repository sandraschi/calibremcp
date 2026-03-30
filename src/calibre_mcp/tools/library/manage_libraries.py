"""
Library management portmanteau tool for CalibreMCP.

Consolidates list_libraries, switch_library, get_library_stats, and cross_library_search
into a single portmanteau tool with operation parameter.

SOTA: ctx: Context, execution_time_ms, recommendations in responses.
"""

import time
from typing import Any

from fastmcp import Context

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error

logger = get_logger("calibremcp.tools.library_management")


def _add_dialogic_fields(
    result: dict[str, Any],
    execution_time_ms: int,
    operation: str,
) -> dict[str, Any]:
    """Add execution_time_ms and recommendations for SOTA dialogic returns."""
    result["execution_time_ms"] = execution_time_ms
    if "recommendations" not in result:
        recs = {
            "list": [
                "Use operation='switch' to change library",
                "Use operation='stats' for details",
            ],
            "switch": [
                "Use operation='list' to see libraries",
                "Use operation='stats' after switch",
            ],
            "stats": ["Use operation='search' for cross-library search"],
            "search": [
                "Use query_books for detailed book search",
                "Use manage_books for book details",
            ],
            "test_connection": ["Use operation='list' to see available libraries"],
            "discover": [
                "Use operation='list' after discovery",
                "Use operation='switch' to activate",
            ],
        }
        result["recommendations"] = recs.get(
            operation, ["Use manage_libraries for library operations"]
        )
    return result


@mcp.tool()
async def manage_libraries(
    operation: str,
    library_name: str | None = None,
    query: str | None = None,
    libraries: list[str] | None = None,
    wizfile_allowed: bool = False,
    calibre_cli_allowed: bool = False,
    common_paths_allowed: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """
    Unified interface for Calibre library management and discovery.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates library listing, switching, stats, search, and discovery into a single interface.
    Prevents tool explosion while maintaining full library lifecycle control.

    OPERATIONS:
    - list: List all discovered libraries with metadata and active status.
    - switch: Change the active library for the current session.
    - stats: Detailed book/author/format metrics for a library.
    - search: Search for books across multiple libraries simultaneously.
    - test_connection: Diagnostic check for library accessibility.
    - discover: Scan filesystem/CLI to find new Calibre libraries.

    Returns:
    FastMCP 3.1+ dialogic response: success, operation, result or error,
    recommendations, next_steps, and execution_time_ms.
    Enables conversational follow-ups for library navigation.
    """
    start_ms = int(time.time() * 1000)
    if ctx:
        try:
            ctx.info(f"manage_libraries operation={operation}")
        except Exception:
            pass
    try:
        if operation == "list":
            r = await _handle_list_libraries()
            return _add_dialogic_fields(r, int(time.time() * 1000) - start_ms, operation)
        elif operation == "switch":
            if not library_name:
                r = format_error_response(
                    error_msg=(
                        "library_name is required for operation='switch'. "
                        "Use operation='list' to see available libraries."
                    ),
                    error_code="MISSING_LIBRARY_NAME",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "First call manage_libraries(operation='list') to see all available libraries",
                        "Then use one of those library names with operation='switch'",
                        "Example: manage_libraries(operation='switch', library_name='Main Library')",
                    ],
                    related_tools=["manage_libraries"],
                    execution_time_ms=int(time.time() * 1000) - start_ms,
                )
                return r
            r = await _handle_switch_library(library_name)
            return _add_dialogic_fields(r, int(time.time() * 1000) - start_ms, operation)
        elif operation == "stats":
            r = await _handle_get_library_stats(library_name)
            return _add_dialogic_fields(r, int(time.time() * 1000) - start_ms, operation)
        elif operation == "search":
            if not query:
                return format_error_response(
                    error_msg="query is required for operation='search'.",
                    error_code="MISSING_QUERY",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide a search query string, e.g., query='python programming'",
                        "Optionally specify libraries=['Library1', 'Library2'] to search specific libraries",
                        "Example: manage_libraries(operation='search', query='machine learning')",
                    ],
                    related_tools=["manage_libraries", "query_books"],
                    execution_time_ms=int(time.time() * 1000) - start_ms,
                )
            r = await _handle_cross_library_search(query, libraries)
            return _add_dialogic_fields(r, int(time.time() * 1000) - start_ms, operation)
        elif operation == "test_connection":
            r = await _handle_test_connection()
            return _add_dialogic_fields(r, int(time.time() * 1000) - start_ms, operation)
        elif operation == "discover":
            r = await _handle_discover(wizfile_allowed, calibre_cli_allowed, common_paths_allowed)
            return _add_dialogic_fields(r, int(time.time() * 1000) - start_ms, operation)
        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. "
                    f"Must be one of: 'list', 'switch', 'stats', 'search', 'test_connection', 'discover'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='list' to see all available libraries",
                    "Use operation='switch' to change the active library",
                    "Use operation='stats' to get library statistics",
                    "Use operation='search' to search across libraries",
                    "Use operation='test_connection' for connection diagnostics",
                    "Use operation='discover' to find libraries via filesystem/CLI",
                ],
                related_tools=["manage_libraries"],
                execution_time_ms=int(time.time() * 1000) - start_ms,
            )
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "library_name": library_name,
                "query": query,
                "libraries": libraries,
            },
            tool_name="manage_libraries",
            context="Library management operation",
            execution_time_ms=int(time.time() * 1000) - start_ms,
        )


async def _handle_list_libraries() -> dict[str, Any]:
    """Handle list libraries operation."""
    # Use helper function (not registered as MCP tool)
    from .library_management import list_libraries_helper

    try:
        result = await list_libraries_helper()
        return result.model_dump()
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="list",
            parameters={},
            tool_name="manage_libraries",
            context="Listing available Calibre libraries",
        )


async def _handle_switch_library(library_name: str) -> dict[str, Any]:
    """Handle switch library operation."""
    # Use helper function (not registered as MCP tool)
    from .library_management import switch_library_helper

    try:
        return await switch_library_helper(library_name)
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="switch",
            parameters={"library_name": library_name},
            tool_name="manage_libraries",
            context=f"Switching to library: {library_name}",
        )


async def _handle_get_library_stats(library_name: str | None) -> dict[str, Any]:
    """Handle get library stats operation."""
    # Use helper function (not registered as MCP tool)
    from .library_management import get_library_stats_helper

    try:
        result = await get_library_stats_helper(library_name)
        return result.model_dump()
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="stats",
            parameters={"library_name": library_name},
            tool_name="manage_libraries",
            context=f"Getting statistics for library: {library_name or 'current'}",
        )


async def _handle_cross_library_search(query: str, libraries: list[str] | None) -> dict[str, Any]:
    """Handle cross-library search operation."""
    # Use helper function (not registered as MCP tool)
    from .library_management import cross_library_search_helper

    try:
        result = await cross_library_search_helper(query, libraries)
        return result.model_dump()
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="search",
            parameters={"query": query, "libraries": libraries},
            tool_name="manage_libraries",
            context=f"Cross-library search for query: {query}",
        )


async def _handle_test_connection() -> dict[str, Any]:
    """Handle test_connection operation (merged from core)."""
    from ..core.library_operations import test_calibre_connection_helper

    try:
        result = await test_calibre_connection_helper()
        return result.model_dump()
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="test_connection",
            parameters={},
            tool_name="manage_libraries",
            context="Testing Calibre connection",
        )


async def _handle_discover(
    wizfile_allowed: bool, calibre_cli_allowed: bool, common_paths_allowed: bool
) -> dict[str, Any]:
    """Handle discover operation (merged from library_discovery)."""
    from .library_discovery import discovery_tool

    try:
        libraries = discovery_tool.discover_libraries(
            wizfile_allowed=wizfile_allowed,
            calibre_cli_allowed=calibre_cli_allowed,
            common_paths_allowed=common_paths_allowed,
        )
        return {
            "success": True,
            "libraries_found": len(libraries),
            "libraries": libraries,
            "methods_used": {
                "common_paths": common_paths_allowed,
                "calibre_cli": calibre_cli_allowed,
                "wizfile": wizfile_allowed,
            },
        }
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="discover",
            parameters={
                "wizfile_allowed": wizfile_allowed,
                "calibre_cli_allowed": calibre_cli_allowed,
                "common_paths_allowed": common_paths_allowed,
            },
            tool_name="manage_libraries",
            context="Discovering Calibre libraries",
        )
