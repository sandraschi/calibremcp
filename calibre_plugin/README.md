# CalibreMCP Integration — Calibre Plugin

A Calibre plugin that surfaces CalibreMCP capabilities inside the Calibre GUI.
Part of the [calibre-mcp](https://github.com/sandraschi/calibre-mcp) project.

---

## What it does

### Extended metadata panel (works standalone, no server needed)

Select any book, press **Ctrl+Shift+M** or use the toolbar button. A dialog opens
with three fields that Calibre doesn't natively support:

- **First Published** — original publication date (e.g. `1599`, `44 BC`, `1984`)
- **Translator** — translator name for translated works
- **Personal notes** — your own annotations, separate from the book's description

Data is saved to a local SQLite DB (`calibre_mcp_data.db`) that CalibreMCP also
reads. Notes you add here appear when Claude queries your library via the MCP server.

### Create Virtual Library from query (requires webapp running)

Toolbar dropdown → **Create VL from Query...** — type a search query, give the VL
a name, and the plugin calls the calibre-mcp webapp backend, retrieves matching book
IDs, and creates a Calibre saved search you can use as a virtual library.

### Bulk Enrich (placeholder — not yet implemented)

Toolbar dropdown → **Bulk Enrich...** — shows server status. AI enrichment
implementation is planned but not built yet.

---

## Requirements

- Calibre 6.0 or later
- Python is Calibre's bundled interpreter — no separate install needed
- For VL from Query: calibre-mcp webapp backend running on port 10720

---

## Install

### Option A — from source directory (fastest for development)

```powershell
& "C:\Program Files\calibre2\calibre-customize.exe" -b D:\Dev\repos\calibre-mcp\calibre_plugin
```

### Option B — from ZIP

```powershell
# Build the ZIP first
.\scripts\build_calibre_plugin.ps1

# Install
& "C:\Program Files\calibre2\calibre-customize.exe" -a D:\Dev\repos\calibre-mcp\calibre_mcp_integration.zip
```

Restart Calibre after installing. The **MCP Metadata** button appears in the toolbar.

### Uninstall

```powershell
& "C:\Program Files\calibre2\calibre-customize.exe" -r "CalibreMCP Integration"
```

---

## Development — test loop

Use the test script for a consistent dev loop:

```powershell
# Dot-source to load helper functions
. D:\Dev\repos\calibre-mcp\scripts\calibre-plugin-test.ps1

# Install from source + launch Calibre with console attached
# (print() output and tracebacks appear in the terminal)
Install-Plugin; Launch-Debug

# Or the full loop including ZIP rebuild:
Test-Loop
```

`calibre-debug -g` is the key tool — it launches the GUI with stdout attached so
you can see import errors and print() output immediately.

---

## Configuration

**Preferences → Plugins → CalibreMCP Integration → Customize**

| Setting | Default | Purpose |
|---------|---------|---------|
| MCP User Data Dir | `%APPDATA%\calibre-mcp` | Override location of `calibre_mcp_data.db` |
| MCP HTTP URL | `http://127.0.0.1:10720` | calibre-mcp webapp backend URL |

The DB location must match where the calibre-mcp MCP server writes its data.
If you haven't changed `CALIBRE_MCP_USER_DATA_DIR`, the default is correct.

---

## Data storage

Extended metadata and personal notes are stored in:

```
%APPDATA%\calibre-mcp\calibre_mcp_data.db
```

Two tables, keyed by `(book_id, library_path)`:

- `book_extended_metadata` — translator, first_published
- `user_comments` — personal notes text

The calibre-mcp MCP server reads the same DB, so data added here is visible
to Claude when querying the library via MCP tools.

---

## Keyboard shortcut

`Ctrl+Shift+M` — opens the extended metadata dialog for the selected book.
Changeable via Calibre's keyboard shortcut preferences.
