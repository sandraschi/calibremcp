"""
Anna's Archive search client for CalibreMCP.

Standalone client for searching Anna's Archive. Uses configurable mirrors.
HTML parsing may break if Anna's changes their page structure.
"""

import asyncio
import os
from typing import Any
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from ...config import CalibreConfig
from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.import_export.annas")

DEFAULT_MIRRORS = [
    "https://annas-archive.gl",
    "https://annas-archive.li",
    "https://annas-archive.se",
    "https://annas-archive.org",
]


class AnnasError(Exception):
    """Base exception for Anna's Archive operations."""
    pass

class AnnasNoLinksError(AnnasError):
    """No download links found for the MD5."""
    pass

class AnnasLinkRestrictionError(AnnasError):
    """Mirrors found, but they require manual interaction (landing pages)."""
    pass

class AnnasDownloadTimeoutError(AnnasError):
    """Download attempt timed out."""
    pass

def _get_mirrors() -> list[str]:
    """Get mirror list from CalibreConfig."""
    config = CalibreConfig.load_config()
    return config.annas_mirrors.copy()


async def search_annas(
    query: str,
    max_results: int = 20,
    timeout: float = 30.0,
    mirrors: list[str] | None = None,
) -> dict[str, Any]:
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
    if not mirrors:
        mirrors = DEFAULT_MIRRORS

    encoded_query = quote_plus(query)
    # display=table is preferred but it might fallback to grid
    url_template = "{base}/search?page=1&q={q}&display=table"

    for mirror in mirrors:
        try:
            url = url_template.format(base=mirror.rstrip("/"), q=encoded_query)
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                },
            ) as client:
                resp = await client.get(url)
                if resp.status_code >= 500:
                    logger.warning(f"Mirror {mirror} returned {resp.status_code}, trying next")
                    continue
                resp.raise_for_status()
                html = resp.text
                results = _parse_search_results(html, mirror, max_results)
                if results:
                    return {
                        "success": True,
                        "query": query,
                        "results": results,
                        "total_found": len(results),
                        "mirror_used": mirror,
                    }
                else:
                    logger.warning(f"No results parsed from {mirror}, trying next")
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
        "error": "No working mirrors. Anna's Archive may be down or layout changed.",
    }


def _parse_search_results(html: str, base_url: str, max_results: int) -> list[dict[str, Any]]:
    """
    Parse Anna's search results HTML. Supports both table and grid layouts.
    """
    results = []
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Layout 1: Table display
        rows = soup.select("table tr")
        if len(rows) > 1:
            for row in rows[: max_results + 1]:
                cols = row.find_all("td")
                if len(cols) < 5:  # Brittle, but safer check
                    continue
                cover_cell = cols[0]
                cover_link = cover_cell.find("a", tabindex="-1")
                if not cover_link:
                    continue
                href = cover_link.get("href", "")
                detail_item = href.split("/")[-1] if href else ""
                if not detail_item or "/md5/" not in href:
                    continue
                detail_url = f"{base_url.rstrip('/')}/md5/{detail_item}"

                title = "".join(cols[1].stripped_strings) if cols[1] else "Unknown Title"
                author = "".join(cols[2].stripped_strings) if cols[2] else "Unknown Author"
                # Some mirrors use different column counts, try to find formats at end
                formats = "".join(cols[-1].stripped_strings).upper() if cols else ""

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

        # Layout 2: Grid/List display (common fallback)
        if not results:
            # Often links look like <a href="/md5/..."> with <h3> for title
            md5_links = soup.select("a[href^='/md5/']")
            for link in md5_links:
                href = link.get("href", "")
                detail_item = href.split("/")[-1]
                detail_url = f"{base_url.rstrip('/')}/md5/{detail_item}"

                # Title is usually in h3 or next to the MD5 link
                title_node = link.select_one("h3")
                title = title_node.get_text(strip=True) if title_node else "Unknown Title"

                # Info string usually contains author and formats
                info_node = link.find_next("div", class_=lambda x: x and "italic" in x)
                info_text = info_node.get_text(strip=True) if info_node else ""
                
                # Naive split for author/format if in grid view
                author = info_text.split("[")[0] if "[" in info_text else info_text
                formats = info_text.split("[")[-1].replace("]", "").upper() if "[" in info_text else ""

                results.append(
                    {
                        "title": title,
                        "author": author.strip(),
                        "formats": formats.strip(),
                        "detail_url": detail_url,
                        "detail_item": detail_item,
                    }
                )
                if len(results) >= max_results:
                    break

    except Exception as e:
        logger.error(f"Failed to parse Anna's search results: {e}", exc_info=True)

    return results


