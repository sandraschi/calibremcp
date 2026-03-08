# Semantic Search (Metadata RAG)

**Description:** Find books by meaning using LanceDB over title, authors, tags, comments, and series.

## Steps

1. Ensure metadata index exists: call `calibre_metadata_index_build()` once per library (or after large changes).
2. Use `calibre_metadata_search(query="...", top_k=10)` for natural-language search.
3. Optionally use `rag_index_build()` and `rag_retrieve()` for full-text semantic search over book content.

## Example

"Find programming books about Python and data science." → `calibre_metadata_search(query="programming Python data science")`
