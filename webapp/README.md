# Calibre Webapp

Modern web application frontend for CalibreMCP server.

## Architecture

- **Backend**: FastAPI HTTP wrapper around MCP server
- **Frontend**: Next.js 15 with React Server Components, Tailwind CSS
- **Dual Interface**: FastMCP HTTP endpoints for webapp, stdio for MCP clients

## Features

- **Retractable Sidebar** - Full navigation with collapse toggle (state in localStorage)
- **Overview Dashboard** - Library stats (books, authors, series, tags), quick links
- **Libraries** - List, switch, stats, operations
- **Books** - Browse with pagination, cover thumbnails, book modal with full metadata
- **Search** - Filter by author, tag, text, min rating; author/tag dropdowns
- **Authors** - List with search, click to filter books; Wikipedia links in book modal
- **Series** - List with search, drill into series and books
- **Tags** - List with search, click to filter books
- **Import** - Add books by file path (server-accessible path)
- **Export** - Export to CSV or JSON with author/tag filters
- **Chat** - AI chatbot (Ollama, LM Studio, OpenAI-compatible)
- **Settings** - LLM provider (Ollama/LM Studio/OpenAI), base URL, model list
- **Logs** - Log file viewer (tail, filter, level filter, live tail with backoff) and System status (diagnostic)
- **Help** - System help content

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
- `NEXT_PUBLIC_API_URL` - Backend URL (default: http://127.0.0.1:10720)
- `NEXT_PUBLIC_APP_URL` - App URL for SSR (default: http://127.0.0.1:10721)

### All-in-one (recommended)

**Reservoir ports** (10720 backend, 10721 frontend):
```powershell
cd webapp
powershell -ExecutionPolicy Bypass -File .\start.ps1
```
Or from repo root: `.\webapp\start.bat` (calls start.ps1). Uses kill-port to clear ports before bind.

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
