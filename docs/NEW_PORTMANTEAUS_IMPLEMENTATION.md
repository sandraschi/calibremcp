# New Portmanteaus Implementation - manage_descriptions, manage_series, manage_publishers, manage_user_comments

**Date**: 2025-01-30

## Summary

Implemented four new portmanteau tools analogous to `manage_authors`, plus a CalibreMCP-owned SQLite database for user data.

---

## 1. manage_descriptions

**Purpose**: Browse and query Calibre's comment field (description = synopsis). Same field as `manage_comments`; this tool provides browse/query operations.

**Operations**:
- `list`: List books with optional `has_description` (true/false) and `query` (search in description text)
- `get`: Get description for a book by `book_id`
- `stats`: Description coverage (how many books have descriptions, avg length)
- `by_letter`: Books with descriptions whose title starts with letter

**For editing** (create/update/delete): Use `manage_comments`.

**Location**: `src/calibre_mcp/tools/descriptions/`

---

## 2. manage_series

**Purpose**: Full series management analogous to `manage_authors`. Uses Calibre's metadata.db (series table).

**Operations**:
- `list`: List series with search and pagination
- `get`: Get series details by `series_id`
- `get_books`: Get books in a series (ordered by series_index)
- `stats`: Total series, by-letter distribution, top series by book count
- `by_letter`: Series whose names start with letter

**Location**: `src/calibre_mcp/tools/series/`

---

## 3. manage_user_comments

**Purpose**: User annotations/notes on books, stored separately from Calibre's description. Uses CalibreMCP-owned SQLite DB.

**Operations**:
- `create` / `update`: Add or overwrite user comment (upsert)
- `read`: Get user comment for a book
- `delete`: Remove user comment
- `append`: Append text to existing comment

**Scoping**: Comments are scoped by `(book_id, library_path)` so the same book_id in different libraries has separate comments.

**Location**: `src/calibre_mcp/tools/user_comments/`

---

## 4. manage_publishers

**Purpose**: Full publisher management analogous to `manage_authors`. Uses Calibre's publishers table (or identifiers fallback).

**Operations**:
- `list`: List publishers with search and pagination
- `get`: Get publisher details by `publisher_id` or `publisher_name`
- `get_books`: Get books from a publisher
- `stats`: Total publishers, by-letter distribution, top publishers
- `by_letter`: Publishers whose names start with letter

**Data source**: Calibre `publishers` table + `books_publishers_link`; falls back to `identifiers` (type='publisher') if publishers table does not exist.

**Location**: `src/calibre_mcp/tools/publishers/`

---

## 5. CalibreMCP-Owned SQLite Database

**File**: `calibre_mcp_data.db`

**Default location**:
- Windows: `%APPDATA%\calibre-mcp\calibre_mcp_data.db`
- macOS: `~/Library/Application Support/calibre-mcp/calibre_mcp_data.db`
- Linux: `~/.local/share/calibre-mcp/calibre_mcp_data.db`

**Override**: Set `CALIBRE_MCP_USER_DATA_DIR` to use a different directory.

**Fallback**: If the default directory is not writable, falls back to `<cwd>/.calibre-mcp-data/`.

**Tables**:
- `user_comments`: book_id, library_path, comment_text, created_at, updated_at, user_id (nullable, for future auth)
- `book_extended_metadata`: book_id, library_path, translator, first_published, created_at, updated_at

**Extensible for**:
- Auth (users table, sessions)
- Preferences
- Reading progress
- Other CalibreMCP-specific state

**Initialization**: Called at server startup in `server.py` main(). Also lazy-initializes on first use.

---

## 6. manage_extended_metadata

**Purpose**: Store translator and first_published outside Calibre's schema. metadata.db is never modified.

**Operations**:
- `get`: Get translator and first_published for a book
- `set_translator`: Set translator name
- `set_first_published`: Set original publication (e.g. "1599", "44 BC")
- `upsert`: Set both (partial updates OK)
- `delete`: Remove extended metadata

**Use case**: Julius Caesar's pubdate might be 2025 (edition); first_published = "1599".

**Location**: `src/calibre_mcp/tools/extended_metadata/`

---

## 7. manage_times

**Purpose**: Query books by date - added (timestamp) or published (pubdate/edition).

**Operations**:
- `added_in_range`: Books added between added_after and added_before
- `published_in_range`: Books with pubdate in range
- `recent_additions`: Most recently added books
- `stats_by_month_added`: Count per month (added)
- `stats_by_month_published`: Count per month (pubdate)
- `date_stats`: Summary (earliest/latest dates)

