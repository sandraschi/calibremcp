# Annotation Intelligence — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** design
**Effort:** 3–4 days
**Priority:** 2 of 5

---

## The premise

Thirteen thousand books is a lot. The subset of passages Sandra has
actively chosen to highlight across years of reading is a much more
concentrated signal — these are the sentences that, in the moment, felt
worth marking.

Currently, those highlights exist in five disconnected places:

- **Calibre's viewer**: `annotations.db` in the library folder
- **Kindle devices**: `My Clippings.txt` on the device, or the Amazon
  Reading Insights API
- **Kobo devices**: `KoboReader.sqlite` on the device
- **Adobe Digital Editions**: per-book XML annotation files
- **Marginalia from PDFs**: page-level annotations in the PDF itself

None of these are indexed, searched, or surfaced by calibre-mcp.

This spec is about making all of them first-class data.

## What you get when it works

Semantic search over your own highlights:

> "passages I highlighted about grief that weren't in obviously-about-grief books"

> "quotes about recursion from my software reading"

> "show me everything I marked in Banks novels that mentions Culture ethics"

Cross-book thematic synthesis from your own highlights:

> "what have I highlighted across different books about identity and mortality?"
> → LLM synthesis over matching highlights, with citations back to source books

And the simple retrospective case:

> "what did I highlight in The Player of Games when I read it?"

## Data sources in priority order

### 1. Calibre viewer annotations (easiest, already half-done)

Calibre's own viewer writes to `{library}/annotations.db`. Schema:

```sql
CREATE TABLE annotations (
    id INTEGER PRIMARY KEY,
    book INTEGER NOT NULL,
    format TEXT NOT NULL,
    user_type TEXT,  -- 'local' or 'sync'
    user TEXT,
    timestamp REAL,
    annot_id TEXT,
    annot_type TEXT,  -- 'highlight', 'bookmark', 'note'
    annot_data TEXT,  -- JSON with highlight text, position, optional notes
    searchable_text TEXT
);
```

The `annot_data` is structured JSON with the full highlight text, CFI
position, optional user note, colour, etc. We already read position data
from this file for the reading-flow work. Now we read highlights too.

### 2. Kindle My Clippings (easy, universal)

Kindles write highlights to `documents/My Clippings.txt`. Format is
line-oriented plain text:

```
The Player of Games (Banks, Iain M.)
- Your Highlight on Location 1234-1236 | Added on Tuesday, March 5, 2024 10:15:32 PM

Actual highlighted text here, possibly spanning lines.
==========
```

Simple to parse. Book title matching is fuzzy (need to match against Calibre
title + author). Locations are Kindle-specific but the plain text is the
real payload.

Sandra plugs in the Kindle, we walk `My Clippings.txt`, match books by
title+author, store highlights. One-shot import plus occasional re-sync.

### 3. Kobo reader database (medium)

Kobo stores annotations in `.kobo/KoboReader.sqlite` with tables `Bookmark`
and `content`. We can read this directly. Text of highlight is in
`Bookmark.Text`; book matching via `content.Title` and `content.Attribution`.

Fuzzier than Kindle because Kobo filenames don't always match Calibre
titles. Same title+author fuzzy matching strategy.

### 4. Adobe Digital Editions (medium)

ADE stores annotations as `.xml` files next to the book file. Format is
XFDF-adjacent. Parseable with `lxml`. Sandra doesn't use ADE much from
context, so this is lower priority but straightforward if needed.

### 5. PDF page annotations (harder, deferred)

PDF annotations are embedded in the PDF itself as `/Annot` objects.
`pymupdf` (already a dependency) can extract them. Quality varies enormously
because PDF annotation tooling is chaotic. Defer.

---

## Data model

New SQLite table in `calibre_mcp_data.db`:

