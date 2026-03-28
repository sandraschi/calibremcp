# MCP Apps (Prefab) — rich cards

**Server:** CalibreMCP · **Tools:** `show_book_prefab_card(book_id)`, `show_libraries_prefab_card()` · **FastMCP:** `@mcp.tool(app=True)` + `ToolResult` / `PrefabApp`

## Install

```powershell
uv sync --extra apps
```

Optional extra **`[project.optional-dependencies] apps`** pulls **`prefab-ui`**. Disable registration with **`CALIBRE_PREFAB_APPS=0`**.

## Behavior

- **Book card:** loads book metadata and cover (data URI, size-capped); **synopsis** from Calibre **comments** with **HTML stripped**; **Authors / Series / Tags** as separate `Text` lines for layout in the host. **Not found:** small Prefab card + text error.
- **Libraries card (“Our Calibre”):** lists all discovered libraries with **book count**, **size (MB)**, **active** flag, **truncated path**; **empty** list shows a short help card.
- **Webapp:** `webapp/backend/app/mcp/client.py` maps **`show_book_prefab_card`** / **`show_libraries_prefab_card`** for dynamic tool import (`…book_card:…`, `…libraries_card:…`).

## Fleet documentation (MCP Central Docs)

| Doc | Purpose |
|-----|---------|
| [mcp-apps-prefab-ui.md](https://github.com/sandraschi/mcp-central-docs/blob/master/fastmcp/mcp-apps-prefab-ui.md) | Mechanics, packaging, `ToolResult`, UX rules |
| [mcp-apps-prefab-use-cases-and-examples.md](https://github.com/sandraschi/mcp-central-docs/blob/master/fastmcp/mcp-apps-prefab-use-cases-and-examples.md) | Use cases, client UX, examples |

**Code:** `src/calibre_mcp/tools/prefab/book_card.py`, `libraries_card.py` · `register_prefab_tools()` from `register_tools()`.
