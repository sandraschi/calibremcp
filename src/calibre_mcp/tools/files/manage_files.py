"""
File operations portmanteau tool for CalibreMCP.

Consolidates all file-related operations into a single unified interface.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import ConversionRequest, mcp
from ..shared.error_handling import format_error_response, handle_tool_error

# Import helper functions (NOT registered as MCP tools)
from . import file_operations

logger = get_logger("calibremcp.tools.files")


@mcp.tool()
async def manage_files(
    operation: str,
    # Convert operation parameters
    conversion_requests: list[ConversionRequest] | None = None,
    # Download operation parameters
    book_id: int | None = None,
    format_preference: str = "EPUB",
    # Bulk operation parameters
    operation_type: str | None = None,
    target_format: str | None = None,
    book_ids: list[int] | None = None,
) -> dict[str, Any]:
    """
    Comprehensive book file management and format conversion.

    Operations:
    - convert: Transform books between formats (EPUB, PDF, AZW3, etc.).
    - download: Retrieve the local filesystem path for a specific book format.
    - bulk: Perform mass validation, cleanup, or conversion across multiple IDs.

    Example:
    - manage_files(operation="download", book_id=123, format_preference="PDF")
    - manage_files(operation="convert", conversion_requests=[{"book_id": 45, "target_format": "EPUB"}])
    """
    try:
        if operation == "convert":
            if not conversion_requests:
                return format_error_response(
                    error_msg=(
                        "conversion_requests is required for operation='convert'. "
                        "Provide a list of conversion requests."
                    ),
                    error_code="MISSING_CONVERSION_REQUESTS",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide conversion_requests parameter (e.g., conversion_requests=[{'book_id': 123, 'target_format': 'PDF'}])",
                        "Each request must contain: book_id, target_format (and optionally source_format, quality)",
                    ],
                    related_tools=["manage_files"],
                )
            try:
                result = await file_operations.convert_book_format_helper(conversion_requests)
                return result if isinstance(result, list) else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"conversion_requests": conversion_requests},
                    tool_name="manage_files",
                    context="Converting book formats",
                )

        elif operation == "download":
            if not book_id:
                return format_error_response(
                    error_msg=(
                        "book_id is required for operation='download'. "
                        "Provide the ID of the book to download."
                    ),
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide book_id parameter (e.g., book_id=123)",
                        "Use query_books() or manage_books() to find book IDs",
                    ],
                    related_tools=["manage_files"],
                )
            try:
                result = await file_operations.download_book_helper(book_id, format_preference)
                return result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "format_preference": format_preference},
                    tool_name="manage_files",
                    context=f"Downloading book {book_id} in {format_preference} format",
                )

        elif operation == "bulk":
            if not operation_type:
                return format_error_response(
                    error_msg=(
                        "operation_type is required for operation='bulk'. "
                        "Provide the type of bulk operation to perform."
                    ),
                    error_code="MISSING_OPERATION_TYPE",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide operation_type parameter (e.g., operation_type='convert')",
                        "Valid values: 'convert', 'validate', 'cleanup'",
                        "For 'convert', also provide target_format parameter",
                    ],
                    related_tools=["manage_files"],
                )
            try:
                result = await file_operations.bulk_format_operations_helper(
                    operation_type=operation_type,
                    target_format=target_format,
                    book_ids=book_ids,
                )
                return result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={
                        "operation_type": operation_type,
                        "target_format": target_format,
                        "book_ids": book_ids,
                    },
                    tool_name="manage_files",
                    context=f"Bulk format operation: {operation_type}",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'convert', 'download', 'bulk'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='convert' to convert book formats",
                    "Use operation='download' to download book files",
                    "Use operation='bulk' for bulk format operations",
                ],
                related_tools=["manage_files"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "book_id": book_id,
                "format_preference": format_preference,
                "operation_type": operation_type,
            },
            tool_name="manage_files",
            context="File operations",
        )
