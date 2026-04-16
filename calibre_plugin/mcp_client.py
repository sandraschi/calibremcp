"""
Client for calibre-mcp webapp backend (HTTP API, port 10720).
All calls use stdlib urllib only — no external deps.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def _get_base_url() -> str:
    from calibre_plugins.calibre_mcp_integration.config import prefs
    return prefs.get("mcp_http_url", "http://127.0.0.1:10720").rstrip("/")


def _get(path: str, params: dict | None = None, timeout: int = 10) -> dict | None:
    url = _get_base_url() + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _post(path: str, body: dict | None = None, timeout: int = 30) -> dict | None:
    url = _get_base_url() + path
    data = json.dumps(body or {}).encode()
    try:
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def is_available() -> bool:
    """Check if calibre-mcp webapp backend is reachable."""
    try:
        req = urllib.request.Request(_get_base_url() + "/health",
                                     headers={"Accept": "application/json"})
        urllib.request.urlopen(req, timeout=2)
        return True
    except Exception:
        return False


def call_search(query: str | None = None, author: str | None = None,
                limit: int = 100) -> dict[str, Any] | None:
    """GET /api/search — metadata keyword search."""
    params: dict = {"limit": limit}
    if query:
        params["query"] = query
    if author:
        params["author"] = author
    return _get("/api/search", params)


def semantic_search(query: str, top_k: int = 20) -> list[dict]:
    """GET /api/rag/metadata/search — semantic search over LanceDB metadata index.
    Returns list of {book_id, title, text, score} dicts."""
    result = _get("/api/rag/metadata/search", {"q": query, "top_k": top_k})
    if not result:
        return []
    return result.get("results") or []


def passage_search(query: str, top_k: int = 15) -> list[dict]:
    """GET /api/rag/retrieve — semantic passage retrieval from full-text index.
    Returns list of {book_id, title, chunk_idx, snippet, rank} dicts."""
    result = _get("/api/rag/retrieve", {"q": query, "top_k": top_k})
    if not result:
        return []
    return result.get("hits") or []


def series_analysis(series_name: str) -> dict | None:
    """GET /api/series/analysis — reading order and completion for a named series."""
    return _get("/api/series/analysis", {"series_name": series_name}, timeout=15)


def get_book(book_id: int) -> dict | None:
    """GET /api/books/{book_id} — full book metadata."""
    return _get(f"/api/books/{book_id}")


def wikipedia_summary(title: str, author: str = "") -> str:
    """Fetch Wikipedia summary for a book title. Returns plain text or empty string."""
    import urllib.parse as up
    slug = up.quote(title.replace(" ", "_"), safe="_")
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "CalibreMCPPlugin/1.0 (calibre plugin; research tool)"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
            if data.get("type") != "disambiguation" and data.get("extract"):
                return data["extract"]
    except Exception:
        pass
    # Retry with "(novel)" disambiguator
    try:
        slug2 = up.quote(f"{title} (novel)".replace(" ", "_"), safe="_")
        url2 = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug2}"
        req2 = urllib.request.Request(
            url2,
            headers={"User-Agent": "CalibreMCPPlugin/1.0 (calibre plugin; research tool)"},
        )
        with urllib.request.urlopen(req2, timeout=8) as r2:
            data2 = json.loads(r2.read().decode())
            if data2.get("extract"):
                return data2["extract"]
    except Exception:
        pass
    return ""


def sf_encyclopedia(title: str) -> str:
    """Fetch SF Encyclopedia entry text. Returns plain text or empty string."""
    import re
    import unicodedata
    # SFE slug: lowercase, spaces→underscores, remove punctuation
    slug = unicodedata.normalize("NFKD", title)
    slug = re.sub(r"[^\w\s]", "", slug).strip().lower()
    slug = re.sub(r"\s+", "_", slug)
    try:
        url = f"https://www.sf-encyclopedia.com/entry/{slug}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "CalibreMCPPlugin/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode("utf-8", errors="replace")
        # Simple extraction — find main content between <article> or <div class="entry
        import re as _re
        m = _re.search(
            r'<(?:article|div[^>]*class="[^"]*entry[^"]*")[^>]*>(.*?)</(?:article|div)>',
            html, _re.DOTALL | _re.IGNORECASE
        )
        if m:
            # Strip tags
            text = _re.sub(r"<[^>]+>", " ", m.group(1))
            text = _re.sub(r"\s+", " ", text).strip()
            return text[:2500]
    except Exception:
        pass
    return ""
