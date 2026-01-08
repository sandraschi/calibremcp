"""
Export books to various formats (CSV, JSON, etc.).

DEPRECATED: These individual export functions are deprecated in favor of the export_books
portmanteau tool (see tools/import_export/export_books_portmanteau.py). These functions are kept
as helpers but are no longer registered with FastMCP 2.13+.

Use export_books(operation="...") instead:
- export_books_csv() → export_books(operation="csv", ...)
- export_books_json() → export_books(operation="json", ...)
- export_books_html() → export_books(operation="html", ...)
- export_books_pandoc() → export_books(operation="pandoc", ...)
"""

import csv
import json
import shutil
import os
import subprocess
import platform
import html as html_module
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...services.book_service import book_service
from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.export")


def _get_export_dir() -> Path:
    """
    Get the export directory (Desktop/calibre_exports/).

    Returns:
        Path to the calibre_exports directory
    """
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path(os.path.expanduser("~/Desktop"))
    export_dir = desktop / "calibre_exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def _open_file_with_app(file_path: Path) -> bool:
    """
    Open a file with the system's default application.

    Args:
        file_path: Path to the file to open

    Returns:
        True if file was opened successfully, False otherwise
    """
    try:
        system = platform.system()
        file_path_str = str(file_path)

        if system == "Windows":
            os.startfile(file_path_str)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path_str], check=False)
        else:  # Linux and others
            subprocess.run(["xdg-open", file_path_str], check=False)

        logger.info(f"Opened file with default application: {file_path}")
        return True
    except Exception as e:
        logger.warning(f"Could not open file {file_path} with default application: {e}")
        return False


def _generate_intelligent_filename(
    author: Optional[str] = None,
    tag: Optional[str] = None,
    book_ids: Optional[List[int]] = None,
    format_ext: str = "csv",
) -> str:
    """
    Generate an intelligent filename based on export parameters.

    Args:
        author: Author filter (if any)
        tag: Tag filter (if any)
        book_ids: List of specific book IDs (if any)
        format_ext: File extension (csv, json, docx, etc.)

    Returns:
        Intelligent filename like "Books by Conan Doyle.csv"
    """
    import re

    def sanitize_filename(text: str, max_length: int = 50) -> str:
        """Sanitize text for use in filename."""
        # Remove invalid filename characters
        text = re.sub(r'[<>:"/\\|?*]', "", text)
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)
        # Trim whitespace
        text = text.strip()
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length].rstrip()
        return text

    parts = []

    # Determine filename based on filters
    if book_ids and len(book_ids) <= 10:
        # Specific books - show count
        parts.append(f"Selected Books ({len(book_ids)})")
    elif author and tag:
        # Both filters
        author_clean = sanitize_filename(author, 30)
        tag_clean = sanitize_filename(tag, 20)
        parts.append(f"{tag_clean.title()} Books by {author_clean}")
    elif author:
        # Author filter
        author_clean = sanitize_filename(author, 40)
        parts.append(f"Books by {author_clean}")
    elif tag:
        # Tag filter
        tag_clean = sanitize_filename(tag, 40)
        parts.append(f"{tag_clean.title()} Books")
    elif book_ids:
        # Many specific books
        parts.append(f"Selected Books ({len(book_ids)})")
    else:
        # No filters - all books
        parts.append("All Books")

    # Combine and add extension
    filename = " ".join(parts) if parts else "Books Export"
    return f"{filename}.{format_ext}"


