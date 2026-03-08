# Agentic Workflow

**Description:** Chain multiple CalibreMCP tools in one flow for discovery, search, and action. Supports FastMCP 3.1 sampling.

## Steps

1. **Discover:** `manage_libraries(operation="list")`, then `manage_libraries(operation="switch", library_name="...")`.
2. **Search:** `query_books` or `calibre_metadata_search` or `search_fulltext` depending on intent.
3. **Act:** `manage_viewer(operation="open", book_id=...)` or `manage_metadata(operation="show", book_id=...)`.
4. Use conversational returns: each tool returns `success`, `message`, and data; use them to decide next step.

## Example

"Open a random unread science fiction book." → list libraries → switch → query_books (tags=sci-fi, unread) → manage_viewer(open_random or open with chosen id).
