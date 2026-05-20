# Agentic Workflow

**Description:** Chain multiple CalibreMCP tools in one flow for discovery, search, and action. Supports FastMCP 3.1 sampling for autonomous multi-step ebook processing, batch operations, and import pipelines.

## Trigger Phrases

- "Automate [task] across my library"
- "Batch process all new books"
- "Set up an import pipeline for [folder]"
- "Find and fix [issue] in my library"
- "Process my Calibre library automatically"

## Tools

- `manage_libraries(operation="list")` — List available Calibre libraries.
- `manage_libraries(operation="switch", library_name="...")` — Switch active library context.
- `query_books(search="...", tags=[...], authors=[...], sort="...", unread=True/False)` — Structured book queries.
- `calibre_metadata_search(query="...", top_k=10)` — Semantic metadata search.
- `search_fulltext(query="...")` — Full-text content search.
- `manage_viewer(operation="open", book_id=...)` — Open book in Calibre viewer.
- `manage_metadata(operation="show"/"update", book_id=...)` — Read or modify book metadata.
- `manage_tags(operation="add"/"remove", book_id=..., tags=[...])` — Tag management.
- `manage_analysis(operation="duplicates"/"health"/"reading_stats")` — Library analysis tools.

## Workflow

1. **Discover**: `manage_libraries(operation="list")` to identify the active library. Switch via `manage_libraries(operation="switch", library_name="...")` if multi-library setup.
2. **Search**: Combine `query_books` with `calibre_metadata_search` or `search_fulltext` depending on intent. Use conversational returns (each tool returns `success`, `message`, data dict) to decide next step.
3. **Analyze**: Run `manage_analysis()` to detect duplicates, health issues, or reading patterns before taking action.
4. **Act**: Apply changes via `manage_metadata`, `manage_tags`, or bulk operations. For books to read, chain `manage_viewer(operation="open")` as final step.
5. **Verify**: Optionally re-run analysis to confirm changes took effect.

## Batch Pipeline Pattern

For import workflows: `manage_libraries(operation="list")` → `manage_libraries(operation="switch", library_name="import")` → `query_books(sort="timestamp", limit=50)` for newly added → `manage_analysis(operation="health")` to check quality → `manage_metadata` fixes for any issues → tag normalized batch.

## Example

"Open a random unread science fiction book." → `manage_libraries(operation="switch", library_name="main")` → `query_books(tags=["sci-fi"], unread=True, sort="random", limit=1)` → extract book_id → `manage_viewer(operation="open", book_id=...)`.