# NOTE: @mcp.tool() decorator removed - use export_books portmanteau tool instead
async def export_books_csv(
    output_path: Optional[str] = None,
    book_ids: Optional[List[int]] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 1000,
    include_fields: Optional[List[str]] = None,
    open_file: bool = True,
) -> Dict[str, Any]:
    """
    Export books to CSV format.

    Exports book metadata (title, authors, tags, rating, etc.) to a CSV file
    that can be opened in Excel, Google Sheets, or other spreadsheet applications.

    Args:
        output_path: Path where to save the CSV file. If None, saves to Desktop/calibre_exports/.
                    Example: "C:/Users/Name/Desktop/calibre_exports/books_export.csv"

        book_ids: Optional list of specific book IDs to export.
                 If None, exports all matching books (up to limit).

        author: Filter books by author name (optional)
                Example: export_books_csv(author="Conan Doyle")

        tag: Filter books by tag name (optional)
             Example: export_books_csv(tag="mystery")

        limit: Maximum number of books to export (default: 1000)
               Use -1 for no limit (exports all matching books)

        include_fields: List of fields to include in CSV. If None, includes all common fields.
                       Available fields: id, title, authors, tags, series, rating, pubdate,
                       publisher, isbn, comments, formats, has_cover, timestamp
                       Example: ["title", "authors", "rating", "tags"]

        open_file: If True, opens the exported file with the default application after export
                  (default: True). Works on Windows, macOS, and Linux.
                  Example: export_books_csv(open_file=True)

    Returns:
        Dictionary with export details:
        {
            "success": bool,
            "file_path": str,
            "books_exported": int,
            "fields_included": List[str],
            "export_date": str
        }

    Examples:
        # Export all books to CSV on Desktop
        export_books_csv()

        # Export books by specific author
        export_books_csv(author="Conan Doyle", output_path="conan_doyle_books.csv")

        # Export specific books with custom fields
        export_books_csv(book_ids=[1, 2, 3], include_fields=["title", "authors", "rating"])

        # Export mystery books with no limit
        export_books_csv(tag="mystery", limit=-1)
    """
    try:
        # Determine output path
        if not output_path:
            export_dir = _get_export_dir()
            filename = _generate_intelligent_filename(
                author=author, tag=tag, book_ids=book_ids, format_ext="csv"
            )
            output_path = str(export_dir / filename)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # If file already exists, append number to make it unique
        original_path = output_path
        counter = 1
        while output_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            output_path = original_path.parent / f"{stem} ({counter}){suffix}"
            counter += 1

        # Get books to export
        if book_ids:
            # Get specific books by ID
            books = []
            for book_id in book_ids:
                try:
                    book_data = book_service.get_by_id(book_id)
                    if book_data:
                        books.append(book_data)
                except Exception as e:
                    logger.warning(f"Could not retrieve book {book_id}: {e}")
        else:
            # Search for books with filters
            filters = {}
            if author:
                filters["author_name"] = author
            if tag:
                filters["tag_name"] = tag

            # Get all matching books (respect limit)
            search_limit = limit if limit > 0 else 10000  # Large limit for "all"
            offset = 0
            books = []

            while True:
                result = book_service.get_all(
                    skip=offset,
                    limit=min(search_limit, 1000),  # Page through results
                    **filters,
                )

                items = result.get("items", [])
                if not items:
                    break

                books.extend(items)
                offset += len(items)

                # Check if we've hit the limit
                if limit > 0 and len(books) >= limit:
                    books = books[:limit]
                    break

                # Check if we've gotten all results
                if len(items) < 1000:
                    break

        if not books:
            return {
                "success": False,
                "error": "No books found to export",
                "file_path": None,
                "books_exported": 0,
            }

        # Default fields to include
        default_fields = [
            "id",
            "title",
            "authors",
            "tags",
            "series",
            "rating",
            "pubdate",
            "publisher",
            "isbn",
            "comments",
            "formats",
            "has_cover",
            "timestamp",
        ]

        fields_to_include = include_fields if include_fields else default_fields

        # Flatten book data for CSV
        csv_rows = []
        for book in books:
            row = {}
            for field in fields_to_include:
                value = book.get(field, "")

                # Handle special formatting
                if field == "authors" and isinstance(value, list):
                    value = ", ".join(value)
                elif field == "tags" and isinstance(value, list):
                    value = ", ".join(value)
                elif field == "formats" and isinstance(value, list):
                    value = ", ".join(value)
                elif field == "series" and isinstance(value, dict):
                    value = value.get("name", "") if value else ""
                elif isinstance(value, (dict, list)):
                    value = json.dumps(value) if value else ""
                elif value is None:
                    value = ""

                row[field] = str(value)

            csv_rows.append(row)

        # Write CSV file
        with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            # Use utf-8-sig encoding for Excel compatibility
            writer = csv.DictWriter(csvfile, fieldnames=fields_to_include, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(csv_rows)

        logger.info(f"Exported {len(csv_rows)} books to {output_path}")

        # Open file with default application if requested
        opened = False
        if open_file:
            opened = _open_file_with_app(output_path)

        return {
            "success": True,
            "file_path": str(output_path),
            "books_exported": len(csv_rows),
            "fields_included": fields_to_include,
            "export_date": datetime.now().isoformat(),
            "opened": opened,
        }

    except Exception as e:
        logger.error(f"Error exporting books to CSV: {e}", exc_info=True)
        return {"success": False, "error": str(e), "file_path": None, "books_exported": 0}


# NOTE: @mcp.tool() decorator removed - use export_books portmanteau tool instead
async def export_books_json(
    output_path: Optional[str] = None,
    book_ids: Optional[List[int]] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 1000,
    pretty: bool = True,
    open_file: bool = True,
) -> Dict[str, Any]:
    """
    Export books to JSON format.

    Exports book metadata to a JSON file that can be used for data exchange,
    backup, or import into other systems.

    Args:
        output_path: Path where to save the JSON file. If None, saves to Desktop/calibre_exports/.
                    Example: "C:/Users/Name/Desktop/calibre_exports/books_export.json"

        book_ids: Optional list of specific book IDs to export.
                 If None, exports all matching books (up to limit).

        author: Filter books by author name (optional)

        tag: Filter books by tag name (optional)

        limit: Maximum number of books to export (default: 1000)
               Use -1 for no limit

        pretty: If True, format JSON with indentation (default: True)
                If False, use compact JSON format

        open_file: If True, opens the exported file with the default application after export
                  (default: True). Works on Windows, macOS, and Linux.
                  Example: export_books_json(open_file=True)

    Returns:
        Dictionary with export details:
        {
            "success": bool,
            "file_path": str,
            "books_exported": int,
            "export_date": str
        }

    Examples:
        # Export all books to JSON
        export_books_json()

        # Export specific books with compact format
        export_books_json(book_ids=[1, 2, 3], pretty=False)
    """
    try:
        # Determine output path
        if not output_path:
            export_dir = _get_export_dir()
            filename = _generate_intelligent_filename(
                author=author, tag=tag, book_ids=book_ids, format_ext="json"
            )
            output_path = str(export_dir / filename)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # If file already exists, append number to make it unique
        original_path = output_path
        counter = 1
        while output_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            output_path = original_path.parent / f"{stem} ({counter}){suffix}"
            counter += 1

        # Get books to export (same logic as CSV export)
        if book_ids:
            books = []
            for book_id in book_ids:
                try:
                    book_data = book_service.get_by_id(book_id)
                    if book_data:
                        books.append(book_data)
                except Exception as e:
                    logger.warning(f"Could not retrieve book {book_id}: {e}")
        else:
            filters = {}
            if author:
                filters["author_name"] = author
            if tag:
                filters["tag_name"] = tag

            search_limit = limit if limit > 0 else 10000
            offset = 0
            books = []

            while True:
                result = book_service.get_all(skip=offset, limit=min(search_limit, 1000), **filters)

                items = result.get("items", [])
                if not items:
                    break

                books.extend(items)
                offset += len(items)

                if limit > 0 and len(books) >= limit:
                    books = books[:limit]
                    break

                if len(items) < 1000:
                    break

        if not books:
            return {
                "success": False,
                "error": "No books found to export",
                "file_path": None,
                "books_exported": 0,
            }

        # Write JSON file
        with open(output_path, "w", encoding="utf-8") as jsonfile:
            if pretty:
                json.dump(books, jsonfile, indent=2, ensure_ascii=False, default=str)
            else:
                json.dump(books, jsonfile, ensure_ascii=False, default=str)

        logger.info(f"Exported {len(books)} books to {output_path}")

        # Open file with default application if requested
        opened = False
        if open_file:
            opened = _open_file_with_app(output_path)

        return {
            "success": True,
            "file_path": str(output_path),
            "books_exported": len(books),
            "export_date": datetime.now().isoformat(),
            "opened": opened,
        }

    except Exception as e:
        logger.error(f"Error exporting books to JSON: {e}", exc_info=True)
        return {"success": False, "error": str(e), "file_path": None, "books_exported": 0}


# NOTE: @mcp.tool() decorator removed - use export_books portmanteau tool instead
async def export_books_html(
    output_path: Optional[str] = None,
    book_ids: Optional[List[int]] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 1000,
    open_file: bool = True,
) -> Dict[str, Any]:
    """
    Export books to a beautiful HTML format with embedded CSS styling.

    Creates a standalone HTML file with professional styling that can be viewed
    in any web browser. The file includes a descriptive introduction, styled
    book listings, and is optimized for readability.

    Args:
        output_path: Path where to save the HTML file. If None, saves to Desktop/calibre_exports/.
                    Example: "C:/Users/Name/Desktop/calibre_exports/books_export.html"

        book_ids: Optional list of specific book IDs to export.
                 If None, exports all matching books (up to limit).

        author: Filter books by author name (optional)

        tag: Filter books by tag name (optional)

        limit: Maximum number of books to export (default: 1000)

        open_file: If True, opens the exported file with the default browser after export
                  (default: True).

    Returns:
        Dictionary with export details:
        {
            "success": bool,
            "file_path": str,
            "books_exported": int,
            "export_date": str,
            "opened": bool
        }

    Examples:
        # Export all books to beautiful HTML
        export_books_html()

        # Export books by author
        export_books_html(author="Conan Doyle")

        # Export specific books
        export_books_html(book_ids=[1, 2, 3])
    """
    try:
        # Get books to export (same logic as other exports)
        if book_ids:
            books = []
            for book_id in book_ids:
                try:
                    book_data = book_service.get_by_id(book_id)
                    if book_data:
                        books.append(book_data)
                except Exception as e:
                    logger.warning(f"Could not retrieve book {book_id}: {e}")
        else:
            filters = {}
            if author:
                filters["author_name"] = author
            if tag:
                filters["tag_name"] = tag

            search_limit = limit if limit > 0 else 10000
            offset = 0
            books = []

            while True:
                result = book_service.get_all(skip=offset, limit=min(search_limit, 1000), **filters)

                items = result.get("items", [])
                if not items:
                    break

                books.extend(items)
                offset += len(items)

                if limit > 0 and len(books) >= limit:
                    books = books[:limit]
                    break

                if len(items) < 1000:
                    break

        if not books:
            return {
                "success": False,
                "error": "No books found to export",
                "file_path": None,
                "books_exported": 0,
            }

        # Determine output path
        if not output_path:
            export_dir = _get_export_dir()
            filename = _generate_intelligent_filename(
                author=author, tag=tag, book_ids=book_ids, format_ext="html"
            )
            output_path = str(export_dir / filename)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # If file already exists, append number to make it unique
        original_path = output_path
        counter = 1
        while output_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            output_path = original_path.parent / f"{stem} ({counter}){suffix}"
            counter += 1

        # Generate HTML content
        export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        export_date_formatted = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        html_content = _generate_styled_html(
            books, author, tag, book_ids, export_date, export_date_formatted
        )

        # Write HTML file
        with open(output_path, "w", encoding="utf-8") as htmlfile:
            htmlfile.write(html_content)

        logger.info(f"Exported {len(books)} books to {output_path}")

        # Open file with default browser if requested
        opened = False
        if open_file:
            opened = _open_file_with_app(output_path)

        return {
            "success": True,
            "file_path": str(output_path),
            "books_exported": len(books),
            "export_date": datetime.now().isoformat(),
            "opened": opened,
        }

    except Exception as e:
        logger.error(f"Error exporting books to HTML: {e}", exc_info=True)
        return {"success": False, "error": str(e), "file_path": None, "books_exported": 0}


def _generate_styled_html(
    books: List[Dict[str, Any]],
    author: Optional[str],
    tag: Optional[str],
    book_ids: Optional[List[int]],
    export_date: str,
    export_date_formatted: str,
) -> str:
    """Generate styled HTML content for book export."""

    # Build filter description
    if author and tag:
        filter_desc = f'Books with tag "{tag}" by author "{author}"'
    elif author:
        filter_desc = f'Books by author "{author}"'
    elif tag:
        filter_desc = f'Books with tag "{tag}"'
    elif book_ids:
        ids_str = ", ".join(map(str, book_ids[:10]))
        ids_str += "..." if len(book_ids) > 10 else ""
        filter_desc = f"Selected books (IDs: {ids_str})"
    else:
        filter_desc = "All books in library"

    # CSS Styles
    css = """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .export-info {
            background: #f8f9fa;
            padding: 30px 40px;
            border-bottom: 2px solid #e9ecef;
        }
        
        .export-info h2 {
            color: #495057;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .info-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .info-item strong {
            color: #495057;
            display: block;
            margin-bottom: 5px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .info-item span {
            color: #212529;
            font-size: 1.1em;
        }
        
        .catalog {
            padding: 40px;
        }
        
        .catalog h2 {
            color: #495057;
            font-size: 2em;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }
        
        .book-card {
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 5px solid #667eea;
        }
        
        .book-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        }
        
        .book-card h3 {
            color: #212529;
            font-size: 1.6em;
            margin-bottom: 15px;
            color: #667eea;
        }
        
        .book-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
            margin-top: 15px;
        }
        
        .meta-item {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        
        .meta-item strong {
            color: #495057;
            display: block;
            margin-bottom: 5px;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .meta-item span {
            color: #212529;
            font-size: 1em;
        }
        
        .rating {
            color: #ffc107;
            font-size: 1.2em;
        }
        
        .description {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #28a745;
        }
        
        .description strong {
            color: #495057;
            display: block;
            margin-bottom: 10px;
            font-size: 1em;
        }
        
        .description p {
            color: #495057;
            line-height: 1.8;
            white-space: pre-wrap;
        }
        
        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .tag {
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 30px 40px;
            text-align: center;
            border-top: 2px solid #e9ecef;
            color: #6c757d;
        }
        
        .footer h2 {
            color: #495057;
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        
        .footer p {
            font-size: 1.1em;
            margin: 5px 0;
        }
        
        .separator {
            height: 2px;
            background: linear-gradient(to right, transparent, #667eea, transparent);
            margin: 30px 0;
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            .container {
                box-shadow: none;
                border-radius: 0;
            }
            .book-card:hover {
                transform: none;
                box-shadow: none;
            }
        }
    </style>
    """

    # Build HTML content
    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"    <title>Calibre Library Export - {len(books)} Books</title>",
        css,
        "</head>",
        "<body>",
        '    <div class="container">',
        "        <header>",
        "            <h1>Calibre Library Export</h1>",
        "        </header>",
        '        <div class="export-info">',
        "            <h2>Export Information</h2>",
        '            <div class="info-grid">',
        '                <div class="info-item">',
        "                    <strong>Export Date</strong>",
        f"                    <span>{export_date_formatted}</span>",
        "                </div>",
        '                <div class="info-item">',
        "                    <strong>Total Books</strong>",
        f"                    <span>{len(books)}</span>",
        "                </div>",
        '                <div class="info-item">',
        "                    <strong>Filter</strong>",
        f"                    <span>{filter_desc}</span>",
        "                </div>",
        "            </div>",
        "        </div>",
        '        <div class="catalog">',
        "            <h2>Book Catalog</h2>",
    ]

    # Add book cards
    for idx, book in enumerate(books, 1):
        authors = book.get("authors", [])
        author_str = (
            ", ".join(authors)
            if isinstance(authors, list) and authors
            else (authors if authors else "Unknown")
        )

        series = book.get("series", "")
        series_name = (
            series.get("name") if isinstance(series, dict) else (str(series) if series else "")
        )

        rating = book.get("rating", 0) or 0
        rating_stars = "★" * int(rating) if rating else ""
        rating_text = f"{rating_stars} ({int(rating)}/5 stars)" if rating else "Not rated"

        tags = book.get("tags", [])
        tag_list = tags if isinstance(tags, list) else [tags] if tags else []

        publisher = book.get("publisher", "")
        pubdate = book.get("pubdate", "")
        isbn = book.get("isbn", "")
        formats = book.get("formats", [])
        format_list = formats if isinstance(formats, list) else [formats] if formats else []

        comments = book.get("comments", "")
        if isinstance(comments, list) and comments:
            comments = (
                comments[0].get("text", "") if isinstance(comments[0], dict) else str(comments[0])
            )
        elif not isinstance(comments, str):
            comments = str(comments) if comments else ""

        html_parts.extend(
            [
                '            <div class="book-card">',
                f"                <h3>{idx}. {book.get('title', 'Untitled')}</h3>",
                '                <div class="book-meta">',
                '                    <div class="meta-item">',
                "                        <strong>Library ID</strong>",
                f"                        <span>{book.get('id', 'N/A')}</span>",
                "                    </div>",
            ]
        )

        if author_str != "Unknown":
            html_parts.extend(
                [
                    '                    <div class="meta-item">',
                    "                        <strong>Authors</strong>",
                    f"                        <span>{author_str}</span>",
                    "                    </div>",
                ]
            )

        if series_name:
            html_parts.extend(
                [
                    '                    <div class="meta-item">',
                    "                        <strong>Series</strong>",
                    f"                        <span>{series_name}</span>",
                    "                    </div>",
                ]
            )

        if rating:
            html_parts.extend(
                [
                    '                    <div class="meta-item">',
                    "                        <strong>Rating</strong>",
                    f'                        <span class="rating">{rating_text}</span>',
                    "                    </div>",
                ]
            )

        if tag_list:
            tag_html = "".join([f'<span class="tag">{tag}</span>' for tag in tag_list])
            html_parts.extend(
                [
                    '                    <div class="meta-item" style="grid-column: 1 / -1;">',
                    "                        <strong>Tags</strong>",
                    f'                        <div class="tags">{tag_html}</div>',
                    "                    </div>",
                ]
            )

        if publisher:
            html_parts.extend(
                [
                    '                    <div class="meta-item">',
                    "                        <strong>Publisher</strong>",
                    f"                        <span>{publisher}</span>",
                    "                    </div>",
                ]
            )

        if pubdate:
            html_parts.extend(
                [
                    '                    <div class="meta-item">',
                    "                        <strong>Publication Date</strong>",
                    f"                        <span>{pubdate}</span>",
                    "                    </div>",
                ]
            )

        if isbn:
            html_parts.extend(
                [
                    '                    <div class="meta-item">',
                    "                        <strong>ISBN</strong>",
                    f"                        <span>{isbn}</span>",
                    "                    </div>",
                ]
            )

        if format_list:
            format_str = ", ".join(format_list)
            html_parts.extend(
                [
                    '                    <div class="meta-item">',
                    "                        <strong>Available Formats</strong>",
                    f"                        <span>{format_str}</span>",
                    "                    </div>",
                ]
            )

        html_parts.append("                </div>")

        if comments and comments.strip():
            # Escape HTML in comments
            comments_escaped = html_module.escape(comments)
            html_parts.extend(
                [
                    '                <div class="description">',
                    "                    <strong>Description</strong>",
                    f"                    <p>{comments_escaped}</p>",
                    "                </div>",
                ]
            )

        html_parts.append("            </div>")

        if idx < len(books):
            html_parts.append('            <div class="separator"></div>')

    # Add footer
    html_parts.extend(
        [
            "        </div>",
            '        <div class="footer">',
            "            <h2>Export Summary</h2>",
            f"            <p>This catalog contains <strong>{len(books)} books</strong> exported from your Calibre library.</p>",
            f'            <p style="margin-top: 15px; font-style: italic;">Export generated on {export_date_formatted}</p>',
            "        </div>",
            "    </div>",
            "</body>",
            "</html>",
        ]
    )

    return "\n".join(html_parts)


