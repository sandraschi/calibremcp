"""
MCP tools for book-related operations.

FastMCP 2.12 compliant - all tools self-register using @mcp.tool() decorator.
"""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, validator

from calibre_mcp.logging_config import get_logger
from calibre_mcp.services.book_service import BookSearchResult, book_service

from .shared.query_parsing import parse_intelligent_query

logger = get_logger("calibremcp.tools.book_tools")


def _format_books_table(
    items: list[dict[str, Any]],
    total: int,
    page: int,
    total_pages: int,
    per_page: int,
    include_description: bool = True,
    description_max_length: int = 80,
) -> str:
    """
    Format book search results as a pretty text table with comprehensive columns.

    Includes: ID, Title, Author(s), Year, Rating (stars), Tags, and optionally Description.

    Args:
        items: List of book dictionaries
        total: Total number of matching books
        page: Current page number
        total_pages: Total number of pages
        per_page: Items per page
        include_description: Whether to include description column (default: True)
        description_max_length: Maximum length for description preview (default: 80)

    Returns:
        Formatted table string with columns: ID | Title | Author(s) | Year | Rating | Tags | [Description]
    """
    if not items:
        return "\nNo books found.\n"

    # Import re for HTML cleanup and datetime parsing
    import re
    from datetime import datetime

    # Calculate column widths
    id_width = max(4, len(str(max((b.get("id", 0) for b in items), default=0))))
    title_width = min(40, max(20, max((len(b.get("title", "")) for b in items), default=20)))
    # Extract author names from dict format
    author_strings = []
    for b in items:
        author_list = b.get("authors", [])
        if author_list and isinstance(author_list[0], dict):
            author_names = [a.get("name", "") for a in author_list[:2]]
            author_strings.append(", ".join(author_names) if author_names else "Unknown")
        elif author_list:
            author_strings.append(", ".join(author_list[:2]) if author_list else "Unknown")
        else:
            author_strings.append("Unknown")
    author_width = min(25, max(15, max((len(a) for a in author_strings), default=15)))
    year_width = 6  # "YYYY" or "-"
    rating_width = 6  # "★★★★★" or "-"
    tags_width = 30  # For tags column

    # Build table header
    if include_description:
        desc_width = min(description_max_length + 3, 85)  # +3 for ellipsis, max 85 chars
        header = f"{'ID':<{id_width}} | {'Title':<{title_width}} | {'Author(s)':<{author_width}} | {'Year':<{year_width}} | {'Rating':<{rating_width}} | {'Tags':<{tags_width}} | {'Description':<{desc_width}}"
    else:
        header = f"{'ID':<{id_width}} | {'Title':<{title_width}} | {'Author(s)':<{author_width}} | {'Year':<{year_width}} | {'Rating':<{rating_width}} | {'Tags':<{tags_width}}"

    separator = "-" * len(header)

    # Build table rows
    rows = []
    for book in items:
        book_id = str(book.get("id", ""))
        title = book.get("title", "") or "Untitled"
        if len(title) > title_width:
            title = title[: title_width - 3] + "..."

        # Extract author names from dict format [{"id": X, "name": "Name"}]
        author_list = book.get("authors", [])
        if author_list and isinstance(author_list[0], dict):
            authors = ", ".join([a.get("name", "") for a in author_list[:2]]) or "Unknown"
        elif author_list:
            authors = ", ".join(author_list[:2]) or "Unknown"
        else:
            authors = "Unknown"
        if len(authors) > author_width:
            authors = authors[: author_width - 3] + "..."

        # Extract year from pubdate
        year = "-"
        pubdate = book.get("pubdate") or book.get("published") or book.get("published_date")
        if pubdate:
            try:
                if isinstance(pubdate, str):
                    # Try parsing ISO format or date strings
                    for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y"]:
                        try:
                            dt = datetime.strptime(
                                pubdate.split("T")[0] if "T" in pubdate else pubdate, fmt
                            )
                            year = str(dt.year)
                            break
                        except (ValueError, AttributeError):
                            continue
                elif isinstance(pubdate, datetime):
                    year = str(pubdate.year)
                elif hasattr(pubdate, "year"):
                    year = str(pubdate.year)
            except (ValueError, AttributeError, TypeError):
                year = "-"

        # Rating as stars
        rating_val = book.get("rating", 0) or 0
        rating = ("★" * int(rating_val)) if rating_val else "-"

        # Tags - Extract tag names from dict format [{"id": X, "name": "Name"}]
        tags_list = book.get("tags", [])
        if isinstance(tags_list, list):
            # Handle both dict and string tags
            tag_names = []
            for tag in tags_list[:5]:  # Show up to 5 tags for table
                if isinstance(tag, dict):
                    tag_names.append(tag.get("name", tag.get("tag", str(tag))))
                else:
                    tag_names.append(str(tag))
            tags = ", ".join(tag_names) or "-"
        else:
            tags = "-"
        if len(tags) > tags_width:
            tags = tags[: tags_width - 3] + "..."

        # Build row
        if include_description:
            # Get description from comments or description field
            description = book.get("description") or book.get("comments", "") or ""
            # Clean up HTML tags if present
            description = re.sub(r"<[^>]+>", "", description)
            # Truncate intelligently (at word boundary)
            if len(description) > description_max_length:
                description = description[:description_max_length].rsplit(" ", 1)[0] + "..."
            elif not description:
                description = "-"
            # Ensure it fits in column
            if len(description) > desc_width:
                description = description[: desc_width - 3] + "..."

            row = f"{book_id:<{id_width}} | {title:<{title_width}} | {authors:<{author_width}} | {year:<{year_width}} | {rating:<{rating_width}} | {tags:<{tags_width}} | {description:<{desc_width}}"
        else:
            row = f"{book_id:<{id_width}} | {title:<{title_width}} | {authors:<{author_width}} | {year:<{year_width}} | {rating:<{rating_width}} | {tags:<{tags_width}}"

        rows.append(row)

    # Combine into table
    table_lines = [
        "",
        separator,
        header,
        separator,
        *rows,
        separator,
        f"\nShowing {len(items)} of {total} books (Page {page}/{total_pages})",
        "",
    ]

    return "\n".join(table_lines)


