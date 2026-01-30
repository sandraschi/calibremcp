# CalibreMCP Plugin - Implementation Notes

**Date**: 2025-01-30

## Step-by-Step Implementation Checklist

### Phase 1: Skeleton and Config

- [ ] Create `calibre_plugin/` directory in repo (or separate repo)
- [ ] `plugin-import-name-calibre_mcp_integration.txt` (empty)
- [ ] `__init__.py`: InterfaceActionBase, name, description, version, actual_plugin
- [ ] `config.py`: JSONConfig `plugins/calibre_mcp_integration`, ConfigWidget with:
  - MCP user data dir (path)
  - MCP HTTP URL (for AI features)
  - Custom column mappings (optional)
- [ ] `is_customizable()`, `config_widget()`, `save_settings()` in base plugin

### Phase 2: DB Adapter (Direct SQLite)

- [ ] `db_adapter.py`: Get DB path from config or platform default
- [ ] Platform default: Windows `%APPDATA%\calibre-mcp`, Linux `~/.local/share/calibre-mcp`, macOS `~/Library/Application Support/calibre-mcp`
- [ ] `get_extended_metadata(book_id, library_path)` -> dict
- [ ] `set_extended_metadata(book_id, library_path, translator, first_published)` -> None
- [ ] `get_user_comment(book_id, library_path)` -> str
- [ ] `set_user_comment(book_id, library_path, text)` -> None
- [ ] Use `sqlite3` stdlib; create tables if not exist (match CalibreMCP schema)

### Phase 3: Extended Metadata Dialog

- [ ] `dialogs/metadata_dialog.py`: QDialog with:
  - QLineEdit: First Published
  - QLineEdit: Translator
  - QTextEdit: User Comment
  - Save / Cancel
- [ ] Load from db_adapter on show; save on Save
- [ ] Get current book from `gui.library_view.selectionModel().selectedRows()` -> book_id
- [ ] Library path: `gui.current_db.backend.library_path` or `gui.current_db.library_path`

### Phase 4: Menu and Actions

- [ ] `ui.py`: InterfaceAction
- [ ] `action_spec`: ("MCP Metadata", None, "Edit MCP extended metadata", "Ctrl+Shift+M")
- [ ] `genesis()`: Connect qaction to show metadata dialog
- [ ] Add to Tools menu or toolbar via plugin preferences

### Phase 5: Right-Click Context Menu

- [ ] Override `create_menu_action` or use `gui.device_menu.addAction` pattern
- [ ] Calibre: `add_menu_action` on context menu - check InterfaceAction API for "Add to context menu"
- [ ] Submenu "MCP" with: Summarize, Suggest tags, Set first published
- [ ] Each triggers MCP client call (Phase 6)

### Phase 6: MCP HTTP Client (Optional)

- [ ] `mcp_client.py`: Simple HTTP client
- [ ] `call_tool(tool_name, arguments)` -> result
- [ ] MCP over HTTP: typically POST to `/mcp` or similar; check FastMCP HTTP API
- [ ] If connection fails: show "CalibreMCP not running" dialog
- [ ] Tools to call: `manage_comments` (edit), tag tools, etc.

### Phase 7: Bulk Enrich Dialog

- [ ] `dialogs/bulk_enrich_dialog.py`: Options, progress, "Enrich" button
- [ ] For each selected book: call MCP enrich or per-tool
- [ ] Use QProgressDialog or worker thread to avoid UI freeze

### Phase 8: Virtual Library from Query

- [ ] `dialogs/vl_query_dialog.py`: QLineEdit for query, "Create VL" button
- [ ] Call MCP `query_books` or `manage_times` with query
- [ ] Parse response for book IDs
- [ ] Calibre VL: `db.new_api.saved_search_add(name, search_string)` - need to build search that matches IDs
- [ ] Or: use `search_expression` like `id:1 or id:2 or id:3` if supported

### Phase 9: Custom Column Sync

- [ ] When saving metadata dialog: if column mapping set, also `db.set_custom(book_id, col, val)`
- [ ] Optional: on metadata dialog load, read from column and merge with MCP DB

### Phase 10: Packaging and Testing

- [x] Plugin in `calibre_plugin/` - skeleton, config, db_adapter, metadata dialog, bulk/VL placeholders
- [ ] ZIP: all files, `plugin-import-name-*.txt`
- [ ] `calibre-customize -b .` to install from folder
- [ ] Test with `calibre-debug -g`
- [ ] Verify DB path resolution on Windows, Linux, macOS

### Status (2025-01-30)

- Extended metadata panel: DONE (direct DB)
- Config: DONE
- VL from query: DONE (calls /api/search, creates Calibre saved search)
- MCP HTTP client: DONE (is_available, call_search)
- Bulk enrich: Placeholder (shows backend status)

---

## Critical Code Snippets

### Library Path (Calibre)

```python
# In Calibre plugin, get current library path:
db = self.gui.current_db
# db.backend.library_path or:
if hasattr(db, 'backend'):
    lib_path = db.backend.library_path
else:
    lib_path = getattr(db, 'library_path', str(db.library_path))
```

### User Data Dir (Match CalibreMCP)

```python
import os
from pathlib import Path

def get_mcp_user_data_dir():
    env = os.getenv("CALIBRE_MCP_USER_DATA_DIR")
    if env:
        return Path(env)
    if os.name == "nt":
        appdata = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        return Path(appdata) / "calibre-mcp"
    home = Path.home()
    import platform
    if platform.system() == "Darwin":
        return home / "Library" / "Application Support" / "calibre-mcp"
    return home / ".local" / "share" / "calibre-mcp"
```

### SQLite Tables (Create if not exist)

```sql
CREATE TABLE IF NOT EXISTS book_extended_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    library_path TEXT NOT NULL,
    translator TEXT,
    first_published TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    library_path TEXT NOT NULL,
    comment_text TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT
);
```

---

## Anna's Archive / Get Books Note

The Get Books plugin URL for Anna's Archive may change. Kovid or maintainers will patch. This plugin does not duplicate that functionality. If desired, a separate "MCP: Search Anna's Archive" action could call an MCP tool that fetches from Anna's - but that would require the MCP tool and is out of scope for initial release.

---

## Testing Commands

```bash
# Build plugin from folder
cd calibre_plugin
zip -r ../calibre_mcp_integration.zip .

# Install
calibre-customize -b /path/to/calibre_plugin
# Or
calibre-customize -a calibre_mcp_integration.zip

# Debug run
calibre-debug -g
```
