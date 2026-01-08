"""
Metadata management portmanteau tool for CalibreMCP.

Consolidates all metadata-related operations into a single unified interface.
"""

from typing import Optional, List, Dict, Any

from ...server import mcp
from ...server import MetadataUpdateRequest
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response

# Import helper functions (NOT registered as MCP tools)
from . import metadata_management

logger = get_logger("calibremcp.tools.metadata")


@mcp.tool()
async def manage_metadata(
    operation: str,
    # Update operation parameters
    updates: Optional[List[MetadataUpdateRequest]] = None,
) -> Dict[str, Any]:
    """
    Comprehensive metadata management tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 3 separate tools (one per operation), this tool consolidates related
    metadata operations into a single interface. This design:
    - Prevents tool explosion (3 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with metadata management tasks
    - Enables consistent metadata interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - update: Update metadata for single or multiple books
    - organize_tags: AI-powered tag organization and cleanup suggestions
    - fix_issues: Automatically fix common metadata problems

    OPERATIONS DETAIL:

    update: Update book metadata
    - Allows bulk updates to book metadata including title, author, publication date, tags, etc.
    - Each update request specifies a book ID, field name, and new value
    - Supports batching updates for multiple books
    - Validates field values (e.g., rating must be 1-5)
    - Parameters: updates (required) - List of MetadataUpdateRequest objects

    organize_tags: AI-powered tag organization
    - Uses similarity matching to identify duplicate tags
    - Suggests tag hierarchies
    - Provides cleanup recommendations
    - Returns tag statistics and organization suggestions
    - Parameters: None required

    fix_issues: Automatic metadata fixes
    - Fixes missing dates
    - Standardizes author names
    - Corrects publication information
    - Resolves other common metadata issues
    - Returns results of automatic fixes
    - Parameters: None required

    Prerequisites:
        - Library must be accessible (auto-loaded on server startup)
        - For 'update' operation: Books must exist (book_id must be valid)

    Parameters:
        operation: The operation to perform. Must be one of: "update", "organize_tags", "fix_issues"

        # Update operation parameters
        updates: List of metadata update requests (required for operation="update")
                 Each request contains:
                 - book_id: ID of the book to update
                 - field: Name of the field to update (e.g., "title", "series_index", "tag_ids")
                 - value: New value for the field (type depends on field)

    Returns:
        Dictionary containing operation-specific results:

        For operation="update":
            {
                "updated_books": List[int] - IDs of successfully updated books
                "failed_updates": List[Dict] - Failed updates with error details
                "success_count": int - Number of successful updates
            }

        For operation="organize_tags":
            TagStatsResponse: Tag organization suggestions and cleanup stats

        For operation="fix_issues":
            MetadataUpdateResponse: Results of automatic metadata fixes

    Usage:
        # Update a book's title
        result = await manage_metadata(
            operation="update",
            updates=[{"book_id": 123, "field": "title", "value": "New Title"}]
        )

        # Update multiple fields for one book
        result = await manage_metadata(
            operation="update",
            updates=[
                {"book_id": 123, "field": "title", "value": "New Title"},
                {"book_id": 123, "field": "series_index", "value": 2.0},
                {"book_id": 123, "field": "rating", "value": 5}
            ]
        )

        # Bulk update multiple books
        result = await manage_metadata(
            operation="update",
            updates=[
                {"book_id": 123, "field": "tag_ids", "value": [1, 2, 3]},
                {"book_id": 124, "field": "tag_ids", "value": [1, 2, 3]},
                {"book_id": 125, "field": "tag_ids", "value": [1, 2, 3]}
            ]
        )

        # Organize tags
        result = await manage_metadata(operation="organize_tags")

        # Fix metadata issues
        result = await manage_metadata(operation="fix_issues")

    Examples:
        # Update book rating
        result = await manage_metadata(
            operation="update",
            updates=[{"book_id": 123, "field": "rating", "value": 5}]
        )

        # Update publication date
        result = await manage_metadata(
            operation="update",
            updates=[{"book_id": 123, "field": "pubdate", "value": "2024-01-01"}]
        )

        # Get tag organization suggestions
        result = await manage_metadata(operation="organize_tags")

        # Automatically fix metadata issues
        result = await manage_metadata(operation="fix_issues")

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "update", "organize_tags", "fix_issues"
        - Missing updates (update operation): Provide updates parameter for update operation
        - Invalid book_id: Verify book exists using query_books() or manage_books()
        - Invalid field value: Check field requirements (e.g., rating must be 1-5)
        - Invalid date format: Use ISO format (YYYY-MM-DD) for dates

    See Also:
        - manage_books(): For book management operations
        - manage_tags(): For tag management operations
        - manage_comments(): For comment CRUD operations
        - query_books(): For finding books to update
    """
    try:
        if operation == "update":
            if not updates:
                return format_error_response(
                    error_msg=(
                        "updates is required for operation='update'. "
                        "Provide a list of metadata update requests."
                    ),
                    error_code="MISSING_UPDATES",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide updates parameter (e.g., updates=[{'book_id': 123, 'field': 'title', 'value': 'New Title'}])",
                        "Each update request must contain: book_id, field, value",
                    ],
                    related_tools=["manage_metadata"],
                )
            try:
                result = await metadata_management.update_book_metadata_helper(updates)
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"updates": updates},
                    tool_name="manage_metadata",
                    context="Updating book metadata",
                )

        elif operation == "organize_tags":
            try:
                result = await metadata_management.auto_organize_tags_helper()
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_metadata",
                    context="Organizing tags with AI-powered analysis",
                )

        elif operation == "fix_issues":
            try:
                result = await metadata_management.fix_metadata_issues_helper()
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_metadata",
                    context="Automatically fixing metadata issues",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'update', 'organize_tags', 'fix_issues'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='update' to update book metadata",
                    "Use operation='organize_tags' for AI-powered tag organization",
                    "Use operation='fix_issues' to automatically fix metadata problems",
                ],
                related_tools=["manage_metadata"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={"operation": operation, "updates": updates},
            tool_name="manage_metadata",
            context="Metadata management operation",
        )

