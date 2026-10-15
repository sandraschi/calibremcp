/** Structured help content for Calibre, Calibre MCP, Guides, and Webapp. */

export const HELP_SECTIONS = {
  webapp: {
    title: 'Webapp',
    content: `
## Overview

Browser UI for CalibreMCP. Backend (FastAPI, port 10720) + Frontend (Next.js, port 10721).
The FastMCP HTTP app is mounted at /mcp on port 10720 alongside the REST API.

Start from repo root: \`webapp\\start.ps1\`

## Navigation

- **Overview** — Dashboard with library stats, AI status, and direct Calibre Content Server launch
- **Libraries** — List, switch active, view stats
- **Books** — Browse with cover thumbnails and one-click Web Reader access
- **Search** — Filter by author, tag, text, rating; "Search inside book content" for FTS
- **Semantic Search** — RAG search over your library with hybrid BM25 + LanceDB rank fusion
- **Library Health** — Database integrity audits (PRAGMA integrity_check), missing files/covers detection, and repair advice
- **Duplicates** — Group duplicate book candidates by title similarity, author match, and ISBN collisions
- **Reading & Priorities** — Smart reading priority queue (weighted by ratings and series continuity) + reading analytics
- **Collections** — Virtual shelves browser with 1-click presets ("5-Star Masterpieces", "Unread Sci-Fi", etc.) and custom rule builder
- **Authors / Series / Tags / Publishers** — Browse as cards or compact list; sort by name or book count; search and filter
- **Series Analysis** — Reading order and completion for any series
- **Import** — Add books from file path, arXiv ID, or Gutenberg (works while the Calibre GUI is open)
- **Export** — CSV or JSON export with filters
- **Chat** — AI chatbot (Ollama / LM Studio / OpenAI-compatible)
- **Logs** — Live log tail with level filter
- **Settings** — Mirror URLs, Content Server URL, LLM provider
- **Help** — This page

## Browsing Authors, Series, Tags & Publishers

All four taxonomy pages share the same controls:

- **Cards / List toggle** (top right) — cards for visual browsing, list for dense scanning of large catalogs
- **Sort by Name or Book count**, ascending or descending — sorting is server-side, so page 1 really is the top
- **Search box** — filters server-side as you submit
- **Authors** additionally offers an A–Z letter jump bar; **Tags** offers an "Unused only" filter plus management tools (create, rename, merge, duplicates, AI organize)

Your view, sort, and filter choices live in the URL, so any view is bookmarkable and shareable.

## Semantic Search & Hybrid RAG

Four modes accessible from the Semantic Search page:

**Hybrid search** — Reciprocal Rank Fusion (RRF with k=60) combining lexical BM25 matches from Calibre's FTS5 database (\`full-text-search.db\`) with semantic vectors from LanceDB. Returns unified fused scores.

**Metadata search** — semantic search over title, authors, tags, comments using LanceDB with fastembed.
Build the metadata index once (fast, seconds), updated incrementally when books are added, updated, or deleted. e.g. "orbital megastructures with melancholy tone".

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

Indexes are per-library; books update incrementally automatically on CRUD operations.

## Series Analysis

Series → Series Analysis (or sidebar). Enter a series name to get:

- Progress bar: how many volumes you own vs total
- Reading order list with Owned / Missing badges
- Direct links to owned books

## Book Modal & In-Browser Reading

Click any book card: cover, full metadata, tags, description.

- **Read book (Desktop)**: Opens the book in the local Calibre desktop reader.
- **Read Here**: Launches the embedded Calibre Content Server web reader (\`viewer.js\`) inside an in-app overlay window without leaving CalibreMCP.
- **New Tab**: Opens the book in a standalone browser tab on the Calibre Content Server.
- **Download metadata (online)**: Uses Calibre command-line tools on PATH to download fresh metadata and high-res covers.

## Environment

Backend (\`webapp/backend/.env\`): CALIBRE_LIBRARY_PATH, LLM_PROVIDER, LLM_BASE_URL, CALIBRE_SERVER_URL
Frontend (\`webapp/frontend/.env.local\`): NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_URL, NEXT_PUBLIC_CALIBRE_CONTENT_SERVER_URL
`,
  },
  guides: {
    title: 'Guides',
    content: `
## Import a book (GUI can stay open)

The classic Calibre limitation — "another program has the library open" — does not apply here.
Imports go through a two-route runner: direct when the GUI is closed, automatically via your
Calibre Content Server when it is open.

1. **Import page** → paste a file path (PDF, EPUB, …) → Add. Title/authors/tags are
   detected; override them in the form.
2. Or via chat/tools: \`manage_books(operation="add", file_path="C:\\\\path\\\\book.pdf", metadata={"title": "…", "authors": ["…"]})\`
3. The result tells you the route: \`"via": "content_server"\` or \`"via": "direct"\`.

Prerequisite (one-time): Calibre → Preferences → **Sharing over the net** → enable + autostart,
and put the server URL plus sharing username/password into the repo \`.env\`
(\`CALIBRE_SERVER_URL\`, \`CALIBRE_USERNAME\`, \`CALIBRE_PASSWORD\`).

## Import from arXiv

Import page → arXiv tab → paste an ID (e.g. \`2610.13455\`) or URL. The PDF is fetched
and imported with paper title/authors as metadata. Large papers (30+ MB) take a while —
the progress survives slow/network libraries via the content-server route.

## Edit metadata & delete with the GUI open

Same fallback covers the other writers:

- \`manage_books(operation="update", book_id="123", metadata={"tags": [...]})\` → \`set_metadata\`
- \`manage_books(operation="delete", book_id="123")\` → \`remove\`
- Online metadata download ("Download metadata" button) → fetch + apply

Reads never contend: search, browse, RAG, and exports work regardless of what Calibre is doing.

## Find anything in seconds

- **Know roughly what**: Search page (title/author/tag/rating filters) or Semantic Search
  ("books about X with mood Y").
- **Know who/where**: Authors / Series / Tags / Publishers pages — switch to List view,
  sort by Book count to find your heavy hitters.
- **Know it's in the text**: "Search inside book content" (FTS) or Passage retrieval (semantic).
- **Recently added**: Books sorted by timestamp, or \`query_books(operation="recent")\` in chat.

## Tidy a messy library

1. **Duplicates page** — merge or delete title/author/ISBN collisions.
2. **Tags page → Tag tools** — find duplicates, merge renames, list + delete unused tags, AI organize.
3. **Library Health** — integrity check, missing files/covers, repair advice.
4. **Reading queue** — star ratings first; the priority queue weights ratings + series continuity.

## Troubleshooting quick hits

| Symptom | Cause | Fix |
|---|---|---|
| Import fails "library is locked" | No content server configured | Set CALIBRE_SERVER_URL + sharing credentials in .env |
| Import fails "username/password incorrect" | Sharing credentials changed | Update CALIBRE_USERNAME / CALIBRE_PASSWORD in .env, restart backend |
| Backend dot red | Port 10720 busy | Re-run \`webapp\\start.ps1\` (clears zombies) |
| Empty results everywhere | Wrong library folder | Library must contain \`metadata.db\`; switch via Libraries page |
| Semantic search empty | Index not built | Build metadata index (seconds) / content index (minutes) on the RAG page |
| Slow imports | Network drive / huge PDF | Normal for 30 MB+ files; content-server route has a 180 s budget |

Full write-ups: \`docs/Troubleshooting.md\`, \`docs/ONBOARDING.md\`, \`docs/Configuration.md\`.
`,
  },
  contentServer: {
    title: 'Content Server',
    content: `
## What it is

The webserver built into the Calibre GUI (Preferences → Sharing over the net).
On this machine it serves all local libraries with a modern browse/read UI:
sidebar (Home, Search, Downloaded books, Authors/Series/Formats/Publisher/Rating/Tags/Published,
Virtual libraries, Settings), Continue-reading and Newly-added cover shelves, a library
chip chooser, per-user accounts, and an in-browser reader.

## Why it matters here

Only one program may write to \`metadata.db\` directly. When the Calibre GUI is open,
every calibre-mcp write (add, metadata update, delete, online-metadata apply) automatically
goes through the Content Server instead — no action needed on your part.

One-time setup: enable Sharing (+ autostart) in Calibre, then put the server URL and the
sharing username/password into the repo \`.env\` as \`CALIBRE_SERVER_URL\`,
\`CALIBRE_USERNAME\`, \`CALIBRE_PASSWORD\` and restart the backend.

## How to tell which route was used

Write results report \`"via": "direct"\` (GUI was closed) or
\`"via": "content_server"\` (GUI was open). Our own imports appear on the server's
Newly-added shelf within seconds.

## Manual use

Browse/read at the server URL from any device on your network. With
\`calibredb --with-library <url> --username … --password …\` you get the same
add/update/delete verbs the tools use — see \`docs/CONTENT_SERVER.md\` for recipes,
the full fallback table, and the UI ideas we are watching to copy back.
`,
  },
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

## Content Server (Sharing over the net)

- Built-in HTTP server for remote access and for tool imports while the GUI is open
- Enable: Preferences → Sharing over the net → enable + autostart; note the port (default 8080)
- \`calibredb --with-library http://host:port --username … --password …\` performs writes through it
- Reads via the server need no auth unless you require it; writes need the sharing account

## The "library locked" rule, explained

Only one writer may touch \`metadata.db\` directly. When the GUI is open, command-line writes
must go through the Content Server instead — which is exactly what CalibreMCP's import/update/delete
paths do automatically (see the Guides tab).

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
| query_books | search, list, recent, by_author, by_series |
| manage_books | get, add, update, delete, details |
| manage_libraries | list, switch, stats |
| manage_authors | list, get, get_books, stats, by_letter |
| manage_series | list, get, get_books, stats, by_letter |
| manage_tags | list, get, create, rename, merge + stats/cleanup |
| manage_publishers | list, get, get_books, stats |
| manage_viewer | open, open_file, open_random, get_page |
| manage_system | status, list_tools |

List operations support \`query\` + pagination; authors/series/tags/publishers lists also
support \`sort_by\` (name, book_count) and \`sort_order\` (asc, desc).

## Writes With the GUI Open

Add / update / delete go through a shared runner: direct \`--library-path\` first,
automatic \`--with-library\` content-server fallback when Calibre holds the lock.
Needs \`CALIBRE_SERVER_URL\` (+ username/password if Sharing requires auth). Results
report the route as \`"via": "direct"\` or \`"via": "content_server"\`.

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
- **CALIBRE_SERVER_URL** — Content Server URL for GUI-open writes (e.g. http://localhost:8099)
- **CALIBRE_USERNAME / CALIBRE_PASSWORD** — Sharing account when the server requires auth
- **CALIBRE_MCP_USER_DATA_DIR** — Override location of calibre_mcp_data.db

## Installation

- **MCPB**: drag calibre-mcp.mcpb into Claude Desktop
- **Editable**: \`uv sync && uv run python -m calibre_mcp --stdio\`
`,
  },
} as const;
