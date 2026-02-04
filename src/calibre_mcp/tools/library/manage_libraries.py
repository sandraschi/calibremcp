"""
Library management portmanteau tool for CalibreMCP.

Consolidates list_libraries, switch_library, get_library_stats, and cross_library_search
into a single portmanteau tool with operation parameter.
"""

from typing import Optional, List, Dict, Any

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response

logger = get_logger("calibremcp.tools.library_management")


@mcp.tool()
async def manage_libraries(
    operation: str,
    library_name: Optional[str] = None,
    query: Optional[str] = None,
    libraries: Optional[List[str]] = None,
    wizfile_allowed: bool = False,
    calibre_cli_allowed: bool = False,
    common_paths_allowed: bool = True,
) -> Dict[str, Any]:
    """
    Manage Calibre libraries with multiple operations in a single unified interface.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 4 separate tools (one per operation), this tool consolidates related
    library management operations into a single interface. This design:
    - Prevents tool explosion (4 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with library management tasks
    - Enables consistent library interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - list: List all available Calibre libraries with metadata and statistics
    - switch: Switch the active library for all subsequent operations
    - stats: Get detailed statistics for a specific or current library
    - search: Search for books across multiple libraries simultaneously
    - test_connection: Test Calibre connection (local SQLite or remote server)
    - discover: Discover Calibre libraries via filesystem/CLI (common_paths, calibre_cli, wizfile)

    OPERATIONS DETAIL:

    list: List all available libraries
    - Discovers all Calibre libraries on the system
    - Returns metadata including name, path, book count, size, and active status
    - No parameters required
    - Returns: List of libraries with metadata

    switch: Switch active library
    - Changes the active library for all subsequent operations
    - Requires library_name parameter (must match a library from list operation)
    - Case-sensitive library name matching
    - Returns: Success status and new active library info

    stats: Get library statistics
    - Provides detailed statistics for a specific or current library
    - Includes book counts, author counts, format distribution, language distribution
    - library_name is optional (uses current library if omitted)
    - Returns: Comprehensive statistics dictionary

    search: Cross-library search
    - Searches for books across multiple libraries simultaneously
    - Requires query parameter (searches titles, authors, tags, etc.)
    - Optional libraries parameter to limit search scope
    - Returns: Books found with library_name included per result

    Prerequisites:
        - For 'switch' and 'stats': Library must exist (use 'list' to see available libraries)
        - For 'search': At least one library must be accessible
        - Calibre libraries must be discoverable (contain metadata.db files)

    Parameters:
        operation: The operation to perform. Must be one of: "list", "switch", "stats", "search"
            - "list": List all available libraries with metadata. No other parameters required.
            - "switch": Switch to a different library. Requires `library_name` parameter.
            - "stats": Get statistics for a library. `library_name` is optional (uses current if omitted).
            - "search": Search across libraries. Requires `query` parameter, `libraries` is optional.

        library_name: Name of the library (required for 'switch', optional for 'stats')
            - Must exactly match a library name from operation="list"
            - Case-sensitive (e.g., "Main Library" not "main library")
            - For 'stats': If omitted, uses currently active library

        query: Search query text (required for 'search')
            - Searches in book titles, authors, tags, etc.
            - Works across multiple libraries simultaneously

        libraries: List of library names to search (optional, for 'search' only)
            - If omitted, searches all available libraries
            - Each name must match a library from operation="list"
            - Example: ["Main Library", "IT Library"]

    Returns:
        Dictionary containing operation-specific results:

        For operation="list":
            {
                "libraries": List[Dict] - Library objects with name, path, book_count, size_mb, is_active
                "current_library": str - Name of currently active library
                "total_libraries": int - Total number of discovered libraries
            }

        For operation="switch":
            {
                "success": bool - Whether switch completed successfully
                "library_name": str - Name of newly active library
                "library_path": str - Full path to the library
                "message": str - Status message
            }

        For operation="stats":
            {
                "library_name": str - Name of analyzed library
                "total_books": int - Total number of books
                "total_authors": int - Number of unique authors
                "total_series": int - Number of series
                "total_tags": int - Number of tags
                "format_distribution": Dict[str, int] - Format counts (e.g., {"epub": 100})
                "language_distribution": Dict[str, int] - Language counts
                "rating_distribution": Dict[str, int] - Rating counts
                "last_modified": Optional[str] - Last modification timestamp
            }

        For operation="search":
            {
                "results": List[Dict] - Books found across libraries (includes library_name per result)
                "total_found": int - Total number of matching books
                "query_used": str - The search query used
                "search_time_ms": int - Search execution time
                "library_searched": str - Names of libraries searched (comma-separated)
            }

    Usage:
        # List all libraries
        result = await manage_libraries(operation="list")
        print(f"Found {result['total_libraries']} libraries")

        # Switch to a library
        result = await manage_libraries(operation="switch", library_name="Main Library")
        if result["success"]:
            print(f"Switched to: {result['library_name']}")

        # Get statistics
        result = await manage_libraries(operation="stats", library_name="Main Library")
        print(f"Total books: {result['total_books']}")

        # Search across libraries
        result = await manage_libraries(
            operation="search",
            query="python programming",
            libraries=["Main Library", "IT Library"]
        )
        print(f"Found {result['total_found']} books")

    Examples:
        # Basic library listing
        libraries = await manage_libraries(operation="list")
        for lib in libraries["libraries"]:
            print(f"{lib['name']}: {lib['book_count']} books")

        # Switch library with validation
        switch_result = await manage_libraries(operation="switch", library_name="Main Library")
        if not switch_result["success"]:
            print(f"Error: {switch_result.get('message', 'Unknown error')}")

        # Get stats for current library (library_name omitted)
        stats = await manage_libraries(operation="stats")
        print(f"Current library has {stats['total_books']} books")

        # Cross-library search
        search_results = await manage_libraries(
            operation="search",
            query="machine learning",
            libraries=["Main Library"]  # Search only in Main Library
        )
        for book in search_results["results"][:5]:  # Show first 5
            print(f"{book['title']} (in {book['library_name']})")

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "list", "switch", "stats", "search"
        - Library not found (switch/stats): Use operation="list" first to see available library names
        - Missing library_name (switch): Provide library_name parameter for switch operation
        - Missing query (search): Provide query parameter for search operation
        - No libraries found: Ensure Calibre libraries exist and contain metadata.db files

    See Also:
        - For individual operations: See list_libraries, switch_library, get_library_stats, cross_library_search
          (these are deprecated in favor of this portmanteau tool)
    """
    try:
        if operation == "list":
            return await _handle_list_libraries()
        elif operation == "switch":
            if not library_name:
                return format_error_response(
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
                )
            return await _handle_switch_library(library_name)
        elif operation == "stats":
            return await _handle_get_library_stats(library_name)
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
                )
            return await _handle_cross_library_search(query, libraries)
        elif operation == "test_connection":
            return await _handle_test_connection()
        elif operation == "discover":
            return await _handle_discover(wizfile_allowed, calibre_cli_allowed, common_paths_allowed)
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
        )


async def _handle_list_libraries() -> Dict[str, Any]:
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


async def _handle_switch_library(library_name: str) -> Dict[str, Any]:
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


async def _handle_get_library_stats(library_name: Optional[str]) -> Dict[str, Any]:
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


async def _handle_cross_library_search(
    query: str, libraries: Optional[List[str]]
) -> Dict[str, Any]:
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


async def _handle_test_connection() -> Dict[str, Any]:
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
) -> Dict[str, Any]:
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
