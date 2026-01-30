# CalibreMCP Calibre Plugin - Design Document

**Date**: 2025-01-30

## Executive Summary

A Calibre plugin that integrates CalibreMCP with the Calibre GUI. Enables viewing/editing extended metadata (translator, first_published, user_comments), bulk AI enrichment, right-click AI actions, virtual library creation from MCP queries, and optional sync with Calibre custom columns.

---

## Architecture Overview

```
+------------------+     +------------------------+     +---------------------+
|   Calibre GUI    |     |   CalibreMCP Plugin    |     |   CalibreMCP / DB   |
|                  |     |                        |     |                     |
| - Library view   |---->| - MCP Metadata dialog  |---->| calibre_mcp_data.db |
| - Edit metadata  |     | - Right-click actions  |     | (direct SQLite)     |
| - Preferences    |     | - Bulk enrich dialog   |     |                     |
| - Virtual libs   |     | - Config (paths, URL)  |---->| CalibreMCP HTTP     |
+------------------+     +------------------------+     | (optional, AI)      |
                                                       +---------------------+
```

---

## Communication Modes

### Mode A: Direct Database Access (no MCP process)

- **Used for**: Extended metadata panel, user comments, custom column sync
- **How**: Plugin reads/writes `calibre_mcp_data.db` directly via SQLite
- **DB path**: Same as CalibreMCP - `CALIBRE_MCP_USER_DATA_DIR` or platform default
- **Advantage**: Works offline, no process to manage, instant

### Mode B: HTTP API (MCP must be running)

- **Used for**: AI actions (summarize, suggest tags, bulk enrich), VL from query
- **How**: Plugin calls CalibreMCP HTTP endpoint (when available)
- **Requirement**: User runs CalibreMCP with HTTP transport (webapp or `--transport http`)
- **Fallback**: If MCP unavailable, AI features disabled with clear message

---

## Feature Specifications

### 1. Extended Metadata Panel

**Purpose**: View/edit first_published, translator, user_comments in Calibre.

**UI**:
- Menu: Tools -> MCP Metadata (or toolbar button)
- Dialog opens for currently selected book(s); if multiple, iterates or shows list
- Fields: First Published, Translator, User Comment (multi-line)
- Save writes to `calibre_mcp_data.db` (book_extended_metadata, user_comments)
- Library path: `gui.current_db.library_path` or equivalent

**Data flow**:
- Read: `SELECT * FROM book_extended_metadata WHERE book_id=? AND library_path=?`
- Read: `SELECT * FROM user_comments WHERE book_id=? AND library_path=?`
- Write: UPSERT on both tables

**Scoping**: (book_id, library_path) - same as CalibreMCP.

---

### 2. Bulk Enrich

**Purpose**: AI-fill missing metadata for selected books.

**UI**:
- Select N books -> Right-click -> "MCP: Enrich metadata" (or Tools menu)
- Dialog: Options (fill description, first_published, translator, tags)
- Progress bar; runs async or in background
- **Requires**: Mode B (MCP HTTP)

**MCP tools used** (conceptual):
- `manage_extended_metadata` (set_first_published, set_translator)
- `manage_comments` (if filling description)
- Tag suggestions -> `manage_books` or tag tools

**Implementation note**: CalibreMCP may need a batch/enrich tool or we call tools per-book.

---

### 3. Right-Click AI Actions

**Purpose**: Single-book AI actions from context menu.

**Actions**:
- **Summarize**: AI generates description -> write to Calibre comment
- **Suggest tags**: AI suggests tags -> user picks -> apply
- **Set first published**: AI infers from content -> write to extended metadata

**UI**: Right-click book -> "MCP" submenu -> action

**Requires**: Mode B (MCP HTTP).

---

### 4. Virtual Library from MCP Query

**Purpose**: Create Calibre virtual library from MCP query result.

**UI**:
- Menu: Tools -> MCP: Create virtual library from query
- Dialog: Query text (e.g. "books added last month", "unread fiction")
- Plugin calls MCP, gets book IDs, creates VL via Calibre API
- **Requires**: Mode B

