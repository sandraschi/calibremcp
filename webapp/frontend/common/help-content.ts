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
- **Chat** — AI chatbot ([Ollama](https://ollama.com) / [LM Studio](https://lmstudio.ai) / OpenAI-compatible)
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

Full write-ups: [Troubleshooting](https://github.com/sandraschi/calibremcp/blob/master/docs/Troubleshooting.md), [ONBOARDING](https://github.com/sandraschi/calibremcp/blob/master/docs/ONBOARDING.md), [Configuration](https://github.com/sandraschi/calibremcp/blob/master/docs/Configuration.md).
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
add/update/delete verbs the tools use — see [CONTENT_SERVER.md](https://github.com/sandraschi/calibremcp/blob/master/docs/CONTENT_SERVER.md) for recipes,
the full fallback table, and the UI ideas we are watching to copy back.
`,
  },
  ebooks: {
    title: 'Ebooks Guide',
    content: `
## Free sources

**[Project Gutenberg](https://www.gutenberg.org)** (70k+ public-domain), **[Standard Ebooks](https://standardebooks.org)** (polished Gutenberg editions),
**[Internet Archive texts](https://archive.org/details/texts)**, **[Open Library](https://openlibrary.org)** (borrowable scans + metadata), **[Wikisource](https://wikisource.org)**,
**[Projekt Gutenberg-DE](https://www.projekt-gutenberg.org)** and **[Zeno.org](http://www.zeno.org)** for German texts. Our Import page fetches
Gutenberg books directly from ebook number or URL.

## Commercial stores

[Kindle](https://www.amazon.com/Kindle-eBooks) (largest, DRM-friction), [Kobo](https://www.kobo.com), [Google Play Books](https://play.google.com/store/books), [Apple Books](https://www.apple.com/apple-books/), [Thalia](https://www.thalia.de), [Hugendubel](https://www.hugendubel.de)/[ebook.de](https://www.ebook.de) for DE. Prefer **DRM-free** when possible: [O'Reilly](https://www.oreilly.com), [No Starch](https://nostarch.com), [Manning](https://www.manning.com), [Leanpub](https://leanpub.com),
[Smashwords](https://www.smashwords.com)/[D2D](https://draft2digital.com), [Tor/Forge](https://publishing.tor.com) — buy, download, import, done.

## Communities

**[MobileRead Forums](https://www.mobileread.com/forums)** (Calibre's nerve center), [r/ebooks](https://www.reddit.com/r/ebooks), [Goodreads](https://www.goodreads.com) (+ export your shelves),
[LibraryThing](https://www.librarything.com), [BookWyrm](https://joinbookwyrm.com) (federated), [Hardcover.app](https://hardcover.app), **[ISFDB](https://www.isfdb.org)** for SF/F series data,
[Grand Comics Database](https://www.comics.org) for comics.

## Bibliography tools

[Open Library API](https://openlibrary.org/developers/api), [Google Books API](https://developers.google.com/books), [WorldCat](https://www.worldcat.org), [DNB](https://www.dnb.de) (German publishing), [Library of Congress](https://www.loc.gov),
[VIAF](https://viaf.org), [Crossref](https://www.crossref.org)/[DOI](https://www.doi.org). The "Download metadata" button and \`media_research_book\` query several.

Full map with import notes: [EBOOKS_GUIDE.md](https://github.com/sandraschi/calibremcp/blob/master/docs/EBOOKS_GUIDE.md).
`,
  },
  law: {
    title: 'Copyright & AI',
    content: `
## Grey libraries ("shadow libraries")

Searchable mega-collections assembled without rightsholder permission. The big names:

- **[Z-Library](https://en.wikipedia.org/wiki/Z-Library)** — FBI seized its domains in Nov 2022 and arrested two alleged operators; mirrors keep resurfacing.
- **[Anna's Archive](https://en.wikipedia.org/wiki/Anna%27s_Archive)** — meta-search over Z-Lib, Sci-Hub and LibGen dumps (~61M books claimed); its \`.org\` domain was suspended (serverHold) in Jan 2026 and it resurfaced via mirrors.
- **Library Genesis / Sci-Hub** — the older dumps underneath much of it all (Sci-Hub is papers-focused).
- **[SLUM](https://open-slum.org)** — independent uptime monitor tracking which mirrors are alive.

No links to live mirrors here — they move weekly and their legality depends on where you stand.
Status above is October 2026.

## Copyright basics for library owners

- Owning a **file** is not owning the **rights**: you may read, lend within limits, and (jurisdiction-dependent) format-shift for personal use.
- Germany's *Privatkopie* allows private copies from lawful sources; breaking DRM to get there is its own legal question — check local law, not forums.
- Keep receipts: store invoices with your library (or as book notes). If a file's origin ever matters, "bought at Thalia 2024-03-11" ends the discussion.

## The great book gobble (AI training data)

Why books: edited long-form prose is the highest-signal training text there is. Known corpora
included **Books3** (~196k pirated books, part of The Pile) and LibGen dumps — which is why
the labs ended up in court over *where they got the books*, not just how they trained.

## The court cases (US, as of Oct 2026)

| Case | What happened | Why it matters |
|---|---|---|
| **Bartz v. Anthropic** | $1.5B class settlement, final approval 20 July 2026 (~482k works, ~$3k each) | Largest US copyright settlement ever; training ruled transformative fair use, but *pirated sourcing* created the liability |
| **Kadrey v. Meta** (June 2025) | Fair-use win for Meta on Llama training — on technical grounds (plaintiffs failed the market-dilution argument); judge warned most such training likely infringes; separate torrenting claim | Wins turn on evidence quality, not principle |
| **NYT v. OpenAI/Microsoft** (Dec 2023) | Core claims survived dismissal; at summary judgment Oct 2026, folded into multi-district litigation | The marquee training-data case still running |
| **Authors Guild** | Class counsel in Bartz; claim portal + webinars for members | Where working authors go for leverage |

## Writer anger, summarized fairly

Authors see years of work vacuumed into products that compete with them, via copies nobody
paid for — plaintiffs include names like Sarah Silverman (Kadrey). Labs reply that training is
transformative reading, like a human studying books. Courts so far: *how you learned* can be
fair use; *stealing the textbooks* still costs $1.5B.

## What this means in this app

Nothing adjudicates a file's provenance — not metadata, not covers, not RAG. Prefer DRM-free
stores (see Ebooks Guide), keep purchase notes, and treat grey-library files as exactly what
they are: convenient, legally grey, and periodically vanishing (check SLUM before citing one).

Deeper map: [EBOOKS_GUIDE.md](https://github.com/sandraschi/calibremcp/blob/master/docs/EBOOKS_GUIDE.md) · voices: [Authors Guild](https://authorsguild.org) · [Society of Authors](https://societyofauthors.org) · [EFF](https://www.eff.org/issues/ai-and-copyright).
`,
  },
  reading: {
    title: 'Why E-Reading',
    content: `
## How reading went electric (condensed)

In 1971 Michael Hart typed the Declaration of Independence into a mainframe and
gave it away — [Project Gutenberg](https://www.gutenberg.org) was born, thirty years early.
The nineties paraded almosts (Palm readers, Rocket eBook 1998), until the Kindle (Nov 2007)
nailed the three things that mattered: one-minute buying, a real store, E Ink at scale.

## Why it stuck

EPUB won everywhere but Amazon; DRM taught a generation that they rent, not own —
which is why DRM-free sellers and Calibre-as-your-shelf thrived. E Ink owns the couch,
glass owns the commute. Self-publishing (70% royalties), BookTok, and library lending
(Libby) rewired who gets paid; Germany's *Buchpreisbindung* kept its bookshops standing.

## What screens do to readers

Small but real print edge for long-form comprehension and mental maps of a text —
plus worse self-calibration on screens. Counterweights: the effect shrinks with familiar
devices and short texts, and accessibility (type size, dyslexia fonts, TTS, dictionaries)
makes ebooks strictly better for millions.

## The quiet superpowers

Dictionary, full-text search, adjustable type, night mode, one-hand reading, 200-gram
libraries, instant delivery, sync, TTS. Each minor; together the reason even paper
loyalists carry a reader. This webapp leans into them: search-inside, semantic search,
reading queues, one-click reader.

## The full essay

Twelve chapters — mainframes, wilderness years, Kindle detonation, DRM saga, E-ink vs glass,
psychology, commerce, two readers, bibliophilia, culture, QoL, and where AI takes it:
[READING_ESSAY.md](https://github.com/sandraschi/calibremcp/blob/master/docs/READING_ESSAY.md).

Talk back: [GitHub Discussions](https://github.com/sandraschi/calibremcp/discussions) for
corrections and arguments; Discord and blog are coming soon.
`,
  },
  calibre: {
    title: 'About Calibre',
    content: `
## What is Calibre?

Calibre is a free, open-source e-book library management application by Kovid Goyal. It organizes, converts, syncs, and manages e-books across devices and formats. Used by millions for personal and institutional libraries.

## History

- **31 Oct 2006** — Sony launches the PRS-500 reader; the same day Kovid Goyal starts
  **libprs500**, Linux tools for the new device, reverse-engineering Sony's BBeB format
  with help from the [MobileRead forums](https://www.mobileread.com/forums).
- **2008** — Renamed **calibre** as it outgrows "a collection of routines" into a full
  library system with a graphical interface.
- **The 1.x–6.x years** — Becomes the universal e-book Swiss knife: conversion between
  nearly all formats, metadata editing, device sync, news fetching, and its own reader.
- **Content-server era** — The built-in web server turns any library into a browsable,
  readable website (see the Content Server tab).
- **June 2026 (9.10)** — The Content Server gets its modern UI + PWA support; the
  "suspiciously good" redesign we keep stealing ideas from.
- **Now (9.16, Oct 2026)** — The version this repo integrates with ([calibre-ebook.com](https://calibre-ebook.com)).

Twenty years, one maintainer-led project, no acquisition, no pivot: the reason your
library still opens.

## Competitors (short list, honestly)

No one covers Calibre's full scope (manage + convert + edit + serve + sync) in one
open-source app. Partial alternatives by job:

- **Same job, commercial**: [Alfa Ebooks Manager](https://www.alfaebooks.com) (Windows, paid) — the only direct analogue.
- **Serve a Calibre library**: [calibre-web](https://github.com/janeczku/calibre-web) / [COPS](https://blog.slucas.fr/en/oss/calibre-opds-php-server) — companions, not replacements (they sit on your library).
- **Comics-first servers**: [Kavita](https://www.kavitareader.com), [Komga](https://komga.org), [Stump](https://www.stumpapp.dev).
- **Audiobooks**: [Audiobookshelf](https://www.audiobookshelf.org).
- **Store silos**: Kindle / Kobo / Apple Books apps — reading endpoints, not managers.
- **Readers only**: [KOReader](https://koreader.rocks) (devices), [Thorium](https://www.edrlab.org/software/thorium-reader), [Foliate](https://johnfactotum.github.io/foliate), [SumatraPDF](https://www.sumatrapdfreader.org).

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

CalibreMCP is a Model Context Protocol (MCP) server that connects AI assistants (Claude, Cursor, etc.) to your Calibre library. Built on [FastMCP 3.2](https://github.com/jlowin/fastmcp).

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
| canon_coverage | gutenberg_top100, nobel_laureates, delphi_coverage, check_list, list_canons |
| inspect_contents | scan, index, contents, search |

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