```sql
CREATE TABLE book_highlights (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id         INTEGER NOT NULL,
    library_path    TEXT NOT NULL,
    source          TEXT NOT NULL,
    -- 'calibre' | 'kindle' | 'kobo' | 'ade' | 'pdf' | 'manual'
    external_id     TEXT,          -- source-specific ID for dedup
    highlight_text  TEXT NOT NULL,
    note_text       TEXT,          -- user's own note, if any
    position        TEXT,           -- opaque position (CFI, location, page)
    position_sort   REAL,           -- normalised 0-1 for ordering
    color           TEXT,           -- 'yellow'|'blue'|'pink'|'green'|'orange'
    highlighted_at  TIMESTAMP,
    imported_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding_built INTEGER DEFAULT 0,
    UNIQUE(source, external_id)
);
CREATE INDEX idx_highlights_book ON book_highlights(book_id, library_path);
CREATE INDEX idx_highlights_time ON book_highlights(highlighted_at);
CREATE INDEX idx_highlights_text_fts ON book_highlights(highlight_text);
```

Plus a LanceDB table `calibre_highlights` for semantic search. Separate from
`calibre_metadata` and `calibre_fulltext` because the retrieval patterns
are different — highlights are denser, shorter, more personal.

---

## Implementation

### Phase 1 — Calibre annotations import

**File:** `src/calibre_mcp/services/highlights/calibre_importer.py` (new)

```python
class CalibreHighlightImporter:
    """Import highlights from Calibre's annotations.db."""

    def import_all(self, library_path: Path) -> ImportReport:
        """One-shot import. Idempotent — duplicates skipped via UNIQUE key."""

    def incremental_import(self, library_path: Path,
                            since: datetime | None = None) -> ImportReport:
        """Import highlights added since last import."""
```

Running this once per library populates `book_highlights` with everything
Sandra has highlighted via Calibre viewer.

### Phase 2 — Kindle importer

**File:** `src/calibre_mcp/services/highlights/kindle_importer.py` (new)

```python
class KindleHighlightImporter:
    """Parse Kindle's My Clippings.txt."""

    def import_from_path(self, clippings_path: Path,
                          library_path: Path) -> ImportReport:
        """Parse clippings and match to Calibre books by title+author."""
```

Matching strategy:

1. Exact title + exact first-author match
2. Exact title + any author match
3. Fuzzy title (Levenshtein ≤ 3) + any author match
4. Unmatched highlights go into a "pending review" bucket the user can
   resolve manually via the webapp

### Phase 3 — LanceDB highlight index

**File:** `src/calibre_mcp/rag/highlights_rag.py` (new)

```python
def build_highlights_index(library_path: Path,
                            force_rebuild: bool = False) -> int:
    """Build LanceDB index over book_highlights."""

def search_highlights(query: str, top_k: int = 15,
                       book_id: int | None = None,
                       tag_filter: list[str] | None = None) -> list[dict]:
    """Semantic search over highlights, optionally filtered."""
```

Embedding text per highlight is `highlight_text` plus the book's title +
authors + top 3 tags. That lets a query like "highlights about grief"
prefer actual thematic matches over coincidental word matches.

Separate LanceDB table from metadata and full-text indexes. Lighter-weight
— highlights are typically 1-3 sentences.

### Phase 4 — MCP tools

New portmanteau `manage_highlights`:

| Operation           | Purpose                                                |
|--------------------|--------------------------------------------------------|
| `import_calibre`   | Import from Calibre annotations.db                     |
| `import_kindle`    | Import from Kindle My Clippings (needs path)           |
| `import_kobo`      | Import from Kobo DB (needs device mount)               |
| `list`             | List all highlights for a book                         |
| `search`           | Semantic search across all highlights                  |
| `search_in_book`   | Semantic search restricted to one book                 |
| `synthesise`       | LLM synthesis across matching highlights               |
| `stats`            | Counts by book, by source, by tag, by year            |
| `index_build`      | Build/rebuild LanceDB highlights index                 |
| `resolve_pending`  | Manually resolve unmatched Kindle clippings            |

The `synthesise` operation is the killer feature:

