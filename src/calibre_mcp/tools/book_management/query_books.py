"""
Book query portmanteau tool for CalibreMCP.

Consolidates search_books, list_books, get_books_by_author, get_books_by_series
into a single portmanteau tool with operation parameter.
"""

from typing import Optional, Dict, Any, List

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error
from ..shared.query_parsing import parse_intelligent_query

# Import helper functions (NOT registered as MCP tools)
from ..book_tools import search_books_helper as _search_books_helper
from ..core.library_operations import list_books_helper as _list_books_helper
from ..book_tools import get_books_by_author_helper as _get_books_by_author_helper
from ..book_tools import get_books_by_series_helper as _get_books_by_series_helper

logger = get_logger("calibremcp.tools.book_management")


@mcp.tool()
async def query_books(
    operation: str,
    # Search parameters (all passed through to search_books_helper)
    author: Optional[str] = None,
    authors: Optional[List[str]] = None,
    exclude_authors: Optional[List[str]] = None,
    author_id: Optional[int] = None,
    series_id: Optional[int] = None,
    series: Optional[str] = None,
    exclude_series: Optional[List[str]] = None,
    text: Optional[str] = None,
    title: Optional[str] = None,  # Direct title search (bypasses FTS)
    query: Optional[str] = None,
    tag: Optional[str] = None,
    tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    publisher: Optional[str] = None,
    publishers: Optional[List[str]] = None,
    has_publisher: Optional[bool] = None,
    rating: Optional[int] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    unrated: Optional[bool] = None,
    pubdate_start: Optional[str] = None,
    pubdate_end: Optional[str] = None,
    added_after: Optional[str] = None,
    added_before: Optional[str] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    formats: Optional[List[str]] = None,
    comment: Optional[str] = None,
    has_empty_comments: Optional[bool] = None,
    # Display/formatting
    format_table: bool = False,
    limit: int = 50,
    offset: int = 0,
    # Auto-open functionality
    auto_open: bool = False,
    auto_open_format: str = "EPUB",
) -> Dict[str, Any]:
    """
    Query and search books in the Calibre library with comprehensive filtering options.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates search, list, and filtered query operations into single interface. Prevents tool explosion while maintaining
    full functionality. Follows FastMCP 2.13+ best practices.

    NATURAL LANGUAGE USAGE:
    The MCP client LLM should parse natural language queries into appropriate parameter combinations:
    - "search books by harari" → operation="search", author="harari"
    - "books about china" → operation="search", tag="china"
    - "books from last year" → operation="search", added_after="2024-01-01"
    - "find sapiens book" → operation="search", title="sapiens"
    - "mystery novels" → operation="search", tag="mystery"

    Args:
        operation (Literal, required): The operation to perform. Must be one of: "search", "list".
            - "search": Search/find books with flexible filters (author, tag, text, etc.). Use for ALL filtered queries.
            - "list": List all books in library with basic pagination. Use only for unfiltered "show all" requests.

        author (str | None): Filter by specific author name (case-insensitive word-based matching).
            Example: "Conan Doyle" matches "Arthur Conan Doyle" or "Conan Doyle Jr."
            Example: "Dickson Carr" matches "John Dickson Carr"
            Note: Author search requires ALL words to be present in the author name (AND logic).

        authors (List[str] | None): Filter by multiple author names (OR logic between authors).

        exclude_authors (List[str] | None): Exclude books by these authors.

        author_id (int | None): Filter by author database ID.

        series_id (int | None): Filter by series database ID.

        series (str | None): Filter by series name.

        exclude_series (List[str] | None): Exclude books from these series.

        text (str | None): General search across titles, authors, tags, series, and comments (uses FTS if available).

        title (str | None): Search specifically in book titles only (bypasses FTS for fast exact matching).
            Example: title="The Hollow Man" finds books with that exact title
            Note: Much faster than text search for title-specific queries.

        query (str | None): Advanced query string (same syntax as Calibre search).

        tag (str | None): Filter by specific tag/category.

        tags (List[str] | None): Filter by multiple tags (OR logic between tags).

        exclude_tags (List[str] | None): Exclude books with these tags.

        publisher (str | None): Filter by publisher name.

        publishers (List[str] | None): Filter by multiple publishers (OR logic between publishers).

        has_publisher (bool | None): Filter books with/without publisher info (True/False).

        rating (int | None): Filter by exact rating (1-5 stars).

        min_rating (int | None): Filter by minimum rating (1-5).

        max_rating (int | None): Filter by maximum rating (1-5).

        unrated (bool | None): Include only unrated books.

        pubdate_start (str | None): Filter by publication date start (YYYY-MM-DD format).

        pubdate_end (str | None): Filter by publication date end (YYYY-MM-DD format).

        added_after (str | None): Filter books added after date (YYYY-MM-DD format).

        added_before (str | None): Filter books added before date (YYYY-MM-DD format).

        min_size (int | None): Filter by minimum file size in bytes.

        max_size (int | None): Filter by maximum file size in bytes.

        formats (List[str] | None): Filter by available formats (e.g., ["EPUB", "PDF"]).

        comment (str | None): Search in book comments field.

        has_empty_comments (bool | None): Filter books with empty/non-empty comments.

        format_table (bool): Format results as a pretty text table (default: False).

        limit (int): Maximum number of results to return (default: 50).

        offset (int): Number of results to skip for pagination (default: 0).

        publisher (str | None): Filter by publisher name.

        rating (int | None): Filter by exact rating (1-5 stars).

        min_rating (int | None): Filter by minimum rating.

        max_rating (int | None): Filter by maximum rating.

        pubdate_start (str | None): Filter by publication date start (YYYY-MM-DD).

        pubdate_end (str | None): Filter by publication date end (YYYY-MM-DD).

        formats (List[str] | None): Filter by available formats (epub, pdf, mobi, etc.).

        limit (int): Maximum number of books to return (default: 50, max: 200).

        offset (int): Number of books to skip for pagination (default: 0).

    Returns:
        Dictionary with operation-specific results and conversational response patterns:

        For operation="search":
            {
                "success": bool - Whether search completed successfully
                "results": List[Dict] - Books matching the search criteria
                "total_found": int - Total number of matching books
                "query_used": str - The search query that was executed
                "search_time_ms": int - Time taken to perform search
                "library_searched": str - Name of library that was searched
                "available_filters": List[str] - Other filters that could be applied
                "recommendations": List[str] - Suggested next steps or related searches
                "summary": str - Conversational summary of results
            }

        For operation="list":
            {
                "success": bool - Whether listing completed successfully
                "results": List[Dict] - Books in the requested range
                "total_found": int - Total number of books in library
                "limit": int - Number of books returned
                "offset": int - Starting position in results
                "library_searched": str - Name of library that was searched
                "next_offset": int | None - Offset for next page (if more results available)
                "summary": str - Conversational summary of results
            }

        min_rating: Filter by minimum rating (for 'search')
            - Integer 1-5

        max_rating: Filter by maximum rating (for 'search')
            - Integer 1-5

        unrated: Filter for unrated books only (for 'search')
            - Boolean, default: False

        publisher: Filter by publisher name (for 'search')
            - Example: "O'Reilly Media"

        publishers: Filter by multiple publishers (for 'search')
            - Example: ["O'Reilly Media", "No Starch Press"]

        has_publisher: Filter books with/without publisher (for 'search')
            - Boolean: True = has publisher, False = no publisher

        pubdate_start: Filter by publication date start (for 'search')
            - Format: "YYYY-MM-DD"
            - Example: "2023-01-01"

        pubdate_end: Filter by publication date end (for 'search')
            - Format: "YYYY-MM-DD"
            - Example: "2023-12-31"

        added_after: Filter by date added after (for 'search')
            - Format: "YYYY-MM-DD"
            - Example: "2024-01-01"

        added_before: Filter by date added before (for 'search')
            - Format: "YYYY-MM-DD"
            - Example: "2024-12-31"

        min_size: Minimum file size in bytes (for 'search')
            - Example: 1048576 (1 MB)

        max_size: Maximum file size in bytes (for 'search')
            - Example: 10485760 (10 MB)

        formats: List of file formats to include (for 'search')
            - Example: ["EPUB", "PDF", "MOBI"]

        comment: Search in book comments only (for 'search')
            - Searches only the comments field

        has_empty_comments: Filter books with empty/non-empty comments (for 'search')
            - Boolean: True = empty comments, False = has comments

        format_table: Format results as table (for 'search')
            - Boolean, default: False

        limit: Maximum results to return (default: 50)

        offset: Results offset for pagination (default: 0)

        auto_open: Auto-open book if search returns exactly 1 result (for 'search')
            - Boolean, default: False
            - Launches the book's file with the system's default application (e.g., Calibre Viewer, Adobe Reader, Edge)

        auto_open_format: Preferred format for auto-opening (default: "EPUB")
            - String: "EPUB", "PDF", "MOBI", "AZW3", etc.
            - Falls back to first available format if preferred format not found

    Returns:
        Dictionary containing operation-specific results with book list and pagination info.

    Usage:
        # Search for books by author (what Claude will use for "list books by conan doyle")
        # This works immediately - default library is auto-loaded on server startup
        result = await query_books(
            operation="search",
            author="Conan Doyle"
        )
        print(f"Found {result['total']} books")

        # No need to load/switch libraries first - default library is already loaded!

        # List all books
        result = await query_books(operation="list", limit=20)

        # Get books by author ID
        result = await query_books(
            operation="by_author",
            author_id=42
        )

        # Get recently added books
        result = await query_books(
            operation="recent",
            limit=10
        )

    Examples:
        # Claude says: "list books by conan doyle"
        result = await query_books(
            operation="search",
            author="Conan Doyle",
            format_table=True
        )

        # Advanced search: author + publisher + year
        result = await query_books(
            operation="search",
            author="Conan Doyle",
            publisher="Penguin",
            pubdate_start="1900-01-01",
            pubdate_end="1930-12-31"
        )

        # Search with multiple filters (AND logic) - tags, rating, excludes
        result = await query_books(
            operation="search",
            author="Agatha Christie",
            tags=["mystery", "crime"],
            min_rating=4,
            exclude_tags=["horror"],
            format_table=True
        )

        # Search by publisher with year range
        result = await query_books(
            operation="search",
            publishers=["O'Reilly Media", "No Starch Press"],
            pubdate_start="2023-01-01",
            pubdate_end="2024-12-31"
        )

        # Search with file size and format filters
        result = await query_books(
            operation="search",
            author="Stephen King",
            min_size=1048576,  # 1 MB
            max_size=10485760,  # 10 MB
            formats=["EPUB", "PDF"]
        )

        # Search recently added books with rating
        result = await query_books(
            operation="search",
            added_after="2024-01-01",
            min_rating=4,
            format_table=True
        )

        # Search by multiple authors (OR logic)
        result = await query_books(
            operation="search",
            authors=["Shakespeare", "Homer"]
        )

        # List all books (simple operation)
        result = await query_books(operation="list", limit=10)

        # Get books by author ID
        result = await query_books(
            operation="by_author",
            author_id=42,
            limit=10
        )

        # Get books in a series
        result = await query_books(
            operation="by_series",
            series_id=15
        )

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "search", "list", "recent", "by_author", "by_series"
        - Missing author_id: Provide author_id for 'by_author' operation
        - Missing series_id: Provide series_id for 'by_series' operation

    See Also:
        - manage_books(): For adding, updating, deleting books
        - Helper functions: search_books, list_books (NOT visible to Claude, used internally)
    """
    try:
        if operation == "search":
            # Intelligently parse query to extract author, tag, pubdate, etc.
            search_text = text or query
            parsed = parse_intelligent_query(search_text) if search_text else {
                "text": "", "author": None, "tag": None, "pubdate": None, 
                "rating": None, "series": None, "content_type": None,
                "added_after": None, "added_before": None,
            }
            
            # Use parsed values if no explicit parameters provided
            final_author = author or parsed["author"]
            final_tag = tag or parsed["tag"]
            final_series = series or parsed["series"]
            final_text = parsed["text"] if (parsed["author"] or parsed["tag"] or parsed["series"] or parsed["pubdate"] or parsed["rating"] or parsed["added_after"]) else search_text
            
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
                logger.info(f"Content type hint detected: {parsed['content_type']}", extra={"content_type": parsed["content_type"]})
            
            # Use search_books helper - pass ALL search parameters
            result = await _search_books_helper(
                # Text/search (after removing structured params if parsed)
                text=final_text if final_text else None,
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

            # Auto-open functionality: if enabled and exactly 1 result found
            if auto_open and result.get("total") == 1 and result.get("items"):
                book = result["items"][0]
                logger.info(f"Auto-opening unique search result: {book['title']}", extra={"book_id": book["id"], "auto_open_format": auto_open_format})

                # Find the preferred format
                file_path = None
                for fmt in book.get('formats', []):
                    if isinstance(fmt, dict) and fmt.get('format', '').upper() == auto_open_format.upper():
                        file_path = fmt.get('path')
                        break

                # Fallback to first available format
                if not file_path and book.get('formats'):
                    first_format = book['formats'][0]
                    if isinstance(first_format, dict):
                        file_path = first_format.get('path')

                if file_path:
                    try:
                        from ..viewer.manage_viewer import manage_viewer
                        open_result = await manage_viewer.fn(
                            operation="open_file",
                            book_id=book['id'],
                            file_path=file_path
                        )

                        # Add viewer info to the result
                        result["auto_opened"] = True
                        result["viewer_result"] = open_result
                        result["opened_book"] = {
                            "id": book["id"],
                            "title": book["title"],
                            "format": auto_open_format,
                            "file_path": file_path
                        }

                        logger.info("Book auto-opened successfully", extra={"book_id": book["id"], "file_path": file_path})

                    except Exception as open_error:
                        logger.warning(f"Auto-open failed: {open_error}", extra={"book_id": book["id"], "error": str(open_error)})
                        result["auto_open_error"] = str(open_error)
                else:
                    logger.warning("No suitable format found for auto-open", extra={"book_id": book["id"], "preferred_format": auto_open_format})

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
