"""
Metadata management portmanteau tool for CalibreMCP.

Consolidates all metadata-related operations into a single unified interface.
"""

import tempfile
from pathlib import Path
from typing import Any

from ...logging_config import get_logger
from ...server import MetadataUpdateRequest, mcp
from ..shared.error_handling import format_error_response, handle_tool_error

# Import helper functions (NOT registered as MCP tools)
from . import metadata_management

logger = get_logger("calibremcp.tools.metadata")


@mcp.tool()
async def manage_metadata(
    operation: str,
    # Update operation parameters
    updates: list[MetadataUpdateRequest] | None = None,
    # Show operation parameters
    query: str | None = None,
    author: str | None = None,
    open_browser: bool = True,
) -> dict[str, Any]:
    """
    Comprehensive metadata management for Calibre.

    Operations:
    - update: Bulk update fields (title, tags, rating, etc.) for multiple books.
    - organize_tags: AI-powered tag organization and cleanup suggestions.
    - fix_issues: Automatically fix common metadata inconsistencies.
    - show: Display deep metadata for a book in a formatted view/browser.

    Example:
    - manage_metadata(operation="update", updates=[{"book_id": 12, "field": "rating", "value": 5}])
    - manage_metadata(operation="show", query="Gormenghast")
    """
    try:
        if operation == "update":
            if not updates:
                return format_error_response(
                    error_msg=(
                        "updates is required for operation='update'. "
                        "Provide a list of metadata update requests."
                    ),
                    error_code="MISSING_UPDATES",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide updates parameter (e.g., updates=[{'book_id': 123, 'field': 'title', 'value': 'New Title'}])",
                        "Each update request must contain: book_id, field, value",
                    ],
                    related_tools=["manage_metadata"],
                )
            try:
                result = await metadata_management.update_book_metadata_helper(updates)
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"updates": updates},
                    tool_name="manage_metadata",
                    context="Updating book metadata",
                )

        elif operation == "organize_tags":
            try:
                result = await metadata_management.auto_organize_tags_helper()
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_metadata",
                    context="Organizing tags with AI-powered analysis",
                )

        elif operation == "fix_issues":
            try:
                result = await metadata_management.fix_metadata_issues_helper()
                return result.model_dump() if hasattr(result, "model_dump") else result
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_metadata",
                    context="Automatically fixing metadata issues",
                )

        elif operation == "show":
            try:
                import os
                import platform
                import subprocess

                from ...services import book_service
                from ...tools.book_tools import search_books_helper

                # Validate query parameter
                if not query and not author:
                    return format_error_response(
                        error_msg="Either 'query' (title) or 'author' parameter is required for show operation.",
                        error_code="MISSING_QUERY",
                        error_type="ValueError",
                        operation=operation,
                        suggestions=[
                            "Provide query parameter: query='Gormenghast'",
                            "Or provide author parameter: author='Mervyn Peake'",
                        ],
                        related_tools=["query_books"],
                    )

                # Search for the book
                search_params = {"limit": 10}
                if query:
                    search_params["text"] = query
                if author:
                    search_params["author"] = author

                search_result = await search_books_helper(**search_params)
                books = search_result.get("items", [])

                if not books:
                    return format_error_response(
                        error_msg=f"No books found matching query='{query}', author='{author}'.",
                        error_code="NO_BOOKS_FOUND",
                        error_type="ValueError",
                        operation=operation,
                        suggestions=[
                            "Check spelling of title/author",
                            "Try a broader search (partial title/author name)",
                            "Use query_books() to verify books exist",
                        ],
                        related_tools=["query_books"],
                    )

                # Use first result (best match)
                selected_book = books[0]
                book_id = selected_book["id"]

                # Get comprehensive metadata
                book_data = book_service.get_by_id(book_id)

                # Format metadata as text
                title = book_data.get("title", "Unknown")
                authors_list = book_data.get("authors", [])
                if authors_list and isinstance(authors_list[0], dict):
                    authors_str = ", ".join([a.get("name", "") for a in authors_list])
                else:
                    authors_str = ", ".join(authors_list) if authors_list else "Unknown"

                tags_list = book_data.get("tags", [])
                tags_str = (
                    ", ".join(
                        [t.get("name", "") if isinstance(t, dict) else str(t) for t in tags_list]
                    )
                    if tags_list
                    else "None"
                )

                series_info = book_data.get("series")
                series_str = ""
                if series_info:
                    if isinstance(series_info, dict):
                        series_name = series_info.get("name", "")
                        series_index = book_data.get("series_index", 1.0)
                        series_str = f"{series_name} (#{series_index})"
                    else:
                        series_str = str(series_info)

                rating = book_data.get("rating")
                rating_str = f"{rating}/5" if rating else "Not rated"

                pubdate = book_data.get("pubdate")
                pubdate_str = pubdate[:10] if pubdate else "Unknown"

                isbn = book_data.get("isbn", "None")
                formats_list = book_data.get("formats", [])
                formats_str = (
                    ", ".join(
                        [
                            f.get("format", "") if isinstance(f, dict) else str(f)
                            for f in formats_list
                        ]
                    )
                    if formats_list
                    else "None"
                )

                comments = book_data.get("comments", [])
                comment_text = ""
                if comments:
                    if isinstance(comments, list) and comments:
                        comment_text = (
                            comments[0].get("text", "")
                            if isinstance(comments[0], dict)
                            else str(comments[0])
                        )
                    elif isinstance(comments, str):
                        comment_text = comments

                formatted_text = f"""
═══════════════════════════════════════════════════════════════
BOOK METADATA
═══════════════════════════════════════════════════════════════

Title:       {title}
Author(s):   {authors_str}
Series:      {series_str if series_str else "None"}
Rating:      {rating_str}
Published:   {pubdate_str}
ISBN:        {isbn}

Tags:        {tags_str}
Formats:     {formats_str}

Description:
{comment_text[:500] + "..." if len(comment_text) > 500 else comment_text if comment_text else "No description available"}

Book ID:     {book_id}
═══════════════════════════════════════════════════════════════
""".strip()

                html_path = None
                if open_browser:
                    # Create HTML file
                    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Book Metadata: {title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .metadata-card {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .field {{
            margin: 15px 0;
            padding: 10px;
            background: #f8f9fa;
            border-left: 4px solid #3498db;
        }}
        .field-label {{
            font-weight: bold;
            color: #555;
            display: inline-block;
            min-width: 120px;
        }}
        .field-value {{
            color: #2c3e50;
        }}
        .description {{
            margin-top: 20px;
            padding: 15px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            line-height: 1.6;
        }}
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }}
        .tag {{
            background: #3498db;
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.9em;
        }}
        .format {{
            background: #27ae60;
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.9em;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <div class="metadata-card">
        <h1>{title}</h1>

        <div class="field">
            <span class="field-label">Author(s):</span>
            <span class="field-value">{authors_str}</span>
        </div>

        {f'<div class="field"><span class="field-label">Series:</span><span class="field-value">{series_str}</span></div>' if series_str else ""}

        <div class="field">
            <span class="field-label">Rating:</span>
            <span class="field-value">{rating_str}</span>
        </div>

        <div class="field">
            <span class="field-label">Published:</span>
            <span class="field-value">{pubdate_str}</span>
        </div>

        <div class="field">
            <span class="field-label">ISBN:</span>
            <span class="field-value">{isbn}</span>
        </div>

        <div class="field">
            <span class="field-label">Tags:</span>
            <div class="tags">
                {"".join([f'<span class="tag">{t}</span>' for t in tags_str.split(", ") if t and t != "None"])}
            </div>
        </div>

        <div class="field">
            <span class="field-label">Formats:</span>
            <div>
                {"".join([f'<span class="format">{f}</span>' for f in formats_str.split(", ") if f and f != "None"])}
            </div>
        </div>

        {f'<div class="description"><strong>Description:</strong><br>{comment_text}</div>' if comment_text else ""}

        <div class="field" style="margin-top: 20px; border-left-color: #95a5a6;">
            <span class="field-label">Book ID:</span>
            <span class="field-value">{book_id}</span>
        </div>
    </div>
</body>
</html>"""

                    # Save to temp file
                    temp_dir = Path(tempfile.gettempdir())
                    html_file = temp_dir / f"calibre_metadata_{book_id}.html"
                    html_file.write_text(html_content, encoding="utf-8")
                    html_path = str(html_file)

                    # Open in browser
                    system = platform.system()
                    if system == "Windows":
                        os.startfile(html_path)
                    elif system == "Darwin":  # macOS
                        subprocess.run(["open", html_path], check=False)
                    else:  # Linux
                        subprocess.run(["xdg-open", html_path], check=False)

                return {
                    "success": True,
                    "book_id": book_id,
                    "title": title,
                    "author": authors_str,
                    "metadata": book_data,
                    "html_path": html_path,
                    "formatted_text": formatted_text,
                }

            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"query": query, "author": author, "open_browser": open_browser},
                    tool_name="manage_metadata",
                    context="Showing book metadata",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'update', 'organize_tags', 'fix_issues', 'show'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='update' to update book metadata",
                    "Use operation='organize_tags' for AI-powered tag organization",
                    "Use operation='fix_issues' to automatically fix metadata problems",
                    "Use operation='show' to display book metadata",
                ],
                related_tools=["manage_metadata"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={"operation": operation, "updates": updates},
            tool_name="manage_metadata",
            context="Metadata management operation",
        )