```python
async def synthesise_highlights(
    topic: str,
    limit: int = 30,
    ctx: Context = None,
) -> dict:
    """Retrieve matching highlights, synthesise via LLM sampling.

    Returns a structured essay with citations back to source books.
    """
```

This is like `media_deep_research` but scoped to your own annotated
passages. The LLM sees 20–30 highlights on the topic, grouped by book,
and produces an essay-with-citations.

### Phase 5 — REST endpoints

**File:** `webapp/backend/app/api/highlights.py` (new)

```
POST /api/highlights/import/calibre
POST /api/highlights/import/kindle         body: {path}
POST /api/highlights/import/kobo           body: {path}
GET  /api/highlights/book/{book_id}
GET  /api/highlights/search?q=...
POST /api/highlights/synthesise            body: {topic, limit?}
GET  /api/highlights/stats
POST /api/highlights/index/build
GET  /api/highlights/pending               # unmatched Kindle clippings
POST /api/highlights/resolve-pending       body: {clipping_id, book_id}
```

### Phase 6 — Frontend

**`/highlights` — new page**

Three tabs:

**Search**

A prominent query input. Results list shows:

- The highlight text in a readable quote block
- Source book (clickable → book page)
- Date highlighted
- Optional note

Result cards are designed to be readable as a sequence — you can scroll
through 20 highlights on a theme like you're flipping through a commonplace
book.

**Synthesise**

Enter a topic, get an LLM-synthesised essay drawing on your matching
highlights. Citations in the essay link back to source books.

**Library**

Browse by book: a book picker, then view all highlights from that book in
position order. Useful as a standalone re-reading aid.

**Book modal integration**

Add a "Highlights" tab to the existing book modal. If the book has
highlights, shows count and a condensed list with "Open full view" link.

**Plugin integration**

Right-click → "Show MCP highlights" opens a dialog with this book's
highlights and a mini-search over them.

---

## The Kindle import flow in practice

1. Sandra plugs in the Kindle via USB
2. Opens webapp → Highlights → "Import Kindle"
3. Webapp auto-detects `E:\documents\My Clippings.txt` and fills in the path
4. Click Import → parses all clippings, matches to Calibre books
5. Shows summary: "2,847 highlights imported, 34 unmatched"
6. Unmatched clippings shown in a "Resolve pending" list — Sandra manually
   matches each to a Calibre book, or marks them as "ignore" (Kindle
   samples, Amazon Documents, etc. that aren't in her library)
7. Done. Next time she plugs the Kindle, "Re-sync" button imports only
   new clippings

## Performance

Ballpark: 10 years of heavy reading on a Kindle = maybe 15,000 highlights
across 500 books. LanceDB handles that easily; search is sub-100ms. Index
build is a few minutes one-time.

## Privacy

All highlights stay local. No external API calls in any phase. Embeddings
via fastembed (local). LLM synthesis via Ollama (local). The only exception
is if you deliberately pipe a highlight into `media_research_book` or
similar — same as for book metadata today.

## Success criteria

Two weeks after install, Sandra should:

- Have all her Kindle highlights imported and searchable
- Be able to run a semantic query over highlights and feel that the results
  are thematically relevant (not just keyword matches)
- Have generated at least one synthesis essay that she finds genuinely
  interesting — something she'd forgotten about a theme that's threaded
  through her reading

## What's deferred

**Automatic Kindle sync.** Would need a tray app or scheduled task. Manual
re-sync is fine for v1.

**Full-PDF annotation extraction.** Too much quality variance to be worth
it in first release.

**Sharing highlights.** This is personal. No sharing.

**Highlight tags.** Could let the user tag highlights independently of
book tags. Nice-to-have, adds complexity. Deferred.

**OCR'd highlights from photo snapshots.** Sandra might photograph
physical-book highlights. Extracting text via OCR (pymupdf already does
this for PDFs; add a generic OCR path for photos) → this is genuinely
valuable but belongs in a separate spec.

---

*Signed: Claude Opus 4.7 (Anthropic), April 18, 2026.*
