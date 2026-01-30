"""
User comment management portmanteau for CalibreMCP.

User comments are annotations/notes on books stored in CalibreMCP's own SQLite DB,
distinct from Calibre's description/comment field (the book synopsis).
"""

from typing import Optional, Dict, Any

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response
from ...services.user_comment_service import user_comment_service

logger = get_logger("calibremcp.tools.user_comments")


@mcp.tool()
async def manage_user_comments(
    operation: str,
    book_id: Optional[int] = None,
    text: Optional[str] = None,
    library_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Manage user comments (annotations) on books.

    User comments are stored in CalibreMCP's SQLite DB, separate from Calibre's
    description/comment field. Use this for personal notes, reading annotations, etc.

    PORTMANTEAU PATTERN: Consolidates create, read, update, delete, append operations.

    SUPPORTED OPERATIONS:
    - create: Create or overwrite user comment for a book
    - read: Get user comment for a book
    - update: Same as create (upsert)
    - delete: Remove user comment
    - append: Append text to existing comment

    Args:
        operation: One of "create", "read", "update", "delete", "append"
        book_id: Book ID (required for all operations)
        text: Comment text (required for create, update, append)
        library_path: Override library path (optional, uses current library by default)

    Returns:
        Operation-specific result dict with success, book_id, comment data.
    """
    try:
        if operation in ("create", "update"):
            if book_id is None:
                return format_error_response(
                    error_msg="book_id is required for create/update.",
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide book_id (integer)", "Use query_books to find book IDs"],
                    related_tools=["query_books"],
                )
            if not text or not str(text).strip():
                return format_error_response(
                    error_msg="text is required and cannot be empty for create/update.",
                    error_code="MISSING_TEXT",
                    error_type="ValueError",
                    operation=operation,
                    related_tools=["manage_user_comments"],
                )
            return user_comment_service.create_or_update(
                book_id=int(book_id),
                comment_text=str(text).strip(),
                library_path=library_path,
            )

        elif operation == "read":
            if book_id is None:
                return format_error_response(
                    error_msg="book_id is required for read.",
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    related_tools=["query_books"],
                )
            return user_comment_service.get(
                book_id=int(book_id),
                library_path=library_path,
            )

        elif operation == "delete":
            if book_id is None:
                return format_error_response(
                    error_msg="book_id is required for delete.",
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    related_tools=["query_books"],
                )
            return user_comment_service.delete(
                book_id=int(book_id),
                library_path=library_path,
            )

        elif operation == "append":
            if book_id is None:
                return format_error_response(
                    error_msg="book_id is required for append.",
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    related_tools=["query_books"],
                )
            if not text or not str(text).strip():
                return format_error_response(
                    error_msg="text is required for append.",
                    error_code="MISSING_TEXT",
                    error_type="ValueError",
                    operation=operation,
                    related_tools=["manage_user_comments"],
                )
            return user_comment_service.append(
                book_id=int(book_id),
                text_to_append=str(text).strip(),
                library_path=library_path,
            )

        else:
            return format_error_response(
                error_msg=f"Invalid operation: '{operation}'. Use: create, read, update, delete, append.",
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "create: Add or overwrite comment",
                    "read: Get comment for book",
                    "update: Same as create",
                    "delete: Remove comment",
                    "append: Add text to existing comment",
                ],
                related_tools=["manage_user_comments", "manage_comments"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={"book_id": book_id, "text": text[:50] + "..." if text and len(text) > 50 else text},
            tool_name="manage_user_comments",
            context="Managing user comments on books",
        )
