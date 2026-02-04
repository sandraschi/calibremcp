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
from datetime import datetime
from pathlib import Path
from typing import Any

from ...logging_config import get_logger
from ...services.book_service import book_service

logger = get_logger("calibremcp.tools.export.helpers")


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


async def export_csv_helper(
    output_path: str | None = None,
    book_ids: list[int] | None = None,
    author: str | None = None,
    tag: str | None = None,
    limit: int = 1000,
    include_fields: list[str] | None = None,
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

        fields_to_include = include_fields if include_fields else default_fields

        csv_rows = []
        for book in books:
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


async def export_html_helper(
    output_path: str | None = None,
    book_ids: list[int] | None = None,
    author: str | None = None,
    tag: str | None = None,
    limit: int = 1000,
    open_file: bool = True,
) -> dict[str, Any]:
    """Helper function - NOT registered as MCP tool."""
    # Import HTML generation from original file
    from .export_books import _generate_styled_html

    try:
        books = _get_books_for_export(book_ids=book_ids, author=author, tag=tag, limit=limit)

        if not books:
            return {
                "success": False,
                "error": "No books found to export",
                "file_path": None,
                "books_exported": 0,
            }

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
            books, author, tag, book_ids, export_date, export_date_formatted
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
