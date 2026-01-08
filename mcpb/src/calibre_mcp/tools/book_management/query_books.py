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
) -> Dict[str, Any]:
    """
    Query and search books in the Calibre library with multiple operations in a single unified interface.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 4 separate tools (one per operation), this tool consolidates related
    book query operations into a single interface. This design:
    - Prevents tool explosion (4 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with book query tasks
    - Enables consistent query interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    **IMPORTANT FOR CLAUDE - VERB MAPPING:**
    Users may use different verbs (search, list, find, query, get) but they all map to the same operation.
    ALL of these user requests should use operation="search":

    - "search books by [author]" → query_books(operation="search", author="...")
    - "list books by [author]" → query_books(operation="search", author="...")
    - "find books by [author]" → query_books(operation="search", author="...")
    - "query books by [author]" → query_books(operation="search", author="...")
    - "get books by [author]" → query_books(operation="search", author="...")
    - "show me books by [author]" → query_books(operation="search", author="...")
    - "books by [author]" → query_books(operation="search", author="...")

    **Rule:** If the user wants to access/retrieve/discover books with filters (author, tag, publisher, etc.),
    use operation="search" regardless of which verb they use. The "search" operation handles all filtering.

    Only use operation="list" when the user explicitly wants a simple list of ALL books without any filtering.

    Example: "list books by conan doyle" → query_books(operation="search", author="Conan Doyle")
    This searches the currently loaded library (auto-loaded on startup)

    SUPPORTED OPERATIONS:
    - search: Search/find/list/get/query books with flexible filters (author, tag, text, publisher, year, etc.)
              **This is the PRIMARY operation - use for ALL user requests to access books with filters.**
              **Works for ANY verb: "search books", "list books", "find books", "query books", "get books"**
              Maps ALL user intent: "list books by X", "find books with Y", "search for Z", "get books by W"
    - list: List ALL books in the library (simple pagination, minimal filtering)
              **Only use when user explicitly wants to see ALL books without filters**
              Example: "show me all books" or "list everything in the library"
    - recent: Get recently added books (sorted by addition date, most recent first)
              **Use for "recently added", "new books", "latest additions" queries**
              Example: "show me recent books" or "what books were added recently"
    - by_author: Get books by a specific author using author_id (requires numeric author_id)
              **Use only when user provides a numeric author ID**
              **For author names, use operation="search" with author parameter instead**
    - by_series: Get books in a specific series using series_id (requires numeric series_id)
              **Use only when user provides a numeric series ID**
              **For series names, use operation="search" with series parameter instead**

    OPERATIONS DETAIL:

    search: Search books with flexible filters
    - Primary operation for finding books with any combination of filters
    - Supports author, tag, text, publisher, year, rating, format, and more
    - Works with ANY verb: "search", "list", "find", "query", "get"
    - Most parameters apply to this operation
    - Returns: Paginated list of matching books

    list: List all books
    - Simple pagination without complex filtering
    - Only use when user explicitly wants ALL books
    - Supports basic author and tag filters
    - Returns: Paginated list of all books

    by_author: Get books by author ID
    - Requires numeric author_id (not author name)
    - For author names, use operation="search" with author parameter
    - Returns: List of books by the specified author

    recent: Get recently added books
    - Returns books sorted by addition date (most recent first)
    - Parameters: limit (optional, default: 10, range: 1-1000)
    - Returns: List of recently added books

    by_series: Get books by series ID
    - Requires numeric series_id (not series name)
    - For series names, use operation="search" with series parameter
    - Returns: List of books in the specified series

    Prerequisites:
        - **Default library is auto-loaded on server startup** - no manual library loading needed!
        - For 'search': At least one filter parameter recommended (author, text, tag, etc.)
        - For 'by_author': author_id required (integer)
        - For 'by_series': series_id required (integer)
        - Library must be accessible (automatically handled on startup)

    Parameters:
        operation: The operation to perform. Must be one of: "search", "list", "recent", "by_author", "by_series"
            - "search": Search books with flexible filters. Most parameters apply.
            - "list": List all books with basic filters. Supports author, tag, limit, offset.
            - "recent": Get recently added books (sorted by addition date, most recent first). Parameters: limit (optional, default: 10).
            - "by_author": Get books by author_id. Requires author_id parameter.
            - "by_series": Get books by series_id. Requires series_id parameter.

        author: Filter by author name (for 'search' and 'list' operations)
            - Case-insensitive partial match
            - Example: "Conan Doyle" or "conan"

        author_id: Author ID for 'by_author' operation (required for 'by_author')
            - Must be an integer
            - Use search_books to find author IDs

        series_id: Series ID for 'by_series' operation (required for 'by_series')
            - Must be an integer
            - Use search_books to find series IDs

        text: Search text for 'search' operation
            - Searches in title, author, tags, series, comments
            - Example: "python programming"

        query: Alias for text parameter (backward compatibility)

        tag: Filter by tag name (for 'search' and 'list')
            - Example: "mystery"

        tags: Filter by multiple tags (for 'search')
            - Example: ["mystery", "crime"]

        exclude_tags: Exclude books with these tags (for 'search')
            - Example: ["detective"] - excludes books with "detective" tag

        exclude_authors: Exclude books by these authors (for 'search')
            - Example: ["Author Name"] - excludes books by this author

        exclude_series: Exclude books in these series (for 'search')
            - Example: ["Series Name"] - excludes books in this series

        series: Filter by series name (for 'search')
            - Example: "Sherlock Holmes"

        rating: Filter by exact rating (for 'search')
            - Integer 1-5

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
            return await _search_books_helper(
                # Text/search (after removing structured params if parsed)
                text=final_text if final_text else None,
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
