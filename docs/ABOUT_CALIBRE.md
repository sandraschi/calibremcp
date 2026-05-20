# About Calibre

[Calibre](https://calibre-ebook.com) is the gold-standard open-source e-book management tool. Created by Kovid Goyal in 2006, it handles every aspect of a digital library: cataloging, conversion, editing, syncing, and serving.

## What Calibre does

| Capability | Description |
|------------|-------------|
| **Library management** | Organize thousands of books with rich metadata — title, author, series, tags, ratings, comments, custom columns |
| **Format conversion** | Convert between 20+ formats (EPUB, PDF, MOBI, AZW3, CBZ, etc.) |
| **Metadata editing** | Edit titles, authors, covers, descriptions, and 50+ built-in fields |
| **Content server** | Built-in HTTP server (`calibre-server`) for remote browsing and OPDS access |
| **E-book viewer** | Full-featured reader with annotations, search, and text-to-speech |
| **News download** | Scheduled fetching of news/magazine articles from 1600+ sources |
| **Device sync** | Send books to Kindle, Kobo, Android, iOS, and other e-readers |

## How Calibre stores data

Every Calibre library is a directory containing:

```
MyLibrary/
├── metadata.db          # SQLite database — all metadata, tags, series, custom columns
├── full-text-search.db  # SQLite FTS5 index of book contents (optional)
├── Author Name/
│   └── Book Title (1234)/
│       ├── Book Title - Author Name.epub
│       ├── cover.jpg
│       └── metadata.opf
└── ...
```

- **`metadata.db`** — The heart of Calibre. Contains 30+ normalized tables with all bibliographic data.
- **`full-text-search.db`** — FTS5 virtual tables indexing the extracted text of every book.
- **`calibre_mcp_data.db`** — CalibreMCP's own SQLite DB (in `%APPDATA%\calibre-mcp\`) for extended metadata fields Calibre doesn't natively support (translator, first_published, personal notes).

## Access methods supported by calibre-mcp

| Method | Status | Use case |
|--------|--------|----------|
| **Direct SQLite** (read `metadata.db` directly) | Primary | Local libraries, full read/write, no server needed |
| **Calibre Content Server API** (`calibre-server --port 8080`) | Supported | Remote libraries, network access, OPDS clients |
| **Calibre Content Server** (the browser-based GUI) | Not supported | Designed for human browsing, not API access |
| **calibre-web** (third-party web app by janeczku) | Not directly integrated | Uses its own SQLite DB; calibre-mcp reads Calibre's `metadata.db` directly |

## calibre-mcp vs Calibre

Calibre is the **library engine**. calibre-mcp is the **AI bridge** — it reads Calibre's databases, indexes metadata for semantic search, and exposes 21 portmanteau MCP tools so AI assistants (Claude Desktop, Cursor, etc.) can search, browse, and manage your library using natural language.

> **Next:** [About Calibre Web](ABOUT_CALIBRE_WEB.md) | **Back:** [README](../README.md)