# NOTE: @mcp.tool() decorator removed - use export_books portmanteau tool instead
async def export_books_pandoc(
    output_path: Optional[str] = None,
    format_type: str = "docx",
    book_ids: Optional[List[int]] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 100,
    open_file: bool = True,
) -> Dict[str, Any]:
    """
    Export books to various formats using Pandoc (if available).

    Converts book metadata to formats like DOCX, EPUB, HTML, LaTeX, RTF, etc.
    using Pandoc. Requires Pandoc to be installed on the system.

    **Common Usage Examples:**
    - "export books by Conan Doyle to docx" → export_books_pandoc(format_type="docx", author="Conan Doyle")
    - "export mystery books to pdf" → export_books_pandoc(format_type="pdf", tag="mystery")
    - "export all books to docx" → export_books_pandoc(format_type="docx")

    **How it works (similar to Advanced Memory MCP):**
    1. Fetches book metadata from the library
    2. Converts metadata to Markdown format
    3. Uses Pandoc to convert Markdown to the target format
    4. Saves the result to Desktop/calibre_exports/ with intelligent filename
    5. Automatically opens the file after export (can be disabled)

    **Supported formats:**
    - `docx` - Microsoft Word document (default) - **Recommended for most uses**
    - `html` - HTML webpage
    - `pdf` - PDF document (requires LaTeX)
    - `epub` - EPUB ebook
    - `latex` - LaTeX source
    - `odt` - OpenDocument Text
    - `rtf` - Rich Text Format
    - `txt` - Plain text

    Args:
        output_path: Path where to save the exported file. If None, saves to Desktop/calibre_exports/.
                    Example: "C:/Users/Name/Desktop/calibre_exports/books_export.docx"
                    If not provided, auto-generates filename: "calibre_books_export_YYYYMMDD_HHMMSS.{format}"

        format_type: Output format (default: "docx")
                    Supported: docx, epub, html, latex, odt, pdf, rtf, txt
                    Note: PDF export requires LaTeX (e.g., MiKTeX or TeX Live)

        book_ids: Optional list of specific book IDs to export.
                 If None, exports all matching books (up to limit).
                 Example: [1, 2, 3]

        author: Filter books by author name (optional)
                Example: "Conan Doyle"

        tag: Filter books by tag name (optional)
             Example: "mystery"

        limit: Maximum number of books to export (default: 100)
               Note: Pandoc processing can be slow for large exports
               Use smaller limits for formats like PDF that require more processing

        open_file: If True, opens the exported file with the default application after export
                  (default: True). Works on Windows, macOS, and Linux.
                  Example: export_books_pandoc(open_file=True)

    Returns:
        Dictionary with export details:
        {
            "success": bool,
            "file_path": str,
            "books_exported": int,
            "format": str,
            "pandoc_available": bool,
            "export_date": str,
            "error": Optional[str]  # Only present if success=False
        }

    Examples:
        # Export books by Conan Doyle to DOCX (most common use case)
        export_books_pandoc(format_type="docx", author="Conan Doyle")
        # OR (since docx is default): export_books_pandoc(author="Conan Doyle")

        # Export all books to DOCX (requires Pandoc installed)
        export_books_pandoc(format_type="docx")

        # Export books by author to HTML
        export_books_pandoc(format_type="html", author="Conan Doyle")

        # Export mystery books to DOCX
        export_books_pandoc(format_type="docx", tag="mystery")

        # Export specific books to PDF (requires Pandoc + LaTeX)
        export_books_pandoc(format_type="pdf", book_ids=[1, 2, 3], limit=10)

        # Export to custom path
        export_books_pandoc(format_type="docx", output_path="C:/Exports/my_books.docx")

        # Export mystery books to EPUB
        export_books_pandoc(format_type="epub", tag="mystery", limit=50)

    Note:
        - Pandoc must be installed and available in your system PATH
        - Check availability with: pandoc --version
        - For PDF export, you also need LaTeX (MiKTeX on Windows, TeX Live on Linux/Mac)
        - If Pandoc is not found, the function returns success=False with an error message
    """
    try:
        # Check if Pandoc is available
        pandoc_path = shutil.which("pandoc")
        if not pandoc_path:
            return {
                "success": False,
                "error": "Pandoc is not installed or not in PATH. Please install Pandoc to use this feature.",
                "pandoc_available": False,
                "file_path": None,
                "books_exported": 0,
            }

        # Get books to export (same logic as other exports)
        if book_ids:
            books = []
            for book_id in book_ids:
                try:
                    book_data = book_service.get_by_id(book_id)
                    if book_data:
                        books.append(book_data)
                except Exception as e:
                    logger.warning(f"Could not retrieve book {book_id}: {e}")
        else:
            filters = {}
            if author:
                filters["author_name"] = author
            if tag:
                filters["tag_name"] = tag

            search_limit = limit if limit > 0 else 1000
            offset = 0
            books = []

            while True:
                result = book_service.get_all(skip=offset, limit=min(search_limit, 1000), **filters)

                items = result.get("items", [])
                if not items:
                    break

                books.extend(items)
                offset += len(items)

                if limit > 0 and len(books) >= limit:
                    books = books[:limit]
                    break

                if len(items) < 1000:
                    break

        if not books:
            return {
                "success": False,
                "error": "No books found to export",
                "file_path": None,
                "books_exported": 0,
                "pandoc_available": True,
            }

        # Build descriptive introduction
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        export_date_formatted = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        intro_lines = [
            "# Calibre Library Export",
            "",
            "## Export Information",
            "",
            f"**Export Date:** {export_date_formatted}",
            f"**Total Books:** {len(books)}",
            "",
        ]

        # Add descriptive context based on filters
        if author and tag:
            intro_lines.extend([f'**Filter:** Books with tag "{tag}" by author "{author}"', ""])
        elif author:
            intro_lines.extend([f'**Filter:** Books by author "{author}"', ""])
        elif tag:
            intro_lines.extend([f'**Filter:** Books with tag "{tag}"', ""])
        elif book_ids:
            intro_lines.extend(
                [
                    f"**Filter:** Selected books (IDs: {', '.join(map(str, book_ids[:10]))}"
                    f"{'...' if len(book_ids) > 10 else ''})",
                    "",
                ]
            )
        else:
            intro_lines.extend(["**Filter:** All books in library", ""])

        intro_lines.extend(["---", "", "## Book Catalog", ""])

        markdown_lines = intro_lines

        for idx, book in enumerate(books, 1):
            markdown_lines.append(f"## {idx}. {book.get('title', 'Untitled')}")
            markdown_lines.append("")

            # Book ID
            markdown_lines.append(f"**Library ID:** {book.get('id', 'N/A')}")

            # Authors (primary information)
            authors = book.get("authors", [])
            if authors:
                author_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
                markdown_lines.append(f"**Authors:** {author_str}")

            # Series information
            if book.get("series"):
                series_name = (
                    book["series"].get("name")
                    if isinstance(book.get("series"), dict)
                    else str(book.get("series"))
                )
                markdown_lines.append(f"**Series:** {series_name}")

            # Rating
            if book.get("rating"):
                rating_val = int(book["rating"])
                markdown_lines.append(f"**Rating:** {'★' * rating_val} ({rating_val}/5 stars)")

            # Tags
            tags = book.get("tags", [])
            if tags:
                tag_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
                markdown_lines.append(f"**Tags:** {tag_str}")

            # Publisher
            if book.get("publisher"):
                markdown_lines.append(f"**Publisher:** {book['publisher']}")

            # Publication date
            if book.get("pubdate"):
                pubdate = book["pubdate"]
                if isinstance(pubdate, str):
                    markdown_lines.append(f"**Publication Date:** {pubdate}")
                else:
                    markdown_lines.append(f"**Publication Date:** {pubdate}")

            # ISBN
            if book.get("isbn"):
                markdown_lines.append(f"**ISBN:** {book['isbn']}")

            # Formats available
            formats = book.get("formats", [])
            if formats:
                format_str = ", ".join(formats) if isinstance(formats, list) else str(formats)
                markdown_lines.append(f"**Available Formats:** {format_str}")

            # Comments/Description
            if book.get("comments"):
                comments = book["comments"]
                if isinstance(comments, list) and comments:
                    comments = (
                        comments[0].get("text", "")
                        if isinstance(comments[0], dict)
                        else str(comments[0])
                    )
                if comments and comments.strip():
                    markdown_lines.append("")
                    markdown_lines.append("**Description:**")
                    markdown_lines.append("")
                    # Indent comments for better readability
                    comment_lines = comments.split("\n")
                    for line in comment_lines:
                        markdown_lines.append(f"  {line}")

            # Separator between books
            if idx < len(books):
                markdown_lines.append("")
                markdown_lines.append("---")
                markdown_lines.append("")

        # Add footer
        markdown_lines.extend(
            [
                "",
                "---",
                "",
                "## Export Summary",
                "",
                f"This catalog contains **{len(books)} books** exported from your Calibre library.",
                "",
                f"*Export generated on {export_date_formatted}*",
                "",
            ]
        )

        # Create temporary markdown file
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp_md:
            tmp_md.write("\n".join(markdown_lines))
            tmp_md_path = tmp_md.name

        # Determine output path
        if not output_path:
            export_dir = _get_export_dir()
            filename = _generate_intelligent_filename(
                author=author, tag=tag, book_ids=book_ids, format_ext=format_type
            )
            output_path = str(export_dir / filename)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # If file already exists, append number to make it unique
        original_path = output_path
        counter = 1
        while output_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            output_path = original_path.parent / f"{stem} ({counter}){suffix}"
            counter += 1

        # Convert using Pandoc
        import subprocess

        cmd = [
            pandoc_path,
            str(tmp_md_path),
            "-o",
            str(output_path),
            "-f",
            "markdown",
            "-t",
            format_type,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                raise Exception(f"Pandoc conversion failed: {result.stderr}")

            # Clean up temp file
            Path(tmp_md_path).unlink()

            logger.info(f"Exported {len(books)} books to {output_path} using Pandoc")

            # Open file with default application if requested
            opened = False
            if open_file:
                opened = _open_file_with_app(output_path)

            return {
                "success": True,
                "file_path": str(output_path),
                "books_exported": len(books),
                "format": format_type,
                "pandoc_available": True,
                "export_date": datetime.now().isoformat(),
                "opened": opened,
            }

        except subprocess.TimeoutExpired:
            Path(tmp_md_path).unlink()
            raise Exception("Pandoc conversion timed out")
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Pandoc executable not found",
                "pandoc_available": False,
                "file_path": None,
                "books_exported": 0,
            }

    except Exception as e:
        logger.error(f"Error exporting books with Pandoc: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "file_path": None,
            "books_exported": 0,
            "pandoc_available": shutil.which("pandoc") is not None,
        }
