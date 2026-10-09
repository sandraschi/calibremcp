# Calibre Webapp

Modern web application frontend for CalibreMCP server.

## Architecture

- **Backend**: FastAPI HTTP wrapper around MCP server
- **Frontend**: Next.js 15 with React Server Components, Tailwind CSS
- **Dual Interface**: FastMCP HTTP endpoints for webapp, stdio for MCP clients

## Features

- **Grouped Sidebar** - Content / Discover / AI & Tools / Manage / System accordion groups (persisted), retractable to icon rail
- **Overview Dashboard** - Library stats (books, authors, series, tags), quick links
- **Libraries** - Card/list browser with search, sort, pagination, per-library stats, editable descriptions, cross-library search, discovery, connection test
- **Books** - Hidable filter/sort toolbar (text, title, author, tag, series, publisher, ratings, formats, date ranges, sort by title/author/series/rating/added/published), pagination, Surprise-me random pick, book modal with edit/delete/review-comments/file info
- **Search** - Keyword, Advanced (12-field AND form), and Smart (auto/keyword/advanced/semantic/full-text engine picker) tabs
- **Authors** - A-Z letter strip, stats chips, search; Wikipedia links in book modal
- **Series** - Stats chips, completion report (missing volumes), search, drill into series and books
- **Tags** - Sort, unused-only filter, full management (create/rename/delete/merge/duplicates/unused/AI organize)
- **Collections** - Smart shelves with templates, auto-generators (series/recent/unread/AI), per-shelf counts, delete
- **Curated** - Japanese organizer, IT curator, reading recommendations
- **Bulk Ops** - Batch metadata update, export, convert, delete, file validate/cleanup by book-ID list
- **RAG Search** - Metadata, passages, combined, synopsis, deep research, multi-book thematic essays, critical reception, index build + metadata export
- **Import** - Add books by file path (server-accessible path), Annas/Gutenberg/ArXiv importers
- **Export** - CSV, JSON, HTML catalog, Pandoc documents with author/tag filters
- **Chat** - AI chatbot (Ollama, LM Studio, OpenAI-compatible)
- **Library Health** - Audit + one-click auto-fix of metadata issues
- **API Docs** - Proxied Swagger/ReDoc plus MCP tools, health-check, content-server probes
- **Settings** - LLM provider (Ollama/LM Studio/OpenAI), base URL, model list
- **Logs** - Log file viewer (tail, filter, level filter, live tail with backoff) and System status (diagnostic)
- **Help** - System help content
- **Remote access** - `start-lan.ps1` binds LAN/Tailscale with firewall rule (no auth — trusted networks only); see [Remote Access](#remote-access-lan--tailscale) below

### AI / LLM

- **Providers**: Ollama (default), LM Studio, OpenAI / cloud APIs
- **Settings**: Configure base URL, API key (OpenAI), list/load models
- **Chat**: Personality presets (Default, Librarian, Casual), model selection, message history; uses backend `/api/llm/chat`

### Logs

- **Log file**: Reads `logs/calibremcp.log` (MCP stdio) or `logs/webapp.log` (webapp backend); configurable via `LOG_FILE` env
- **Filtering**: Substring filter, level filter (DEBUG/INFO/WARNING/ERROR)
- **Tail**: Configurable line count (100-10000)
- **Live tail**: Polling with exponential backoff (2s to 30s max)

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Install calibre_mcp in editable mode
pip install -e ../../

# Run the server (or use start.ps1 for reserved ports 10720/10721)
uvicorn app.main:app --reload --host 0.0.0.0 --port 10720
```

Backend runs on http://localhost:10720

**Environment** (optional, in `backend/.env`):
- `LLM_PROVIDER` - ollama | lmstudio | openai (default: ollama)
- `LLM_BASE_URL` - e.g. http://127.0.0.1:11434 (Ollama)
- `LLM_API_KEY` - For OpenAI/cloud APIs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:10721 (when using start.ps1).

**Environment** (optional, in `frontend/.env.local`):
- `NEXT_PUBLIC_API_BASE` - Backend base URL. Unset = same-origin via Next.js `/api` rewrites (recommended; works over LAN with zero config). Set explicitly only for split-host or reverse-proxy setups.
- `NEXT_PUBLIC_CALIBRE_CONTENT_SERVER_URL` - Kovid's `calibre-server` reader URL for "Read Here / New Tab" links (default: `http://goliath:8099`). Point at the LAN/tailnet host when reading from other devices.
- `CALIBRE_DEV_ORIGINS` - Extra hosts allowed to load the dev frontend, comma-separated (e.g. `192.168.1.10,goliath.tail12345.ts.net`). `start-lan.ps1` sets this automatically.
- `NEXT_PUBLIC_APP_URL` - App URL for SSR (default: http://127.0.0.1:10721)

### All-in-one (recommended)

**Reservoir ports** (10720 backend, 10721 frontend):
```powershell
cd webapp
powershell -ExecutionPolicy Bypass -File .\start.ps1
```
Or from repo root: `.\webapp\start.bat` (calls start.ps1). Uses kill-port to clear ports before bind.

## Remote Access (LAN / Tailscale)

`start.ps1` binds `127.0.0.1` only — other devices cannot reach it. For a phone,
tablet (iPad), or second PC on the same network, use the LAN launcher:

```powershell
cd webapp
powershell -ExecutionPolicy Bypass -File .\start-lan.ps1
```

What it does:

1. Creates a Windows Firewall inbound rule for TCP 10720/10721 (once; needs elevation — otherwise it prints the exact command to run as admin and continues).
2. Starts the backend bound to `0.0.0.0` via `CALIBRE_BIND` (honored by `fleet-start.config.ps1` → central fleet engine; plain `start.ps1` stays loopback-only).
3. Starts the Next.js frontend bound to `0.0.0.0` with `CALIBRE_DEV_ORIGINS` auto-filled from detected interface addresses (Next.js dev blocks cross-host loads without this).
4. Prints reachable URLs for every local IPv4.

No client configuration is needed: the frontend uses same-origin `/api` rewrites, so the browser never needs a backend address.

### Tailscale

A tailnet is just IP connectivity, so everything above works unchanged — with advantages:

- The **library can live on another PC**: run the stack (this repo + `start-lan.ps1`) on the PC that holds `metadata.db`; browse it from anywhere via the tailnet. The tools always read the library off local disk, which is exactly how Calibre likes it (no SQLite-over-network fragility).
- From the iPad: install the Tailscale app, sign in, open `http://100.x.y.z:10721/` or the MagicDNS name, e.g. `http://goliath.<tailnet>.ts.net:10721/`. The script flags detected `100.*` addresses.
- The in-browser reader (`:8099`) is Kovid's `calibre-server`, not this stack: make sure it listens beyond loopback on the library PC, and set `NEXT_PUBLIC_CALIBRE_CONTENT_SERVER_URL=http://<tailnet-host>:8099` (frontend env, restart dev) so reader links work off-device. The API Docs "Open in browser" link is loopback-only by design (use the proxied Swagger in-page instead).
- Windows usually classifies the Tailscale adapter as a Public network — the firewall rule covers all profiles, so this is handled.

### Security warning

The backend has **no authentication**. Loopback was the security model. Anyone who can reach ports 10720/10721 can read, edit, and **delete** your library. Use LAN mode only on trusted networks (home LAN, your own tailnet). Never port-forward these to the internet; tailnet membership is your access boundary.

### Manual equivalent (no script)

```powershell
$env:CALIBRE_BIND = '0.0.0.0'
$env:CALIBRE_DEV_ORIGINS = '192.168.1.10,goliath.tail12345.ts.net'
.\start.ps1 -BackendOnly -NoBrowser          # backend on 0.0.0.0:10720
Set-Location webapp\frontend
npm run dev -- -p 10721 -H 0.0.0.0           # frontend on 0.0.0.0:10721
```

If the page loads but API calls fail from the remote device, the remote hostname/IP is missing from `CALIBRE_DEV_ORIGINS` (dev) or `CALIBRE_CORS_EXTRA` (backend `.env`, only needed for absolute-base / cross-origin setups).

## Project Structure

```
webapp/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── cache.py
│   │   ├── api/
│   │   │   ├── books.py
│   │   │   ├── search.py
│   │   │   ├── library.py
│   │   │   ├── authors.py
│   │   │   ├── series.py
│   │   │   ├── tags.py
│   │   │   ├── export.py
│   │   │   ├── viewer.py
│   │   │   ├── llm.py       # Ollama/LM Studio/OpenAI chat
│   │   │   ├── logs.py      # Log file tail, filter, level
│   │   │   └── ...
│   │   └── mcp/
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx         # Overview
│   │   ├── books/
│   │   ├── authors/
│   │   ├── series/
│   │   ├── tags/
│   │   ├── import/
│   │   ├── export/
│   │   ├── chat/
│   │   ├── logs/
│   │   ├── settings/
│   │   ├── help/
│   │   └── api/             # Next.js API proxies
│   └── components/
│       ├── layout/          # Sidebar, Topbar, AppLayout
│       ├── books/           # BookCard, BookGrid, BookModal
│       ├── authors/         # AuthorLinks (Wikipedia)
│       └── ...
└── README.md
```

## Documentation

- [docs/WEBAPP_IMPLEMENTATION_GUIDE.md](../docs/WEBAPP_IMPLEMENTATION_GUIDE.md) - Implementation details
- [backend/ENDPOINTS.md](backend/ENDPOINTS.md) - API reference (if present)
