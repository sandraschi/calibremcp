"""
Library management portmanteau tool for CalibreMCP.

Consolidates list_libraries, switch_library, get_library_stats, and cross_library_search
into a single portmanteau tool with operation parameter.
"""

from typing import Optional, List, Dict, Any

from ...server import mcp
from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.library_management")


@mcp.tool()
async def manage_libraries(
    operation: str,
    library_name: Optional[str] = None,
    query: Optional[str] = None,
    libraries: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Manage Calibre libraries with multiple operations in a single unified interface.

    This portmanteau tool consolidates all library management operations (listing,
    switching, statistics, and cross-library search) into a single interface. Use the
    `operation` parameter to select which operation to perform.

    Operations:
    - list: List all available Calibre libraries with metadata and statistics
    - switch: Switch the active library for all subsequent operations
    - stats: Get detailed statistics for a specific or current library
    - search: Search for books across multiple libraries simultaneously

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
    if operation == "list":
        return await _handle_list_libraries()
    elif operation == "switch":
        if not library_name:
            return {
                "success": False,
                "error": "library_name is required for operation='switch'. Use operation='list' to see available libraries.",
                "suggestions": [
                    "First call manage_libraries(operation='list') to see all available libraries",
                    "Then use one of those library names with operation='switch'",
                ],
            }
        return await _handle_switch_library(library_name)
    elif operation == "stats":
        return await _handle_get_library_stats(library_name)
    elif operation == "search":
        if not query:
            return {
                "success": False,
                "error": "query is required for operation='search'.",
                "suggestions": [
                    "Provide a search query string, e.g., query='python programming'",
                    "Optionally specify libraries=['Library1', 'Library2'] to search specific libraries",
                ],
            }
        return await _handle_cross_library_search(query, libraries)
    else:
        return {
            "success": False,
            "error": f"Invalid operation: '{operation}'. Must be one of: 'list', 'switch', 'stats', 'search'",
            "suggestions": [
                "Use operation='list' to see all available libraries",
                "Use operation='switch' to change the active library",
                "Use operation='stats' to get library statistics",
                "Use operation='search' to search across libraries",
            ],
        }


async def _handle_list_libraries() -> Dict[str, Any]:
    """Handle list libraries operation."""
    # Use helper function (not registered as MCP tool)
    from .library_management import list_libraries_helper

    try:
        result = await list_libraries_helper()
        return result.model_dump()
    except Exception as e:
        logger.error(f"Error listing libraries: {e}", exc_info=True)
        return {
            "libraries": [],
            "current_library": "",
            "total_libraries": 0,
            "error": str(e),
        }


async def _handle_switch_library(library_name: str) -> Dict[str, Any]:
    """Handle switch library operation."""
    # Use helper function (not registered as MCP tool)
    from .library_management import switch_library_helper

    try:
        return await switch_library_helper(library_name)
    except Exception as e:
        logger.error(f"Error switching library: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Error switching library: {str(e)}",
            "library_name": library_name,
            "library_path": "",
        }


async def _handle_get_library_stats(library_name: Optional[str]) -> Dict[str, Any]:
    """Handle get library stats operation."""
    # Use helper function (not registered as MCP tool)
    from .library_management import get_library_stats_helper

    try:
        result = await get_library_stats_helper(library_name)
        return result.model_dump()
    except Exception as e:
        logger.error(f"Error getting library stats: {e}", exc_info=True)
        return {
            "library_name": library_name or "unknown",
            "total_books": 0,
            "total_authors": 0,
            "total_series": 0,
            "total_tags": 0,
            "format_distribution": {},
            "language_distribution": {},
            "rating_distribution": {},
            "last_modified": None,
            "error": str(e),
        }


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
        logger.error(f"Error in cross-library search: {e}", exc_info=True)
        return {
            "results": [],
            "total_found": 0,
            "query_used": query,
            "search_time_ms": 0,
            "library_searched": "",
            "error": str(e),
        }
