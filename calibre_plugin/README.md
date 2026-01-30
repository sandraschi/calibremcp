# CalibreMCP Integration Plugin

Calibre plugin for CalibreMCP - extended metadata, user comments, and future AI integration.

## Install

```bash
# From plugin folder
calibre-customize -b /path/to/calibre_plugin

# Or as ZIP
calibre-customize -a calibre_mcp_integration.zip
```

## Usage

1. Select a book in Calibre
2. Press **Ctrl+Shift+M** or Tools -> MCP Metadata
3. Edit First Published, Translator, User Comment
4. Click Save

Data is stored in `calibre_mcp_data.db` (same DB as CalibreMCP). Claude/Cursor using CalibreMCP will see the same data.

## Config

Preferences -> Plugins -> CalibreMCP Integration -> Customize:
- **MCP User Data Dir**: Override DB location (default: %APPDATA%\calibre-mcp)
- **MCP HTTP URL**: For future AI features (bulk enrich, etc.)

## Icon

Add `images/icon.png` (e.g. 64x64) to the plugin ZIP for a toolbar icon. Optional.
