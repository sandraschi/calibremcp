# Book Deep Research — Spec

**Tool:** `media_research_book`
**Status:** Implemented 2026-04-16
**Location:** `src/calibre_mcp/tools/portmanteau/media_agentic.py`
**REST endpoint:** `POST /api/rag/research/{book_id}`
**Frontend:** RAG page → Research tab

---

## What it does

Given a book ID from your Calibre library, fetches and synthesises everything worth
knowing about the book from external sources: Wikipedia, the SF Encyclopedia (for
genre fiction), TVTropes, and the author's Wikipedia page. Combines this with your
own library data (your rating, read status, personal notes, RAG passages from the
book itself if indexed). Returns a structured markdown research report.

This is distinct from `media_critical_reception` (which does a single DuckDuckGo
search and synthesises snippets) and `media_synopsis` (which works only from your
local text). This tool goes wide externally and deep locally.

---

## Source routing

Source selection is automatic based on book tags/genres from Calibre metadata:

| Condition | Sources added |
|-----------|--------------|
| Always | Wikipedia (book) + Wikipedia (author) |
| tags contain: sf, science fiction, fantasy, space opera, cyberpunk | SF Encyclopedia |
| tags contain: anime, manga, light novel, manhwa | Anime News Network Encyclopedia |
| Any fiction | TVTropes (best-effort — JS-heavy, graceful fallback) |
| Book has ISBN | Open Library |
| Book has Goodreads identifier | Goodreads page (best-effort) |

Sources are fetched concurrently with a 10s timeout each. Failed sources are noted
in the report rather than causing the whole thing to fail.

---

## Source implementations

### Wikipedia
`GET https://en.wikipedia.org/api/rest_v1/page/summary/{title_slug}`
→ extract/disambiguate → `GET /api/rest_v1/page/sections/{title_slug}`
Clean JSON API, no scraping. Sections of interest: Plot, Reception, Adaptations,
Accolades, Legacy, See also.

### SF Encyclopedia
`GET https://www.sf-encyclopedia.com/entry/{slug}`
BeautifulSoup extraction. Well-structured HTML, no JS. Authoritative for SF/fantasy.

### Anime News Network Encyclopedia
`GET https://www.animenewsnetwork.com/encyclopedia/manga.php?id={id}`
or search: `GET https://www.animenewsnetwork.com/search?q={title}`
Structured HTML, extractable.

### TVTropes
`GET https://tvtropes.org/pmwiki/pmwiki.php/Literature/{TitleSlug}`
JS-rendered but the core text is in the initial HTML. Extract tropes list + description.
Graceful fallback: if blocked/failed, skip silently and note in report.

### Open Library
`GET https://openlibrary.org/isbn/{isbn}.json`
Clean JSON. Extracts: subjects, first_publish_date, description, covers.

### Local data
- Calibre metadata: title, authors, series, tags, rating, identifiers, comments
- Personal notes from `calibre_mcp_data.db` (user_comments table)
- RAG passages from content index if available (top 5 thematically relevant chunks)

---

## Synthesis prompt structure

The LLM synthesis (via `ctx.sample()`) receives all fetched content and is asked
to produce a report with these sections:

1. **Overview** — what the book is, where it fits, one-paragraph orientation
2. **Plot/Content** — from Wikipedia + local synopsis chunks
3. **Context** — author background, where this fits in their bibliography
4. **Critical reception** — reviews, awards, legacy from Wikipedia + web
5. **Themes & tropes** — from TVTropes + SF Encyclopedia + own analysis
6. **Adaptations** — film, TV, games, manga from Wikipedia
7. **If you liked this** — related works from SF Encyclopedia / Wikipedia See Also
8. **Your library** — your rating, notes, read status (personalised section)

Sections are omitted if no source data was available for them.

---

## Return shape

```json
{
  "success": true,
  "book_id": 1234,
  "title": "Use of Weapons",
  "authors": ["Iain M. Banks"],
  "report": "# Use of Weapons\n\n## Overview\n...",
  "sources_fetched": ["wikipedia_book", "wikipedia_author", "sf_encyclopedia", "tvtropes"],
  "sources_failed": ["goodreads"],
  "local_data": {
    "rating": 5,
    "read": true,
    "personal_notes": "...",
    "rag_passages": 3
  }
}
```

---

## Webapp endpoint

`POST /api/rag/research/{book_id}`

No query params needed — everything is driven from the book's Calibre metadata.
Optional: `?include_spoilers=false`

Response time: 10–30 seconds depending on source availability and LLM sampling speed.
The frontend should show a spinner with status messages.

---

## Frontend

RAG page: add **Research** as a fourth tab alongside Metadata / Passages / Synopsis.
Input: book ID (same as Synopsis tab).
Output: rendered markdown in a scrollable panel with source attribution footer.

---

## Limitations

- Requires `ctx.sample()` — only works in Claude Desktop / Cursor, not raw HTTP calls.
  The REST endpoint returns an error if called without a sampling-capable client context.
  (Same limitation as `media_synopsis`.)
- TVTropes and Goodreads are unreliable scrapers — always treated as optional.
- SF Encyclopedia slugs require normalisation (spaces → underscores, remove subtitles).
- Japanese titles: Wikipedia redirect logic handles romaji → Japanese title pages.
- No caching — each call refetches. Add Redis/SQLite cache later if needed.
