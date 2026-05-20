# CalibreOps Bridge — Architecture Spec & Project Plan

Plugin: `calibreops-bridge`
Status: Active development — existing plugin in calibre-mcp repo
Author: sandraschi
Target Calibre: 6.0+

Last updated: 2026-04-15

---

## Situation Assessment

The calibre-mcp repo already contains a working Calibre plugin at:
`D:\Dev\repos\calibre-mcp\calibre_plugin\`

Import name: `calibre_mcp_integration`
Current features (as of ~2025-01-30): Extended metadata panel (direct SQLite),
VL from query (calls webapp /api/search), bulk enrich placeholder, config dialog.

**This workspace (`calibre-plugins/calibreops-bridge`) is therefore for PHASE 2 work** —
surfacing the RAG/semantic-search/AI capabilities that the existing plugin does not yet have.
The two plugins can coexist, or the new work can be merged back into calibre-mcp's plugin.

---

## Transport — RESOLVED (FastMCP 3.2 simultaneous stdio + HTTP)

calibre-mcp is already on FastMCP 3.2.0 (pyproject.toml: `fastmcp>=3.2.0`).

The webapp backend (`main.py`) already does:
```python
mcp_app = create_mcp_app()
app.mount("/mcp", mcp_app)
```

This means the FastMCP server is mounted inside the FastAPI app on port 10720.
**Simultaneous stdio (for Claude Desktop) and HTTP (for the webapp + plugin) on the same
process, same port. No shim required. No separate port.**

The MCP client in `webapp/backend/app/mcp/client.py` uses `MCP_USE_HTTP=false` by default,
meaning tool calls go direct in-process (no HTTP round-trip at all — just Python function calls).
This is the fastest possible path and what the webapp uses.

For the Calibre plugin, the REST endpoints in `app/api/*.py` are the right interface.
These call `mcp_client.call_tool(...)` which resolves to in-process direct calls.

**All stale port 13000 references have been fixed to 10720.**
- **stdio**: default, used by Claude Desktop
- **HTTP Streamable**: `--http` flag or `MCP_TRANSPORT=http`, binds to port 10720 at `/mcp`
- **SSE**: deprecated

The webapp backend (port 10720, FastAPI) already exposes a full REST API — not MCP JSON-RPC,
but plain HTTP endpoints. This is the correct integration surface for the plugin.

Key confirmed REST endpoints (from ENDPOINTS.md):
```
GET  /health                         health check
GET  /api/search?query=...&limit=N   metadata search
GET  /api/books/{id}                 book details
POST /api/metadata/show              rich metadata display
GET  /api/analysis                   library analysis
GET  /api/specialized                reading recommendations, etc.
```

The existing `mcp_client.py` in the calibre_plugin already calls `/api/search` on port 13000
(old/different port). **The correct port for the active webapp is 10720.**

RAG endpoints are not yet exposed via REST. The `rag_retrieve`, `calibre_metadata_search`,
`media_synopsis` etc. are MCP tools — to call them from a plugin, we need either:
  A) A thin REST wrapper in the webapp backend (add FastAPI routes)
  B) Call MCP JSON-RPC directly over HTTP at `http://localhost:10720/mcp`

**Recommendation: Option A** — add `/api/rag`, `/api/synopsis`, `/api/series` to the webapp
backend. This is clean, consistent with existing REST pattern, and also benefits the webapp
frontend.

---

## Architecture

```
Calibre GUI
│
├── Existing plugin (calibre_mcp_integration, calibre-mcp repo)
│   └── Extended metadata, VL from query, bulk enrich stub
│
└── calibreops-bridge (this plugin — new features)
    ├── Toolbar button "CalibreOps Search"
    ├── SearchDialog — RAG + metadata semantic search
    ├── Right-click: "Synopsis" and "Series analysis"
    └── Config: server URL, timeout, result limit

Both plugins talk to:
  calibre-mcp webapp backend (http://localhost:10720)
  - Existing: /api/search, /api/books, /api/health
  - New (to add): /api/rag, /api/synopsis, /api/series
```

---

## What needs to be built

### In calibre-mcp (server side) — prerequisites

Add to `webapp/backend/app/`:

```python
# routes/rag.py
@router.post("/api/rag")
async def rag_search(query: str, top_k: int = 10):
    """Calls rag_retrieve MCP tool internally, returns results as JSON."""

@router.post("/api/synopsis")
async def synopsis(book_id: int, spoilers: bool = False):
    """Calls media_synopsis MCP tool internally."""

@router.post("/api/series")
async def series_analysis(series_name: str):
    """Calls get_series_analysis MCP tool internally."""
```

This is ~50-80 lines. The webapp backend already imports calibre_mcp internals so
these tools are directly callable — no MCP round-trip needed.

### In calibreops-bridge (plugin side)

**Update `client/calibreops_client.py`**: Point to port 10720 (not 13000).
The existing `mcp_client.py` calls port 13000 — this was probably a test/old config.
Correct URL from WEBAPP_PORTS.md: http://localhost:10720

**Build SearchDialog** (ui/search_dialog.py):
- QDialog with QLineEdit query input
- QComboBox: RAG / Metadata search mode
- QListWidget with results (title, author, snippet)
- Double-click or "Open in Calibre" button selects the book in library view

**Build SynopsisDialog** (ui/synopsis_dialog.py):
- Modal showing synopsis text
- "Copy" button

**Build SeriesDialog** (ui/series_dialog.py):
- QTableWidget: index, title, owned/not owned, read/unread

**Threading**: All HTTP calls go through a SearchThread(QThread) so the UI doesn't block.

---

## File layout (this workspace)

```
calibreops-bridge/
├── plugin-import-name-calibreops_bridge.txt
├── __init__.py                           ✓ done
├── action.py                             ✓ stub done
├── config.py                             ✓ stub done (fix port to 10720)
├── client/
│   └── calibreops_client.py             ✓ stub done (fix port to 10720)
├── ui/
│   ├── __init__.py                       ✓ done
│   ├── search_dialog.py                  → Phase 1
│   ├── result_widget.py                  → Phase 1
│   ├── synopsis_dialog.py                → Phase 2
│   └── series_dialog.py                  → Phase 2
├── images/
│   └── calibreops.png                    → Phase 3 (need to create)
└── build.py                              → Phase 3
```

---

## Revised project phases

### Phase 0 — Fix port + verify connectivity (0.5 days) ← START HERE
- [ ] Fix `config.py` default URL to http://localhost:10720 (not 13000)
- [ ] Fix `calibreops_client.py` base URL
- [ ] Load stub plugin with `calibre-customize -b` and verify "hello" dialog appears
- [ ] Test `http://localhost:10720/health` is reachable when webapp is running
- [ ] Test `http://localhost:10720/api/search?query=Banks&limit=5` returns results

### Phase 1 — SearchDialog + metadata search (2 days)
- [ ] Add `/api/rag` endpoint to calibre-mcp webapp backend
- [ ] Build `ui/search_dialog.py`: query input, mode selector, results list
- [ ] Build `ui/result_widget.py`: custom list item (title, authors, snippet)
- [ ] Wire SearchThread (QThread) for async HTTP calls
- [ ] "Open in Calibre": select the returned book_id in library view
- [ ] Replace action.py stub with real SearchDialog call
- [ ] Error handling: server not running → user-friendly dialog

### Phase 2 — Synopsis + series (1–2 days)
- [ ] Add `/api/synopsis` and `/api/series` to calibre-mcp webapp backend
- [ ] Build `ui/synopsis_dialog.py`
- [ ] Build `ui/series_dialog.py`
- [ ] Right-click context menu: "CalibreOps: Synopsis", "CalibreOps: Series analysis"

### Phase 3 — Polish + packaging (1 day)
- [ ] Icon: calibreops.png (32x32 or 48x48)
- [ ] `build.py` producing clean ZIP
- [ ] Config dialog fully wired (URL, timeout, limit all editable)
- [ ] Test clean install from ZIP on Goliath

### Phase 4 — Decision: merge or publish separately
Either:
  A) Merge this plugin's features into calibre-mcp's calibre_plugin/ directory — single plugin
  B) Publish as separate plugin focused on RAG/AI features

Option A is architecturally cleaner; option B is lower friction for the existing plugin.

---

## Total realistic timeline

Phase 0: afternoon
Phases 1–3: 3–4 days
Phase 4: 1 day

---

## Open questions — still outstanding

1. Is the calibre-mcp webapp backend (port 10720) currently set up for autostart?
   Check mcp-central-docs/starts/ for a start script.

2. Does the webapp backend directly import the calibre_mcp tool functions
   (so we can call rag_retrieve internally), or does it go through the MCP server?
   Check webapp/backend/app/ to confirm.

3. The existing calibre_plugin/ uses port 13000. Is that a separate old instance or
   just a stale config that was never updated to 10720?
