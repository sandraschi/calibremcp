"""
Anna's Archive search client for CalibreMCP.

Standalone client for searching Anna's Archive. Uses configurable mirrors.
HTML parsing may break if Anna's changes their page structure.
"""

import os
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.import_export.annas")

DEFAULT_MIRRORS = [
    "https://annas-archive.se",
    "https://annas-archive.in",
]


def _get_mirrors() -> List[str]:
    """Get mirror list from env or default."""
    raw = os.environ.get("ANNAS_MIRRORS", "")
    if raw.strip():
        return [m.strip() for m in raw.split(",") if m.strip()]
    return DEFAULT_MIRRORS.copy()


async def search_annas(
    query: str,
    max_results: int = 20,
    timeout: float = 30.0,
    mirrors: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Search Anna's Archive for books.

    Args:
        query: Search query (title, author, etc.)
        max_results: Maximum number of results to return
        timeout: Request timeout in seconds

    Returns:
        {
            "success": bool,
            "query": str,
            "results": [{"title": str, "author": str, "formats": str, "detail_url": str, "detail_item": str}],
            "total_found": int,
            "mirror_used": str,
            "error": Optional[str]
        }
    """
    mirrors = mirrors if mirrors else _get_mirrors()
    encoded_query = quote_plus(query)
    url_template = "{base}/search?page=1&q={q}&display=table"

    for mirror in mirrors:
        try:
            url = url_template.format(base=mirror.rstrip("/"), q=encoded_query)
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers={"User-Agent": "CalibreMCP/1.0 (ebook library manager)"},
            ) as client:
                resp = await client.get(url)
                if resp.status_code >= 500:
                    logger.warning(f"Mirror {mirror} returned {resp.status_code}, trying next")
                    continue
                resp.raise_for_status()
                html = resp.text
                results = _parse_search_results(html, mirror, max_results)
                return {
                    "success": True,
                    "query": query,
                    "results": results,
                    "total_found": len(results),
                    "mirror_used": mirror,
                }
        except httpx.HTTPError as e:
            logger.warning(f"Mirror {mirror} failed: {e}")
            continue
        except Exception as e:
            logger.warning(f"Mirror {mirror} error: {e}")
            continue

    return {
        "success": False,
        "query": query,
        "results": [],
        "total_found": 0,
        "mirror_used": "",
        "error": "No working mirrors. Anna's Archive may be down or URL structure changed.",
    }


def _parse_search_results(html: str, base_url: str, max_results: int) -> List[Dict[str, Any]]:
    """
    Parse Anna's search results HTML.

    Structure (from ScottBot10 plugin): table/tr, columns:
    0=cover/link, 1=title, 2=author, ... 9=formats
    """
    results = []
    try:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tr")
        for row in rows[: max_results + 1]:
            cols = row.find_all("td")
            if len(cols) < 10:
                continue
            cover_cell = cols[0]
            cover_link = cover_cell.find("a", tabindex="-1")
            if not cover_link:
                continue
            href = cover_link.get("href", "")
            detail_item = href.split("/")[-1] if href else ""
            if not detail_item:
                continue
            detail_url = f"{base_url.rstrip('/')}/md5/{detail_item}"

            title = "".join(cols[1].stripped_strings) if cols[1] else ""
            author = "".join(cols[2].stripped_strings) if cols[2] else ""
            formats = "".join(cols[9].stripped_strings).upper() if cols[9] else ""

            results.append(
                {
                    "title": title,
                    "author": author,
                    "formats": formats,
                    "detail_url": detail_url,
                    "detail_item": detail_item,
                }
            )
            if len(results) >= max_results:
                break
    except Exception as e:
        logger.error(f"Failed to parse Anna's search results: {e}", exc_info=True)
    return results
