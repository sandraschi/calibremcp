"""
Client for Calibre webapp backend (HTTP API).
Used for bulk enrich, VL from query when backend is running on port 13000.
"""

import json
import urllib.error
import urllib.request
from typing import Any


def _get_base_url() -> str:
    from calibre_plugins.calibre_mcp_integration.config import prefs

    return prefs.get("mcp_http_url", "http://127.0.0.1:13000").rstrip("/")


def is_available() -> bool:
    """Check if Calibre webapp backend is reachable."""
    try:
        req = urllib.request.Request(
            _get_base_url() + "/docs",
            method="GET",
            headers={"Accept": "text/html"},
        )
        urllib.request.urlopen(req, timeout=2)
        return True
    except Exception:
        return False


def call_search(
    query: str | None = None,
    author: str | None = None,
    limit: int = 100,
) -> dict[str, Any] | None:
    """Call /api/search. Returns result with items/results/books list or None on failure."""
    try:
        from urllib.parse import urlencode

        params = {"limit": limit}
        if query:
            params["query"] = query
        if author:
            params["author"] = author
        qs = urlencode(params)
        req = urllib.request.Request(
            _get_base_url() + "/api/search?" + qs,
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None
