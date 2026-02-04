"""
Library operations portmanteau tool for Calibre MCP server.

Consolidates all library-level operations into a single unified interface:
- Series analysis and management
- Library-wide metadata operations
- Bulk organizational tasks
"""

from typing import Any, Dict, Optional

from ...logging_config import get_logger
from ...server import mcp
from .list_books import list_books

# Import operation implementations
from .series_manager import SeriesManager

logger = get_logger("calibremcp.tools.library_operations")


@mcp.tool()
async def manage_library_operations(
    operation: str,
    # Common parameters
    library_path: str | None = None,
    dry_run: bool = True,
    # Series management parameters
    update_metadata: bool = False,
    source_series: str | None = None,
    target_series: str | None = None,
    # Book listing parameters
    query: str = "",
    author: str = "",
    tag: str = "",
    format_filter: str = "",
    status: str = "",
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "title",
    sort_order: str = "asc",
) -> dict[str, Any]:
    """
    Comprehensive library operations portmanteau tool for Calibre MCP server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 4 related library operations into single interface. Prevents tool explosion while maintaining
    full functionality. Enables unified library management workflow.

    SUPPORTED OPERATIONS:
    - analyze_series: Analyze series structure and identify issues
    - fix_series_metadata: Repair series metadata problems
    - merge_series: Combine series entries
    - list_books: Search and filter books with pagination

    OPERATIONS DETAIL:

    analyze_series:
    - Scan all series in library for consistency issues
    - Identify missing volumes, incorrect ordering, duplicates
    - Parameters: library_path (optional), update_metadata (default: False)

    fix_series_metadata:
    - Automatically repair common series metadata issues
    - Standardize series names, fix volume numbering
    - Parameters: library_path (optional), dry_run (default: True)

    merge_series:
    - Combine one series into another, updating all references
    - Useful for fixing duplicate series entries
    - Parameters: source_series, target_series (required), dry_run (default: True)

    list_books:
    - Search and filter books with advanced criteria
    - Paginated results with sorting options
    - Parameters: query, author, tag, format_filter, status, limit, offset, sort_by, sort_order

    Prerequisites:
        - Valid Calibre library path configured
        - For series operations: Series data must exist in library
        - For book listing: Database must be accessible

    Returns:
        Dict with operation results, success status, and conversational messaging

    Examples:
        # Analyze series structure
        {"operation": "analyze_series", "update_metadata": false}

        # Fix series metadata issues
        {"operation": "fix_series_metadata", "dry_run": true}

        # List books with filters
        {"operation": "list_books", "author": "Tolkien", "limit": 20}
    """

    try:
        if operation == "analyze_series":
            series_manager = SeriesManager()
            return await series_manager.analyze_series(
                library_path=library_path, update_metadata=update_metadata
            )

        elif operation == "fix_series_metadata":
            series_manager = SeriesManager()
            return await series_manager.fix_series_metadata(
                library_path=library_path, dry_run=dry_run
            )

        elif operation == "merge_series":
            if not source_series or not target_series:
                return {
                    "success": False,
                    "error": "source_series and target_series parameters required for merging",
                    "message": "Please specify both source and target series names for the merge operation.",
                }
            series_manager = SeriesManager()
            return await series_manager.merge_series(
                library_path=library_path,
                source_series=source_series,
                target_series=target_series,
                dry_run=dry_run,
            )

        elif operation == "list_books":
            return await list_books(
                query=query,
                author=author,
                tag=tag,
                format=format_filter,
                status=status,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order,
                library_path=library_path,
            )

        else:
            available_ops = ["analyze_series", "fix_series_metadata", "merge_series", "list_books"]
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "message": f"Available operations: {', '.join(available_ops)}",
                "available_operations": available_ops,
            }

    except Exception as e:
        logger.error(f"Library operation '{operation}' failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Library operation failed: {str(e)}",
            "operation": operation,
            "message": f"Sorry, the {operation.replace('_', ' ')} operation encountered an error. Please check the logs for details.",
        }
