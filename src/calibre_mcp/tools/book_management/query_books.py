"""
Book query portmanteau tool for CalibreMCP.

Consolidates search_books, list_books, get_books_by_author, get_books_by_series
into a single portmanteau tool with operation parameter.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..book_tools import get_books_by_author_helper as _get_books_by_author_helper
from ..book_tools import get_books_by_series_helper as _get_books_by_series_helper

# Import helper functions (NOT registered as MCP tools)
from ..book_tools import search_books_helper as _search_books_helper
from ..core.library_operations import list_books_helper as _list_books_helper
from ..shared.error_handling import handle_tool_error
from ..shared.query_parsing import parse_intelligent_query, strip_inventory_question_phrases

logger = get_logger("calibremcp.tools.book_management")


@mcp.tool()
async def query_books(
    operation: str,
    # Search parameters (all passed through to search_books_helper)
    author: str | None = None,
    authors: list[str] | None = None,
    exclude_authors: list[str] | None = None,
    author_id: int | None = None,
    series_id: int | None = None,
    series: str | None = None,
    exclude_series: list[str] | None = None,
    text: str | None = None,
    title: str | None = None,  # Direct title search (bypasses FTS)
    query: str | None = None,
    tag: str | None = None,
    tags: list[str] | None = None,
    exclude_tags: list[str] | None = None,
    publisher: str | None = None,
    publishers: list[str] | None = None,
    has_publisher: bool | None = None,
    rating: int | None = None,
    min_rating: int | None = None,
    max_rating: int | None = None,
    unrated: bool | None = None,
    pubdate_start: str | None = None,
    pubdate_end: str | None = None,
    added_after: str | None = None,
    added_before: str | None = None,
    min_size: int | None = None,
    max_size: int | None = None,
    formats: list[str] | None = None,
    comment: str | None = None,
    has_empty_comments: bool | None = None,
    # Display/formatting
    format_table: bool = False,
    limit: int = 50,
    offset: int = 0,
    # Auto-open functionality
    auto_open: bool = False,
    auto_open_format: str = "EPUB",
) -> dict[str, Any]:
    """
    Query and search books in the Calibre library with comprehensive filtering.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates full-text search, metadata filtering, and collection listing into a single entry point.
    Optimizes for both precision (SQL) and discovery (recent/by_author) search patterns.

    OPERATIONS:
    - search: Find books with flexible filters (author, tag, text, title, rating, dates, formats).
    - list: List all books in library (pagination only).
    - recent: Get recently added books.
    - by_author: Get books by specific author_id.
    - by_series: Get books in a series by series_id.

    Returns:
    FastMCP 3.1+ dialogic response: success, operation, result or error,
    recommendations, next_steps, and execution_time_ms.
    Enables deep discovery and iterative filtering of library content.
    """
    try:
        if operation == "search":
            # Intelligently parse query to extract author, tag, pubdate, etc.
            # Ensure string: caller may pass wrong type (e.g. function) via MCP/API
            raw = text or query
            search_text = str(raw).strip() if isinstance(raw, str) else None
            parsed = (
                parse_intelligent_query(search_text)
                if search_text
                else {
                    "text": "",
                    "author": None,
                    "tag": None,
                    "pubdate": None,
                    "rating": None,
                    "series": None,
                    "content_type": None,
                    "added_after": None,
                    "added_before": None,
                    "prefer_semantic_search": False,
                    "language_hints": [],
                }
            )

            # Use parsed values if no explicit parameters provided
            final_author = author or parsed["author"]
            final_tag = tag or parsed["tag"]
            final_series = series or parsed["series"]
            final_text = (
                parsed["text"]
                if (
                    parsed["author"]
                    or parsed["tag"]
                    or parsed["series"]
                    or parsed["pubdate"]
                    or parsed["rating"]
                    or parsed["added_after"]
                )
                else search_text
            )

            # Parse pubdate if found
            final_pubdate_start = pubdate_start
            final_pubdate_end = pubdate_end
            if parsed["pubdate"] and not pubdate_start and not pubdate_end:
                final_pubdate_start = f"{parsed['pubdate']}-01-01"
                final_pubdate_end = f"{parsed['pubdate']}-12-31"

            # Use parsed rating if found
            final_rating = rating or parsed["rating"]

            # Use parsed date filters if found
            final_added_after = added_after or parsed["added_after"]
            final_added_before = added_before or parsed["added_before"]

            # Handle content_type hint for library selection
            # If content_type is "manga", "comic", or "paper", we could filter by library
            # For now, we'll just log it - library selection happens at a higher level
            if parsed["content_type"]:
                logger.info(
                    f"Content type hint detected: {parsed['content_type']}",
                    extra={"content_type": parsed["content_type"]},
                )

            # Use search_books helper - pass ALL search parameters
            fts_text = final_text if final_text else None
            if parsed.get("prefer_semantic_search") and search_text:
                fts_text = strip_inventory_question_phrases(search_text) or fts_text

            result = await _search_books_helper(
                # Text/search (after removing structured params if parsed)
                text=fts_text,
                title=title,  # NEW: Direct title search
                query=None,  # Already handled via text
                # Authors (use parsed author if "by" was in query)
                author=final_author,
                authors=authors,
                exclude_authors=exclude_authors,
                # Tags (use parsed tag if "tagged as" was in query)
                tag=final_tag,
                tags=tags,
                exclude_tags=exclude_tags,
                # Series (use parsed series if "series" was in query)
                series=final_series,
                exclude_series=exclude_series,
                # Publication date (use parsed year if "published" was in query)
                pubdate_start=final_pubdate_start,
                pubdate_end=final_pubdate_end,
                # Rating (use parsed rating if "rating" was in query)
                rating=final_rating,
                min_rating=min_rating,
                max_rating=max_rating,
                unrated=unrated,
                # Publisher
                publisher=publisher,
                publishers=publishers,
                has_publisher=has_publisher,
                # Dates
                added_after=final_added_after,
                added_before=final_added_before,
                # Size
                min_size=min_size,
                max_size=max_size,
                # Formats
                formats=formats,
                # Comments
                comment=comment,
                has_empty_comments=has_empty_comments,
                # Display/pagination
                format_table=format_table,
                limit=limit,
                offset=offset,
            )

            if parsed.get("prefer_semantic_search") and isinstance(result, dict):
                result["semantic_search_recommended"] = True
                result["semantic_query_suggestion"] = (
                    strip_inventory_question_phrases(search_text or "")
                    or (search_text or "").strip()
                )
                result["language_hints"] = parsed.get("language_hints") or []
                if result.get("message") is None or isinstance(result.get("message"), str):
                    base = result.get("message") or ""
                    hint = (
                        " For richer matches on niche genres or multilingual collections, "
                        "run calibre_metadata_search with the same intent after calibre_metadata_index_build."
                    )
                    result["message"] = (base + hint).strip()

            # Auto-open functionality: if enabled and exactly 1 result found
            if auto_open and result.get("total") == 1 and result.get("items"):
                book = result["items"][0]
                logger.info(
                    f"Auto-opening unique search result: {book['title']}",
                    extra={"book_id": book["id"], "auto_open_format": auto_open_format},
                )

                # Find the preferred format
                file_path = None
                for fmt in book.get("formats", []):
                    if (
                        isinstance(fmt, dict)
                        and fmt.get("format", "").upper() == auto_open_format.upper()
                    ):
                        file_path = fmt.get("path")
                        break

                # Fallback to first available format
                if not file_path and book.get("formats"):
                    first_format = book["formats"][0]
                    if isinstance(first_format, dict):
                        file_path = first_format.get("path")

                if file_path:
                    try:
                        from ..viewer.manage_viewer import manage_viewer

                        open_result = await (
                            manage_viewer.fn if hasattr(manage_viewer, "fn") else manage_viewer
                        )(operation="open_file", book_id=book["id"], file_path=file_path)

                        # Add viewer info to the result
                        result["auto_opened"] = True
                        result["viewer_result"] = open_result
                        result["opened_book"] = {
                            "id": book["id"],
                            "title": book["title"],
                            "format": auto_open_format,
                            "file_path": file_path,
                        }

                        logger.info(
                            "Book auto-opened successfully",
                            extra={"book_id": book["id"], "file_path": file_path},
                        )

                    except Exception as open_error:
                        logger.warning(
                            f"Auto-open failed: {open_error}",
                            extra={"book_id": book["id"], "error": str(open_error)},
                        )
                        result["auto_open_error"] = str(open_error)
                else:
                    logger.warning(
                        "No suitable format found for auto-open",
                        extra={"book_id": book["id"], "preferred_format": auto_open_format},
                    )

            return result

        elif operation == "list":
            # Use list_books helper (simplified parameters)
            return await _list_books_helper(
                query=author or tag or text or query,
                limit=limit,
            )

        elif operation == "recent":
            # Get recently added books
            from calibre_mcp.services.book_service import book_service

            books = book_service.get_recent_books(limit=limit)
            return {
                "success": True,
                "books": [book.dict() for book in books],
                "total": len(books),
                "limit": limit,
            }

        elif operation == "by_author":
            if author_id is None:
                return {
                    "success": False,
                    "error": "author_id is required for operation='by_author'.",
                    "error_code": "MISSING_AUTHOR_ID",
                    "suggestions": [
                        "First use query_books(operation='search', author='Author Name') to find the author_id",
                        "Then use query_books(operation='by_author', author_id=<id>)",
                    ],
                    "related_tools": ["query_books"],
                }
            return await _get_books_by_author_helper(
                author_id=author_id,
                limit=limit,
                offset=offset,
            )

        elif operation == "by_series":
            if series_id is None:
                return {
                    "success": False,
                    "error": "series_id is required for operation='by_series'.",
                    "error_code": "MISSING_SERIES_ID",
                    "suggestions": [
                        "First use query_books(operation='search', series='Series Name') to find the series_id",
                        "Then use query_books(operation='by_series', series_id=<id>)",
                    ],
                    "related_tools": ["query_books"],
                }
            return await _get_books_by_series_helper(series_id=series_id)

        else:
            return {
                "success": False,
                "error": f"Invalid operation: '{operation}'. Must be one of: 'search', 'list', 'recent', 'by_author', 'by_series'",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Use operation='search' to search books with filters (author, tag, text, etc.)",
                    "Use operation='list' to list all books",
                    "Use operation='recent' to get recently added books",
                    "Use operation='by_author' to get books by author_id",
                    "Use operation='by_series' to get books by series_id",
                ],
                "related_tools": ["query_books"],
            }

    except Exception as e:
        # Use standardized error handling
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "author": author,
                "text": text or query,
                "tag": tag,
                "series": series,
                "limit": limit,
                "offset": offset,
            },
            tool_name="query_books",
            context="Searching/listing books in Calibre library",
        )
