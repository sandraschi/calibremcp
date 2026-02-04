"""
Import management portmanteau tool for CalibreMCP.

Consolidates import operations: from local path, from URL, from Anna's Archive.
"""

import tempfile
from pathlib import Path
from typing import Any

import httpx

from ...logging_config import get_logger
from ...server import mcp
from ..book_management.add_book import add_book_helper
from ..shared.error_handling import format_error_response, handle_tool_error
from .annas_client import search_annas

logger = get_logger("calibremcp.tools.import_export")


@mcp.tool()
async def manage_import(
    operation: str,
    file_path: str | None = None,
    url: str | None = None,
    query: str | None = None,
    max_results: int = 20,
    library_path: str | None = None,
) -> dict[str, Any]:
    """
    Import books from various sources.

    SUPPORTED OPERATIONS:
    - from_path: Add book from local file path (delegates to manage_books)
    - from_url: Download book from URL and add to library
    - annas_search: Search Anna's Archive, return matching results (no download)

    OPERATIONS DETAIL:

    from_path: Add from local file
    - Uses manage_books(operation='add') under the hood
    - Parameters: file_path (required)

    from_url: Download and add
    - Downloads file from URL to temp location, adds via calibredb
    - Supports direct download URLs (e.g. LibGen, IA)
    - Parameters: url (required)

    annas_search: Search Anna's Archive
    - Returns list of matches with title, author, formats, detail_url
    - User can open detail_url in browser to download, then use from_url or from_path
    - Parameters: query (required), max_results (default 20)
    """
    try:
        if operation == "annas_search":
            if not query or not query.strip():
                return format_error_response(
                    error_msg="query is required for annas_search",
                    error_code="MISSING_PARAM",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide query='author title' or similar"],
                    related_tools=["manage_import"],
                )
            result = await search_annas(query=query.strip(), max_results=max_results)
            return result

        if operation == "from_url":
            if not url or not url.strip():
                return format_error_response(
                    error_msg="url is required for from_url",
                    error_code="MISSING_PARAM",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide url='https://...' to a direct book download"],
                    related_tools=["manage_import"],
                )
            return await _download_and_add(url.strip(), library_path)

        if operation == "from_path":
            if not file_path or not file_path.strip():
                return format_error_response(
                    error_msg="file_path is required for from_path",
                    error_code="MISSING_PARAM",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide file_path to a local book file"],
                    related_tools=["manage_books"],
                )
            return await add_book_helper(
                file_path=file_path.strip(),
                fetch_metadata=True,
                library_path=library_path,
            )

        return format_error_response(
            error_msg=(
                f"Invalid operation: '{operation}'. Must be one of: "
                "'annas_search', 'from_url', 'from_path'"
            ),
            error_code="INVALID_OPERATION",
            error_type="ValueError",
            operation=operation,
            suggestions=[
                "Use operation='annas_search' to search Anna's Archive",
                "Use operation='from_url' to add book from download URL",
                "Use operation='from_path' to add book from local file",
            ],
            related_tools=["manage_import", "manage_books"],
        )
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={"query": query, "url": url, "file_path": file_path},
            tool_name="manage_import",
            context="Import operation",
        )


async def _download_and_add(
    url: str,
    library_path: str | None = None,
) -> dict[str, Any]:
    """Download file from URL to temp and add via add_book_helper."""
    suffix = ""
    if ".epub" in url.lower() or "epub" in url:
        suffix = ".epub"
    elif ".pdf" in url.lower() or "pdf" in url:
        suffix = ".pdf"
    elif ".mobi" in url.lower() or "mobi" in url:
        suffix = ".mobi"
    elif ".azw3" in url.lower() or "azw3" in url:
        suffix = ".azw3"
    else:
        suffix = ".epub"

    try:
        async with httpx.AsyncClient(
            timeout=120.0,
            follow_redirects=True,
            headers={"User-Agent": "CalibreMCP/1.0 (ebook library manager)"},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            content = resp.content
            content_type = resp.headers.get("content-type", "")
            if "text/html" in content_type and len(content) < 10000:
                return {
                    "success": False,
                    "error": "URL returned HTML instead of a book file. Use a direct download link.",
                    "hint": "For Anna's Archive results, open the detail page in a browser and use the direct download link from LibGen/Z-Library etc.",
                }

    except httpx.HTTPError as e:
        logger.error(f"Download failed for {url}: {e}")
        return {
            "success": False,
            "error": f"Download failed: {str(e)}",
        }

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = await add_book_helper(
            file_path=tmp_path,
            fetch_metadata=True,
            library_path=library_path,
        )
        return result
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except OSError:
            pass
