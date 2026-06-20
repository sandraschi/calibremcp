"""
Helper functions for bulk operations.

These functions are NOT registered as MCP tools - they are called by
the manage_bulk_operations portmanteau tool.
"""

from typing import Any

from ...logging_config import get_logger
from ..shared.error_handling import format_error_response

# Import the deprecated BulkOperationsTool as a helper
from .bulk_operations import BulkOperationsTool

logger = get_logger("calibremcp.tools.bulk_operations")

# Create a singleton instance for helper functions
_bulk_tool_instance = None


def _get_bulk_tool() -> BulkOperationsTool:
    """Get or create the BulkOperationsTool instance."""
    global _bulk_tool_instance
    if _bulk_tool_instance is None:
        _bulk_tool_instance = BulkOperationsTool()
    return _bulk_tool_instance


async def update_metadata_helper(
    book_ids: list[int | str],
    updates: dict[str, Any],
    library_path: str | None = None,
    batch_size: int = 10,
) -> dict[str, Any]:
    """Helper to update metadata for multiple books."""
    try:
        tool = _get_bulk_tool()
        return await tool.bulk_update_metadata(
            book_ids=book_ids, updates=updates, library_path=library_path, batch_size=batch_size
        )
    except Exception as e:
        logger.error(f"Error updating metadata: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to update metadata: {str(e)}",
            error_code="UPDATE_METADATA_ERROR",
            error_type=type(e).__name__,
            operation="update_metadata",
        )


async def export_helper(
    book_ids: list[int | str],
    export_path: str,
    library_path: str | None = None,
    format: str = "directory",
) -> dict[str, Any]:
    """Helper to export multiple books."""
    try:
        tool = _get_bulk_tool()
        return await tool.bulk_export(
            book_ids=book_ids, export_path=export_path, library_path=library_path, format=format
        )
    except Exception as e:
        logger.error(f"Error exporting books: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to export books: {str(e)}",
            error_code="EXPORT_ERROR",
            error_type=type(e).__name__,
            operation="export",
        )


async def delete_helper(
    book_ids: list[int | str],
    library_path: str | None = None,
    delete_files: bool = True,
) -> dict[str, Any]:
    """Helper to delete multiple books."""
    try:
        tool = _get_bulk_tool()
        return await tool.bulk_delete(
            book_ids=book_ids, library_path=library_path, delete_files=delete_files
        )
    except Exception as e:
        logger.error(f"Error deleting books: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to delete books: {str(e)}",
            error_code="DELETE_ERROR",
            error_type=type(e).__name__,
            operation="delete",
        )


async def convert_helper(
    book_ids: list[int | str],
    target_format: str,
    library_path: str | None = None,
    output_path: str | None = None,
) -> dict[str, Any]:
    """Helper to convert multiple books."""
    try:
        tool = _get_bulk_tool()
        return await tool.bulk_convert(
            book_ids=book_ids,
            target_format=target_format,
            library_path=library_path,
            output_path=output_path,
        )
    except Exception as e:
        logger.error(f"Error converting books: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to convert books: {str(e)}",
            error_code="CONVERT_ERROR",
            error_type=type(e).__name__,
            operation="convert",
        )
