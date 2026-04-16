# Calibre Integration Guide

How calibre-mcp integrates with Calibre — the plugin, the webapp backend,
and how the two relate to each other.

---

## Architecture

```
Calibre GUI
└── CalibreMCP Integration plugin (calibre_plugin/)
    ├── Extended metadata dialog  →  calibre_mcp_data.db (direct SQLite, no server)
    ├── VL from Query dialog      →  http://localhost:10720/api/search (webapp)
    └── Bulk Enrich dialog        →  http://localhost:10720/api/... (webapp, stub)

calibre-mcp MCP server (src/calibre_mcp/)
└── reads same calibre_mcp_data.db
└── exposes tools to Claude Desktop via stdio

calibre-mcp webapp backend (webapp/backend/)
└── FastAPI on port 10720
└── REST API wrapping the same MCP tools
└── FastMCP HTTP app mounted at /mcp on same port
```

The plugin and the MCP server share one SQLite DB for extended metadata.
They do not need to be running simultaneously — the plugin writes directly
to the DB, and the MCP server reads it whenever it's queried.

---

## The plugin in detail

See `calibre_plugin/README.md` for install and usage instructions.

### What works now

**Extended metadata** (standalone, no server required): translator, first_published,
personal notes per book. Stored in `calibre_mcp_data.db`, scoped by
`(book_id, library_path)` so multi-library setups work correctly.

**VL from Query** (requires webapp on port 10720): calls `GET /api/search`,
gets back book IDs, creates a Calibre saved search that acts as a virtual library.
Useful for semantic queries — ask the webapp for "unread Banks novels" and get
a VL containing exactly those books.

### What's a stub

**Bulk Enrich**: dialog exists, checks server reachability, displays a status
message. AI enrichment logic is not implemented. Tracked in the project backlog.

### Planned (calibreops-bridge)

A second, separate plugin (`calibre-plugins/calibreops-bridge/`) is in early
development that will add RAG search, semantic metadata search, synopsis generation,
and series analysis directly in the Calibre GUI. See
`D:\Dev\repos\calibre-plugins\docs\CALIBREOPS_BRIDGE_SPEC.md`.

---

## The webapp backend

Start it:
```powershell
cd D:\Dev\repos\calibre-mcp\webapp\backend
uv run uvicorn app.main:app --host 127.0.0.1 --port 10720
```

Swagger UI at `http://localhost:10720/docs` — all endpoints documented there.

Key endpoints the plugin uses:
- `GET /health` — reachability check
- `GET /api/search?query=...&limit=N` — metadata search, returns book list

Endpoints added in the Apr 2026 session (plugin does not yet use these,
but they're available for the next plugin phase):
- `GET /api/rag/retrieve?q=...` — full-text passage RAG
- `GET /api/rag/metadata/search?q=...` — semantic metadata search
- `POST /api/rag/synopsis/{book_id}` — spoiler-aware synopsis
- `GET /api/series/analysis?series_name=...` — reading order + completion

---

## Data locations

| Item | Path |
|------|------|
| Plugin extended metadata DB | `%APPDATA%\calibre-mcp\calibre_mcp_data.db` |
| Override via env var | `CALIBRE_MCP_USER_DATA_DIR` |
| Webapp logs | `D:\Dev\repos\calibre-mcp\logs\webapp.log` |
| MCP server logs | `D:\Dev\repos\calibre-mcp\logs\calibremcp.log` |
| Plugin ZIP | `D:\Dev\repos\calibre-mcp\calibre_mcp_integration.zip` |
| Plugin source | `D:\Dev\repos\calibre-mcp\calibre_plugin\` |
| Build script | `D:\Dev\repos\calibre-mcp\scripts\build_calibre_plugin.ps1` |
| Test script | `D:\Dev\repos\calibre-mcp\scripts\calibre-plugin-test.ps1` |

---

## Multi-library support

All plugin data is keyed by `(book_id, library_path)`. When you switch libraries
in Calibre, the plugin reads and writes data for the active library automatically.
No configuration needed.

The MCP server discovers libraries via `CALIBRE_BASE_PATH` (shallow scan for
`metadata.db`) or `CALIBRE_SERVER_URL` (remote Calibre Content Server).
