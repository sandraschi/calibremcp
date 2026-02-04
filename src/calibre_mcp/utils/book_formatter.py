"""
Book formatting utilities for pretty output.

Handles:
- Table format for multiple books (with truncated descriptions)
- Flowing text format for single book (with full description)
"""

import textwrap
from typing import Any


def format_book_table(
    items: list[dict[str, Any]],
    total: int,
    page: int,
    total_pages: int,
    per_page: int,
    include_description: bool = True,
    description_max_length: int = 100,
) -> str:
    """
    Format multiple books as a pretty text table with optional descriptions.

    Args:
        items: List of book dictionaries
        total: Total number of matching books
        page: Current page number
        total_pages: Total number of pages
        per_page: Items per page
        include_description: Whether to include description column
        description_max_length: Maximum length for description preview

    Returns:
        Formatted table string
    """
    if not items:
        return "\nNo books found.\n"

    # Calculate column widths
    id_width = max(4, len(str(max((b.get("id", 0) for b in items), default=0))))
    title_width = min(40, max(15, max((len(b.get("title", "")) for b in items), default=15)))
    author_strings = [", ".join(b.get("authors", [])[:2]) or "Unknown" for b in items]
    author_width = min(25, max(10, max((len(a) for a in author_strings), default=10)))

    # Build table header
    if include_description:
        desc_width = min(description_max_length + 3, 80)  # +3 for ellipsis
        header = f"{'ID':<{id_width}} | {'Title':<{title_width}} | {'Author(s)':<{author_width}} | {'Rating':<6} | {'Description':<{desc_width}}"
    else:
        header = f"{'ID':<{id_width}} | {'Title':<{title_width}} | {'Author(s)':<{author_width}} | {'Rating':<6} | {'Tags':<20}"

    separator = "-" * len(header)

    # Build table rows
    rows = []
    for book in items:
        book_id = str(book.get("id", ""))
        title = book.get("title", "") or "Untitled"
        if len(title) > title_width:
            title = title[: title_width - 3] + "..."

        authors = ", ".join(book.get("authors", [])[:2]) or "Unknown"
        if len(authors) > author_width:
            authors = authors[: author_width - 3] + "..."

        rating_val = book.get("rating", 0) or 0
        rating = ("★" * int(rating_val)) if rating_val else "-"

        if include_description:
            # Get description from comments or description field
            description = book.get("description") or book.get("comments", "") or ""
            # Clean up HTML tags if present
            import re

            description = re.sub(r"<[^>]+>", "", description)
            # Truncate and wrap
            if len(description) > description_max_length:
                description = description[:description_max_length].rsplit(" ", 1)[0] + "..."
            elif not description:
                description = "-"
            # Ensure it fits in column
            if len(description) > desc_width:
                description = description[: desc_width - 3] + "..."

            row = f"{book_id:<{id_width}} | {title:<{title_width}} | {authors:<{author_width}} | {rating:<6} | {description:<{desc_width}}"
        else:
            tags = ", ".join(book.get("tags", [])[:3]) or "-"
            if len(tags) > 20:
                tags = tags[:17] + "..."
            row = f"{book_id:<{id_width}} | {title:<{title_width}} | {authors:<{author_width}} | {rating:<6} | {tags:<20}"

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


def format_book_details(book: dict[str, Any]) -> str:
    """
    Format a single book in flowing text with full description.

    Args:
        book: Book dictionary with all metadata

    Returns:
        Formatted text string with complete book information
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"📖 {book.get('title', 'Untitled')}")
    lines.append("=" * 80)
    lines.append("")

    # Basic metadata
    authors = book.get("authors", [])
    if authors:
        lines.append(f"**Authors:** {', '.join(authors)}")

    if book.get("series"):
        series_index = book.get("series_index")
        if series_index:
            lines.append(f"**Series:** {book['series']} (#{series_index})")
        else:
            lines.append(f"**Series:** {book['series']}")

    if book.get("rating"):
        rating = int(book.get("rating", 0))
        lines.append(f"**Rating:** {'★' * rating} ({rating}/5)")

    if book.get("publisher"):
        lines.append(f"**Publisher:** {book['publisher']}")

    if book.get("pubdate"):
        lines.append(f"**Published:** {book['pubdate']}")

    tags = book.get("tags", [])
    if tags:
        lines.append(f"**Tags:** {', '.join(tags)}")

    formats = book.get("formats", [])
    if formats:
        lines.append(f"**Formats:** {', '.join(formats)}")

    languages = book.get("languages", [])
    if languages:
        lines.append(f"**Languages:** {', '.join(languages)}")

    identifiers = book.get("identifiers", {})
    if identifiers:
        id_str = ", ".join(f"{k}: {v}" for k, v in identifiers.items())
        lines.append(f"**Identifiers:** {id_str}")

    lines.append("")
    lines.append("-" * 80)
    lines.append("")

    # Full description
    description = book.get("description") or book.get("comments", "")
    if description:
        # Clean HTML tags
        import re

        description = re.sub(r"<[^>]+>", "", description)
        # Wrap text nicely (80 chars per line)
        wrapped = textwrap.fill(description, width=76, initial_indent="  ", subsequent_indent="  ")
        lines.append("**Description:**")
        lines.append("")
        lines.append(wrapped)
        lines.append("")
    else:
        lines.append("**Description:** (No description available)")
        lines.append("")

    lines.append("-" * 80)

    # Additional metadata
    if book.get("date_added"):
        lines.append(f"**Added:** {book['date_added']}")

    if book.get("last_modified"):
        lines.append(f"**Last Modified:** {book['last_modified']}")

    if book.get("cover_url"):
        lines.append(f"**Cover:** {book['cover_url']}")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)
