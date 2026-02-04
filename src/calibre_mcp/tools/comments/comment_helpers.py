"""
Helper functions for comment CRUD operations.

These functions are NOT registered as MCP tools - they are called by
the manage_comments portmanteau tool.
"""

from typing import Any

from ...calibre_api import CalibreAPIError
from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.comments")


def _normalize_comment(comment: Any) -> str:
    """
    Normalize comment format from Calibre API.

    Calibre returns comments in various formats:
    - String: "comment text"
    - List: [{"text": "comment text"}]
    - None/empty: None or ""

    Returns normalized string format.
    """
    if comment is None:
        return ""
    if isinstance(comment, str):
        return comment
    if isinstance(comment, list) and comment:
        # Handle list format: [{"text": "..."}]
        if isinstance(comment[0], dict) and "text" in comment[0]:
            return comment[0]["text"]
        return str(comment[0])
    return str(comment) if comment else ""


async def create_comment_helper(book_id: int, text: str) -> dict[str, Any]:
    """
    Create a new comment for a book.

    Args:
        book_id: ID of the book
        text: Comment text to create

    Returns:
        Dictionary with created comment information

    Raises:
        CalibreAPIError: If book not found or API error occurs
    """
    try:
        from ...server import get_api_client

        if not text or not text.strip():
            raise ValueError("Comment text cannot be empty")

        client = await get_api_client()
        if not client:
            raise CalibreAPIError("Calibre API client not available")

        # Verify book exists
        book_data = await client.get_book_details(book_id)
        if not book_data:
            raise CalibreAPIError(f"Book with id {book_id} not found")

        # Update book metadata with comment
        # Calibre API updates comments via book metadata endpoint
        update_data = {"comments": text}
        await client._make_request(
            f"book/{book_id}",
            method="PUT",
            json_data=update_data,
        )

        logger.info(
            f"Created comment for book {book_id}",
            extra={"book_id": book_id, "text_length": len(text)},
        )

        return {
            "success": True,
            "book_id": book_id,
            "comment": {
                "book_id": book_id,
                "text": text,
            },
            "message": "Comment created successfully",
        }

    except ValueError as e:
        logger.error(f"Validation error creating comment: {e}", exc_info=True)
        raise
    except CalibreAPIError:
        raise
    except Exception as e:
        logger.error(
            f"Error creating comment for book {book_id}: {e}",
            extra={"book_id": book_id},
            exc_info=True,
        )
        raise CalibreAPIError(f"Failed to create comment: {str(e)}")


async def read_comment_helper(book_id: int) -> dict[str, Any]:
    """
    Read comment for a book.

    Args:
        book_id: ID of the book

    Returns:
        Dictionary with comment information, or empty if no comment exists

    Raises:
        CalibreAPIError: If book not found or API error occurs
    """
    try:
        from ...server import get_api_client

        client = await get_api_client()
        if not client:
            raise CalibreAPIError("Calibre API client not available")

        # Get book details which includes comments
        book_data = await client.get_book_details(book_id)
        if not book_data:
            raise CalibreAPIError(f"Book with id {book_id} not found")

        # Extract and normalize comment
        comment_raw = book_data.get("comments")
        comment_text = _normalize_comment(comment_raw)

        logger.info(
            f"Read comment for book {book_id}",
            extra={"book_id": book_id, "has_comment": bool(comment_text)},
        )

        if not comment_text:
            return {
                "success": True,
                "book_id": book_id,
                "comment": None,
                "message": "No comment found for this book",
            }

        return {
            "success": True,
            "book_id": book_id,
            "comment": {
                "book_id": book_id,
                "text": comment_text,
            },
        }

    except CalibreAPIError:
        raise
    except Exception as e:
        logger.error(
            f"Error reading comment for book {book_id}: {e}",
            extra={"book_id": book_id},
            exc_info=True,
        )
        raise CalibreAPIError(f"Failed to read comment: {str(e)}")