async def get_annas_download_links(md5: str, mirror: str | None = None) -> list[dict[str, str]]:
    """
    Search the MD5 detail page for download links.

    Returns:
        [{"label": str, "url": str, "type": str}]
    """
    mirrors = [mirror] if mirror else _get_mirrors()
    timeout = 30.0
    links = []

    for base_mirror in mirrors:
        try:
            url = f"{base_mirror.rstrip('/')}/md5/{md5}"
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers={"User-Agent": "CalibreMCP/1.0 (ebook library manager)"},
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                # Look for "Slow-partner server" or "Libgen.rs" or "Z-Library"
                # They are usually in sections with specific classes or text labels
                # We'll look for all 'a' tags that look like download links
                a_tags = soup.find_all("a")
                for a in a_tags:
                    text = a.get_text(strip=True).lower()
                    href = a.get("href", "")
                    if not href:
                        continue

                    # Canonicalize href
                    if href.startswith("/"):
                        href = f"{base_mirror.rstrip('/')}{href}"

                    # Prioritize certain links
                    link_type = "other"
                    if "slow-partner" in text:
                        link_type = "slow"
                    elif "libgen.rs" in text or "libgen.li" in text:
                        link_type = "fast"
                    elif "z-library" in text:
                        link_type = "fast"
                    elif "ipfs" in text:
                        link_type = "fast"

                    if any(x in text for x in ["download", "mirror", "server", "link"]):
                        links.append({"label": text, "url": href, "type": link_type})

                if links:
                    return links
        except Exception as e:
            logger.warning(f"Failed to get download links from {base_mirror}: {e}")
            continue

    return links


async def download_annas_book(
    md5: str,
    target_format: str | None = None,
) -> str | None:
    """
    Advanced download logic: finds links, picks best, and downloads.
    This is complex because many links on Anna's are redirects or require interaction.
    For now, we'll try to find a direct-ish link.
    """
    links = await get_annas_download_links(md5)
    if not links:
        logger.error(f"No download links found for MD5: {md5}")
        return None

    # Sort links to prioritize "fast" or "slow" mirrors that are more reliable
    # 1. libgen, 2. ipfs, 3. slow-partner
    fast_links = [link for link in links if link["type"] == "fast"]
    slow_links = [link for link in links if link["type"] == "slow"]
    others = [link for link in links if link["type"] == "other"]

    best_links = fast_links + slow_links + others

    skipped_landing_pages = 0
    total_mirrors = len(best_links)

    # Try each link until one works or returns a file
    import tempfile

    for link_info in best_links:
        url = link_info["url"]
        logger.info(f"Attempting download from: {url} ({link_info['label']})")
        try:
            async with httpx.AsyncClient(
                timeout=300.0,  # Long timeout for slow downloads
                follow_redirects=True,
                headers={"User-Agent": "CalibreMCP/1.0 (ebook library manager)"},
            ) as client:
                # Some links might trigger a redirect to a real file
                async with client.stream("GET", url) as response:
                    if response.status_code != 200:
                        continue

                    content_type = response.headers.get("Content-Type", "").lower()
                    # If we got HTML, it's probably a landing page, not a file
                    if "text/html" in content_type:
                        logger.debug(f"Link {url} is a landing page, skipping")
                        skipped_landing_pages += 1
                        continue

                    # Create temp file with appropriate suffix if possible
                    suffix = ".epub"
                    if "application/pdf" in content_type:
                        suffix = ".pdf"
                    elif "application/epub+zip" in content_type:
                        suffix = ".epub"

                    fd, path = tempfile.mkstemp(suffix=suffix)
                    with os.fdopen(fd, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
                    return path
        except asyncio.TimeoutError:
            logger.warning(f"Download timed out from {url}")
            continue
        except Exception as e:
            logger.warning(f"Download failed from {url}: {e}")
            continue

    if skipped_landing_pages == total_mirrors and total_mirrors > 0:
        raise AnnasLinkRestrictionError(
            "All available mirrors are interactive landing pages (CAPTCHA/Timer). Manual download required."
        )

    if total_mirrors == 0:
         raise AnnasNoLinksError(f"No download links found for MD5: {md5}")

    return None
