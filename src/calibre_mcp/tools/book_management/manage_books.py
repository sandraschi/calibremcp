"""
Book management portmanteau tool for CalibreMCP.

Consolidates add_book, get_book, update_book, and delete_book
into a single portmanteau tool with operation parameter.
"""

from typing import Optional, Dict, Any

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response

# Import the individual tool implementations (helper functions, not registered as MCP tools)
from .add_book import add_book_helper
from .get_book import get_book_helper
from .update_book import update_book_helper
from .delete_book import delete_book_helper

logger = get_logger("calibremcp.tools.book_management")


@mcp.tool()
async def manage_books(
    operation: str,
    book_id: Optional[str] = None,
    file_path: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    fetch_metadata: bool = True,
    convert_to: Optional[str] = None,
    include_metadata: bool = True,
    include_formats: bool = True,
    include_cover: bool = False,
    status: Optional[str] = None,
    progress: Optional[float] = None,
    cover_path: Optional[str] = None,
    update_timestamp: bool = True,
    delete_files: bool = True,
    force: bool = False,
    library_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Manage books in the Calibre library with multiple operations in a single unified interface.

    This portmanteau tool consolidates all book management operations (adding, retrieving,
    updating, and deleting books) into a single interface. Use the `operation` parameter
    to select which operation to perform.

    Operations:
    - add: Add a new book to the library from a file or URL
    - get: Retrieve detailed information about a specific book
    - update: Update a book's metadata and properties
    - delete: Delete a book from the library

    Prerequisites:
        - For 'add': Book file must exist and be accessible
        - For 'get', 'update', 'delete': Book must exist (book_id required)
        - Library must be accessible (library_path will be auto-detected if not provided)

    Parameters:
        operation: The operation to perform. Must be one of: "add", "get", "update", "delete"
            - "add": Add a new book. Requires `file_path` parameter.
            - "get": Retrieve book information. Requires `book_id` parameter.
            - "update": Update book metadata. Requires `book_id` parameter, `metadata` optional.
            - "delete": Delete a book. Requires `book_id` parameter.

        book_id: ID of the book (required for 'get', 'update', 'delete')
            - Can be numeric ID or UUID
            - Use search_books() to find book IDs
            - Example: "123" or "550e8400-e29b-41d4-a716-446655440000"

        file_path: Path to the book file to add (required for 'add')
            - Must be a valid file path
            - Supported formats: epub, pdf, mobi, azw3, txt, html
            - Example: "/path/to/book.epub"

        metadata: Metadata dictionary (optional, used by 'add' and 'update')
            - For 'add': Overrides extracted metadata
            - For 'update': Fields to update (title, authors, tags, etc.)
            - Example: {"title": "New Title", "authors": ["Author Name"]}

        fetch_metadata: Whether to fetch metadata from online sources (for 'add', default: True)

        convert_to: Convert book to this format before adding (for 'add', optional)
            - Supported: epub, pdf, mobi, azw3, txt, html

        include_metadata: Include full metadata in response (for 'get', default: True)

        include_formats: Include format information in response (for 'get', default: True)

        include_cover: Include cover image data in response (for 'get', default: False)

        status: Reading status to set (for 'update', optional)
            - Values: "unread", "reading", "finished", "abandoned"

        progress: Reading progress 0.0 to 1.0 (for 'update', optional)

        cover_path: Path to new cover image (for 'update', optional)

        update_timestamp: Update last_modified timestamp (for 'update', default: True)

        delete_files: Delete book files from disk (for 'delete', default: True)

        force: Skip dependency checks (for 'delete', default: False)

        library_path: Path to Calibre library (optional, auto-detected if not provided)

    Returns:
        Dictionary containing operation-specific results:

        For operation="add":
            {
                "id": str - Book ID
                "title": str - Book title
                "authors": List[str] - Book authors
                "formats": List[str] - Available formats
                "cover_url": Optional[str] - Cover image URL
                "status": str - Reading status
                "progress": float - Reading progress
                "date_added": Optional[str] - ISO timestamp
            }

        For operation="get":
            {
                "id": str - Book ID
                "title": str - Book title
                "authors": List[str] - Book authors
                "has_cover": bool - Whether cover exists
                "timestamp": Optional[str] - ISO timestamp
                "last_modified": Optional[str] - ISO timestamp
                "path": Optional[str] - Book file path
                "uuid": str - Book UUID
                "formats": List[Dict] - Format information (if include_formats=True)
                "cover": Optional[Dict] - Cover data (if include_cover=True)
            }

        For operation="update":
            {
                "success": bool - Whether update succeeded
                "book_id": str - Book ID
                "updated_fields": List[str] - List of fields that were updated
                "book": Dict - Updated book information
            }

        For operation="delete":
            {
                "success": bool - Whether deletion succeeded
                "message": str - Status message
                "book_id": str - Deleted book ID
                "files_deleted": bool - Whether files were deleted
                "timestamp": str - Deletion timestamp
            }

    Usage:
        # Add a new book
        result = await manage_books(
            operation="add",
            file_path="/path/to/book.epub",
            metadata={"title": "My Book", "authors": ["Author Name"]}
        )
        print(f"Added book: {result['title']} (ID: {result['id']})")

        # Get book details
        result = await manage_books(
            operation="get",
            book_id="123",
            include_metadata=True,
            include_formats=True
        )
        print(f"Book: {result['title']} by {', '.join(result['authors'])}")

        # Update book metadata
        result = await manage_books(
            operation="update",
            book_id="123",
            metadata={"rating": 5, "tags": ["favorite", "scifi"]}
        )
        print(f"Updated: {result['updated_fields']}")

        # Delete a book
        result = await manage_books(
            operation="delete",
            book_id="123",
            delete_files=True
        )
        if result["success"]:
            print(f"Deleted: {result['message']}")

    Examples:
        # Add book with metadata override
        new_book = await manage_books(
            operation="add",
            file_path="/books/python-guide.epub",
            metadata={
                "title": "Python Programming Guide",
                "authors": ["John Doe"],
                "tags": ["programming", "python"]
            },
            fetch_metadata=True
        )

        # Get book with cover
        book_details = await manage_books(
            operation="get",
            book_id="123",
            include_metadata=True,
            include_cover=True
        )

        # Update reading progress
        update_result = await manage_books(
            operation="update",
            book_id="123",
            status="reading",
            progress=0.5
        )

        # Delete book without deleting files
        delete_result = await manage_books(
            operation="delete",
            book_id="123",
            delete_files=False
        )

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "add", "get", "update", "delete"
        - Missing book_id (get/update/delete): Provide book_id parameter
        - Missing file_path (add): Provide file_path parameter for adding books
        - Book not found: Verify book_id is correct using search_books()
        - File not found (add): Verify file_path exists and is accessible
        - Unsupported format: Use supported formats (epub, pdf, mobi, azw3, txt, html)

    See Also:
        - search_books(): Find books by query to get book_id
        - list_books(): List all books in the library
        - For individual operations: See add_book, get_book, update_book, delete_book
          (these are deprecated in favor of this portmanteau tool)
    """
    try:
        if operation == "add":
            if not file_path:
                return format_error_response(
                    error_msg=(
                        f"file_path is required for operation='add'. "
                        f"Provide the path to the book file you want to add to the library."
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
                        f"book_id is required for operation='get'. "
                        f"Use query_books() to find books and get their book_id values."
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

        elif operation == "update":
            if not book_id:
                return format_error_response(
                    error_msg=(
                        f"book_id is required for operation='update'. "
                        f"Use query_books() to find books and get their book_id values."
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
                        f"book_id is required for operation='delete'. "
                        f"Use query_books() to find books and get their book_id values."
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
                    f"Invalid operation: '{operation}'. Must be one of: 'add', 'get', 'update', 'delete'. "
                    f"Received: '{operation}'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='add' to add a new book to the library",
                    "Use operation='get' to retrieve book information",
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
