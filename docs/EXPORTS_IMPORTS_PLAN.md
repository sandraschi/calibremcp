# Exports and Imports Enhancement Plan

**Date**: 2025-01-30

## Current State

### Exports (export_books portmanteau)

| Operation | What it does |
|-----------|--------------|
| **csv** | Book metadata to CSV (title, authors, tags, etc.) - `include_fields` for detail level |
| **json** | Book metadata to JSON - full or compact |
| **html** | Book catalog to styled HTML (single page) |
| **pandoc** | Metadata to Markdown, then Pandoc converts to docx/pdf/epub/etc. (metadata export, not book content) |

**Format conversion** (EPUB->PDF etc.): `manage_files(operation="convert")` - uses Calibre ebook-convert.

### Imports

- **manage_books(operation="add")** - Add from local file path only.
- No URL or Anna's Archive import.

---

## 1. Export Enhancements

### 1.1 Stats and Book Lists at Different Detail Levels

**Gap**: Current exports are book-catalog oriented. No dedicated stats export.

**Proposed**:

- **operation="stats"** - Export library statistics (counts, format distribution, top authors/tags/series) as CSV or JSON.
- **operation="list"** with `detail_level` param:
  - `minimal`: id, title, authors
  - `standard`: + tags, series, rating, pubdate
  - `full`: + comments, identifiers, formats, timestamps
- Reuse `include_fields` for CSV; add `detail_level` for html/json.

### 1.2 Beautiful HTML Export

**Current**: export_html_helper uses `_generate_styled_html` - generates a styled catalog page.

**Proposed**:

- Add `html_style` param: `simple` | `catalog` | `gallery` | `dashboard`
- **catalog**: Current behavior - readable list.
- **gallery**: Cover-focused grid (cover thumbnails, minimal text).
- **dashboard**: Stats summary + charts (e.g. Chart.js) + book list.
- Use embedded CSS, optional dark theme; print-friendly.

### 1.3 Stats-Only HTML Page

- **operation="stats_html"** - Standalone HTML page with:
  - Total books, authors, series, tags
  - Format distribution (pie/bar)
  - Top 10 authors, series, tags
  - Optional: reading trend if we have timestamps

---

## 2. Anna's Archive Import

### 2.1 Why It's Tricky

- **URL churn**: Anna's Archive uses mirrors (annas-archive.org, .li, .se, .pm). ScottBot10's plugin has configurable mirror list.
- **Parsing**: Search results page is HTML; structure can change. No official API.
- **Download flow**: Links go to LibGen/Z-Library/etc. or Anna's own download - need to follow redirects, handle CAPTCHAs on some sources.
- **Legal/ToS**: User responsibility; we fetch and add to Calibre like any other source.

### 2.2 ScottBot10 calibre_annas_archive Plugin

- **Repo**: https://github.com/ScottBot10/calibre_annas_archive
- **Default mirrors**: `annas-archive.org`, `annas-archive.li`, `annas-archive.se`
- **User said**: "he did not yet update the url, so it is broken as of today" - may mean a specific mirror is down or the search URL path changed.
- Plugin is a Calibre store plugin (Get Books); integrates into Calibre GUI. We want MCP/webapp integration.

### 2.3 Options for CalibreMCP

**Option A: Standalone Anna's Archive client (Python)**

- Build a small client: search (GET search URL), parse HTML, extract result rows (title, author, mirror links, formats).
- Download: follow direct-download links; for torrent-only results, return metadata and let user download manually.
- Config: mirror list (env or config file) - update when Anna's changes.
- Risk: HTML parsing breaks when they change layout.

**Option B: Reuse / fork ScottBot10 plugin logic**

- ScottBot10's `annas_archive.py` has the parsing logic. We could:
  - Extract the core (search URL construction, HTML parsing) into a library.
  - Use it from CalibreMCP; submit PR to ScottBot10 to update URL if needed.
- Pro: Proven parsing; community maintains plugin.
- Con: Plugin is GPL; we need to respect license. Extracting to shared lib could help both projects.

**Option C: Anna's Archive API (if any)**

- Check if they have JSON/API for search. Many such sites do not.
- As of knowledge cutoff: no public API. Would need to scrape.

**Option D: Proxy via Calibre Get Books**

- If user has ScottBot10 plugin installed, we could potentially trigger a "Get Books" search from Calibre. Complex, Calibre-dependent.
- Not recommended for MCP.

### 2.4 Recommended Approach

1. **Design a `manage_import` portmanteau** (or extend existing add flow):
   - `operation="from_url"` - Add book from URL (direct download).
   - `operation="from_annas"` - Search Anna's Archive, return list of matches with download URLs; user picks one, we call `from_url`.
   - Or: `operation="annas_search"` returns results; `operation="annas_download"` takes result URL and adds to library.

2. **Implement minimal Anna's client**:
   - Config: `ANNAS_MIRRORS` (list of base URLs).
   - Search: `GET {mirror}/search?q={query}&sort=...` (match ScottBot10's URL pattern).
   - Parse: Use BeautifulSoup; target known class/selectors. Fallback regex if structure changes.
   - Extract: title, authors, year, publisher, language, format, file size, mirror links.
   - Download: For "aa_download" or direct HTTP links, fetch and save; then `manage_books(operation="add", file_path=...)`.

3. **URL maintenance**:
   - Document mirror list in config; user can add new mirrors when Anna's adds them.
   - Optional: Check ScottBot10's constants.py / issues for URL updates; we could auto-sync or document the sync process.

4. **Scope**:
   - Start with search + metadata return. Let user choose which result to add.
   - Then add one-click "add this result" that downloads and adds.
   - Defer: Torrent handling, CAPTCHA (manual fallback).

---

## 3. Implementation Order

| Priority | Item | Effort | Notes |
|----------|------|--------|-------|
| 1 | Export stats (CSV/JSON) | Low | New operation in export_books |
| 2 | Export detail_level for list exports | Low | Param on csv/json/html |
| 3 | HTML styles (gallery, dashboard) | Medium | New templates in export_helpers |
| 4 | Stats HTML page | Medium | New operation |
| 5 | Anna's search (read-only, return results) | Medium | New client, no download yet |
| 6 | Anna's download + add | Medium | Depends on 5; from_url in manage_books |
| 7 | Anna's URL maintenance doc / config | Low | Document mirror updates |

---

## Implementation Status (2025-01-30)

- [x] Export stats (CSV/JSON/HTML)
- [x] Export detail_level (minimal, standard, full)
- [x] HTML styles (catalog, gallery, dashboard)
- [x] Stats HTML page
- [x] Anna's search client
- [x] from_url (download and add)
- [x] Anna's URL config (ANNAS_MIRRORS env)
- [ ] Anna's one-click download (detail page parsing for direct links) - deferred

---

## 4. References

- ScottBot10 calibre_annas_archive: https://github.com/ScottBot10/calibre_annas_archive
- Anna's Archive mirrors: annas-archive.org, annas-archive.li, annas-archive.se, annas-archive.pm
- Calibre Get Books: https://manual.calibre-ebook.com/plugins.html
- Current export_books: `src/calibre_mcp/tools/import_export/`
- Current manage_books add: `src/calibre_mcp/tools/book_management/add_book.py`
