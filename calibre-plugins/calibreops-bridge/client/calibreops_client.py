"""
calibreops_client.py — HTTP client for calibreops MCP server

Wraps the calibreops backend (http://localhost:10720) for use from
within the Calibre plugin. All methods are synchronous — call from
a QThread, not the main Qt thread.

CURRENT STATUS: Stubs — endpoint paths TBD pending confirmation of
calibreops transport mode (HTTP vs stdio) and API surface.
See docs/CALIBREOPS_BRIDGE_SPEC.md, Open Questions section.

Two candidate approaches:
  A) Direct MCP JSON-RPC if calibreops runs with HTTP transport
  B) Thin REST shim added to calibreops (recommended)

This client is written for Option B (plain REST). Adjust if we go with A.
"""
import json
import urllib.error
import urllib.request
from typing import Any


class CalibreopsClient:
    """
    Thin HTTP client for the calibreops REST shim.

    Instantiate with the server base URL from plugin prefs.
    All methods raise CalibreopsError on failure.
    """

    def __init__(self, base_url: str = 'http://localhost:10720', timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout  = timeout

    # ------------------------------------------------------------------
    # Core helper
    # ------------------------------------------------------------------

    def _post(self, path: str, payload: dict) -> Any:
        url  = f'{self.base_url}{path}'
        data = json.dumps(payload).encode('utf-8')
        req  = urllib.request.Request(
            url, data=data,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise CalibreopsError(f'Cannot reach calibreops at {url}: {e}') from e
        except json.JSONDecodeError as e:
            raise CalibreopsError(f'Invalid JSON response from calibreops: {e}') from e

    def _get(self, path: str, params: dict | None = None) -> Any:
        if params:
            qs = urllib.parse.urlencode(params)
            path = f'{path}?{qs}'
        url = f'{self.base_url}{path}'
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise CalibreopsError(f'Cannot reach calibreops at {url}: {e}') from e

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def health(self) -> bool:
        """Returns True if calibreops server is reachable."""
        try:
            self._get('/health')
            return True
        except CalibreopsError:
            return False

    # ------------------------------------------------------------------
    # Metadata search (confirmed endpoint — /api/search)
    # ------------------------------------------------------------------

    def search(self, query: str, limit: int = 20) -> list[dict]:
        """
        Metadata search via the confirmed webapp endpoint.
        GET /api/search?query=...&limit=N
        Returns list of book dicts.
        """
        import urllib.parse
        params = urllib.parse.urlencode({'query': query, 'limit': limit})
        result = self._get(f'/api/search?{params}')
        # Endpoint returns {items: [...]} or {results: [...]} or {books: [...]}
        return result.get('items') or result.get('results') or result.get('books') or []

    # ------------------------------------------------------------------
    # RAG search
    # ------------------------------------------------------------------

    def rag_retrieve(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Semantic RAG search over book content.
        Returns list of {book_id, title, author, passage, score}.

        Endpoint: POST /api/rag
        Stub — path TBD.
        """
        # TODO: confirm endpoint path after REST shim is added to calibreops
        result = self._post('/api/rag', {'query': query, 'top_k': top_k})
        return result.get('results', [])

    # ------------------------------------------------------------------
    # Metadata search
    # ------------------------------------------------------------------

    def metadata_search(self, query: str, limit: int = 20) -> list[dict]:
        """
        Semantic search over book metadata (title, author, tags, comments).
        Returns list of {book_id, title, authors, tags, score}.

        Endpoint: POST /api/metadata/search
        Stub — path TBD.
        """
        result = self._post('/api/metadata/search', {'query': query, 'limit': limit})
        return result.get('results', [])

    # ------------------------------------------------------------------
    # Series analysis
    # ------------------------------------------------------------------

    def series_analysis(self, series_name: str) -> dict:
        """
        Reading order and completion analysis for a series.
        Returns {series, books: [{index, title, owned, read}], missing: [...]}

        Endpoint: POST /api/series
        Stub — path TBD.
        """
        result = self._post('/api/series', {'series': series_name})
        return result

    # ------------------------------------------------------------------
    # Synopsis
    # ------------------------------------------------------------------

    def synopsis(self, book_id: int, spoilers: bool = False) -> str:
        """
        Generate a synopsis for a book using calibreops RAG synthesis.
        Returns synopsis text.

        Endpoint: POST /api/synopsis
        Stub — path TBD.
        """
        result = self._post('/api/synopsis', {'book_id': book_id, 'spoilers': spoilers})
        return result.get('synopsis', '')


class CalibreopsError(Exception):
    """Raised when a calibreops request fails."""
    pass
