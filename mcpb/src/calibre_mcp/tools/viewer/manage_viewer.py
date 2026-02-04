"""
Viewer management portmanteau tool for CalibreMCP.

Consolidates all book viewer operations into a single unified interface.
"""

from pathlib import Path
from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ...services import book_service
from ...services.viewer_service import viewer_service
from ..shared.error_handling import format_error_response, handle_tool_error

logger = get_logger("calibremcp.tools.viewer")


@mcp.tool()
async def manage_viewer(
    operation: str,
    book_id: int,
    file_path: str,
    # Page-specific parameters
    page_number: int = 0,
    # State update parameters
    current_page: int | None = None,
    reading_direction: str | None = None,
    page_layout: str | None = None,
    zoom_mode: str | None = None,
    zoom_level: float | None = None,
) -> dict[str, Any]:
    """
    Manage book viewer operations in the Calibre library with multiple operations in a single unified interface.

    This portmanteau tool consolidates all viewer operations (opening books, getting pages,
    managing viewer state, and opening files) into a single interface. Use the `operation`
    parameter to select which operation to perform.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 7 separate tools (one per viewer operation), this tool consolidates related
    viewer operations into a single interface. This design:
    - Prevents tool explosion (7 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with viewer tasks
    - Enables consistent viewer interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - open: Open a book in the viewer and return metadata and initial state
    - get_page: Get a specific page from a book for display
    - get_metadata: Get comprehensive metadata for a book
    - get_state: Get the current viewer state (reading position, zoom, etc.)
    - update_state: Update viewer state (save reading progress and preferences)
    - close: Close a viewer session and clean up resources
    - open_file: Open a book file with the system's default application

    OPERATIONS DETAIL:

    open: Open a book in the viewer
    - Initializes a book viewer session
    - Returns metadata, current state, and first page content
    - Parameters: book_id (required), file_path (required)
    - Returns: metadata, state, pages (with total and first_page)

    get_page: Get a specific page
    - Retrieves page content, dimensions, and rendering information
    - Parameters: book_id (required), file_path (required), page_number (default: 0)
    - Returns: ViewerPage object with page content and metadata

    get_metadata: Get book metadata
    - Retrieves detailed metadata including page count, dimensions, format
    - Parameters: book_id (required), file_path (required)
    - Returns: ViewerMetadata object

    get_state: Get current viewer state
    - Retrieves saved reading position and viewer settings
    - Parameters: book_id (required), file_path (required)
    - Returns: ViewerState object with current_page, zoom, layout, etc.

    update_state: Update viewer state
    - Saves reading progress and preferences
    - All state parameters are optional - only provided values are updated
    - Parameters: book_id (required), file_path (required), current_page, reading_direction,
                  page_layout, zoom_mode, zoom_level (all optional)
    - Returns: Updated ViewerState object

    close: Close viewer session
    - Closes viewer and releases resources
    - State is preserved and can be restored when reopening
    - Parameters: book_id (required), file_path (required)
    - Returns: success status

    open_file: Open book file with default application
    - Launches book in default EPUB/PDF reader (Calibre Viewer, Adobe, Edge, etc.)
    - Parameters: book_id (required), file_path (required)
    - Returns: success status and file path

    Prerequisites:
        - Book must exist in library (book_id must be valid)
        - File path must exist and be accessible
        - For 'open_file': System must have default application for file type

    Parameters:
        operation: The operation to perform. Must be one of:
            "open", "get_page", "get_metadata", "get_state", "update_state", "close", "open_file"

        book_id: The unique identifier of the book in the Calibre library (required for all operations)

        file_path: Full path to the book file (PDF, EPUB, CBZ, CBR, etc.) (required for all operations)
                  Use query_books() to get valid format paths from book.formats[].path

        page_number: Zero-based page index to retrieve (for 'get_page' operation, default: 0)

        current_page: Zero-based page number to save as current position (for 'update_state', optional)

        reading_direction: Reading direction to save (for 'update_state', optional):
                          - "ltr" - Left-to-right (default for most languages)
                          - "rtl" - Right-to-left (Arabic, Hebrew)
                          - "vertical" - Vertical reading (some Asian languages)

        page_layout: Page layout mode to save (for 'update_state', optional):
                    - "single" - Display one page at a time
                    - "double" - Display two pages side-by-side (spread)
                    - "auto" - Automatically choose based on book format

        zoom_mode: Zoom mode to save (for 'update_state', optional):
                  - "fit-width" - Fit page width to viewer
                  - "fit-height" - Fit page height to viewer
                  - "fit-both" - Fit entire page to viewer
                  - "original" - Display at original size (100%)
                  - "custom" - Use custom zoom_level value

        zoom_level: Custom zoom level (for 'update_state', optional):
                   - 1.0 = 100%, 0.5 = 50%, 2.0 = 200%
                   - Range: 0.1 to 5.0
                   - Only used when zoom_mode is "custom"

    Returns:
        Dictionary containing operation-specific results:

        For operation="open":
            {
                "success": bool - Whether operation succeeded
                "metadata": dict - ViewerMetadata with book information
                "state": dict - ViewerState with current reading position
                "pages": dict - First page information with total and first_page
            }

        For operation="get_page":
            {
                "success": bool - Whether operation succeeded
                "book_id": int - Book identifier
                "file_path": str - Path to book file
                "page_number": int - Page number (0-based)
                "page_index": int - Display page number (1-based)
                "content": str - Page text content (if available)
                "image_url": str - URL/path to page image (if available)
                "width": int - Page width in pixels
                "height": int - Page height in pixels
                "has_text": bool - Whether page contains extractable text
                "is_blank": bool - Whether page is blank
            }

        For operation="get_metadata":
            {
                "success": bool - Whether operation succeeded
                "book_id": int - Book identifier
                "file_path": str - Path to book file
                "page_count": int - Total number of pages
                "format": str - File format (PDF, EPUB, etc.)
                "dimensions": dict - Page dimensions if available
                "title": str - Book title from metadata
                "author": str - Author name from metadata
                ... (other metadata fields)
            }

        For operation="get_state":
            {
                "success": bool - Whether operation succeeded
                "book_id": int - Book identifier
                "file_path": str - Path to book file
                "current_page": int - Current page number (0-based)
                "reading_direction": str - Reading direction
                "page_layout": str - Layout mode
                "zoom_mode": str - Zoom mode
                "zoom_level": float - Zoom level
                "last_updated": str - ISO timestamp of last update
            }

        For operation="update_state":
            {
                "success": bool - Whether operation succeeded
                ... (same fields as get_state with updated values)
            }

        For operation="close" or "open_file":
            {
                "success": bool - Whether operation succeeded
                "message": str - Status message (for open_file)
                "file_path": str - Actual file path opened (for open_file, if successful)
            }

    Usage:
        # Open a book in the viewer
        result = await manage_viewer(operation="open", book_id=123, file_path="/path/to/book.pdf")

        # Get a specific page
        result = await manage_viewer(operation="get_page", book_id=123, file_path="/path/to/book.pdf", page_number=42)

        # Save reading progress
        result = await manage_viewer(
            operation="update_state",
            book_id=123,
            file_path="/path/to/book.pdf",
            current_page=50,
            zoom_mode="fit-width"
        )

        # Open book in default application
        result = await manage_viewer(operation="open_file", book_id=123, file_path="/path/to/book.epub")

    Examples:
        # Open book and get initial data
        book_data = await manage_viewer(
            operation="open",
            book_id=123,
            file_path="/path/to/library/123/book.pdf"
        )
        print(f"Opened book with {book_data['pages']['total']} pages")

        # Get page 50 (49 in 0-based indexing)
        page = await manage_viewer(
            operation="get_page",
            book_id=123,
            file_path="/path/to/book.pdf",
            page_number=49
        )

        # Update reading position only
        state = await manage_viewer(
            operation="update_state",
            book_id=123,
            file_path="/path/to/book.pdf",
            current_page=42
        )

        # Update multiple settings at once
        state = await manage_viewer(
            operation="update_state",
            book_id=123,
            file_path="/path/to/book.pdf",
            current_page=50,
            zoom_mode="fit-width",
            reading_direction="ltr"
        )

        # Close viewer session
        result = await manage_viewer(
            operation="close",
            book_id=123,
            file_path="/path/to/book.pdf"
        )

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "open", "get_page", "get_metadata", "get_state", "update_state", "close", "open_file"
        - File not found: Verify file_path exists. Use query_books() to get valid format paths
        - Page out of range: Page numbers are 0-based (first page is 0). Check page_count from metadata
        - No viewer available: Supported formats are PDF, EPUB, CBZ, CBR. Check file extension
        - Permission denied (open_file): Check file permissions and default application association

    See Also:
        - query_books(): For finding books and getting file paths
        - manage_books(): For book management operations
    """
    try:
        # Validate file_path exists for operations that need it
        if operation != "close":  # close doesn't need file validation
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return format_error_response(
                    error_msg=f"Book file not found: {file_path}. Verify the file exists and the path is correct. Use query_books to get valid format paths.",
                    error_code="FILE_NOT_FOUND",
                    error_type="FileNotFoundError",
                    operation=operation,
                    suggestions=[
                        "Use query_books() to get valid file paths from book.formats[].path",
                        "Verify the book file exists at the specified path",
                        "Check that the file hasn't been moved or deleted",
                    ],
                    related_tools=["query_books", "manage_books"],
                )

        if operation == "open":
            try:
                metadata = viewer_service.get_metadata(book_id, file_path)
                state = viewer_service.get_state(book_id, file_path)

                return {
                    "success": True,
                    "metadata": metadata.dict(),
                    "state": state.dict(),
                    "pages": {
                        "total": metadata.page_count,
                        "first_page": viewer_service.get_page(book_id, file_path, 0).dict(),
                    },
                }
            except ValueError as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Opening book in viewer",
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Opening book in viewer",
                )

        elif operation == "get_page":
            try:
                page_obj = viewer_service.get_page(book_id, file_path, page_number)
                # Also get the rendered page content from the viewer
                viewer = viewer_service.get_viewer(book_id, file_path)
                page_data = viewer.render_page(page_number)

                return {
                    "success": True,
                    "book_id": book_id,
                    "file_path": file_path,
                    "page_number": page_number,
                    "page_index": page_number + 1,  # 1-based for display
                    "content": page_data.get("content", ""),
                    "image_url": page_obj.url,
                    "width": page_obj.width,
                    "height": page_obj.height,
                    "has_text": bool(page_data.get("text", "")),
                    "is_blank": False,  # Could be enhanced to detect blank pages
                }
            except IndexError:
                return format_error_response(
                    error_msg=f"Page {page_number} is out of range for book {book_id}. Page numbers are 0-based (first page is 0).",
                    error_code="PAGE_OUT_OF_RANGE",
                    error_type="IndexError",
                    operation=operation,
                    suggestions=[
                        "Use get_metadata to check total page count",
                        "Page numbers are 0-based (first page is 0, second page is 1, etc.)",
                        f"Valid page range for this book is 0 to {page_number - 1}",
                    ],
                    related_tools=["manage_viewer"],
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={
                        "book_id": book_id,
                        "file_path": file_path,
                        "page_number": page_number,
                    },
                    tool_name="manage_viewer",
                    context="Getting page from book",
                )

        elif operation == "get_metadata":
            try:
                return {
                    "success": True,
                    **viewer_service.get_metadata(book_id, file_path).dict(),
                }
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Getting book metadata",
                )

        elif operation == "get_state":
            try:
                return {
                    "success": True,
                    **viewer_service.get_state(book_id, file_path).dict(),
                }
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Getting viewer state",
                )

        elif operation == "update_state":
            try:
                state_updates = {}
                if current_page is not None:
                    state_updates["current_page"] = current_page
                if reading_direction is not None:
                    state_updates["reading_direction"] = reading_direction
                if page_layout is not None:
                    state_updates["page_layout"] = page_layout
                if zoom_mode is not None:
                    state_updates["zoom_mode"] = zoom_mode
                if zoom_level is not None:
                    state_updates["zoom_level"] = zoom_level

                return {
                    "success": True,
                    **viewer_service.update_state(book_id, file_path, **state_updates).dict(),
                }
            except ValueError as e:
                return format_error_response(
                    error_msg=f"Invalid viewer state parameter: {str(e)}. Check parameter values and ranges.",
                    error_code="INVALID_STATE_PARAMETER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Check that zoom_level is between 0.1 and 5.0",
                        "Verify reading_direction is one of: ltr, rtl, vertical",
                        "Verify page_layout is one of: single, double, auto",
                        "Verify zoom_mode is one of: fit-width, fit-height, fit-both, original, custom",
                    ],
                    related_tools=["manage_viewer"],
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={
                        "book_id": book_id,
                        "file_path": file_path,
                        "current_page": current_page,
                        "reading_direction": reading_direction,
                        "page_layout": page_layout,
                        "zoom_mode": zoom_mode,
                        "zoom_level": zoom_level,
                    },
                    tool_name="manage_viewer",
                    context="Updating viewer state",
                )

        elif operation == "close":
            try:
                viewer_service.close_viewer(book_id)
                return {"success": True}
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Closing viewer",
                )

        elif operation == "open_file":
            try:
                import os
                import platform
                import subprocess

                # If file_path is not provided or invalid, try to get it from book formats
                if not file_path or not Path(file_path).exists():
                    try:
                        book = book_service.get_by_id(book_id)
                        if book and book.get("formats"):
                            # Prefer EPUB, then PDF, then first available
                            preferred_formats = ["EPUB", "PDF", "MOBI", "AZW3"]
                            for fmt_name in preferred_formats:
                                for fmt in book["formats"]:
                                    if fmt.get("format", "").upper() == fmt_name:
                                        file_path = fmt.get("path")
                                        if file_path and Path(file_path).exists():
                                            break
                                if file_path and Path(file_path).exists():
                                    break

                            # If still no valid path, use first format
                            if (not file_path or not Path(file_path).exists()) and book["formats"]:
                                file_path = book["formats"][0].get("path")
                    except Exception as e:
                        # Log the error but continue with original file_path
                        logger.warning(
                            f"Could not get book format info for book_id={book_id}, "
                            f"continuing with provided file_path",
                            extra={
                                "book_id": book_id,
                                "error_type": type(e).__name__,
                                "error": str(e),
                            },
                            exc_info=True,
                        )

                if not file_path:
                    return format_error_response(
                        error_msg=f"Cannot open book {book_id}: No file path provided and could not get from book formats. Use query_books to get format paths first.",
                        error_code="NO_FILE_PATH",
                        error_type="ValueError",
                        operation=operation,
                        suggestions=[
                            "Use query_books() to get valid file paths from book.formats[].path",
                            "Provide file_path parameter with full path to book file",
                        ],
                        related_tools=["query_books"],
                    )

                file_path_obj = Path(file_path)

                # Normalize path separators for Windows
                if platform.system() == "Windows":
                    file_path_str = str(file_path_obj.resolve())
                else:
                    file_path_str = str(file_path_obj.absolute())

                # Verify file exists
                if not file_path_obj.exists():
                    return format_error_response(
                        error_msg=f"File not found: {file_path_str}. Check that the file exists and the path is correct. The file path should come from query_books results (formats[].path).",
                        error_code="FILE_NOT_FOUND",
                        error_type="FileNotFoundError",
                        operation=operation,
                        suggestions=[
                            "Use query_books() to get valid file paths",
                            "Verify the file hasn't been moved or deleted",
                        ],
                        related_tools=["query_books"],
                    )

                # Open file with system default application
                system = platform.system()

                if system == "Windows":
                    os.startfile(file_path_str)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", file_path_str], check=False)
                else:  # Linux and others
                    subprocess.run(["xdg-open", file_path_str], check=False)

                return {
                    "success": True,
                    "message": f"Opened {file_path_obj.name} with default application",
                    "file_path": file_path_str,
                }
            except PermissionError as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Opening book file with default application",
                )
            except OSError as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Opening book file with default application",
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "file_path": file_path},
                    tool_name="manage_viewer",
                    context="Opening book file with default application",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'open', 'get_page', 'get_metadata', 'get_state', 'update_state', 'close', 'open_file'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='open' to open a book in the viewer",
                    "Use operation='get_page' to get a specific page",
                    "Use operation='get_metadata' to get book metadata",
                    "Use operation='get_state' to get current viewer state",
                    "Use operation='update_state' to save reading progress",
                    "Use operation='close' to close a viewer session",
                    "Use operation='open_file' to open book in default application",
                ],
                related_tools=["manage_viewer"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "book_id": book_id,
                "file_path": file_path,
            },
            tool_name="manage_viewer",
            context="Viewer operation",
        )
