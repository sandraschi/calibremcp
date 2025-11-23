"""
Comment management portmanteau tool for CalibreMCP.

Consolidates all comment-related CRUD operations into a single unified interface.
"""

from typing import Optional, Dict, Any

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response

# Import helper functions (NOT registered as MCP tools)
from .comment_helpers import (
    create_comment_helper,
    read_comment_helper,
    update_comment_helper,
    delete_comment_helper,
    append_comment_helper,
)

logger = get_logger("calibremcp.tools.comments")


@mcp.tool()
async def manage_comments(
    operation: str,
    book_id: Optional[str] = None,
    text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Comprehensive comment management tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 5 separate tools (one per operation), this tool consolidates related
    comment operations into a single interface. This design:
    - Prevents tool explosion (5 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with comment management tasks
    - Enables consistent comment interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - create: Create a new comment for a book
    - read: Get comment(s) for a book
    - update: Update an existing comment (upsert - creates if doesn't exist)
    - delete: Delete a comment for a book
    - append: Append text to existing comment (creates if doesn't exist)
    - replace: Replace entire comment text (alias for update)

    OPERATIONS DETAIL:

    create: Create a new comment
    - Creates a new comment for the specified book
    - Requires book_id and text parameters
    - Returns error if comment already exists (use update instead)
    - Parameters: book_id (required), text (required)
    - Returns: Created comment information

    read: Get comment for a book
    - Retrieves the comment for the specified book
    - Returns None/empty if no comment exists
    - Handles both string and structured comment formats from Calibre
    - Parameters: book_id (required)
    - Returns: Comment information or None if no comment exists

    update: Update an existing comment
    - Updates comment for the specified book
    - Upsert behavior: creates comment if it doesn't exist
    - Replaces entire comment text with new text
    - Parameters: book_id (required), text (required)
    - Returns: Updated comment information

    delete: Delete a comment
    - Removes comment for the specified book
    - Sets comment to empty string (Calibre API behavior)
    - Parameters: book_id (required)
    - Returns: Deletion confirmation

    append: Append text to existing comment
    - Appends new text to existing comment
    - Creates comment if it doesn't exist
    - Adds new text with newline separator
    - Parameters: book_id (required), text (required)
    - Returns: Updated comment with appended text

    replace: Replace entire comment text
    - Alias for update operation
    - Replaces entire comment with new text
    - Parameters: book_id (required), text (required)
    - Returns: Updated comment information

    Prerequisites:
        - Library must be accessible (auto-loaded on server startup)
        - For all operations: Book must exist (book_id must be valid)
        - For create/update/append/replace: text parameter is required

    Parameters:
        operation: The operation to perform. Must be one of:
            "create", "read", "update", "delete", "append", "replace"

        book_id: ID of the book (required for all operations)
            - Can be numeric ID or UUID string
            - Example: "123" or "550e8400-e29b-41d4-a716-446655440000"
            - Use query_books() to find book IDs

        text: Comment text (required for create/update/append/replace operations)
            - For create/update/replace: Full comment text
            - For append: Text to append to existing comment
            - Cannot be empty or whitespace-only

    Returns:
        Dictionary containing operation-specific results:

        For operation="create":
            {
                "success": bool - Whether creation succeeded
                "book_id": int - ID of the book
                "comment": Dict - Created comment with book_id and text
                "message": str - Success message
            }

        For operation="read":
            {
                "success": bool - Whether read succeeded
                "book_id": int - ID of the book
                "comment": Optional[Dict] - Comment information (None if no comment exists)
                "message": Optional[str] - Message if no comment found
            }

        For operation="update" or "replace":
            {
                "success": bool - Whether update succeeded
                "book_id": int - ID of the book
                "comment": Dict - Updated comment with book_id and text
                "message": str - Success message
            }

        For operation="delete":
            {
                "success": bool - Whether deletion succeeded
                "book_id": int - ID of the book
                "message": str - Success message
            }

        For operation="append":
            {
                "success": bool - Whether append succeeded
                "book_id": int - ID of the book
                "comment": Dict - Updated comment with appended text
                "message": str - Success message
            }

    Usage:
        # Create a new comment
        result = await manage_comments(
            operation="create",
            book_id="123",
            text="This is a great book about Python programming."
        )

        # Read a comment
        result = await manage_comments(
            operation="read",
            book_id="123"
        )

        # Update a comment (replaces entire text)
        result = await manage_comments(
            operation="update",
            book_id="123",
            text="Updated comment text with new information."
        )

        # Append to existing comment
        result = await manage_comments(
            operation="append",
            book_id="123",
            text="Additional notes: This book covers advanced topics."
        )

        # Delete a comment
        result = await manage_comments(
            operation="delete",
            book_id="123"
        )

    Examples:
        # Create comment for a book
        result = await manage_comments(
            operation="create",
            book_id="123",
            text="Excellent introduction to machine learning concepts."
        )
        assert result["success"] is True
        assert result["comment"]["text"] == "Excellent introduction to machine learning concepts."

        # Read comment
        result = await manage_comments(operation="read", book_id="123")
        if result["comment"]:
            print(f"Comment: {result['comment']['text']}")
        else:
            print("No comment found for this book")

        # Update comment
        result = await manage_comments(
            operation="update",
            book_id="123",
            text="Revised review: This book is comprehensive and well-written."
        )

        # Append to comment
        result = await manage_comments(
            operation="append",
            book_id="123",
            text="\n\nUpdate: Finished reading. Highly recommended!"
        )

        # Delete comment
        result = await manage_comments(operation="delete", book_id="123")

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "create", "read", "update", "delete", "append", "replace"
        - Missing book_id: Provide book_id parameter for all operations
        - Missing text (create/update/append/replace): Provide text parameter for these operations
        - Book not found: Verify book_id is correct using query_books(operation="search")
        - Empty text: Text cannot be empty or whitespace-only
        - Comment already exists (create): Use update operation instead, or delete first

    See Also:
        - manage_books(): For book management operations (comments included in metadata)
        - query_books(): For finding books and searching comments
        - manage_metadata(): For bulk metadata updates (including comments)
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
            parameters={"operation": operation, "book_id": book_id, "text": text[:100] if text else None},
            tool_name="manage_comments",
            context="Comment management operation",
        )

