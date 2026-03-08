# Full-Text RAG Design (Future)

This document describes the planned full-text RAG feature: semantic search over **book content** (EPUB/PDF text), not just metadata. It is not implemented yet; the current RAG over metadata (title, authors, tags, comments, series) is implemented in `rag/metadata_rag.py` and tools `calibre_metadata_index_build` / `calibre_metadata_search`.

## Scope

- **Sources:** EPUB and PDF (primary); optionally other formats with text extraction.
- **Chunking:** By section/paragraph with configurable max token size (e.g. 512–1024 tokens). Overlap between chunks for context.
- **Storage:** Separate LanceDB table (e.g. `book_chunks`) or namespace so metadata RAG and full-text RAG can coexist.
- **Embedding:** Same embedding model as metadata RAG (e.g. `BAAI/bge-small-en-v1.5`) or configurable per table.
- **Integration:** New tool(s) e.g. `rag_index_build` (already exists for FTS-based content) to be aligned with this design; or a dedicated `full_text_rag_build` and `full_text_rag_retrieve` that use this schema.

## Schema (Reserved)

| Field         | Type     | Description                                |
|---------------|----------|--------------------------------------------|
| `book_id`     | int      | Calibre book id                            |
| `format`      | str      | Source format (epub, pdf)                  |
| `chunk_index` | int      | Order of chunk in book                     |
| `text`        | str      | Plain text of the chunk                    |
| `vector`      | float[]  | Embedding for similarity search            |
| `title`       | str      | Book title (for display/filter)            |
| `authors`     | str      | Author names (for display/filter)         |

## Extraction and Chunking

- **EPUB:** Use `ebooklib` or similar to extract text per chapter/section; split into chunks with overlap.
- **PDF:** Use PyMuPDF or pypdf to extract text by page or by block; merge into chunks with max token size.
- **Tokenization:** Use a simple length-based approximation or tiktoken if dependency is acceptable; document token limit (e.g. 512) and overlap (e.g. 50).

## Dependencies (Future)

- Text extraction: `ebooklib`, `PyMuPDF` (or `pypdf`) — to be added when implementing.
- Embedding: already have `fastembed`; reuse for full-text.
- Storage: already have `lancedb`; add table `book_chunks` with same connection pattern as metadata RAG.

## Sync / Refresh

- On-demand build (like current `rag_index_build`) or incremental: track last_modified per book and re-chunk only changed books.
- Full-text index path: e.g. `{library_path}/lancedb_fulltext` to keep separate from `lancedb_metadata`.

## Implementation Order (When Ready)

1. Add extraction and chunking module for EPUB/PDF.
2. Add LanceDB table `book_chunks` and ingest pipeline.
3. Add or extend retrieve tool to search `book_chunks` and return passages with book_id, title, snippet.
4. Optional: filter by metadata (e.g. only search in certain tags) using book_id join.
