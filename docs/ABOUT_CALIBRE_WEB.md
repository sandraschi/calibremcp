# About Calibre Web

[calibre-web](https://github.com/janeczku/calibre-web) is a popular third-party web application that provides a modern browser interface for browsing, reading, and downloading e-books from a Calibre database. It is **not** the same as Calibre's built-in Content Server.

## calibre-web vs Calibre Content Server

| | calibre-web (janeczku) | Calibre Content Server (built-in) |
|---|---|---|
| **Creator** | Community (janeczku, OzzieIsaacs, et al.) | Kovid Goyal (Calibre) |
| **Purpose** | Modern web UI with user management, reading, OPDS | Lightweight browser access + OPDS API |
| **Database** | Uses its own `app.db` for users, shelves, settings | Uses only Calibre's `metadata.db` |
| **Authentication** | Built-in user system with per-user shelves | Optional basic auth (`--enable-auth`) |
| **E-book reading** | Built-in web reader (EPUB, PDF, CBZ) | Redirects to system viewer or downloads |
| **OPDS** | Yes | Yes |
| **Editing metadata** | Limited (read-only by default) | Not supported via Content Server |

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
