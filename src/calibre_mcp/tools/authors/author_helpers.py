"""
Helper functions for author management operations.

These functions are NOT registered as MCP tools - they are called by
the manage_authors portmanteau tool.
"""

from typing import Any

from ...logging_config import get_logger
from ...services.author_service import author_service
from ..shared.error_handling import format_error_response

logger = get_logger("calibremcp.tools.authors")


async def list_authors_helper(
    query: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """
    Helper function to list authors with filtering and pagination.

    Args:
        query: Search term to filter authors by name (case-insensitive partial match)
        limit: Maximum number of results (1-1000, default: 50)
        offset: Results offset for pagination (default: 0)

    Returns:
        Dictionary with paginated author results
    """
    try:
        # Use search_authors method which handles async wrapper
        # The service method is sync, but we're calling it from async context
        result = author_service.get_all(
            skip=offset,
            limit=limit,
            search=query,
            sort_by="name",
            sort_order="asc",
        )
        return result
    except Exception as e:
        logger.error(f"Error listing authors: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to list authors: {str(e)}",
            error_code="LIST_AUTHORS_ERROR",
            error_type=type(e).__name__,
            operation="list",
        )


async def get_author_helper(author_id: int) -> dict[str, Any]:
    """
    Helper function to get author details by ID.

    Args:
        author_id: Author ID

    Returns:
        Dictionary with author details
    """
    try:
        author = author_service.get_by_id(author_id)
        return author
    except Exception as e:
        logger.error(f"Error getting author {author_id}: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Author with ID {author_id} not found: {str(e)}",
            error_code="AUTHOR_NOT_FOUND",
            error_type=type(e).__name__,
            operation="get",
            suggestions=[
                f"Verify author_id={author_id} is correct",
                "Use operation='list' to see all available authors",
            ],
        )


async def get_author_books_helper(
    author_id: int,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """
    Helper function to get books by author.

    Args:
        author_id: Author ID
        limit: Maximum number of books to return (default: 50)
        offset: Number of books to skip (for pagination)

    Returns:
        Dictionary with author info and paginated books
    """
    try:
        # Get author info first
        author = author_service.get_by_id(author_id)

        # Get author's books
        result = author_service.get_books_by_author(author_id=author_id, limit=limit, offset=offset)

        return {
            "author": author,
            "books": result["items"],
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "total_pages": result["total_pages"],
        }
    except Exception as e:
        logger.error(f"Error getting books for author {author_id}: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get books for author {author_id}: {str(e)}",
            error_code="GET_AUTHOR_BOOKS_ERROR",
            error_type=type(e).__name__,
            operation="get_books",
            suggestions=[
                f"Verify author_id={author_id} is correct",
                "Use operation='list' to see all available authors",
            ],
        )


async def get_author_stats_helper() -> dict[str, Any]:
    """
    Helper function to get author statistics.

    Returns:
        Dictionary with author statistics
    """
    try:
        stats = author_service.get_author_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting author statistics: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get author statistics: {str(e)}",
            error_code="GET_AUTHOR_STATS_ERROR",
            error_type=type(e).__name__,
            operation="stats",
        )


async def get_authors_by_letter_helper(letter: str) -> dict[str, Any]:
    """
    Helper function to get authors by first letter.

    Args:
        letter: Single letter (case-insensitive)

    Returns:
        Dictionary with authors list or error response
    """
    try:
        if len(letter) != 1 or not letter.isalpha():
            return format_error_response(
                error_msg=f"Invalid letter: '{letter}'. Must be a single alphabetic character.",
                error_code="INVALID_LETTER",
                error_type="ValueError",
                operation="by_letter",
                suggestions=[
                    "Provide a single letter (e.g., 'A' or 'a')",
                    "Letter is case-insensitive",
                ],
            )

        authors = author_service.get_authors_by_letter(letter.upper())
        return {"authors": authors, "letter": letter.upper(), "count": len(authors)}
    except Exception as e:
        logger.error(f"Error getting authors by letter {letter}: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get authors by letter {letter}: {str(e)}",
            error_code="GET_AUTHORS_BY_LETTER_ERROR",
            error_type=type(e).__name__,
            operation="by_letter",
        )
