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
from .annas_client import download_annas_book, search_annas
from .arxiv_client import download_arxiv_paper, search_arxiv
from .gutenberg_client import download_gutenberg_book, search_gutenberg

logger = get_logger("calibremcp.tools.import_export")


@mcp.tool()
async def manage_import(
    operation: str,
    file_path: str | None = None,
    url: str | None = None,
    query: str | None = None,
    md5: str | None = None,
    book_id: int | None = None,
    arxiv_id: str | None = None,
    format: str | None = None,
    max_results: int = 20,
    library_path: str | None = None,
) -> dict[str, Any]:
    """
    Import books from various sources.

    SUPPORTED OPERATIONS:
    - from_path: Add book from local file path
    - from_url: Download book from URL and add
    - annas_search: Search Anna's Archive
    - annas_download: Download from Anna's by MD5
    - gutenberg_search: Search Project Gutenberg
    - gutenberg_import: Download and add from Gutenberg
    - arxiv_search: Search arXiv research papers
    - arxiv_import: Download and add from arXiv
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

            return await add_book_helper(
                file_path=file_path.strip(),
                fetch_metadata=True,
                library_path=library_path,
            )

        if operation == "annas_download":
            if not md5 or not md5.strip():
                return {"success": False, "error": "md5 is required for annas_download"}
            logger.info(f"Starting Anna's download for MD5: {md5}")
            tmp_path = await download_annas_book(md5.strip())
            if not tmp_path:
                return {"success": False, "error": "Could not extract download link for this MD5."}
            try:
                return await add_book_helper(file_path=tmp_path, library_path=library_path)
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        if operation == "gutenberg_search":
            if not query or not query.strip():
                return {"success": False, "error": "query is required for gutenberg_search"}
            return await search_gutenberg(query.strip())

        if operation == "gutenberg_import":
            if not book_id:
                return {"success": False, "error": "book_id is required for gutenberg_import"}
            logger.info(f"Starting Gutenberg import for #{book_id}")
            tmp_path = await download_gutenberg_book(book_id, preferred_format=format or "application/epub+zip")
            if not tmp_path:
                return {"success": False, "error": f"Failed to download Gutenberg book {book_id}"}
            try:
                return await add_book_helper(file_path=tmp_path, library_path=library_path)
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        if operation == "arxiv_search":
            if not query or not query.strip():
                return {"success": False, "error": "query is required for arxiv_search"}
            return await search_arxiv(query.strip(), max_results=max_results)

        if operation == "arxiv_import":
            target_id = arxiv_id or query
            if not target_id:
                return {"success": False, "error": "arxiv_id or query (as ID) is required for arxiv_import"}
            logger.info(f"Starting arXiv import for {target_id}")
            tmp_path = await download_arxiv_paper(target_id)
            if not tmp_path:
                return {"success": False, "error": f"Failed to download arXiv paper {target_id}"}
            try:
                return await add_book_helper(file_path=tmp_path, library_path=library_path)
            finally:
                Path(tmp_path).unlink(missing_ok=True)

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
                "Use operation='annas_download' with md5 to download mirror",
                "Use operation='from_url' to add book from download URL",
                "Use operation='from_path' to add book from local file",
                "Use operation='gutenberg_search' to search Project Gutenberg",
                "Use operation='gutenberg_import' with book_id to add from Gutenberg",
                "Use operation='arxiv_search' to search arXiv",
                "Use operation='arxiv_import' with arxiv_id to add from arXiv",
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