class BookSearchInput(BaseModel):
    """Input model for advanced book search with fuzzy matching and relevance scoring."""

    text: str | None = Field(
        None,
        description="Search text to look for in the specified fields. Supports quoted phrases for exact matches.",
    )
    fields: str | list[str] | None = Field(
        ["title^3", "authors^2", "tags^2", "series^1.5", "comments^1", "publisher^1.5"],
        description="""Fields to search in with optional boosting (e.g., "title^3" boosts title matches).
        Available fields: title, authors, tags, series, comments, publisher.
        Can be a JSON array or comma-separated string.""",
    )
    operator: str | None = Field(
        "OR", description="Search operator (AND, OR, or FUZZY)", pattern="^(?i)(AND|OR|FUZZY)$"
    )
    fuzziness: int | str | None = Field(
        "AUTO",
        description="""Fuzziness level for fuzzy search. Can be:
        - 'AUTO': automatic fuzziness based on term length
        - 0-2: fixed fuzziness level
        - '0': exact match only""",
    )
    min_score: float | None = Field(
        0.1, description="Minimum relevance score (0-1) for results to be included", ge=0.0, le=1.0
    )
    highlight: bool | None = Field(
        False, description="Whether to include highlighted snippets of matching text in results"
    )
    suggest: bool | None = Field(
        False, description="Whether to include search suggestions for misspelled queries"
    )
    author: str | None = Field(
        None, description="Filter by author name (case-insensitive partial match)"
    )
    tag: str | None = Field(None, description="Filter by tag name (case-insensitive partial match)")
    series: str | None = Field(
        None, description="Filter by series name (case-insensitive partial match)"
    )
    comment: str | None = Field(
        None, description="Search in book comments (case-insensitive partial match)"
    )
    has_empty_comments: bool | None = Field(
        None, description="Filter books with empty (True) or non-empty (False) comments"
    )
    rating: int | None = Field(None, description="Filter by exact star rating (1-5)", ge=1, le=5)
    min_rating: int | None = Field(
        None,
        description="Filter by minimum star rating (1-5). Use with max_rating for range filtering.",
        ge=1,
        le=5,
    )
    max_rating: int | None = Field(
        None,
        description="Filter by maximum star rating (1-5). Use with min_rating for range filtering.",
        ge=1,
        le=5,
    )
    unrated: bool | None = Field(None, description="Filter for books with no rating when True")
    publisher: str | None = Field(
        None, description="Filter by publisher name (case-insensitive partial match)"
    )
    publishers: list[str] | None = Field(
        None, description="Filter by multiple publishers (OR condition)"
    )
    has_publisher: bool | None = Field(
        None, description="Filter books with (True) or without (False) a publisher"
    )
    pubdate_start: str | None = Field(
        None, description="Filter by publication date (YYYY-MM-DD format), inclusive start date"
    )
    pubdate_end: str | None = Field(
        None, description="Filter by publication date (YYYY-MM-DD format), inclusive end date"
    )
    added_after: str | None = Field(
        None, description="Filter by date added (YYYY-MM-DD format), inclusive start date"
    )
    added_before: str | None = Field(
        None, description="Filter by date added (YYYY-MM-DD format), inclusive end date"
    )
    min_size: int | None = Field(None, description="Minimum file size in bytes", ge=0)
    max_size: int | None = Field(None, description="Maximum file size in bytes", ge=0)
    formats: str | list[str] | None = Field(
        None, description="Filter by file formats (e.g., 'EPUB,PDF' or ['EPUB', 'PDF'])"
    )
    limit: int = Field(50, description="Maximum number of results to return", ge=1, le=1000)
    offset: int = Field(0, description="Number of results to skip for pagination", ge=0)

    @validator("fields", pre=True)
    def parse_fields(cls, v):
        if isinstance(v, str):
            try:
                # Try to parse as JSON array first
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, split by comma and strip whitespace
                return [field.strip() for field in v.split(",") if field.strip()]
        return v

    @validator("formats", pre=True)
    def parse_formats(cls, v):
        if isinstance(v, str):
            try:
                # Try to parse as JSON array first
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, split by comma and strip whitespace, convert to uppercase
                return [fmt.strip().upper() for fmt in v.split(",") if fmt.strip()]
        elif isinstance(v, list):
            # Ensure all formats are uppercase
            return [fmt.upper() if isinstance(fmt, str) else str(fmt).upper() for fmt in v]
        return v

    class Config:
        json_encoders = {"datetime": lambda v: v.isoformat() if v else None}


class BookSearchResultOutput(BookSearchResult):
    """Output model for book search results."""

    class Config:
        json_encoders = {"datetime": lambda v: v.isoformat() if v else None}


class BookSearchOutput(BaseModel):
    """Output model for paginated book search results."""

    items: list[BookSearchResultOutput] = Field(..., description="List of matching books")
    total: int = Field(..., description="Total number of matching books")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class BookDetailOutput(BookSearchResult):
    """Output model for book details."""

    class Config:
        json_encoders = {"datetime": lambda v: v.isoformat() if v else None}


