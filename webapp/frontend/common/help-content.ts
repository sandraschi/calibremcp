/** Structured help content for Calibre, Calibre MCP, and Webapp. */

export const HELP_SECTIONS = {
  calibre: {
    title: 'About Calibre',
    content: `
## What is Calibre?

Calibre is a free, open-source e-book library management application by Kovid Goyal. It organizes, converts, syncs, and manages e-books across devices and formats. Used by millions for personal and institutional libraries.

## Library Structure

- **metadata.db** - SQLite database storing all metadata: books, authors, tags, series, publishers, identifiers, custom columns
- **Author Name/Book Title (ID)/** - Each book in its own folder; contains cover.jpg and format files (.epub, .pdf, .mobi, etc.)
- **Multiple libraries** - Calibre supports separate library locations (e.g. Main, Comics, Manga, IT)

## Common Formats

- **EPUB** - Widely supported, reflowable
- **PDF** - Fixed layout, print-friendly
- **MOBI, AZW3** - Kindle
- **CBZ, CBR** - Comics (ZIP/RAR of images)
- **TXT, HTML, RTF** - Plain text

## Content Server

- **calibre-server** - Built-in HTTP server for remote access
- Start: calibre-server --port=8080
- Read operations work without auth; write operations require authentication if enabled
- Default port: 8080

## Key Concepts

- **Authors** - One or more per book; author sort for display order
- **Tags** - User-defined categories; hierarchical (tag.subtag)
- **Series** - Ordered sequences with series index (e.g. "Harry Potter #3")
- **Publishers, Identifiers** - ISBN, etc.
- **Custom columns** - Extend metadata (dates, text, yes/no, etc.)
- **Virtual libraries** - Saved searches as filtered views
`,
  },
  calibreMcp: {
    title: 'Calibre MCP Server',
    content: `
## Overview

CalibreMCP is a Model Context Protocol (MCP) server that connects AI assistants (Claude, Cursor, etc.) to your Calibre library. Built on FastMCP 3.2.

Runs simultaneously as stdio (for Claude Desktop / Cursor) and HTTP (for the webapp) on the same process — no separate server needed.

## Access Methods

1. **Direct database** (default) — reads metadata.db directly; no Calibre app needed; fastest
2. **Calibre Content Server** — HTTP API for remote libraries; requires calibre-server running

## Portmanteau Tools

Tools consolidate related operations via an \`operation\` parameter:

| Tool | Operations |
|------|------------|
| query_books | search, list, by_author, by_series |
| manage_books | get, add, update, delete, details |
| manage_libraries | list, switch, stats |
| manage_authors | list, get, get_books |
| manage_series | list, get, get_books, stats, analysis, completion_report |
| manage_tags | list, get, get_books |
| manage_viewer | open, open_file, open_random, get_page |
| manage_system | status, list_tools |

## RAG Tools

| Tool | Purpose |
|------|---------|
| calibre_metadata_index_build | Build LanceDB metadata index (title, authors, tags, comments) |
| calibre_metadata_search | Semantic search over metadata |
| rag_index_build | Build LanceDB content index (full book text) |
| rag_retrieve | Semantic passage retrieval from full book text |
| calibre_rag | Combined portmanteau: metadata + content search |
| media_synopsis | RAG-synthesised spoiler-aware synopsis for a book |
| media_critical_reception | Critical reception synthesis (web + library) |
| media_deep_research | Cross-book thematic analysis |
| media_research_book | Deep external research: Wikipedia, SF Encyclopedia, TVTropes, ANN, Open Library + local data |

## Calibre Plugin

A Calibre plugin ships with this repo (\`calibre_plugin/\`):
- **Ctrl+Shift+M** — Extended metadata panel (First Published, Translator, personal notes)
- Toolbar dropdown → **Create VL from Query** — semantic virtual library creation
- Data stored in \`calibre_mcp_data.db\`, shared with the MCP server

Install: \`calibre-customize -b calibre_plugin\` or use the pre-built ZIP.

## Configuration

- **CALIBRE_LIBRARY_PATH** — Library directory (required for direct access)
- **CALIBRE_BASE_PATH** — Parent of multiple library directories (auto-discovery)
- **CALIBRE_SERVER_URL** — For remote Calibre Content Server (optional)
- **CALIBRE_MCP_USER_DATA_DIR** — Override location of calibre_mcp_data.db

## Installation

- **MCPB**: drag calibre-mcp.mcpb into Claude Desktop
- **Editable**: \`uv sync && uv run python -m calibre_mcp --stdio\`
`,
  },
  webapp: {
    title: 'Webapp',
    content: `
## Overview

Browser UI for CalibreMCP. Backend (FastAPI, port 10720) + Frontend (Next.js, port 10721).
The FastMCP HTTP app is mounted at /mcp on port 10720 alongside the REST API.

Start from repo root: \`webapp\\start.ps1\`

## Navigation

- **Overview** — Dashboard with library stats
- **Libraries** — List, switch active, view stats
- **Books** — Browse with cover thumbnails
- **Search** — Filter by author, tag, text, rating; "Search inside book content" for FTS
- **Semantic Search** — RAG search over your library (see below)
- **Authors / Series / Tags / Publishers** — Browse and filter
- **Series Analysis** — Reading order and completion for any series
- **Import** — Add books from file path, arXiv ID, or Gutenberg
- **Export** — CSV or JSON export with filters
- **Chat** — AI chatbot (Ollama / LM Studio / OpenAI-compatible)
- **Logs** — Live log tail with level filter
- **Settings** — Mirror URLs, LLM provider
- **Help** — This page

## Semantic Search (RAG)

Four modes accessible from the Semantic Search page:

**Metadata search** — semantic search over title, authors, tags, comments using LanceDB.
Build the metadata index once (fast, seconds). e.g. "orbital megastructures with melancholy tone".

**Passage retrieval** — semantic search over full book text.
Build the content index first (slow — minutes for large libraries).
e.g. "Zakalwe manipulated into a mission".

**Synopsis** — enter a book ID, get a RAG-synthesised synopsis. Toggle spoilers.

**Research** — deep external research on a book. Enter a book ID; the tool fetches
Wikipedia (book + author), SF Encyclopedia (genre fiction), TVTropes (fiction),
Anime News Network (manga/light novels), and Open Library (if ISBN present).
Combines with your Calibre rating, personal notes, and RAG passages if indexed.
Synthesises via LLM into a structured report: Overview, Author Context, Plot,
Critical Reception, Themes & Tropes, Adaptations, Related Works, Your Library.
Takes 10–30 seconds. Requires Claude Desktop or Cursor (LLM sampling).

Indexes are per-library; rebuild after adding many books.

**Metadata search** — semantic search over title, authors, tags, comments using LanceDB.
Build the metadata index once (fast, seconds). Then search with natural language:
e.g. "orbital megastructures with melancholy tone", "Japanese mystery light novels".

**Passage retrieval** — semantic search over full book text.
Build the content index first (slow — minutes for large libraries).
e.g. "Zakalwe manipulated into a mission", "the ship minds discussing ethics".

**Synopsis** — enter a book ID, get a RAG-synthesised synopsis.
Toggle spoilers on/off. Book ID is visible in the URL when viewing a book.

Indexes are per-library; rebuild after adding many books.

## Series Analysis

Series → Series Analysis (or sidebar). Enter a series name to get:
- Progress bar: how many volumes you own vs total
- Reading order list with Owned / Missing badges
- Direct links to owned books

## Book Modal

Click any book card: cover, full metadata, tags, description.
**Read** opens in system default app.

## Environment

Backend (\`webapp/backend/.env\`): CALIBRE_LIBRARY_PATH, LLM_PROVIDER, LLM_BASE_URL
Frontend (\`webapp/frontend/.env.local\`): NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_URL
`,
  },
## Overview

CalibreMCP is a Model Context Protocol (MCP) server that connects AI assistants (Claude, Cursor, etc.) to your Calibre library. Built on FastMCP 2.14+.

## Access Methods

1. **Direct database** (default) - Reads metadata.db directly; no Calibre app needed; fastest
2. **Calibre Content Server** - HTTP API for remote libraries; requires calibre-server running

## Portmanteau Tools

Tools consolidate related operations via an \`operation\` parameter:

| Tool | Operations |
|------|------------|
| query_books | search, list, by_author, by_series |
| manage_books | get, add, update, delete, details |
| manage_libraries | list, switch, stats |
| manage_authors | list, get, get_books |
| manage_series | list, get, get_books, stats |
| manage_tags | list, get, get_books |
| manage_viewer | open, open_file, open_random, get_page |
| manage_system | status, list_tools |

## Key Tools

- **query_books(operation="search")** - Primary book access; author, tag, text, rating, date filters
- **search_fulltext** - Search inside book content (Calibre full-text-search.db); returns books with snippets
- **manage_viewer(operation="open_file")** - Open book in system default app (EPUB, PDF, etc.)
- **manage_viewer(operation="open_random")** - Open random book by author/tag/series
- **manage_libraries(operation="list")** - List libraries; operation="switch" to change active

## Configuration

- **CALIBRE_LIBRARY_PATH** - Library directory (required for direct access)
- **CALIBRE_SERVER_URL** - For remote (optional)
- Auto-discovery reads Calibre config (global.py, library_infos.json)

## Installation

- **PyPI**: pip install calibre-mcp
- **MCPB**: Drag .mcpb into Claude Desktop (one-click)
- **Editable**: pip install -e . from repo
`,
  },
  webapp: {
    title: 'Webapp',
    content: `
## Overview

Browser UI for CalibreMCP. Backend (FastAPI) + Frontend (Next.js). All API calls go through Next.js proxies (same-origin).

**Ports:** backend 10720, frontend 10721.

## Start

From repo root: \`webapp\\start.ps1\` (PowerShell). Requires CALIBRE_LIBRARY_PATH in webapp\\.env.

## Navigation (Sidebar)

- **Overview** - Dashboard with library stats (books, authors, series, tags)
- **Libraries** - List, switch active, view stats
- **Books** - Browse with pagination, cover thumbnails
- **Search** - Filter by author, tag, text, min rating; check "Search inside book content" for full-text search (requires Calibre FTS index)
- **Authors** - List with search; click to filter books by author
- **Series** - List; click to drill into series and books
- **Tags** - List; click to filter books by tag
- **Import** - Add book by file path (path must be on server machine)
- **Export** - CSV or JSON; filter by author, tag, limit
- **Chat** - AI chatbot (Ollama/LM Studio/OpenAI)
- **Settings** - LLM provider, base URL, model list
- **Logs** - System status (diagnostic)
- **Help** - This page

## Book Modal

Click a book card: modal shows cover, full metadata (title, authors, series, publisher, dates, identifiers), tags, description. **Read** opens in system default app (e.g. Adobe, Edge).

## Author Wikipedia Links

Click author name in book modal to open Wikipedia search in new tab.

## AI Chat

1. Open Settings; choose provider (Ollama, LM Studio, OpenAI)
2. Set base URL (e.g. http://127.0.0.1:11434 for Ollama)
3. Click "List models" to verify
4. Open Chat; enter model name; send messages

## Environment

**Backend** (backend/.env): LLM_PROVIDER, LLM_BASE_URL, LLM_API_KEY, CORS_ORIGINS  
**Frontend** (frontend/.env.local): NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_URL
`,
  },
} as const;
