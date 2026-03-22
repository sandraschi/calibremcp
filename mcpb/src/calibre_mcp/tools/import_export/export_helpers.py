"""
Helper functions for book export operations.

These functions are NOT registered as MCP tools - they are used internally
by the export_books portmanteau tool.
"""

import csv
import json
import os
import platform
import shutil
import subprocess
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from ...logging_config import get_logger
from ...services.book_service import book_service

logger = get_logger("calibremcp.tools.export.helpers")

DETAIL_LEVEL_FIELDS = {
    "minimal": ["id", "title", "authors"],
    "standard": ["id", "title", "authors", "tags", "series", "rating", "pubdate"],
    "full": None,  # All fields
}


def _get_export_dir() -> Path:
    """Get the export directory (Desktop/calibre_exports/)."""
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path(os.path.expanduser("~/Desktop"))
    export_dir = desktop / "calibre_exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def _open_file_with_app(file_path: Path) -> bool:
    """Open a file with the system's default application."""
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
    author: str | None = None,
    tag: str | None = None,
    book_ids: list[int] | None = None,
    format_ext: str = "csv",
) -> str:
    """Generate an intelligent filename based on export parameters."""
    import re

    def sanitize_filename(text: str, max_length: int = 50) -> str:
        """Sanitize text for use in filename."""
        text = re.sub(r'[<>:"/\\|?*]', "", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        if len(text) > max_length:
            text = text[:max_length].rstrip()
        return text

    parts = []

    if book_ids and len(book_ids) <= 10:
        parts.append(f"Selected Books ({len(book_ids)})")
    elif author and tag:
        author_clean = sanitize_filename(author, 30)
        tag_clean = sanitize_filename(tag, 20)
        parts.append(f"{tag_clean.title()} Books by {author_clean}")
    elif author:
        author_clean = sanitize_filename(author, 40)
        parts.append(f"Books by {author_clean}")
    elif tag:
        tag_clean = sanitize_filename(tag, 40)
        parts.append(f"{tag_clean.title()} Books")
    elif book_ids:
        parts.append(f"Selected Books ({len(book_ids)})")
    else:
        parts.append("All Books")

    filename = " ".join(parts) if parts else "Books Export"
    return f"{filename}.{format_ext}"


def _get_books_for_export(
    book_ids: list[int] | None = None,
    author: str | None = None,
    tag: str | None = None,
    limit: int = 1000,
) -> list[dict[str, Any]]:
    """Helper to get books for export (shared logic)."""
    if book_ids:
        books = []
        for book_id in book_ids:
            try:
                book_data = book_service.get_by_id(book_id)
                if book_data:
                    books.append(book_data)
            except Exception as e:
                logger.warning(f"Could not retrieve book {book_id}: {e}")
        return books
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

        return books


def _get_library_stats_for_export(
    book_ids: list[int] | None = None,
    author: str | None = None,
    tag: str | None = None,
    limit: int = 10000,
) -> dict[str, Any]:
    """Compute library statistics from books (for stats export)."""
    books = _get_books_for_export(book_ids=book_ids, author=author, tag=tag, limit=limit)
    if not books:
        return {
            "total_books": 0,
            "total_authors": 0,
            "total_series": 0,
            "total_tags": 0,
            "format_distribution": {},
            "top_authors": [],
            "top_series": [],
            "top_tags": [],
        }

    authors_count: dict[str, int] = defaultdict(int)
    series_count: dict[str, int] = defaultdict(int)
    tags_count: dict[str, int] = defaultdict(int)
    format_dist: dict[str, int] = defaultdict(int)

    for book in books:
        for a in book.get("authors") or []:
            authors_count[a] += 1
        s = book.get("series")
        if s:
            name = s.get("name", str(s)) if isinstance(s, dict) else str(s)
            if name:
                series_count[name] += 1
        for t in book.get("tags") or []:
            tags_count[t] += 1
        for fmt in book.get("formats") or []:
            format_dist[fmt.lower() if isinstance(fmt, str) else str(fmt).lower()] += 1

    def top_n(d: dict[str, int], n: int = 10) -> list[dict[str, Any]]:
        sorted_items = sorted(d.items(), key=lambda x: (-x[1], x[0]))[:n]
        return [{"name": k, "count": v} for k, v in sorted_items]

    return {
        "total_books": len(books),
        "total_authors": len(authors_count),
        "total_series": len(series_count),
        "total_tags": len(tags_count),
        "format_distribution": dict(format_dist),
        "top_authors": top_n(dict(authors_count)),
        "top_series": top_n(dict(series_count)),
        "top_tags": top_n(dict(tags_count)),
        "export_date": datetime.now().isoformat(),
    }


def _filter_book_by_detail_level(book: dict[str, Any], detail_level: str) -> dict[str, Any]:
    """Return book with only fields for the given detail level."""
    fields = DETAIL_LEVEL_FIELDS.get(detail_level, DETAIL_LEVEL_FIELDS["full"])
    if fields is None:
        return book
    return {k: v for k, v in book.items() if k in fields}


async def export_csv_helper(
    output_path: str | None = None,
    book_ids: list[int] | None = None,
    author: str | None = None,
    tag: str | None = None,
    limit: int = 1000,
    include_fields: list[str] | None = None,
    detail_level: str | None = None,
    open_file: bool = True,
) -> dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        if not output_path:
            export_dir = _get_export_dir()
            filename = _generate_intelligent_filename(
                author=author, tag=tag, book_ids=book_ids, format_ext="csv"
            )
            output_path = str(export_dir / filename)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        original_path = output_path
        counter = 1
        while output_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            output_path = original_path.parent / f"{stem} ({counter}){suffix}"
            counter += 1

        books = _get_books_for_export(book_ids=book_ids, author=author, tag=tag, limit=limit)

        if not books:
            return {
                "success": False,
                "error": "No books found to export",
                "file_path": None,
                "books_exported": 0,
            }

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
        if (
            detail_level
            and detail_level in DETAIL_LEVEL_FIELDS
            and DETAIL_LEVEL_FIELDS[detail_level]
        ):
            default_fields = DETAIL_LEVEL_FIELDS[detail_level]
        fields_to_include = include_fields if include_fields else default_fields

        csv_rows = []
        for book in books:
            if detail_level:
                book = _filter_book_by_detail_level(book, detail_level)
            row = {}
            for field in fields_to_include:
                value = book.get(field, "")

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

        with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields_to_include, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(csv_rows)

        logger.info(f"Exported {len(csv_rows)} books to {output_path}")

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


async def export_json_helper(
    output_path: str | None = None,
    book_ids: list[int] | None = None,
    author: str | None = None,
    tag: str | None = None,
    limit: int = 1000,
    pretty: bool = True,
    detail_level: str | None = None,
    open_file: bool = True,
) -> dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        if not output_path:
            export_dir = _get_export_dir()
            filename = _generate_intelligent_filename(
                author=author, tag=tag, book_ids=book_ids, format_ext="json"
            )
            output_path = str(export_dir / filename)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        original_path = output_path
        counter = 1
        while output_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            output_path = original_path.parent / f"{stem} ({counter}){suffix}"
            counter += 1

        books = _get_books_for_export(book_ids=book_ids, author=author, tag=tag, limit=limit)

        if not books:
            return {
                "success": False,
                "error": "No books found to export",
                "file_path": None,
                "books_exported": 0,
            }

        if detail_level:
            books = [_filter_book_by_detail_level(b, detail_level) for b in books]

        with open(output_path, "w", encoding="utf-8") as jsonfile:
            if pretty:
                json.dump(books, jsonfile, indent=2, ensure_ascii=False, default=str)
            else:
                json.dump(books, jsonfile, ensure_ascii=False, default=str)

        logger.info(f"Exported {len(books)} books to {output_path}")

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


def _generate_styled_html(
    books: list[dict[str, Any]],
    author: str | None,
    tag: str | None,
    book_ids: list[int] | None,
    export_date: str,
    export_date_formatted: str,
    style: str = "catalog",
) -> str:
    """Generate styled HTML catalog. Style: catalog, gallery, dashboard."""
    if style == "gallery":
        return _generate_html_gallery(
            books, author, tag, book_ids, export_date, export_date_formatted
        )
    if style == "dashboard":
        return _generate_html_dashboard(
            books, author, tag, book_ids, export_date, export_date_formatted
        )
    return _generate_html_catalog(books, author, tag, book_ids, export_date, export_date_formatted)


def _generate_html_catalog(
    books: list[dict[str, Any]],
    author: str | None,
    tag: str | None,
    book_ids: list[int] | None,
    export_date: str,
    export_date_formatted: str,
) -> str:
    """Generate catalog-style HTML (readable list)."""
    filter_desc = "All books"
    if author and tag:
        filter_desc = f'Books with tag "{tag}" by author "{author}"'
    elif author:
        filter_desc = f'Books by author "{author}"'
    elif tag:
        filter_desc = f'Books with tag "{tag}"'
    elif book_ids:
        filter_desc = f"Selected books ({len(book_ids)})"

    rows = []
    for book in books:
        authors = book.get("authors", [])
        author_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
        tags = book.get("tags", [])
        tag_str = ", ".join(tags[:5]) if isinstance(tags, list) else str(tags)
        if isinstance(tags, list) and len(tags) > 5:
            tag_str += "..."
        series = book.get("series", {}) or {}
        series_name = series.get("name", "") if isinstance(series, dict) else str(series)
        rows.append(
            f"""
        <tr>
            <td>{book.get("id", "")}</td>
            <td>{_escape_html(book.get("title", "Untitled"))}</td>
            <td>{_escape_html(author_str)}</td>
            <td>{_escape_html(series_name)}</td>
            <td>{book.get("rating", "")}</td>
            <td>{_escape_html(tag_str)}</td>
            <td>{book.get("pubdate", "")}</td>
        </tr>"""
        )

    html_table = "\n".join(rows) if rows else "<tr><td colspan='7'>No books</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calibre Library Export - {filter_desc}</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #1e1e2e; color: #cdd6f4; }}
        h1 {{ color: #cba6f7; }}
        .meta {{ color: #a6adc8; margin-bottom: 1.5rem; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #45475a; padding: 0.5rem 0.75rem; text-align: left; }}
        th {{ background: #313244; color: #cba6f7; }}
        tr:nth-child(even) {{ background: #181825; }}
    </style>
</head>
<body>
    <h1>Calibre Library Export</h1>
    <p class="meta"><strong>Filter:</strong> {_escape_html(filter_desc)} | <strong>Exported:</strong> {export_date_formatted} | <strong>Books:</strong> {len(books)}</p>
    <table>
        <thead><tr><th>ID</th><th>Title</th><th>Authors</th><th>Series</th><th>Rating</th><th>Tags</th><th>Pub Date</th></tr></thead>
        <tbody>{html_table}
        </tbody>
    </table>
</body>
</html>"""


def _escape_html(s: str) -> str:
    """Escape HTML entities."""
    if not s:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _generate_html_gallery(
    books: list[dict[str, Any]],
    author: str | None,
    tag: str | None,
    book_ids: list[int] | None,
    export_date: str,
    export_date_formatted: str,
) -> str:
    """Generate gallery-style HTML (cover grid)."""
    filter_desc = "All books"
    if author and tag:
        filter_desc = f'Tag "{tag}" by "{author}"'
    elif author:
        filter_desc = f'Author "{author}"'
    elif tag:
        filter_desc = f'Tag "{tag}"'
    elif book_ids:
        filter_desc = f"Selected ({len(book_ids)})"

    cards = []
    for book in books:
        title = _escape_html(book.get("title", "Untitled"))
        authors = book.get("authors", [])
        author_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
        cards.append(
            f"""
        <div class="card">
            <div class="cover">[Cover]</div>
            <div class="title">{title}</div>
            <div class="author">{_escape_html(author_str)}</div>
        </div>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calibre Gallery - {filter_desc}</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #1e1e2e; color: #cdd6f4; }}
        h1 {{ color: #cba6f7; }}
        .meta {{ color: #a6adc8; margin-bottom: 1.5rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 1rem; }}
        .card {{ text-align: center; }}
        .cover {{ width: 100px; height: 150px; margin: 0 auto 0.5rem; background: #313244; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #6c7086; font-size: 0.75rem; }}
        .title {{ font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem; }}
        .author {{ font-size: 0.8rem; color: #a6adc8; }}
    </style>
</head>
<body>
    <h1>Calibre Library - Gallery</h1>
    <p class="meta"><strong>{_escape_html(filter_desc)}</strong> | {export_date_formatted} | {len(books)} books</p>
    <div class="grid">{"".join(cards)}</div>
</body>
</html>"""


def _generate_html_dashboard(
    books: list[dict[str, Any]],
    author: str | None,
    tag: str | None,
    book_ids: list[int] | None,
    export_date: str,
    export_date_formatted: str,
) -> str:
    """Generate dashboard-style HTML (stats + book list)."""
    stats = _get_library_stats_for_export(
        book_ids=book_ids, author=author, tag=tag, limit=len(books) + 1
    )
    fmt_items = "".join(
        f"<li>{k}: {v}</li>"
        for k, v in sorted(stats.get("format_distribution", {}).items(), key=lambda x: -x[1])
    )
    top_authors = "".join(
        f"<li>{x['name']} ({x['count']})</li>" for x in stats.get("top_authors", [])[:10]
    )
    filter_desc = "All books"
    if author:
        filter_desc = f'Author "{author}"'
    if tag:
        filter_desc = (
            f'Tag "{tag}"' if filter_desc == "All books" else f'{filter_desc}, tag "{tag}"'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calibre Dashboard - {_escape_html(filter_desc)}</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #1e1e2e; color: #cdd6f4; }}
        h1 {{ color: #cba6f7; }}
        .stats {{ display: flex; gap: 2rem; margin-bottom: 2rem; flex-wrap: wrap; }}
        .stat {{ background: #313244; padding: 1rem 1.5rem; border-radius: 8px; }}
        .stat h3 {{ margin: 0 0 0.5rem; font-size: 1rem; color: #a6adc8; }}
        .stat .num {{ font-size: 1.5rem; font-weight: 700; color: #cba6f7; }}
        .columns {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }}
        @media (max-width: 768px) {{ .columns {{ grid-template-columns: 1fr; }} }}
        ul {{ margin: 0.5rem 0; padding-left: 1.5rem; }}
        .meta {{ color: #a6adc8; margin-bottom: 1rem; }}
    </style>
</head>
<body>
    <h1>Calibre Library Dashboard</h1>
    <p class="meta">{export_date_formatted} | {_escape_html(filter_desc)}</p>
    <div class="stats">
        <div class="stat"><h3>Books</h3><div class="num">{stats.get("total_books", 0)}</div></div>
        <div class="stat"><h3>Authors</h3><div class="num">{stats.get("total_authors", 0)}</div></div>
        <div class="stat"><h3>Series</h3><div class="num">{stats.get("total_series", 0)}</div></div>
        <div class="stat"><h3>Tags</h3><div class="num">{stats.get("total_tags", 0)}</div></div>
    </div>
    <div class="columns">
        <div>
            <h3>Format Distribution</h3>
            <ul>{fmt_items or "<li>None</li>"}</ul>
        </div>
        <div>
            <h3>Top Authors</h3>
            <ul>{top_authors or "<li>None</li>"}</ul>
        </div>
    </div>
    <h3>Books ({len(books)})</h3>
    <ul>
        {"".join(f"<li>{_escape_html(b.get('title', 'Untitled'))} - {_escape_html(', '.join(b.get('authors') or []))}</li>" for b in books[:50])}
        {f"<li><em>... and {len(books) - 50} more</em></li>" if len(books) > 50 else ""}
    </ul>
</body>
</html>"""


async def export_html_helper(
    output_path: str | None = None,
    book_ids: list[int] | None = None,
    author: str | None = None,
    tag: str | None = None,
    limit: int = 1000,
    html_style: str = "catalog",
    detail_level: str | None = None,
    open_file: bool = True,
) -> dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        books = _get_books_for_export(book_ids=book_ids, author=author, tag=tag, limit=limit)

        if not books:
            return {
                "success": False,
                "error": "No books found to export",
                "file_path": None,
                "books_exported": 0,
            }

        if detail_level:
            books = [_filter_book_by_detail_level(b, detail_level) for b in books]

        if not output_path:
            export_dir = _get_export_dir()
            filename = _generate_intelligent_filename(
                author=author, tag=tag, book_ids=book_ids, format_ext="html"
            )
            output_path = str(export_dir / filename)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        original_path = output_path
        counter = 1
        while output_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            output_path = original_path.parent / f"{stem} ({counter}){suffix}"
            counter += 1

        export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        export_date_formatted = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        html_content = _generate_styled_html(
            books, author, tag, book_ids, export_date, export_date_formatted, style=html_style
        )

        with open(output_path, "w", encoding="utf-8") as htmlfile:
            htmlfile.write(html_content)

        logger.info(f"Exported {len(books)} books to {output_path}")

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


async def export_pandoc_helper(
    output_path: str | None = None,
    format_type: str = "docx",
    book_ids: list[int] | None = None,
    author: str | None = None,
    tag: str | None = None,
    limit: int = 100,
    open_file: bool = True,
) -> dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    try:
        pandoc_path = shutil.which("pandoc")
        if not pandoc_path:
            return {
                "success": False,
                "error": "Pandoc is not installed or not in PATH. Please install Pandoc to use this feature.",
                "pandoc_available": False,
                "file_path": None,
                "books_exported": 0,
            }

        books = _get_books_for_export(book_ids=book_ids, author=author, tag=tag, limit=limit)

        if not books:
            return {
                "success": False,
                "error": "No books found to export",
                "file_path": None,
                "books_exported": 0,
                "pandoc_available": True,
            }

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
            markdown_lines.append(f"**Library ID:** {book.get('id', 'N/A')}")

            authors = book.get("authors", [])
            if authors:
                author_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
                markdown_lines.append(f"**Authors:** {author_str}")

            if book.get("series"):
                series_name = (
                    book["series"].get("name")
                    if isinstance(book.get("series"), dict)
                    else str(book.get("series"))
                )
                markdown_lines.append(f"**Series:** {series_name}")

            if book.get("rating"):
                rating_val = int(book["rating"])
                markdown_lines.append(f"**Rating:** {'★' * rating_val} ({rating_val}/5 stars)")

            tags = book.get("tags", [])
            if tags:
                tag_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
                markdown_lines.append(f"**Tags:** {tag_str}")

            if book.get("publisher"):
                markdown_lines.append(f"**Publisher:** {book['publisher']}")

            if book.get("pubdate"):
                pubdate = book["pubdate"]
                markdown_lines.append(f"**Publication Date:** {pubdate}")

            if book.get("isbn"):
                markdown_lines.append(f"**ISBN:** {book['isbn']}")

            formats = book.get("formats", [])
            if formats:
                format_str = ", ".join(formats) if isinstance(formats, list) else str(formats)
                markdown_lines.append(f"**Available Formats:** {format_str}")

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
                    comment_lines = comments.split("\n")
                    for line in comment_lines:
                        markdown_lines.append(f"  {line}")

            if idx < len(books):
                markdown_lines.append("")
                markdown_lines.append("---")
                markdown_lines.append("")

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

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp_md:
            tmp_md.write("\n".join(markdown_lines))
            tmp_md_path = tmp_md.name

        if not output_path:
            export_dir = _get_export_dir()
            filename = _generate_intelligent_filename(
                author=author, tag=tag, book_ids=book_ids, format_ext=format_type
            )
            output_path = str(export_dir / filename)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        original_path = output_path
        counter = 1
        while output_path.exists():
            stem = original_path.stem
            suffix = original_path.suffix
            output_path = original_path.parent / f"{stem} ({counter}){suffix}"
            counter += 1

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
                timeout=300,
            )

            if result.returncode != 0:
                raise Exception(f"Pandoc conversion failed: {result.stderr}")

            Path(tmp_md_path).unlink()

            logger.info(f"Exported {len(books)} books to {output_path} using Pandoc")

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


async def export_stats_csv_helper(
    output_path: str | None = None,
    library_name: str | None = None,
    open_file: bool = True,
) -> dict[str, Any]:
    """Export library statistics to CSV."""
    try:
        stats = _get_library_stats_for_export(limit=100000)
        if not output_path:
            export_dir = _get_export_dir()
            filename = f"Library Stats {datetime.now().strftime('%Y-%m-%d')}.csv"
            output_path = str(export_dir / filename)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        counter = 1
        orig = output_path
        while output_path.exists():
            output_path = orig.parent / f"{orig.stem} ({counter}){orig.suffix}"
            counter += 1

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Metric", "Value"])
            w.writerow(["total_books", stats.get("total_books", 0)])
            w.writerow(["total_authors", stats.get("total_authors", 0)])
            w.writerow(["total_series", stats.get("total_series", 0)])
            w.writerow(["total_tags", stats.get("total_tags", 0)])
            for fmt, cnt in sorted(
                stats.get("format_distribution", {}).items(), key=lambda x: -x[1]
            ):
                w.writerow([f"format_{fmt}", cnt])
            for item in stats.get("top_authors", [])[:20]:
                w.writerow([f"author:{item['name']}", item["count"]])

        opened = _open_file_with_app(output_path) if open_file else False
        return {
            "success": True,
            "file_path": str(output_path),
            "export_date": datetime.now().isoformat(),
            "opened": opened,
        }
    except Exception as e:
        logger.error(f"Error exporting stats to CSV: {e}", exc_info=True)
        return {"success": False, "error": str(e), "file_path": None}


async def export_stats_json_helper(
    output_path: str | None = None,
    library_name: str | None = None,
    pretty: bool = True,
    open_file: bool = True,
) -> dict[str, Any]:
    """Export library statistics to JSON."""
    try:
        stats = _get_library_stats_for_export(limit=100000)
        if not output_path:
            export_dir = _get_export_dir()
            filename = f"Library Stats {datetime.now().strftime('%Y-%m-%d')}.json"
            output_path = str(export_dir / filename)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        counter = 1
        orig = output_path
        while output_path.exists():
            output_path = orig.parent / f"{orig.stem} ({counter}){orig.suffix}"
            counter += 1

        with open(output_path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(stats, f, indent=2, default=str)
            else:
                json.dump(stats, f, default=str)

        opened = _open_file_with_app(output_path) if open_file else False
        return {
            "success": True,
            "file_path": str(output_path),
            "export_date": datetime.now().isoformat(),
            "opened": opened,
        }
    except Exception as e:
        logger.error(f"Error exporting stats to JSON: {e}", exc_info=True)
        return {"success": False, "error": str(e), "file_path": None}


async def export_stats_html_helper(
    output_path: str | None = None,
    library_name: str | None = None,
    open_file: bool = True,
) -> dict[str, Any]:
    """Export library statistics to standalone HTML page."""
    try:
        stats = _get_library_stats_for_export(limit=100000)
        if not output_path:
            export_dir = _get_export_dir()
            filename = f"Library Stats {datetime.now().strftime('%Y-%m-%d')}.html"
            output_path = str(export_dir / filename)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        counter = 1
        orig = output_path
        while output_path.exists():
            output_path = orig.parent / f"{orig.stem} ({counter}){orig.suffix}"
            counter += 1

        fmt_rows = "".join(
            f"<tr><td>{k}</td><td>{v}</td></tr>"
            for k, v in sorted(stats.get("format_distribution", {}).items(), key=lambda x: -x[1])
        )
        top_authors = "".join(
            f"<tr><td>{x['name']}</td><td>{x['count']}</td></tr>"
            for x in stats.get("top_authors", [])[:15]
        )
        top_tags = "".join(
            f"<tr><td>{x['name']}</td><td>{x['count']}</td></tr>"
            for x in stats.get("top_tags", [])[:15]
        )
        top_series = "".join(
            f"<tr><td>{x['name']}</td><td>{x['count']}</td></tr>"
            for x in stats.get("top_series", [])[:15]
        )
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calibre Library Statistics</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #1e1e2e; color: #cdd6f4; }}
        h1 {{ color: #cba6f7; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .stat {{ background: #313244; padding: 1rem; border-radius: 8px; text-align: center; }}
        .stat .num {{ font-size: 1.75rem; font-weight: 700; color: #cba6f7; }}
        .stat .label {{ font-size: 0.85rem; color: #a6adc8; margin-top: 0.25rem; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }}
        th, td {{ border: 1px solid #45475a; padding: 0.5rem 0.75rem; text-align: left; }}
        th {{ background: #313244; color: #cba6f7; }}
        .columns {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; }}
        .meta {{ color: #a6adc8; margin-bottom: 1.5rem; }}
    </style>
</head>
<body>
    <h1>Calibre Library Statistics</h1>
    <p class="meta">Generated {date_str}</p>
    <div class="stats">
        <div class="stat"><div class="num">{stats.get("total_books", 0)}</div><div class="label">Books</div></div>
        <div class="stat"><div class="num">{stats.get("total_authors", 0)}</div><div class="label">Authors</div></div>
        <div class="stat"><div class="num">{stats.get("total_series", 0)}</div><div class="label">Series</div></div>
        <div class="stat"><div class="num">{stats.get("total_tags", 0)}</div><div class="label">Tags</div></div>
    </div>
    <div class="columns">
        <div>
            <h2>Format Distribution</h2>
            <table><tr><th>Format</th><th>Count</th></tr>{fmt_rows or '<tr><td colspan="2">None</td></tr>'}</table>
        </div>
        <div>
            <h2>Top Authors</h2>
            <table><tr><th>Author</th><th>Books</th></tr>{top_authors or '<tr><td colspan="2">None</td></tr>'}</table>
        </div>
        <div>
            <h2>Top Tags</h2>
            <table><tr><th>Tag</th><th>Count</th></tr>{top_tags or '<tr><td colspan="2">None</td></tr>'}</table>
        </div>
        <div>
            <h2>Top Series</h2>
            <table><tr><th>Series</th><th>Books</th></tr>{top_series or '<tr><td colspan="2">None</td></tr>'}</table>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        opened = _open_file_with_app(output_path) if open_file else False
        return {
            "success": True,
            "file_path": str(output_path),
            "export_date": datetime.now().isoformat(),
            "opened": opened,
        }
    except Exception as e:
        logger.error(f"Error exporting stats to HTML: {e}", exc_info=True)
        return {"success": False, "error": str(e), "file_path": None}
