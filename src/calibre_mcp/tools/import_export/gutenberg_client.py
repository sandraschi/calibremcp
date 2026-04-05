"""
Project Gutenberg client for CalibreMCP.
Uses Gutendex (gutendex.com) for searching.
"""

import tempfile
from typing import Any

import httpx

from ...config import CalibreConfig
from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.import_export.gutenberg")

GUTENDEX_BASE = "https://gutendex.com/books/"


async def search_gutenberg(query: str) -> dict[str, Any]:
    """
    Search Project Gutenberg via Gutendex.

    Returns:
        {
            "success": bool,
            "results": [{"id": int, "title": str, "authors": list, "formats": dict, "detail_url": str}],
            "count": int
        }
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(GUTENDEX_BASE, params={"search": query})
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("results", []):
                # Clean up authors
                authors = [a.get("name", "Unknown") for a in item.get("authors", [])]

                # Use configured mirror for detail URL
                config = CalibreConfig.load_config()
                mirror = config.gutenberg_mirror.rstrip("/")

                results.append(
                    {
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "authors": authors,
                        "formats": item.get("formats", {}),
                        "detail_url": f"{mirror}/ebooks/{item.get('id')}",
                    }
                )

            return {
                "success": True,
                "results": results,
                "count": data.get("count", 0),
            }
    except Exception as e:
        logger.error(f"Gutenberg search failed: {e}")
        return {"success": False, "error": str(e), "results": [], "count": 0}


async def download_gutenberg_book(
    book_id: int,
    preferred_format: str = "application/epub+zip",
) -> str | None:
    """
    Download a book from Project Gutenberg.

    Args:
        book_id: Gutenberg book ID
        preferred_format: Mime type of the preferred format

    Returns:
        Path to temporary file
    """
    # Gutendex usually provides direct URLs to gutenberg.org or mirrors
    # We first need to get the book details to find the format URLs
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{GUTENDEX_BASE}{book_id}/")
            resp.raise_for_status()
            data = resp.json()
            formats = data.get("formats", {})

            # Selection logic: preferred -> epub -> any
            url = formats.get(preferred_format)
            if not url:
                url = formats.get("application/epub+zip")
            if not url:
                # Last resort: find any non-html link
                for fmt, f_url in formats.items():
                    if "text/html" not in fmt:
                        url = f_url
                        break

            if not url:
                logger.error(f"No suitable download format found for Gutenberg book {book_id}")
                return None

            # Download the file
            async with httpx.AsyncClient(
                timeout=120.0,
                follow_redirects=True,
                headers={"User-Agent": "CalibreMCP/1.0 (ebook library manager)"},
            ) as dl_client:
                dl_resp = await dl_client.get(url)
                dl_resp.raise_for_status()

                # Save to temp file
                suffix = ".epub"
                if "pdf" in url.lower():
                    suffix = ".pdf"
                elif "mobi" in url.lower():
                    suffix = ".mobi"
                elif "txt" in url.lower():
                    suffix = ".txt"

                fd, path = tempfile.mkstemp(suffix=suffix)
                with open(path, "wb") as f:
                    f.write(dl_resp.content)
                return path

    except Exception as e:
        logger.error(f"Gutenberg download failed for {book_id}: {e}")
        return None