**Note**: query_books already supports added_after, added_before, pubdate_start, pubdate_end (now fixed in book_service). manage_times adds stats and dedicated date-centric operations.

**Location**: `src/calibre_mcp/tools/times/`

---

## Usage Examples

```python
# manage_publishers
await manage_publishers(operation="list", query="O'Reilly", limit=20)
await manage_publishers(operation="get", publisher_id=5)
await manage_publishers(operation="get", publisher_name="Penguin")
await manage_publishers(operation="get_books", publisher_name="No Starch", limit=10)
await manage_publishers(operation="stats")
await manage_publishers(operation="by_letter", letter="O")
```

---

## Files Added/Modified

### New Files
- `src/calibre_mcp/db/user_data.py` - User data SQLite DB + UserComment model
- `src/calibre_mcp/services/user_comment_service.py`
- `src/calibre_mcp/services/series_service.py`
- `src/calibre_mcp/services/description_service.py`
- `src/calibre_mcp/tools/user_comments/__init__.py`
- `src/calibre_mcp/tools/user_comments/manage_user_comments.py`
- `src/calibre_mcp/tools/series/__init__.py`
- `src/calibre_mcp/tools/series/series_helpers.py`
- `src/calibre_mcp/tools/series/manage_series.py`
- `src/calibre_mcp/tools/descriptions/__init__.py`
- `src/calibre_mcp/tools/descriptions/description_helpers.py`
- `src/calibre_mcp/tools/descriptions/manage_descriptions.py`
- `src/calibre_mcp/tools/publishers/__init__.py`
- `src/calibre_mcp/tools/publishers/publisher_helpers.py`
- `src/calibre_mcp/tools/publishers/manage_publishers.py`
- `src/calibre_mcp/services/publisher_service.py`
- `src/calibre_mcp/db/user_data.py` - Added BookExtendedMetadata model
- `src/calibre_mcp/services/extended_metadata_service.py`
- `src/calibre_mcp/services/times_service.py`
- `src/calibre_mcp/tools/extended_metadata/` (manage_extended_metadata)
- `src/calibre_mcp/tools/times/` (manage_times)

### Modified Files
- `src/calibre_mcp/tools/__init__.py` - Registered new portmanteaus
- `src/calibre_mcp/services/book_service.py` - Date filtering (pubdate_start/end, added_after/before)
- `src/calibre_mcp/server.py` - Added init_user_data_db() at startup
- `.gitignore` - Added `.calibre-mcp-data/`

---

## Usage Examples

```python
# manage_descriptions - browse Calibre descriptions
await manage_descriptions(operation="list", has_description=True, limit=20)
await manage_descriptions(operation="get", book_id=42)
await manage_descriptions(operation="stats")
await manage_descriptions(operation="by_letter", letter="A")

# manage_series - series operations
await manage_series(operation="list", query="Sherlock", limit=20)
await manage_series(operation="get", series_id=5)
await manage_series(operation="get_books", series_id=5, limit=10)
await manage_series(operation="stats")
await manage_series(operation="by_letter", letter="S")

# manage_user_comments - personal annotations
await manage_user_comments(operation="create", book_id=42, text="Great read, recommend to friends")
await manage_user_comments(operation="read", book_id=42)
await manage_user_comments(operation="append", book_id=42, text="Re-read in 2025 - still holds up")
await manage_user_comments(operation="delete", book_id=42)

# manage_extended_metadata - translator, first_published (external DB)
await manage_extended_metadata(operation="set_first_published", book_id=42, first_published="1599")
await manage_extended_metadata(operation="set_translator", book_id=42, translator="John Florio")
await manage_extended_metadata(operation="get", book_id=42)
await manage_extended_metadata(operation="upsert", book_id=42, translator="X", first_published="44 BC")

# manage_times - date-based queries
await manage_times(operation="added_in_range", added_after="2024-12-01", added_before="2024-12-31")
await manage_times(operation="recent_additions", limit=20)
await manage_times(operation="stats_by_month_added", year=2024)
await manage_times(operation="date_stats")
```

---

## Terminology Note

In Calibre: **comment** = **description** (the book synopsis). Both terms refer to the same metadata field. `manage_comments` edits it; `manage_descriptions` browses it.

**User comments** are a separate concept: personal annotations stored in CalibreMCP's own DB.
