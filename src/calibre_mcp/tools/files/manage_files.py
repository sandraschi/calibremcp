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
    Comprehensive file operations tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 3 separate tools (one per operation), this tool consolidates related
    file operations into a single interface. This design:
    - Prevents tool explosion (3 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with file operations
    - Enables consistent file interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - convert: Convert books between different formats (EPUB, PDF, MOBI, etc.)
    - download: Download a book file in the specified format
    - bulk: Perform bulk operations on book formats (convert, validate, cleanup)

    OPERATIONS DETAIL:

    convert: Convert book formats
    - Handles format conversion requests for single or multiple books
    - Supports various input and output formats with quality options
    - Parameters: conversion_requests (required) - List of ConversionRequest objects

    download: Download book file
    - Retrieves and returns the file path for a book in the preferred format
    - If preferred format is not available, checks for alternative formats
    - Returns the best available match
    - Parameters: book_id (required), format_preference (optional, default: "EPUB")

    bulk: Bulk format operations
    - Supports bulk conversion, format validation, and cleanup operations
    - Efficient management of large book collections
    - Parameters: operation_type (required: "convert", "validate", "cleanup"),
                  target_format (required for convert), book_ids (optional)

    Prerequisites:
        - Library must be accessible (auto-loaded on server startup)
        - For 'download' and 'convert': Books must exist (book_id must be valid)
        - For 'convert': Calibre ebook-convert must be available

    Parameters:
        operation: The operation to perform. Must be one of: "convert", "download", "bulk"

        # Convert operation parameters
        conversion_requests: List of conversion requests (required for operation="convert")
                            Each request contains book_id, source_format, target_format, quality

        # Download operation parameters
        book_id: Book ID to download (required for operation="download")
        format_preference: Preferred file format (default: "EPUB")
                          Common formats: EPUB, PDF, MOBI, AZW3, TXT

        # Bulk operation parameters
        operation_type: Type of bulk operation (required for operation="bulk")
                       Must be one of: "convert", "validate", "cleanup"
        target_format: Target format for conversion (required for operation_type="convert")
        book_ids: List of book IDs to process (optional, processes all if None)

    Returns:
        Dictionary containing operation-specific results:

        For operation="convert":
            List[ConversionResponse]: Results of conversion operations

        For operation="download":
            {
                "book_id": int - ID of the book
                "format": str - Format of the returned file
                "file_path": str - Full path to the book file
                "size": int - File size in bytes
                "available_formats": List[str] - All formats available
                "format_found": bool - Whether preferred format was found
            }

        For operation="bulk":
            Dict[str, Any]: Results of bulk operations with statistics

    Usage:
        # Convert a book to PDF
        result = await manage_files(
            operation="convert",
            conversion_requests=[{
                "book_id": 123,
                "source_format": "EPUB",
                "target_format": "PDF",
                "quality": "high"
            }]
        )

        # Download book in preferred format
        result = await manage_files(
            operation="download",
            book_id=123,
            format_preference="EPUB"
        )

        # Bulk convert multiple books
        result = await manage_files(
            operation="bulk",
            operation_type="convert",
            target_format="PDF",
            book_ids=[123, 124, 125]
        )

    Examples:
        # Convert book to PDF
        result = await manage_files(
            operation="convert",
            conversion_requests=[{
                "book_id": 123,
                "target_format": "PDF"
            }]
        )

        # Download in PDF if available
        result = await manage_files(
            operation="download",
            book_id=123,
            format_preference="PDF"
        )

        # Bulk validate formats
        result = await manage_files(
            operation="bulk",
            operation_type="validate",
            book_ids=[123, 124, 125]
        )

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "convert", "download", "bulk"
        - Missing conversion_requests (convert): Provide conversion_requests parameter
        - Missing book_id (download): Provide book_id parameter for download operation
        - Missing operation_type (bulk): Provide operation_type parameter for bulk operation
        - Book not found: Verify book exists using query_books() or manage_books()
        - Format not available: Check available_formats in response

    See Also:
        - manage_books(): For book management operations
        - query_books(): For finding books to download/convert
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