**MCP**: `query_books` or `manage_times` returns book IDs. Plugin uses `db.new_api.set_custom()` or VL creation API.

---

### 5. Custom Column Sync

**Purpose**: Bidirectional sync between Calibre custom columns and MCP extended metadata.

**Config**:
- User defines mapping: e.g. `#translator` <-> translator, `#first_published` <-> first_published
- Direction: Calibre -> MCP, MCP -> Calibre, or both

**Behaviour**:
- On save in MCP metadata dialog: if column mapped, also write to Calibre custom column
- On book load in Calibre: if pref "Sync on view", read from column and ensure MCP DB in sync
- **Implementation**: Use `db.new_api.set_custom(book_id, 'column_name', value)` and `get_custom()`

---

## Plugin Structure

```
calibre_mcp_plugin/
├── plugin-import-name-calibre_mcp_integration.txt
├── __init__.py           # InterfaceActionBase, metadata
├── ui.py                 # InterfaceAction, menu, dialogs
├── config.py             # JSONConfig, ConfigWidget (paths, MCP URL)
├── db_adapter.py         # Direct SQLite access to calibre_mcp_data.db
├── mcp_client.py         # HTTP client for MCP (when available)
├── dialogs/
│   ├── __init__.py
│   ├── metadata_dialog.py    # Extended metadata panel
│   ├── bulk_enrich_dialog.py
│   └── vl_query_dialog.py
├── images/
│   └── icon.png
└── about.txt
```

---

## Configuration (JSONConfig)

| Key | Default | Description |
|-----|---------|-------------|
| `mcp_user_data_dir` | (platform default) | Override for calibre_mcp_data.db location |
| `mcp_http_url` | `http://127.0.0.1:8765` | CalibreMCP HTTP base URL (if running) |
| `sync_translator_column` | `""` | Calibre custom column for translator (empty = no sync) |
| `sync_first_published_column` | `""` | Custom column for first_published |
| `sync_user_comment_column` | `""` | Custom column for user comments |

---

## Database Schema (calibre_mcp_data.db)

Plugin must match CalibreMCP schema:

**book_extended_metadata**:
- id, book_id, library_path, translator, first_published, created_at, updated_at

**user_comments**:
- id, book_id, library_path, comment_text, created_at, updated_at, user_id

---

## Calibre Plugin API Usage

- **InterfaceActionBase**: Base class; `actual_plugin` points to ui module
- **InterfaceAction**: `self.gui`, `self.gui.current_db`, `self.gui.library_view`
- **db.new_api**: `all_book_ids()`, `get_metadata()`, `set_custom()`, `get_custom()`
- **Library path**: `db.backend.library_path` or `db.library_path`
- **Virtual library**: `db.new_api.get_search_terms()` / `set_custom()` for saved searches

---

## Dependencies

- Calibre 6.x+ (uses bundled Python)
- No external Python packages (plugin uses Calibre's env; stdlib `sqlite3`, `urllib`/`http.client`)

---

## Future Considerations

- **Anna's Archive / Get Books**: URL maintenance is upstream; plugin does not duplicate
- **Calibre native AI**: If Calibre adds AI, plugin can delegate or coexist
- **HTTP transport**: CalibreMCP may add `uv run calibre-mcp serve --transport http` for standalone HTTP

---

## Implementation Status (2025-01-30)

- **Extended metadata panel**: DONE (direct DB)
- **VL from query**: DONE (calls webapp /api/search, creates Calibre saved search)
- **Bulk enrich**: Placeholder (shows backend status)
- **Custom column sync**: Config keys present; deferred
- **Right-click AI actions**: Deferred

## References

- [Calibre Plugin Tutorial](https://manual.calibre-ebook.com/creating_plugins.html)
- [Calibre Plugin API](https://manual.calibre-ebook.com/plugins.html)
- CalibreMCP: `docs/NEW_PORTMANTEAUS_IMPLEMENTATION.md`
