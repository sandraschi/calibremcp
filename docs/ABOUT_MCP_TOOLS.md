# About MCP Server Tools

calibre-mcp exposes **21 portmanteau tools** via FastMCP 3.2, giving AI assistants structured, concurrency-safe access to your Calibre library. Tools register at import time via `@mcp.tool` decorators and support simultaneous stdio + HTTP (universal connect).

## What are portmanteau tools?

Instead of having one tool per action (50+ tools), related operations are consolidated into a single tool with an `operation` parameter. Example:

```
manage_libraries(operation="list")      → list all libraries
manage_libraries(operation="switch")    → switch to a different library
manage_libraries(operation="stats")     → get library statistics
manage_libraries(operation="discover")  → auto-discover libraries
```

This keeps the tool list manageable while maintaining full functionality.

## Key tools at a glance

| Tool | What it does | Key operations |
|------|-------------|----------------|
| `query_books` | Find, list, and retrieve books | `search`, `list`, `by_author`, `by_series` |
| `manage_libraries` | Discover, switch, and analyze libraries | `list`, `switch`, `stats`, `discover` |
| `calibre_metadata_search` | Semantic search over metadata (LanceDB RAG) | `query`, `top_k` |
| `search_fulltext` | Keyword/phrase search in book content (FTS5) | `query`, `resolve_locations` |
| `calibre_metadata_index_build` | Build/rebuild LanceDB metadata index | `force_rebuild` |
| `calibre_rag` | Full-text RAG retrieval (DeepIngestor) | `query`, `top_k` |
| `rag_index_build` / `rag_retrieve` | Build/search chunk-level FTS→LanceDB index | — |
| `manage_books` | Add, get details, update, delete books | `add`, `get`, `details`, `update`, `delete` |
| `manage_metadata` | Update metadata, organize tags, show book info | `update`, `organize_tags`, `show` |
| `manage_authors` | List, get books by author, stats | `list`, `get_books`, `stats` |
| `manage_series` | List, create, update, delete series | `list`, `create`, `update`, `delete` |
| `manage_tags` | List, create, merge tags | `list`, `create`, `merge` |
| `manage_comments` | CRUD for book comments/descriptions | `create`, `read`, `update`, `delete` |
| `manage_viewer` | Open/close books in system viewer | `open`, `close`, `open_random` |
| `manage_publishers` | List, create, update, delete publishers | `list`, `create`, `update`, `delete` |
| `manage_files` | Read, write, convert book files | `read`, `write`, `convert` |
| `manage_analysis` | Library health and statistics | `analyze`, `stats`, `health` |
| `manage_library_operations` | Series fixes, merges, list all books | `analyze_series`, `fix_series_metadata`, `merge_series` |
| `export_books` | Export/import book lists | `export`, `import` |
| `calibre_ocr` | OCR operations on PDF/image books | — |
| `calibre_metadata_export_json` | Export full library metadata as JSON | — |
| `show_book_prefab_card` | Rich MCP Prefab card for a book | `book_id` |
| `show_libraries_prefab_card` | Rich MCP Prefab card for library list | — |

## How tools work with AI assistants

### Typical agentic flow

```
User: "Find unread sci-fi by Banks and open one"
  ↓
Claude calls: query_books(operation="search", tag="Science Fiction", author="Banks", has_been_read=False)
  ↓  returns [{book_id: 42, title: "Consider Phlebas"}, ...]
Claude calls: manage_viewer(operation="open", book_id=42)
  ↓
Book opens in Calibre viewer
```

### Verb mapping

Users use different verbs — the AI maps them correctly:
- "search", "list", "find", "query", "get", "show me" → `query_books(operation="search", ...)`

### Return format

All tools return a consistent schema:
```json
{
    "success": true,
    "message": "Found 3 books",
    "data": { ... }
}
```

## Architecture

```
Claude Desktop / Cursor / AI Client
  ↓ stdio or HTTP
FastMCP 3.2 Server (src/calibre_mcp/)
  ├── 21 portmanteau tools
  ├── LanceDB RAG engine (rag/)
  ├── FTS resolver (utils/fts_location_resolver.py)
  ├── Calibre DB adapter (read/write metadata.db)
  └── calibre_mcp_data.db (extended metadata)
  ↓
Calibre Library (metadata.db + full-text-search.db)
```

## Concurrency safety

Thread-safe database operations with row-level locking for multi-client access. Multiple AI clients can connect simultaneously via universal connect (stdio + HTTP).

## Beta tools

Experimental tools available behind `CALIBRE_BETA_TOOLS=true`:
- `manage_import`, `manage_descriptions`, `manage_user_comments`
- `manage_extended_metadata`, `manage_times`, `manage_content_sync`
- `manage_ai_operations` (requires Ollama), `manage_bulk_operations`
- `agentic_calibre_workflow`

Full API reference: [API.md](API.md) | Tools consolidation history: [TOOLS_CONSOLIDATION.md](TOOLS_CONSOLIDATION.md)

> **Next:** [About AI Workflows](ABOUT_AI_WORKFLOWS.md) | **Back:** [About Plugins](ABOUT_PLUGINS.md)