# Helper function - called by query_books portmanteau tool
# NOT registered as MCP tool (no @mcp.tool() decorator)
async def search_books_helper(
    text: str | None = None,
    fields: str | list[str] | None = None,
    operator: str = "OR",
    fuzziness: int | str = "AUTO",
    min_score: float = 0.1,
    highlight: bool = False,
    suggest: bool = False,
    query: str | None = None,  # For backward compatibility
    author: str | None = None,
    authors: list[str] | None = None,
    exclude_authors: list[str] | None = None,
    tag: str | None = None,
    tags: list[str] | None = None,
    exclude_tags: list[str] | None = None,
    series: str | None = None,
    exclude_series: list[str] | None = None,
    comment: str | None = None,
    has_empty_comments: bool | None = None,
    rating: int | None = None,
    min_rating: int | None = None,
    max_rating: int | None = None,
    unrated: bool | None = None,
    publisher: str | None = None,
    publishers: list[str] | None = None,
    has_publisher: bool | None = None,
    pubdate_start: str | None = None,
    pubdate_end: str | None = None,
    added_after: str | None = None,
    added_before: str | None = None,
    min_size: int | None = None,
    max_size: int | None = None,
    formats: list[str] | None = None,
    limit: int = 50,
    offset: int = 0,
    format_table: bool = False,
) -> dict[str, Any]:
    """
    Search and list books with various filters.

    This tool allows searching through the entire library with flexible filtering
    by title, author, tags, series, dates, file size, and formats. Results are
    paginated for efficient browsing of large libraries.

    **IMPORTANT: Use explicit filters for best results!**

    To search for books by a specific author, use the `author` parameter:
    - CORRECT: search_books(author="Mick Herron")
    - CORRECT: search_books(author="herron")  # Partial match works
    - WRONG: search_books(text="Mick Herron")  # This searches titles too

    To search for books with a specific title, use the `text` parameter:
    - CORRECT: search_books(text="python programming")
    - CORRECT: search_books(query="python")  # Same as text

    To combine filters, use multiple parameters:
    - search_books(author="Mick Herron", tag="mystery", min_rating=4)

    Examples:
        # Search for books by a specific author (RECOMMENDED)
        search_books(author="Mick Herron")
        search_books(author="Martin Fowler")

        # Search for books by multiple authors (OR logic - any of them)
        search_books(authors=["Shakespeare", "Homer"])
        search_books(authors=["Mick Herron", "John le Carré", "Ian Fleming"])

        # Search for books with text in title, author, tags, series (general search)
        search_books(text="python")
        search_books(query="machine learning")

        # Search for books containing specific phrases (uses FTS if available)
        search_books(text="it was the worst of times")  # Searches book content
        search_books(text="call me Ishmael")  # Searches for phrase in content
        search_books(text="to be or not to be")  # Searches Shakespeare quotes

        # Search for books by title only (using text parameter)
        search_books(text="The Lord of the Rings")

        # Search for books in a series
        search_books(series="Slough House")

        # Search for books with a specific tag
        search_books(tag="mystery")

        # Search for books with multiple tags (any of them)
        search_books(tags=["mystery", "crime", "thriller"])
        search_books(tags=["science fiction", "fantasy"])

        # Search for books by publisher
        search_books(publisher="O'Reilly Media")

        # Combine filters: author AND tag AND rating
        search_books(author="Mick Herron", tag="spy", min_rating=4)

        # Search for books published in 2023
        search_books(pubdate_start="2023-01-01", pubdate_end="2023-12-31")

        # Get books added in the last 30 days
        from datetime import datetime, timedelta
        last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        search_books(added_after=last_month, added_before=today)

        # Get 5-star books added in the last week
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        search_books(rating=5, added_after=week_ago, added_before=today)

        # Get highly rated books (4-5 stars) added recently
        month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        search_books(min_rating=4, added_after=month_ago, format_table=True)

        # Get books between 1MB and 10MB in size
        search_books(min_size=1048576, max_size=10485760)  # 1MB to 10MB

        # Get books in specific formats
        search_books(formats=["EPUB", "PDF"])

        # Find books with empty comments
        search_books(has_empty_comments=True)

        # Find highly rated books
        search_books(min_rating=4)

        # Find detective story with minimum 4 stars and locked room mystery
        search_books(tag="detective", min_rating=4, text="locked room", format_table=True)

        # Find unrated books
        search_books(unrated=True)

        # Find books by multiple publishers
        search_books(publishers=["O'Reilly Media", "No Starch Press"])

        # Exclude tags - books by Conan Doyle that are NOT detective
        search_books(author="Conan Doyle", exclude_tags=["detective"])

        # Exclude authors - mystery books NOT by Stephen King
        search_books(tag="mystery", exclude_authors=["Stephen King"])

        # Combine inclusions and exclusions
        search_books(authors=["Shakespeare", "Homer"], exclude_tags=["poetry", "drama"])

        # Format results as a table
        search_books(author="Conan Doyle", format_table=True)

    Args:
        text: **FULL-TEXT SEARCH** - Search text to look for in book content, title, author, series, tags, comments.
              **Use this for phrase searches within book content.**

              **Phrase Search Examples:**
              - search_books(text="it was the worst of times")  # Searches book content for exact phrase
              - search_books(text="call me Ishmael")  # Searches for phrase in content
              - search_books(text="to be or not to be")  # Searches Shakespeare quotes

              **How it works:**
              1. If Calibre FTS database exists, uses Full-Text Search for content within books
                 (searches actual book text/content, not just metadata)
              2. If FTS not available, falls back to LIKE queries on metadata (title, author, tags, series, comments)
              3. Phrases (multiple words) are automatically quoted for exact phrase matching when FTS is available

              **Use cases:**
              - Finding books containing specific quotes or phrases: text="it was the best of times"
              - Searching for content snippets: text="once upon a time"
              - General metadata search: text="python programming"

              Note: Field boosting and relevance scoring parameters (fields, min_score, etc.)
              are currently not implemented. FTS uses phrase matching when available.

        query: Alias for `text` parameter (for backward compatibility)

        fields: Currently NOT IMPLEMENTED - Field boosting (e.g., "title^3") is not functional.
               The search will use simple LIKE matching across all fields regardless.

        operator: Currently NOT IMPLEMENTED - AND/OR/FUZZY operators are not functional.
                  All searches use OR logic (matches any field).

        fuzziness: Currently NOT IMPLEMENTED - Fuzzy matching is not functional.

        min_score: Currently NOT IMPLEMENTED - Minimum score filtering is not functional.

        highlight: Currently NOT IMPLEMENTED - Result highlighting is not functional.

        suggest: Currently NOT IMPLEMENTED - Search suggestions are not functional.

        author: **EXPLICIT AUTHOR FILTER** - Filter books by author name only
                Use this when searching for books by a single specific author.
                Case-insensitive partial match (e.g., "herron" matches "Mick Herron").
                Example: search_books(author="Mick Herron")
                Note: Use `authors` parameter for multiple authors (OR logic).

        authors: **MULTIPLE AUTHORS (OR logic)** - Filter books by any of the specified authors
                 Use this to search for books by Shakespeare OR Homer OR any other authors.
                 Books matching ANY of the authors in the list will be returned.
                 Case-insensitive partial matching.
                 Example: search_books(authors=["Shakespeare", "Homer"])
                 Example: search_books(authors=["Mick Herron", "John le Carré", "Ian Fleming"])
                 Note: This uses OR logic within the authors list, but is ANDed with other filters.

        tag: Filter books by tag name (case-insensitive partial match)
             Use this when searching for books with a single specific tag.
             Example: search_books(tag="mystery")
             Note: Use `tags` parameter for multiple tags (OR logic).

        tags: **MULTIPLE TAGS (OR logic)** - Filter books by any of the specified tags
              Use this to search for books with any of the specified tags.
              Books matching ANY of the tags in the list will be returned.
              Case-insensitive partial matching.
              Example: search_books(tags=["mystery", "crime", "thriller"])
              Example: search_books(tags=["science fiction", "fantasy"])
              Note: This uses OR logic within the tags list, but is ANDed with other filters.

        exclude_tags: **EXCLUDE TAGS (NOT logic)** - Exclude books with any of these tags
                       Use this to exclude books with specific tags.
                       Books matching ANY of the tags in the list will be excluded.
                       Case-insensitive partial matching.
                       Example: search_books(author="Conan Doyle", exclude_tags=["detective"])
                       Returns books by Conan Doyle that do NOT have the "detective" tag.
                       Note: Exclusions are applied AFTER inclusions (AND NOT logic).

        exclude_authors: **EXCLUDE AUTHORS (NOT logic)** - Exclude books by any of these authors
                         Use this to exclude books by specific authors.
                         Books matching ANY of the authors in the list will be excluded.
                         Case-insensitive partial matching.
                         Example: search_books(tag="mystery", exclude_authors=["Stephen King"])
                         Returns mystery books that are NOT by Stephen King.

        exclude_series: **EXCLUDE SERIES (NOT logic)** - Exclude books in any of these series
                        Use this to exclude books in specific series.
                        Example: search_books(tag="fiction", exclude_series=["Harlem Renaissance"])

        series: Filter books by series name (case-insensitive partial match)
                Example: search_books(series="Slough House")

        comment: Search in book comments only (case-insensitive partial match)
                 Example: search_books(comment="review")

        has_empty_comments: Filter books with empty (True) or non-empty (False) comments
                            Example: search_books(has_empty_comments=True)

        rating: Filter by exact star rating (1-5)
                Example: search_books(rating=5)

        min_rating: Filter by minimum star rating (1-5)
                    Example: search_books(min_rating=4)  # 4 or 5 stars
                    Use with max_rating for range: search_books(min_rating=3, max_rating=4)

        max_rating: Filter by maximum star rating (1-5)
                    Example: search_books(max_rating=2)  # 1 or 2 stars
                    Use with min_rating for range: search_books(min_rating=3, max_rating=4)

        unrated: Filter for books with no rating when True
                 Example: search_books(unrated=True)

        publisher: Filter by publisher name (case-insensitive partial match)
                   Example: search_books(publisher="O'Reilly")

        publishers: Filter by multiple publishers (OR condition)
                    Example: search_books(publishers=["O'Reilly", "No Starch Press"])

        has_publisher: Filter books with (True) or without (False) a publisher
                       Example: search_books(has_publisher=False)

        pubdate_start: Filter by publication date (YYYY-MM-DD), inclusive start
                       Example: search_books(pubdate_start="2023-01-01")

        pubdate_end: Filter by publication date (YYYY-MM-DD), inclusive end
                     Example: search_books(pubdate_end="2023-12-31")

        added_after: Filter by date added (YYYY-MM-DD), inclusive start
                     Example: search_books(added_after="2024-01-01")

        added_before: Filter by date added (YYYY-MM-DD), inclusive end
                      Example: search_books(added_before="2024-12-31")

        min_size: Minimum file size in bytes
                  Example: search_books(min_size=1048576)  # 1MB

        max_size: Maximum file size in bytes
                  Example: search_books(max_size=10485760)  # 10MB

        formats: List of file formats to include (e.g., ["EPUB", "PDF"])
                 Example: search_books(formats=["EPUB", "PDF"])

        limit: Maximum number of results to return (1-1000, default: 50)

        offset: Number of results to skip for pagination (default: 0)

        format_table: If True, format results as a pretty text table with comprehensive columns.
                      When True, returns a formatted table string in the 'table' field
                      with columns: ID | Title | Author(s) | Year | Rating (stars) | Tags | Description
                      Descriptions are truncated to 80 characters for readability.
                      Example: search_books(author="Conan Doyle", format_table=True)

    Returns:
        Dictionary containing paginated list of books and metadata:
        {
            "items": [book1, book2, ...],  # List of book objects
            "total": 42,                   # Total number of matching books
            "page": 1,                     # Current page number
            "per_page": 10,                # Number of items per page
            "total_pages": 5,              # Total number of pages
            "table": "..."                 # Formatted table string (if format_table=True)
        }

        If format_table=True, the response will also include a 'table' field containing
        a formatted text table with columns: ID | Title | Author(s) | Year | Rating (stars) | Tags | Description

    Raises:
        ValueError: If input validation fails
        Exception: For other unexpected errors

    Best Practices:
        1. **Always use explicit filters when possible**: Use `author="..."` for author searches,
           `series="..."` for series searches, `tag="..."` for tag searches, etc.

        2. **Use `text` for general searches**: When you want to search across multiple fields
           (title, author, tags, series, comments) with relevance scoring.

        3. **All filters use AND logic BETWEEN different filter types**: When you provide multiple
           filter types, they are combined with AND.
           Example: search_books(text="crime novels", publisher="shueisha")
           returns books that match BOTH "crime novels" in title/author/tags AND publisher="shueisha"

        4. **OR logic WITHIN list parameters**: Parameters that accept lists (authors, tags, publishers)
           use OR logic within those lists.
           Example: search_books(authors=["Shakespeare", "Homer"]) returns books by Shakespeare OR Homer.
           Example: search_books(tags=["mystery", "crime"]) returns books with mystery tag OR crime tag.

        5. **Combining list and other filters**: List parameters (OR) are ANDed with other filters.
           Example: search_books(authors=["Shakespeare", "Homer"], tag="drama")
           returns books by (Shakespeare OR Homer) AND with tag="drama".

        6. **Exclusion logic (NOT)**: Use `exclude_tags`, `exclude_authors`, `exclude_series` to exclude
           books matching those criteria. Exclusions are applied with AND NOT logic.
           Example: search_books(author="Conan Doyle", exclude_tags=["detective"])
           returns books by Conan Doyle that do NOT have the "detective" tag.
           Example: search_books(tag="mystery", exclude_authors=["Stephen King"])
           returns mystery books that are NOT by Stephen King.

        7. **Combine filters for precise results**: You can use multiple filters together
           (e.g., text + authors + tags + rating + publisher + exclude_tags) to narrow down results.
           Different filter types are ANDed together, exclusions use AND NOT.

        8. **Author searches**: Always use `author` parameter when searching for books by author.
           Example: search_books(author="Mick Herron") NOT search_books(text="Mick Herron")

        9. **Title searches**: Use `text` parameter when searching for book titles.
           Example: search_books(text="The Lord of the Rings")
    """
    logger.info(
        "Listing books",
        extra={
            "service": "book_tools",
            "action": "list_books",
            "query": query,
            "author": author,
            "tag": tag,
            "series": series,
            "comment": comment,
            "has_empty_comments": has_empty_comments,
            "rating": rating,
            "min_rating": min_rating,
            "unrated": unrated,
            "publisher": publisher,
            "publishers": publishers,
            "has_publisher": has_publisher,
            "pubdate_start": pubdate_start,
            "pubdate_end": pubdate_end,
            "added_after": added_after,
            "added_before": added_before,
            "min_size": min_size,
            "max_size": max_size,
            "formats": formats,
            "limit": limit,
            "offset": offset,
        },
    )

    try:
        # Verify database is initialized (that's all we need - it's already connected to the right library)
        from calibre_mcp.db.database import get_database

        try:
            db = get_database()
            # Test database connection with a simple query to ensure it works
            with db.session_scope() as session:
                from ..db.models import Book

                session.query(Book).limit(1).first()
        except RuntimeError as e:
            # Try to auto-initialize from config - use same priority as server startup
            from ..config import CalibreConfig
            from ..config_discovery import get_active_calibre_library
            from ..db.database import init_database

            config = CalibreConfig()
            if config.auto_discover_libraries:
                config.discover_libraries()

            # Try to find and load a library - SAME PRIORITY AS SERVER STARTUP
            library_to_load = None
            library_name = None

            # 1. Try persisted library from storage (if available)
            try:
                from ..server import storage as server_storage

                if server_storage:
                    # Check if storage has get_current_library method (it's async)
                    if hasattr(server_storage, "get_current_library"):
                        try:
                            persisted_library = await server_storage.get_current_library()
                            if persisted_library and config.discovered_libraries:
                                persisted_lib_info = config.discovered_libraries.get(
                                    persisted_library
                                )
                                if (
                                    persisted_lib_info
                                    and persisted_lib_info.path.exists()
                                    and (persisted_lib_info.path / "metadata.db").exists()
                                ):
                                    library_to_load = persisted_lib_info.path
                                    library_name = persisted_library
                                    logger.info(
                                        f"Auto-initializing with persisted library: {persisted_library}"
                                    )
                        except Exception as storage_e:
                            logger.debug(
                                f"Could not get persisted library from storage: {storage_e}"
                            )
            except (ImportError, AttributeError):
                pass  # Storage might not be available, continue with other options

            # 2. Try config.local_library_path
            if not library_to_load and config.local_library_path:
                lib_path = Path(config.local_library_path)
                metadata_db = lib_path / "metadata.db"
                if (
                    lib_path.exists()
                    and lib_path.is_dir()
                    and metadata_db.exists()
                    and metadata_db.is_file()
                ):
                    library_to_load = lib_path
                    # Find library name from discovered libraries
                    if config.discovered_libraries:
                        for name, lib_info in config.discovered_libraries.items():
                            if Path(lib_info.path) == library_to_load:
                                library_name = name
                                break
                    if not library_name:
                        library_name = library_to_load.name
                    logger.info(f"Auto-initializing with config library: {library_to_load}")

            # 3. Try active library from Calibre config
            if not library_to_load:
                active_lib = get_active_calibre_library()
                if (
                    active_lib
                    and active_lib.path.exists()
                    and active_lib.path.is_dir()
                    and (active_lib.path / "metadata.db").exists()
                ):
                    library_to_load = active_lib.path
                    library_name = active_lib.name
                    logger.info(f"Auto-initializing with active Calibre library: {active_lib.name}")

            # 4. Fallback to first discovered library
            if not library_to_load and config.discovered_libraries:
                for lib_name, lib_info in config.discovered_libraries.items():
                    if (
                        lib_info.path.exists()
                        and lib_info.path.is_dir()
                        and (lib_info.path / "metadata.db").exists()
                    ):
                        library_to_load = lib_info.path
                        library_name = lib_name
                        logger.info(f"Auto-initializing with first discovered library: {lib_name}")
                        break

            if library_to_load:
                metadata_db = library_to_load / "metadata.db"
                try:
                    init_database(str(metadata_db.absolute()), echo=False)
                    # Update config to use this library
                    config.local_library_path = library_to_load
                    # Persist to storage if available
                    try:
                        from ..server import storage as server_storage

                        if (
                            server_storage
                            and library_name
                            and hasattr(server_storage, "set_current_library")
                        ):
                            await server_storage.set_current_library(library_name)
                    except (ImportError, AttributeError, Exception):
                        pass  # Storage might not be available
                    logger.info(
                        f"Auto-initialized database with library: {library_name or library_to_load.name} at {library_to_load}"
                    )
                except Exception as init_e:
                    logger.error(f"Auto-initialization failed: {init_e}", exc_info=True)
                    raise ValueError(
                        f"ERROR: Database not initialized and auto-initialization failed.\n\n"
                        f"**Error:** {str(init_e)}\n\n"
                        f"**Solution:** Use `manage_libraries(operation='list')` to see available libraries,\n"
                        f"then use `manage_libraries(operation='switch', library_name='Library Name')` to select one.\n\n"
                        f"**Note:** The default library should auto-load on startup. If this fails, check your Calibre library path."
                    ) from init_e
            else:
                logger.error("No libraries found for auto-initialization")
                raise ValueError(
                    "ERROR: Database not initialized and no libraries found.\n\n"
                    "**Solution:** Use `manage_libraries(operation='list')` to see available libraries,\n"
                    "then use `manage_libraries(operation='switch', library_name='Library Name')` to select one.\n\n"
                    "**Note:** The default library should auto-load on startup. If this fails, check your Calibre library path."
                ) from e
        except Exception as e:
            raise ValueError(
                f"ERROR: Database error: {str(e)}\n\n"
                "**Solution:** The database connection may have failed. Try:\n"
                "1. Use `manage_libraries(operation='list')` to see available libraries\n"
                "2. Use `manage_libraries(operation='switch', library_name='Library Name')` to re-initialize\n\n"
                "**Note:** Search queries the database directly - the correct library should be auto-loaded on startup."
            ) from e

        # Input validation
        if limit < 1 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
        if offset < 0:
            raise ValueError("Offset cannot be negative")

        # Convert filters to the format expected by book_service.search
        filters = {}

        # Process fields and boost factors
        field_boosts = {}
        if fields is None:
            fields = ["title^3", "authors^2", "tags^2", "series^1.5", "comments^1"]
        elif isinstance(fields, str):
            try:
                fields = json.loads(fields)
            except json.JSONDecodeError:
                fields = [f.strip() for f in fields.split(",") if f.strip()]

        # Parse field boosts (e.g., "title^3" -> {"title": 3.0})
        processed_fields = []
        for field in fields:
            if "^" in field:
                field_name, boost = field.split("^", 1)
                try:
                    field_boosts[field_name] = float(boost)
                    processed_fields.append(field_name)
                except (ValueError, TypeError):
                    processed_fields.append(field)
            else:
                processed_fields.append(field)

        # Intelligently parse query to extract author, tag, pubdate, etc.
        search_text = text or query  # Support both text and query parameters
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
            }
        )

        # Use parsed values if no explicit parameters provided
        if parsed["author"] and not author:
            author = parsed["author"]
        if parsed["tag"] and not tag:
            tag = parsed["tag"]
        if parsed["series"] and not series:
            series = parsed["series"]
        if parsed["pubdate"] and not pubdate_start and not pubdate_end:
            pubdate_start = f"{parsed['pubdate']}-01-01"
            pubdate_end = f"{parsed['pubdate']}-12-31"
        if parsed["rating"] and not rating:
            rating = parsed["rating"]

        # Use remaining query text (after removing structured params) for text search
        if (
            parsed["author"]
            or parsed["tag"]
            or parsed["series"]
            or parsed["pubdate"]
            or parsed["rating"]
        ):
            search_text = parsed["text"] if parsed["text"] else None

        # Handle text search across specified fields
        search_terms = []
        phrases = []

        if search_text:
            # Extract quoted phrases first
            import re

            phrases = re.findall(r'"(.*?)"', search_text)
            remaining_text = re.sub(r'"(.*?)"', "", search_text)

            # Get individual terms from remaining text
            search_terms = [term.strip() for term in remaining_text.split() if term.strip()]

            # If no fields specified, use all with default boosts
            if not processed_fields:
                processed_fields = ["title", "authors", "tags", "series", "comments"]

            # Build field-specific queries with boosts
            search_queries = []

            # Handle exact phrase matches first
            for phrase in phrases:
                if not phrase:
                    continue
                phrase_queries = []
                for field in processed_fields:
                    field_name = field.split("^")[0]  # Remove boost if present
                    if field_name in ["authors", "tags"]:
                        # For multi-value fields, use contains with quoted phrase
                        phrase_queries.append(f'{field_name}:"{phrase}"')
                    else:
                        phrase_queries.append(f'{field_name}:"{phrase}"')

                if phrase_queries:
                    search_queries.append(f"({' OR '.join(phrase_queries)})")

            # Handle individual terms with fuzzy matching
            if operator.upper() == "FUZZY":
                fuzz_str = f"~{fuzziness}" if fuzziness != "AUTO" else "~"
                for term in search_terms:
                    term_queries = []
                    for field in processed_fields:
                        field_name = field.split("^")[0]  # Remove boost if present
                        boost = field_boosts.get(field_name, 1.0)
                        boost_str = f"^{boost}" if boost != 1.0 else ""
                        term_queries.append(f"{field_name}:{term}{fuzz_str}{boost_str}")

                    if term_queries:
                        search_queries.append(f"({' OR '.join(term_queries)})")

            elif operator.upper() == "AND":
                # Require all terms to match (in any field)
                for term in search_terms:
                    term_queries = []
                    for field in processed_fields:
                        field_name = field.split("^")[0]
                        boost = field_boosts.get(field_name, 1.0)
                        boost_str = f"^{boost}" if boost != 1.0 else ""
                        term_queries.append(f"{field_name}:{term}{boost_str}")

                    if term_queries:
                        search_queries.append(f"({' OR '.join(term_queries)})")

            else:  # OR operator (default)
                term_queries = []
                for field in processed_fields:
                    field_name = field.split("^")[0]
                    boost = field_boosts.get(field_name, 1.0)
                    boost_str = f"^{boost}" if boost != 1.0 else ""

                    # Add each term to this field with OR between them
                    field_terms = [f"{field_name}:{term}{boost_str}" for term in search_terms]
                    if field_terms:
                        term_queries.append(f"({' OR '.join(field_terms)})")

                if term_queries:
                    search_queries.extend(term_queries)

            # Combine all queries with the appropriate operator
            if search_queries:
                join_operator = " AND " if operator.upper() in ["AND", "FUZZY"] else " OR "
                filters["search"] = join_operator.join(search_queries)

                # Add minimum score filter if specified
                if min_score > 0:
                    filters["min_score"] = min_score

                # Add highlighting if requested
                if highlight:
                    filters["highlight"] = {
                        "fields": {
                            field: {}
                            for field in processed_fields
                            if field not in ["authors", "tags"]
                        },
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"],
                    }

        # Add other filters
        # Handle author - use authors list if provided, otherwise single author
        if authors:
            filters["authors_list"] = authors if isinstance(authors, list) else [authors]
        elif author:
            filters["author_name"] = author

        # Handle tags - use tags list if provided, otherwise single tag
        if tags:
            filters["tags_list"] = tags if isinstance(tags, list) else [tags]
        elif tag:
            filters["tag_name"] = tag

        # Handle tag exclusions (NOT logic)
        if exclude_tags:
            filters["exclude_tags_list"] = (
                exclude_tags if isinstance(exclude_tags, list) else [exclude_tags]
            )

        # Handle author exclusions (NOT logic)
        if exclude_authors:
            filters["exclude_authors_list"] = (
                exclude_authors if isinstance(exclude_authors, list) else [exclude_authors]
            )

        if series:
            filters["series_name"] = series

        # Handle series exclusions (NOT logic)
        if exclude_series:
            filters["exclude_series_list"] = (
                exclude_series if isinstance(exclude_series, list) else [exclude_series]
            )
        if comment is not None:
            filters["comment"] = comment

        if has_empty_comments is not None:
            filters["has_empty_comments"] = has_empty_comments

        if rating is not None:
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            filters["rating"] = rating

        if min_rating is not None:
            if min_rating < 1 or min_rating > 5:
                raise ValueError("Minimum rating must be between 1 and 5")
            filters["min_rating"] = min_rating

        if max_rating is not None:
            if max_rating < 1 or max_rating > 5:
                raise ValueError("Maximum rating must be between 1 and 5")
            if min_rating is not None and max_rating < min_rating:
                raise ValueError("Maximum rating must be >= minimum rating")
            filters["max_rating"] = max_rating

        if unrated is not None:
            filters["unrated"] = unrated

        if publisher is not None:
            filters["publisher"] = publisher

        if publishers is not None:
            if isinstance(publishers, str):
                try:
                    publishers = json.loads(publishers)
                except json.JSONDecodeError:
                    publishers = [p.strip() for p in publishers.split(",") if p.strip()]
            if publishers:  # Only add if not empty
                filters["publishers"] = publishers

        if has_publisher is not None:
            filters["has_publisher"] = has_publisher

        if pubdate_start:
            filters["pubdate_start"] = pubdate_start
        if pubdate_end:
            filters["pubdate_end"] = pubdate_end

        if added_after:
            filters["added_after"] = added_after
        if added_before:
            filters["added_before"] = added_before

        if min_size is not None:
            filters["min_size"] = min_size
        if max_size is not None:
            filters["max_size"] = max_size

        if formats is not None:
            if isinstance(formats, str):
                try:
                    formats = json.loads(formats)
                except json.JSONDecodeError:
                    formats = [f.strip().upper() for f in formats.split(",") if f.strip()]
            if formats:  # Only add if not empty
                filters["formats"] = [
                    f.upper() if isinstance(f, str) else str(f).upper() for f in formats
                ]

        # Add search suggestions if requested and we have a query
        if suggest and search_text and len(search_terms) > 0:
            filters["suggest"] = {
                "text": search_text,
                "term": {"field": "_all", "sort": "score", "suggest_mode": "popular"},
            }

        # Get paginated results using get_all() method
        # Extract search query and author_name from filters
        search_query = filters.pop("search", None)
        author_name = filters.pop("author_name", None)
        authors_list = filters.pop("authors_list", None)
        exclude_authors_list = filters.pop("exclude_authors_list", None)
        tag_name = filters.pop("tag_name", None)
        tags_list = filters.pop("tags_list", None)
        exclude_tags_list = filters.pop("exclude_tags_list", None)
        series_name = filters.pop("series_name", None)
        exclude_series_list = filters.pop("exclude_series_list", None)
        comment = filters.pop("comment", None)
        has_empty_comments = filters.pop("has_empty_comments", None)
        rating = filters.pop("rating", None)
        min_rating = filters.pop("min_rating", None)
        max_rating = filters.pop("max_rating", None)
        unrated = filters.pop("unrated", None)
        publisher = filters.pop("publisher", None)
        publishers = filters.pop("publishers", None)
        has_publisher = filters.pop("has_publisher", None)
        pubdate_start = filters.pop("pubdate_start", None)
        pubdate_end = filters.pop("pubdate_end", None)
        added_after = filters.pop("added_after", None)
        added_before = filters.pop("added_before", None)
        min_size = filters.pop("min_size", None)
        max_size = filters.pop("max_size", None)
        formats = filters.pop("formats", None)

        # If search query provided, use it for general search
        # Note: The fancy FTS query syntax (fields, boosting, etc.) built above is IGNORED.
        # We just extract the raw search text and pass it to book_service.get_all()
        # which does simple SQL LIKE queries. True FTS would require SQLite FTS5 implementation.
        if search_query:
            # For now, just extract the raw search text from the query
            # The field-specific query building above is not actually used
            search_text = text or query  # Use original text, ignore parsed query
        else:
            search_text = None

        # Build filters dict for get_all()
        get_all_filters = {}
        if rating is not None:
            get_all_filters["rating"] = rating
        if min_rating is not None:
            get_all_filters["min_rating"] = min_rating
        if max_rating is not None:
            get_all_filters["max_rating"] = max_rating
        if has_empty_comments is not None:
            get_all_filters["has_empty_comments"] = has_empty_comments
        if unrated is not None:
            get_all_filters["unrated"] = unrated
        if pubdate_start:
            get_all_filters["pubdate_start"] = pubdate_start
        if pubdate_end:
            get_all_filters["pubdate_end"] = pubdate_end
        if added_after:
            get_all_filters["added_after"] = added_after
        if added_before:
            get_all_filters["added_before"] = added_before
        if min_size is not None:
            get_all_filters["min_size"] = min_size
        if max_size is not None:
            get_all_filters["max_size"] = max_size
        if formats:
            get_all_filters["formats"] = formats

        # Call get_all with proper parameters
        result = book_service.get_all(
            skip=offset,
            limit=limit,
            search=search_text,
            author_name=author_name if not authors_list else None,
            authors_list=authors_list,
            exclude_authors_list=exclude_authors_list,
            tag_name=tag_name if not tags_list else None,
            tags_list=tags_list,
            exclude_tags_list=exclude_tags_list,
            series_name=series_name,
            exclude_series_list=exclude_series_list,
            comment=comment,
            **get_all_filters,
        )

        # Convert to the expected output format
        items = result.get("items", [])
        total = result.get("total", 0)
        page = (offset // limit) + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        response = {
            "items": items,
            "total": total,
            "page": page,
            "per_page": limit,
            "total_pages": total_pages,
            "suggestions": result.get("suggestions", []),
            "max_score": result.get("max_score", 0),
        }

        # Format as table if requested
        if format_table:
            # Include descriptions in table for better overview
            table_text = _format_books_table(
                items,
                total,
                page,
                total_pages,
                limit,
                include_description=True,
                description_max_length=80,
            )
            response["table"] = table_text
            response["format"] = "table"

        return response

    except ValueError as ve:
        logger.error(
            "Invalid input parameters",
            extra={
                "service": "book_tools",
                "action": "list_books_error",
                "error": str(ve),
                "error_type": "validation_error",
            },
        )
        raise

    except ValueError as ve:
        # Re-raise ValueError with helpful error messages (already formatted above)
        logger.error(f"Search validation error: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Error searching books: {str(e)}", exc_info=True)
        # Raise with helpful error message instead of returning empty results
        raise ValueError(
            f"ERROR: Search failed: {str(e)}\n\n"
            "**Possible solutions:**\n"
            "1. Use `list_libraries()` to see available libraries\n"
            "2. Use `switch_library(library_name)` to select a library\n"
            "3. Verify the library path exists and contains metadata.db\n\n"
            "**Important:** This is a LOCAL library search - do NOT try to connect to a Calibre server.\n"
            "Do NOT try to configure or rewrite JSON config files."
        ) from e

    # BookTools class removed - functionality migrated to manage_books portmanteau tool
    # Use manage_books(operation="get") instead of BookTools.get_book()
    # Use query_books(operation="recent") instead of get_recent_books()

    # get_recent_books removed - migrated to query_books(operation="recent")
    # Use query_books(operation="recent", limit=10) instead
    """
    Get a list of the most recently added books in the library.

    Retrieves books sorted by their addition date, with the most recently added
    books first. This is useful for displaying a "recently added" section in the UI,
    tracking new acquisitions, or monitoring library growth.

    Args:
        limit: Maximum number of recent books to return (default: 10, range: 1-1000)

    Returns:
        List of dictionaries, each containing book information for recently added books.
        Books are ordered by addition date (most recent first). Each book dictionary
        includes standard book metadata fields (title, authors, formats, etc.).

    Example:
        # Get 5 most recently added books
        recent = get_recent_books(limit=5)
        for book in recent:
            print(f"{book['title']} - Added recently")

        # Get last 20 additions for a feed
        recent = get_recent_books(limit=20)
    """
    books = book_service.get_recent_books(limit=limit)
    return [book.dict() for book in books]


