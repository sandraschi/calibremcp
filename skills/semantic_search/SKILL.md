# Semantic Search (Metadata RAG)

**Description:** Find books by meaning using LanceDB over title, authors, tags, comments, and series. Supports hybrid keyword + vector search across your entire Calibre library.

## Trigger Phrases

- "Find books about [topic]"
- "Search my library for [query]"
- "What do I have on [subject]?"
- "Show me books similar to [title]"
- "Find [author] books about [theme]"

## Tools

- `calibre_metadata_index_build()` — Build or rebuild the LanceDB metadata index. Run once per library or after large batch imports.
- `calibre_metadata_search(query="...", top_k=10)` — Natural-language semantic search over book metadata. Returns ranked results with relevance scores.
- `rag_index_build()` — Build full-text content index from ebook text (requires epub/mobi extraction).
- `rag_retrieve(query="...", top_k=5)` — Semantic search over full book contents, not just metadata.
- `search_fulltext(query="...")` — Legacy full-text search with exact phrase matching and boolean operators.
- `query_books(search="...", tags=[...], authors=[...])` — Structured metadata filtering with AND/OR logic.

## Workflow

1. **Index check**: If no index exists, call `calibre_metadata_index_build()` first (runs async, takes 1-5 min per 1000 books).
2. **Metadata search**: Use `calibre_metadata_search()` for broad semantic queries. Combine with `top_k` to control result breadth.
3. **Filter refinement**: Narrow results by chaining with `query_books()` using author, tag, or series filters.
4. **Deep content search**: For research-style queries, call `rag_retrieve()` to search inside book text. Caveat: works best on epub format.
5. **Result presentation**: Return title, author, relevance score, and match highlights. Include calibre book_id for follow-up actions (open, metadata edit, export).

## Search Operators

- **Phrase match**: Use quotes in `search_fulltext` — `"machine learning"`
- **Boolean**: `search_fulltext(query="python AND (data science OR ML)")`
- **Tag filter**: `query_books(tags=["python", "tutorial"], limit=20)`
- **Date range**: `query_books(added_since="2024-01-01")`

## Examples

- "Find programming books about Python and data science." → `calibre_metadata_search(query="programming Python data science")`
- "Search inside my books for mentions of gradient descent." → `rag_retrieve(query="gradient descent", top_k=5)`
- "What sci-fi books do I have about AI consciousness?" → `calibre_metadata_search(query="sci-fi AI consciousness")` then filter with `query_books(tags=["science fiction"])`
