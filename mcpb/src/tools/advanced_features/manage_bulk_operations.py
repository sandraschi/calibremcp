"""
Bulk operations management portmanteau tool for CalibreMCP.

Consolidates all bulk operation functions into a single unified interface.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error

# Import helper functions (NOT registered as MCP tools)
from .bulk_operations_helpers import (
    convert_helper,
    delete_helper,
    export_helper,
    update_metadata_helper,
)

logger = get_logger("calibremcp.tools.bulk_operations")


@mcp.tool()
async def manage_bulk_operations(
    operation: str,
    # Common parameters
    book_ids: list[int | str] | None = None,
    library_path: str | None = None,
    # Update metadata parameters
    updates: dict[str, Any] | None = None,
    batch_size: int = 10,
    # Export parameters
    export_path: str | None = None,
    format: str = "directory",
    # Delete parameters
    delete_files: bool = True,
    # Convert parameters
    target_format: str | None = None,
    output_path: str | None = None,
) -> dict[str, Any]:
    """
    Comprehensive bulk operations tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating multiple separate tools, this tool consolidates related
    bulk operations into a single interface. This design:
    - Prevents tool explosion while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with bulk tasks
    - Enables consistent bulk interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - update_metadata: Update metadata for multiple books in bulk
    - export: Export multiple books to a specified location
    - delete: Delete multiple books from the library
    - convert: Convert multiple books to a different format

    OPERATIONS DETAIL:

    update_metadata: Bulk update metadata
    - Updates metadata fields for multiple books simultaneously
    - Processes books in batches to prevent system overload
    - Parameters: book_ids (required), updates (required), batch_size (default: 10)

    export: Bulk export books
    - Exports multiple books to a specified location
    - Supports directory and zip formats
    - Parameters: book_ids (required), export_path (required), format (default: "directory")

    delete: Bulk delete books
    - Deletes multiple books from the library
    - Optionally deletes associated files
    - Parameters: book_ids (required), delete_files (default: True)

    convert: Bulk convert books
    - Converts multiple books to a different format
    - Parameters: book_ids (required), target_format (required), output_path (optional)

    Prerequisites:
        - Library must be configured (use manage_libraries(operation='switch'))
        - For convert: Calibre conversion tools must be available

    Parameters:
        operation: The operation to perform. Must be one of:
            "update_metadata", "export", "delete", "convert"

        # Common parameters
        book_ids: List of book IDs to process (required for all operations)
        library_path: Path to library (optional)

        # Update metadata parameters
        updates: Dictionary of metadata fields to update (required for 'update_metadata')
        batch_size: Number of books to process in parallel (default: 10, for 'update_metadata')

        # Export parameters
        export_path: Path where to export books (required for 'export')
        format: Export format - 'directory' or 'zip' (default: "directory", for 'export')

        # Delete parameters
        delete_files: Whether to delete associated files (default: True, for 'delete')

        # Convert parameters
        target_format: Target format for conversion (required for 'convert')
        output_path: Output path for converted files (optional, for 'convert')

    Returns:
        Dictionary containing operation-specific results

    Usage:
        # Bulk update metadata
        result = await manage_bulk_operations(
            operation="update_metadata",
            book_ids=[1, 2, 3],
            updates={"rating": 5, "tags": ["favorite"]}
        )

        # Bulk export
        result = await manage_bulk_operations(
            operation="export",
            book_ids=[1, 2, 3],
            export_path="/path/to/export",
            format="zip"
        )

        # Bulk delete
        result = await manage_bulk_operations(
            operation="delete",
            book_ids=[1, 2, 3],
            delete_files=True
        )

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of the supported operations listed above
        - Missing book_ids: Provide book_ids list for all operations
        - Missing required parameters: Provide all required parameters for the operation
    """
    try:
        if not book_ids:
            return format_error_response(
                error_msg="book_ids is required for all bulk operations",
                error_code="MISSING_BOOK_IDS",
                error_type="ValueError",
                operation=operation,
                suggestions=["Provide book_ids parameter (list of book IDs)"],
                related_tools=["manage_bulk_operations"],
            )

        if operation == "update_metadata":
            if not updates:
                return format_error_response(
                    error_msg="updates is required for operation='update_metadata'",
                    error_code="MISSING_UPDATES",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide updates parameter (dict of fields to update)"],
                    related_tools=["manage_bulk_operations"],
                )
            try:
                return await update_metadata_helper(
                    book_ids=book_ids,
                    updates=updates,
                    library_path=library_path,
                    batch_size=batch_size,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_ids": book_ids, "updates": updates},
                    tool_name="manage_bulk_operations",
                    context="Bulk updating metadata for multiple books",
                )

        elif operation == "export":
            if not export_path:
                return format_error_response(
                    error_msg="export_path is required for operation='export'",
                    error_code="MISSING_EXPORT_PATH",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide export_path parameter"],
                    related_tools=["manage_bulk_operations"],
                )
            try:
                return await export_helper(
                    book_ids=book_ids,
                    export_path=export_path,
                    library_path=library_path,
                    format=format,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_ids": book_ids, "export_path": export_path},
                    tool_name="manage_bulk_operations",
                    context="Bulk exporting books",
                )

        elif operation == "delete":
            try:
                return await delete_helper(
                    book_ids=book_ids, library_path=library_path, delete_files=delete_files
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_ids": book_ids, "delete_files": delete_files},
                    tool_name="manage_bulk_operations",
                    context="Bulk deleting books",
                )

        elif operation == "convert":
            if not target_format:
                return format_error_response(
                    error_msg="target_format is required for operation='convert'",
                    error_code="MISSING_TARGET_FORMAT",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide target_format parameter (e.g., 'epub', 'pdf')"],
                    related_tools=["manage_bulk_operations"],
                )
            try:
                return await convert_helper(
                    book_ids=book_ids,
                    target_format=target_format,
                    library_path=library_path,
                    output_path=output_path,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_ids": book_ids, "target_format": target_format},
                    tool_name="manage_bulk_operations",
                    context=f"Bulk converting books to {target_format}",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'update_metadata', 'export', 'delete', 'convert'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='update_metadata' to update metadata for multiple books",
                    "Use operation='export' to export multiple books",
                    "Use operation='delete' to delete multiple books",
                    "Use operation='convert' to convert multiple books",
                ],
                related_tools=["manage_bulk_operations"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "book_ids": book_ids,
            },
            tool_name="manage_bulk_operations",
            context="Bulk operation",
        )
