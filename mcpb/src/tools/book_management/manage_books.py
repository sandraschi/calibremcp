"""
Book management portmanteau tool for CalibreMCP.

Consolidates add_book, get_book, update_book, and delete_book
into a single portmanteau tool with operation parameter.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error

# Import the individual tool implementations (helper functions, not registered as MCP tools)
from .add_book import add_book_helper
from .delete_book import delete_book_helper
from .get_book import get_book_helper
from .update_book import update_book_helper

logger = get_logger("calibremcp.tools.book_management")


@mcp.tool()
async def manage_books(
    operation: str,
    book_id: str | None = None,
    file_path: str | None = None,
    metadata: dict[str, Any] | None = None,
    fetch_metadata: bool = True,
    convert_to: str | None = None,
    include_metadata: bool = True,
    include_formats: bool = True,
    include_cover: bool = False,
    status: str | None = None,
    progress: float | None = None,
    cover_path: str | None = None,
    update_timestamp: bool = True,
    delete_files: bool = True,
    force: bool = False,
    library_path: str | None = None,
) -> dict[str, Any]:
    """
    Unified interface for book CRUD operations in Calibre.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates book addition, retrieval, metadata updates, and deletion into a single tool.
    Simplifies book lifecycle management and reduces tool discovery overhead for agents.

    OPERATIONS:
    - add: Add a new book from file (requires file_path).
    - get: Retrieve basic book info by book_id.
    - details: Get full metadata and file information by book_id.
    - update: Update book metadata, status, or progress.
    - delete: Remove a book from the library.

    Returns:
    FastMCP 3.1+ dialogic response: success, operation, result or error,
    recommendations, next_steps, and execution_time_ms.
    Enables iterative refinement of book metadata and library content.
    """
    try:
        if operation == "add":
            if not file_path:
                return format_error_response(
                    error_msg=(
                        "file_path is required for operation='add'. "
                        "Provide the path to the book file you want to add to the library."
                    ),
                    error_code="MISSING_FILE_PATH",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide the file_path parameter with the path to the book file",
                        "Example: file_path='/path/to/book.epub'",
                        "Supported formats: epub, pdf, mobi, azw3, txt, html",
                        "Verify the file exists and is accessible",
                    ],
                    related_tools=["manage_books"],
                )
            try:
                return await add_book_helper(
                    file_path=file_path,
                    metadata=metadata,
                    fetch_metadata=fetch_metadata,
                    convert_to=convert_to,
                    library_path=library_path,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"file_path": file_path, "fetch_metadata": fetch_metadata},
                    tool_name="manage_books",
                    context="Adding new book to library",
                )

        elif operation == "get":
            if not book_id:
                return format_error_response(
                    error_msg=(
                        "book_id is required for operation='get'. "
                        "Use query_books() to find books and get their book_id values."
                    ),
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide the book_id parameter (e.g., book_id='123')",
                        "Use query_books(operation='search', author='Author Name') to find books",
                        "Use query_books(operation='list', limit=10) to see available books",
                    ],
                    related_tools=["query_books", "manage_books"],
                )
            try:
                return await get_book_helper(
                    book_id=book_id,
                    include_metadata=include_metadata,
                    include_formats=include_formats,
                    include_cover=include_cover,
                    library_path=library_path,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id},
                    tool_name="manage_books",
                    context=f"Retrieving book details for book_id={book_id}",
                )

        elif operation == "details":
            if not book_id:
                return format_error_response(
                    error_msg=(
                        "book_id is required for operation='details'. "
                        "Use query_books() to find books and get their book_id values."
                    ),
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide the book_id parameter (e.g., book_id='123')",
                        "Use query_books(operation='search', author='Author Name') to find books",
                        "Use query_books(operation='list', limit=10) to see available books",
                    ],
                    related_tools=["query_books", "manage_books"],
                )
            try:
                from ...server import BookDetailResponse, current_library, get_api_client

                client = await get_api_client()
                book_data = await client.get_book_details(int(book_id))

                if not book_data:
                    return {
                        "success": False,
                        "error": f"Book with id {book_id} not found",
                        "book_id": book_id,
                    }

                return {
                    "success": True,
                    "book": BookDetailResponse(
                        book_id=int(book_id),
                        title=book_data.get("title", "Unknown"),
                        authors=book_data.get("authors", []),
                        series=book_data.get("series"),
                        series_index=book_data.get("series_index"),
                        rating=book_data.get("rating"),
                        tags=book_data.get("tags", []),
                        comments=book_data.get("comments"),
                        published=book_data.get("published"),
                        languages=book_data.get("languages", ["en"]),
                        formats=book_data.get("formats", []),
                        identifiers=book_data.get("identifiers", {}),
                        last_modified=book_data.get("last_modified"),
                        cover_url=book_data.get("cover_url"),
                        download_links=book_data.get("download_links", {}),
                        library_name=current_library,
                    ).dict(),
                }
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id},
                    tool_name="manage_books",
                    context=f"Retrieving complete book details for book_id={book_id}",
                )

        elif operation == "update":
            if not book_id:
                return format_error_response(
                    error_msg=(
                        "book_id is required for operation='update'. "
                        "Use query_books() to find books and get their book_id values."
                    ),
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide the book_id parameter of the book to update",
                        "Use query_books(operation='search') to find books and get their IDs",
                    ],
                    related_tools=["query_books", "manage_books"],
                )
            try:
                return await update_book_helper(
                    book_id=book_id,
                    metadata=metadata,
                    status=status,
                    progress=progress,
                    cover_path=cover_path,
                    update_timestamp=update_timestamp,
                    library_path=library_path,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "metadata": metadata},
                    tool_name="manage_books",
                    context=f"Updating book metadata for book_id={book_id}",
                )

        elif operation == "delete":
            if not book_id:
                return format_error_response(
                    error_msg=(
                        "book_id is required for operation='delete'. "
                        "Use query_books() to find books and get their book_id values."
                    ),
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide the book_id parameter of the book to delete",
                        "Use query_books(operation='search') to find books and get their IDs",
                        "Warning: Deletion is permanent. Use force=True to skip dependency checks.",
                    ],
                    related_tools=["query_books", "manage_books"],
                )
            try:
                return await delete_book_helper(
                    book_id=book_id,
                    delete_files=delete_files,
                    force=force,
                    library_path=library_path,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "delete_files": delete_files, "force": force},
                    tool_name="manage_books",
                    context=f"Deleting book with book_id={book_id}",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: 'add', 'get', 'details', 'update', 'delete'. "
                    f"Received: '{operation}'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='add' to add a new book to the library",
                    "Use operation='get' to retrieve book information",
                    "Use operation='details' to get complete metadata and file information",
                    "Use operation='update' to update book metadata",
                    "Use operation='delete' to delete a book from the library",
                ],
                related_tools=["manage_books"],
            )

    except Exception as e:
        # Catch any unexpected errors at the top level
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "book_id": book_id,
                "file_path": file_path,
            },
            tool_name="manage_books",
            context="Book management operation",
        )
