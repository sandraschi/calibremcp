# About Calibre Web

[calibre-web](https://github.com/janeczku/calibre-web) is a popular third-party web application that provides a modern browser interface for browsing, reading, and downloading e-books from a Calibre database. It is **not** the same as Calibre's built-in Content Server.

## calibre-web vs Calibre Content Server vs CalibreMCP

| Feature | calibre-web (janeczku) | Calibre Content Server (Modern Built-in, e.g. `:8099`) | CalibreMCP WebApp (`:10721`) |
|---|---|---|---|
| **Creator** | Community (janeczku, OzzieIsaacs, et al.) | Kovid Goyal (Calibre core) | Sandra Schipal (Fleet SOTA standard) |
| **Tech Stack** | Python (Tornado/Flask) + SQLite | Python async server (`calibre.srv`) + RapydScript SPA | Next.js 15 (React 19 + Tailwind) + FastAPI |
| **Purpose** | Multi-user web portal with per-user shelves | Fast, single-library browser access & native web reader | AI-native conversational librarian & MCP bridge |
| **Database** | Own `app.db` + reads `metadata.db` | Directly reads `metadata.db` | Reads `metadata.db` + LanceDB vector store |
| **In-Browser Reader** | Built-in web reader (EPUB, PDF, CBZ) | **Full-featured built-in reader** (`viewer.js`/`viewer.html` with offline ServiceWorker support) | Delegates to external viewer / downloads |
| **AI / Semantic RAG** | None | None | **Full LanceDB Vector RAG, Ollama / OpenAI AI chat** |
| **OPDS Feed** | Yes | Yes (native `/opds`) | No (exposes MCP tools + REST) |
| **Metadata Editing** | Limited | Yes (when `--enable-write` or GUI-coupled) | Yes (via 21 MCP portmanteau tools & REST) |

## How the Modern Calibre Content Server is Served

Calibre's Content Server (running on e.g. `http://goliath:8099/` or `http://localhost:8080/`) is served directly by the Calibre core engine:
- **Serving Binary**: Either `calibre.exe --start-in-tray` with sharing active, or standalone `calibre-server.exe`.
- **Engine**: Calibre's custom asynchronous HTTP server (`calibre.srv`).
- **Frontend SPA**: A compiled single-page application bundled in `resources/content-server/index-generated.html` (~3.9 MB). Calibre compiles Python-like UI code to standard JavaScript using RapydScript.
- **Visual Similarity**: Both Calibre's Content Server and CalibreMCP's webapp look strikingly similar because they solve identical library catalog UX challenges: card grids for covers with hover actions, left faceted filters (Tags, Authors, Series, Formats), responsive search, and dark themes.

## Why calibre-mcp doesn't directly integrate with calibre-web

1. **Different database** — calibre-web stores user accounts, reading progress, shelves, and settings in its own `app.db`. calibre-mcp reads Calibre's `metadata.db` directly.
2. **Read-only assumptions** — calibre-web is designed for browsing and reading, not for programmatic metadata editing.
3. **No stable API** — calibre-web has no documented REST API for external tool consumption. Its OPDS feed is read-only.

## Running both together

You can absolutely run calibre-web and calibre-mcp side by side — they access the same Calibre library directory and don't conflict:

```
Calibre Library (L:\Calibre-Bibliothek\)
├── metadata.db  ← read by both
│
├── calibre-mcp         (MCP server via stdio/HTTP)
│   └── tools for AI assistants (Claude Desktop, Cursor)
│   └── webapp on port 10720
│
└── calibre-web         (browser UI via Docker or python)
    └── web interface on port 8083 (typical)
    └── OPDS feed
```

**Configuration tip:** Both calibre-mcp and calibre-web require the path to the same Calibre library. Point both at the same directory — they read the same `metadata.db` and don't lock each other out (SQLite handles concurrent reads).

## Key differences in philosophy

- **calibre-web** = Human-facing. Great for browsing your library, reading on the go, sharing with family.
- **calibre-mcp** = AI-facing. Gives Claude, Cursor, and other AI tools structured access to search, analyze, and manage your library through natural language.

> **Next:** [About Plugins](ABOUT_PLUGINS.md) | **Back:** [About Calibre](ABOUT_CALIBRE.md)
