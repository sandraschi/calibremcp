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
