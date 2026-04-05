"""
arXiv client for CalibreMCP.
Queries the arXiv API (Atom feed) for search and direct PDF acquisition.
"""

import asyncio
import tempfile
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.import_export.arxiv")

ARXIV_API_BASE = "https://export.arxiv.org/api/query"

async def search_arxiv(query: str, max_results: int = 10) -> dict[str, Any]:
    """
    Search arXiv for papers using the official Atom API.
    
    Returns:
        {
            "success": bool,
            "results": [{"id": str, "title": str, "authors": list[str], "summary": str, "pdf_url": str, "abs_url": str}],
            "count": int
        }
    """
    try:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        max_retries = 5
        retry_delay = 5.0  # arXiv suggests 3s, but we use 5s + backoff for safety
        
        headers = {
            "User-Agent": "CalibreMCP/1.0 (https://github.com/sandraschi/calibre-mcp; mailto:contact@example.com)"
        }
        
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            for attempt in range(max_retries):
                try:
                    resp = await client.get(ARXIV_API_BASE, params=params)
                    resp.raise_for_status()
                    break # Success
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429 and attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"arXiv rate limited (429). Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue
                    raise # Re-raise if not 429 or max retries reached
            
            soup = BeautifulSoup(resp.content, "xml") # arXiv uses Atom XML
            entries = soup.find_all("entry")
            
            results = []
            for entry in entries:
                # Extract arXiv ID from <id> e.g. http://arxiv.org/abs/2401.00001v1
                id_node = entry.find("id")
                if not id_node:
                    continue
                entry_id_full = id_node.get_text(strip=True)
                
                if "/abs/" not in entry_id_full:
                    # Fallback ID extraction
                    arxiv_id = entry_id_full.split("/")[-1]
                else:
                    arxiv_id = entry_id_full.split("/abs/")[-1]
                
                # Title often contains extra whitespace/newlines
                title_node = entry.find("title")
                title = " ".join(title_node.get_text().split()) if title_node else "No Title"
                
                # Multiple authors
                authors = []
                for author_node in entry.find_all("author"):
                    name_node = author_node.find("name")
                    if name_node:
                        authors.append(name_node.get_text(strip=True))
                
                # Abstract
                summary_node = entry.find("summary")
                summary = " ".join(summary_node.get_text().split()) if summary_node else ""
                
                # Links
                pdf_url = ""
                abs_url = entry_id_full
                for link in entry.find_all("link"):
                    if link.get("title") == "pdf":
                        pdf_url = link.get("href")
                    elif link.get("type") == "application/pdf":
                        pdf_url = link.get("href")
                
                # Ensure PDF link is HTTPS
                if pdf_url and pdf_url.startswith("http://"):
                    pdf_url = pdf_url.replace("http://", "https://")

                # Published date
                pub_node = entry.find("published")
                published = pub_node.get_text(strip=True) if pub_node else None

                results.append({
                    "id": arxiv_id,
                    "title": title,
                    "authors": authors,
                    "summary": summary,
                    "pdf_url": pdf_url,
                    "abs_url": abs_url,
                    "published": published
                })
                
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
            
    except Exception as e:
        logger.error(f"arXiv search failed: {e}")
        return {"success": False, "error": str(e), "results": [], "count": 0}

async def download_arxiv_paper(arxiv_id_or_url: str) -> str | None:
    """
    Download the PDF for an arXiv paper.
    
    Args:
        arxiv_id_or_url: e.g. '2401.00001' or 'https://arxiv.org/abs/2401.00001'
        
    Returns:
        Path to temporary PDF file
    """
    try:
        # Normalize ID
        arxiv_id = arxiv_id_or_url.split("/abs/")[-1].split("/pdf/")[-1]
        arxiv_id = re.sub(r"^arxiv:", "", arxiv_id, flags=re.IGNORECASE)
        
        # arXiv PDF direct link pattern
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            resp = await client.get(pdf_url)
            
            # Sometimes .pdf suffix isn't needed or redirect fails
            if resp.status_code != 200:
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
                resp = await client.get(pdf_url)
                
            resp.raise_for_status()
            
            # Save to temp file
            fd, path = tempfile.mkstemp(suffix=".pdf")
            with open(path, "wb") as f:
                f.write(resp.content)
            
            logger.info(f"Downloaded arXiv paper {arxiv_id} to {path}")
            return path
            
    except Exception as e:
        logger.error(f"arXiv download failed for {arxiv_id_or_url}: {e}")
        return None
