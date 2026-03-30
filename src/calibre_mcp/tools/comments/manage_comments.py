"""
Comment management portmanteau tool for CalibreMCP.

Consolidates all comment-related CRUD operations into a single unified interface.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error

# Import helper functions (NOT registered as MCP tools)
from .comment_helpers import (
    append_comment_helper,
    create_comment_helper,
    delete_comment_helper,
    read_comment_helper,
    update_comment_helper,
)

logger = get_logger("calibremcp.tools.comments")


@mcp.tool()
async def manage_comments(
    operation: str,
    book_id: str | None = None,
    text: str | None = None,
) -> dict[str, Any]:
    """
    Comprehensive comment management for Calibre books.

    Operations:
    - create: Create a new comment (fails if exists).
    - read: Retrieve existing comment text for a book.
    - update / replace: Overwrite existing comment (upserts).
    - delete: Remove the comment (sets to empty).
    - append: Add text to the end of an existing comment with a newline.

    Example:
    - manage_comments(operation="create", book_id="123", text="Initial review.")
    - manage_comments(operation="append", book_id="123", text="Update: still loving it.")
    """
    try:
        # Validate operation
        valid_operations = ["create", "read", "update", "delete", "append", "replace"]
        if operation not in valid_operations:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    f"{', '.join(valid_operations)}"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='create' to create a new comment",
                    "Use operation='read' to read a comment",
                    "Use operation='update' to update a comment",
                    "Use operation='delete' to delete a comment",
                    "Use operation='append' to append text to a comment",
                    "Use operation='replace' as an alias for update",
                ],
                related_tools=["manage_comments"],
            )

        # Validate book_id is provided
        if not book_id:
            return format_error_response(
                error_msg="book_id is required for all comment operations.",
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

        # Validate text is provided for operations that require it
        text_required_operations = ["create", "update", "append", "replace"]
        if operation in text_required_operations:
            if not text or not text.strip():
                return format_error_response(
                    error_msg=f"text is required for operation='{operation}'. Cannot be empty.",
                    error_code="MISSING_TEXT",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide the text parameter with comment content",
                        "For append: Provide text to append to existing comment",
                        "For update/replace: Provide new comment text",
                    ],
                    related_tools=["manage_comments"],
                )

        # Convert book_id to int for API calls
        try:
            book_id_int = int(book_id)
        except (ValueError, TypeError):
            return format_error_response(
                error_msg=f"Invalid book_id format: '{book_id}'. Must be a numeric ID.",
                error_code="INVALID_BOOK_ID",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Provide a numeric book_id (e.g., book_id='123')",
                    "Use query_books(operation='search') to find books and get their IDs",
                ],
                related_tools=["query_books"],
            )

        # Route to appropriate helper function
        if operation == "create":
            try:
                result = await create_comment_helper(book_id_int, text)
                return result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "text": text[:100] if text else None},
                    tool_name="manage_comments",
                    context=f"Creating comment for book_id={book_id}",
                )

        elif operation == "read":
            try:
                result = await read_comment_helper(book_id_int)
                return result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id},
                    tool_name="manage_comments",
                    context=f"Reading comment for book_id={book_id}",
                )

        elif operation == "update" or operation == "replace":
            try:
                result = await update_comment_helper(book_id_int, text)
                return result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "text": text[:100] if text else None},
                    tool_name="manage_comments",
                    context=f"Updating comment for book_id={book_id}",
                )

        elif operation == "delete":
            try:
                result = await delete_comment_helper(book_id_int)
                return result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id},
                    tool_name="manage_comments",
                    context=f"Deleting comment for book_id={book_id}",
                )

        elif operation == "append":
            try:
                result = await append_comment_helper(book_id_int, text)
                return result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"book_id": book_id, "text": text[:100] if text else None},
                    tool_name="manage_comments",
                    context=f"Appending to comment for book_id={book_id}",
                )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "book_id": book_id,
                "text": text[:100] if text else None,
            },
            tool_name="manage_comments",
            context="Comment management operation",
        )