# Helper function - called by query_books portmanteau tool
# NOT registered as MCP tool (no @mcp.tool() decorator)
async def get_books_by_series_helper(series_id: int) -> list[dict[str, Any]]:
    """
    Get all books that belong to a specific series, ordered by series position.

    Retrieves all books in a series, sorted by their series_index (position in the series).
    This is useful for displaying series in reading order, checking series completion,
    or getting all volumes of a multi-book series.

    Args:
        series_id: The unique identifier of the series in the Calibre library

    Returns:
        List of dictionaries containing book information, ordered by series_index.
        Each book dictionary includes standard metadata plus:
        {
            "series": str - Series name
            "series_index": float - Position in series (1.0 = first book, 2.0 = second, etc.)
            ... (other standard book fields)
        }

    Example:
        # Get all books in "The Lord of the Rings" series
        series_books = get_books_by_series(series_id=42)
        print(f"Series has {len(series_books)} books")
        for book in series_books:
            print(f"  {book['series_index']}: {book['title']}")

        # Check if series is complete (assuming you know expected count)
        if len(series_books) < 6:
            print("Series appears incomplete")
    """
    books = book_service.get_books_by_series(series_id)
    return [book.dict() for book in books]


# Helper function - called by query_books portmanteau tool
# NOT registered as MCP tool (no @mcp.tool() decorator)
async def get_books_by_author_helper(
    author_id: int, limit: int = 50, offset: int = 0
) -> dict[str, Any]:
    """
    Get all books written by a specific author.

    Results are paginated for efficient browsing of large collections.

    Args:
        author_id: The ID of the author
        limit: Maximum number of results to return (default: 50)
        offset: Number of results to skip (for pagination)

    Returns:
        Paginated list of books by the author

    Example:
        # Get first page of books by author with ID 42
        get_books_by_author(author_id=42, limit=10, offset=0)

        # Get next page
        get_books_by_author(author_id=42, limit=10, offset=10)
    """
    from calibre_mcp.services.author_service import author_service

    return author_service.get_books_by_author(author_id=author_id, limit=limit, offset=offset)
