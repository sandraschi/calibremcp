## Session Context (Calibre MCP)

You have access to a Calibre e-book library server with 21+ portmanteau tools for search, management, export, and RAG.

**Before starting work:**
1. Search your library: `query_books(operation="search_books", query="<query>")`
2. Check library health: `manage_libraries(operation="library_health")`

**At end of work, save findings:**
- Use `manage_books` to update metadata and `export_books` to save results
- Tag any books discussed for future reference
