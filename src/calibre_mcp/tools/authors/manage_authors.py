"""
Author management portmanteau tool for CalibreMCP.

Consolidates all author-related operations into a single unified interface.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..author_schemas import MANAGE_AUTHORS_OUTPUT_SCHEMA
from ..shared.error_handling import format_error_response, handle_tool_error

# Import helper functions (NOT registered as MCP tools)
from .author_helpers import (
    get_author_books_helper,
    get_author_helper,
    get_author_stats_helper,
    get_authors_by_letter_helper,
    list_authors_helper,
)

logger = get_logger("calibremcp.tools.authors")


@mcp.tool(output_schema=MANAGE_AUTHORS_OUTPUT_SCHEMA)
async def manage_authors(
    operation: str,
    # List operation parameters
    query: str | None = None,
    limit: int = 50,
    offset: int = 0,
    # Get operation parameters
    author_id: int | None = None,
    # Get books operation parameters
    # (uses author_id from above)
    # Stats operation parameters
    # (no parameters needed)
    # By letter operation parameters
    letter: str | None = None,
) -> dict[str, Any]:
    """
    Comprehensive author management for Calibre.

    Operations:
    - list: List authors with filtering (query) and pagination.
    - get: Get detailed author information and book counts.
    - get_books: Get all books by a specific author.
    - stats: Library-wide author statistics (top authors, distributions).
    - by_letter: Filter authors by their name's first letter.

    Example:
    - manage_authors(operation="list", query="martin")
    - manage_authors(operation="get_books", author_id=42)
    """
    try:
        if operation == "list":
            try:
                return await list_authors_helper(query=query, limit=limit, offset=offset)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"query": query, "limit": limit, "offset": offset},
                    tool_name="manage_authors",
                    context="Listing authors",
                )

        elif operation == "get":
            if not author_id:
                return format_error_response(
                    error_msg=(
                        "author_id is required for operation='get'. "
                        "Use operation='list' to find available authors."
                    ),
                    error_code="MISSING_AUTHOR_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide author_id parameter (e.g., author_id=42)",
                        "Use operation='list' to see all available authors",
                    ],
                    related_tools=["manage_authors"],
                )
            try:
                return await get_author_helper(author_id=author_id)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"author_id": author_id},
                    tool_name="manage_authors",
                    context=f"Getting author details for author_id={author_id}",
                )

        elif operation == "get_books":
            if not author_id:
                return format_error_response(
                    error_msg=(
                        "author_id is required for operation='get_books'. "
                        "Use operation='list' to find available authors."
                    ),
                    error_code="MISSING_AUTHOR_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide author_id parameter (e.g., author_id=42)",
                        "Use operation='list' to see all available authors",
                    ],
                    related_tools=["manage_authors"],
                )
            try:
                return await get_author_books_helper(
                    author_id=author_id, limit=limit, offset=offset
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={
                        "author_id": author_id,
                        "limit": limit,
                        "offset": offset,
                    },
                    tool_name="manage_authors",
                    context=f"Getting books for author_id={author_id}",
                )

        elif operation == "stats":
            try:
                return await get_author_stats_helper()
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_authors",
                    context="Getting author statistics",
                )

        elif operation == "by_letter":
            if not letter:
                return format_error_response(
                    error_msg=(
                        "letter is required for operation='by_letter'. "
                        "Provide a single alphabetic character."
                    ),
                    error_code="MISSING_LETTER",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide letter parameter (e.g., letter='A')",
                        "Letter must be a single alphabetic character",
                        "Letter is case-insensitive",
                    ],
                    related_tools=["manage_authors"],
                )
            try:
                return await get_authors_by_letter_helper(letter=letter)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"letter": letter},
                    tool_name="manage_authors",
                    context=f"Getting authors by letter '{letter}'",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'list', 'get', 'get_books', 'stats', 'by_letter'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='list' to list authors",
                    "Use operation='get' to get author details",
                    "Use operation='get_books' to get books by author",
                    "Use operation='stats' to get author statistics",
                    "Use operation='by_letter' to get authors by first letter",
                ],
                related_tools=["manage_authors"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "author_id": author_id,
                "query": query,
                "letter": letter,
            },
            tool_name="manage_authors",
            context="Author management operation",
        )