async def update_comment_helper(book_id: int, text: str) -> dict[str, Any]:
    """
    Update comment for a book (upsert behavior - creates if doesn't exist).

    Args:
        book_id: ID of the book
        text: New comment text

    Returns:
        Dictionary with updated comment information

    Raises:
        CalibreAPIError: If book not found or API error occurs
    """
    try:
        from ...server import get_api_client

        if not text or not text.strip():
            raise ValueError("Comment text cannot be empty")

        client = await get_api_client()
        if not client:
            raise CalibreAPIError("Calibre API client not available")

        # Verify book exists
        book_data = await client.get_book_details(book_id)
        if not book_data:
            raise CalibreAPIError(f"Book with id {book_id} not found")

        # Update book metadata with new comment
        update_data = {"comments": text}
        await client._make_request(
            f"book/{book_id}",
            method="PUT",
            json_data=update_data,
        )

        logger.info(
            f"Updated comment for book {book_id}",
            extra={"book_id": book_id, "text_length": len(text)},
        )

        return {
            "success": True,
            "book_id": book_id,
            "comment": {
                "book_id": book_id,
                "text": text,
            },
            "message": "Comment updated successfully",
        }

    except ValueError as e:
        logger.error(f"Validation error updating comment: {e}", exc_info=True)
        raise
    except CalibreAPIError:
        raise
    except Exception as e:
        logger.error(
            f"Error updating comment for book {book_id}: {e}",
            extra={"book_id": book_id},
            exc_info=True,
        )
        raise CalibreAPIError(f"Failed to update comment: {str(e)}")


async def delete_comment_helper(book_id: int) -> dict[str, Any]:
    """
    Delete comment for a book.

    Args:
        book_id: ID of the book

    Returns:
        Dictionary with deletion confirmation

    Raises:
        CalibreAPIError: If book not found or API error occurs
    """
    try:
        from ...server import get_api_client

        client = await get_api_client()
        if not client:
            raise CalibreAPIError("Calibre API client not available")

        # Verify book exists
        book_data = await client.get_book_details(book_id)
        if not book_data:
            raise CalibreAPIError(f"Book with id {book_id} not found")

        # Delete comment by setting it to empty string
        update_data = {"comments": ""}
        await client._make_request(
            f"book/{book_id}",
            method="PUT",
            json_data=update_data,
        )

        logger.info(f"Deleted comment for book {book_id}", extra={"book_id": book_id})

        return {
            "success": True,
            "book_id": book_id,
            "message": "Comment deleted successfully",
        }

    except CalibreAPIError:
        raise
    except Exception as e:
        logger.error(
            f"Error deleting comment for book {book_id}: {e}",
            extra={"book_id": book_id},
            exc_info=True,
        )
        raise CalibreAPIError(f"Failed to delete comment: {str(e)}")


async def append_comment_helper(book_id: int, text: str) -> dict[str, Any]:
    """
    Append text to existing comment for a book.

    If no comment exists, creates a new comment with the provided text.

    Args:
        book_id: ID of the book
        text: Text to append to existing comment

    Returns:
        Dictionary with updated comment information

    Raises:
        CalibreAPIError: If book not found or API error occurs
    """
    try:
        from ...server import get_api_client

        if not text or not text.strip():
            raise ValueError("Append text cannot be empty")

        client = await get_api_client()
        if not client:
            raise CalibreAPIError("Calibre API client not available")

        # Get existing comment
        book_data = await client.get_book_details(book_id)
        if not book_data:
            raise CalibreAPIError(f"Book with id {book_id} not found")

        # Get existing comment text
        comment_raw = book_data.get("comments")
        existing_text = _normalize_comment(comment_raw)

        # Append new text
        if existing_text:
            new_text = f"{existing_text}\n\n{text}"
        else:
            new_text = text

        # Update with appended text
        update_data = {"comments": new_text}
        await client._make_request(
            f"book/{book_id}",
            method="PUT",
            json_data=update_data,
        )

        logger.info(
            f"Appended to comment for book {book_id}",
            extra={"book_id": book_id, "appended_length": len(text)},
        )

        return {
            "success": True,
            "book_id": book_id,
            "comment": {
                "book_id": book_id,
                "text": new_text,
            },
            "message": "Comment appended successfully",
        }

    except ValueError as e:
        logger.error(f"Validation error appending comment: {e}", exc_info=True)
        raise
    except CalibreAPIError:
        raise
    except Exception as e:
        logger.error(
            f"Error appending comment for book {book_id}: {e}",
            extra={"book_id": book_id},
            exc_info=True,
        )
        raise CalibreAPIError(f"Failed to append comment: {str(e)}")
