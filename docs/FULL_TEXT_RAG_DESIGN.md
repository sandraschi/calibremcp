# Full-Text RAG Design (Future / Partial)

This document describes the **unified** full-text RAG vision: semantic search over **book content** (EPUB/PDF text), not just metadata.

**Status (2026-03):**

- **Metadata RAG** is implemented: `rag/metadata_rag.py`, tools `calibre_metadata_index_build` / `calibre_metadata_search`, directory `lancedb_metadata/`.
- **Content paths already exist:** Calibre FTS drives `rag_index_build` / `rag_retrieve` (chunks from `full-text-search.db` → `{library}/lancedb`, table `books_rag`); portmanteau `calibre_rag` uses `{library}/lancedb_calibre` (`calibre_media`, `calibre_fulltext`); DeepIngestor fills `calibre_fulltext` from EPUB/PDF files.
- **Phrase-level navigation** is implemented separately: `search_fulltext(..., resolve_locations=True)` plus `utils/fts_location_resolver.py` (PDF page, EPUB spine href, Calibre `ebook-viewer --open-at search:…`). Dependencies: `ebooklib`, `pymupdf`.

The **schema below** (`book_chunks`, single `lancedb_fulltext` tree) remains the **consolidation target** if you merge those pipelines later.

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

## Dependencies

- Text extraction: **`ebooklib`**, **`pymupdf`** — now core dependencies (FTS location resolver, DeepIngestor).
- Embedding: already have `fastembed`; reuse for full-text.
- Storage: already have `lancedb`; add table `book_chunks` with same connection pattern as metadata RAG.

## Sync / Refresh

- On-demand build (like current `rag_index_build`) or incremental: track last_modified per book and re-chunk only changed books.
- Full-text index path: e.g. `{library_path}/lancedb_fulltext` to keep separate from `lancedb_metadata`.

## Chunk RAG filters (FTS path, shipped)

`rag_index_build` reads `books_text` rows from `full-text-search.db`. Operators can tune:

| Env | Default | Meaning |
|-----|---------|--------|
| `CALIBRE_RAG_CHUNK_EXCLUDE_FORMATS` | Unset → PDF excluded | Comma-separated format codes to **skip**. Unset means **PDF only** excluded. EPUB-first libraries: keep default. To include PDFs in chunk RAG, set **`CALIBRE_RAG_CHUNK_EXCLUDE_FORMATS=`** (empty string). |
| `CALIBRE_RAG_MAX_BOOK_TEXT_CHARS` | *(none)* | If set, skip any row whose `searchable_text` length exceeds this (e.g. `5000000` to drop giant medical texts). |

**Metadata RAG** (`calibre_metadata_index_build`) uses the same catalog fields for **every** book (EPUB, PDF, etc.): title, authors, tags, **comments**, series — no format-specific path. PDF vs EPUB only matters for **content** (chunk) RAG, not metadata RAG.

---

## Prioritized backlog (full content RAG + ops)

1. **Must-have — full content RAG quality:** EPUB-first chunk pipeline polish (section-aware splits, token limits), incremental re-index by `last_modified`, and retrieval UX (snippets + book_id + title).
2. **PDF policy:** keep **default exclude PDF** for chunk RAG; document **explicit** opt-in (`CALIBRE_RAG_CHUNK_EXCLUDE_FORMATS=`). Optional future: OCR / layout-aware path **only** for tagged books, not the default.
3. **Size / sanity:** `CALIBRE_RAG_MAX_BOOK_TEXT_CHARS` for “too big” rows; optional per-format caps later.
4. **Reliability + CI:** `just check` + integration test on a tiny fixture SQLite FTS.
5. **Webapp parity:** “Export metadata JSON” button; optional “rebuild chunk index” with filter hints.
6. **Observability:** structured logs for index build duration, rows skipped (format + oversize counts).

---

## Implementation Order (legacy list — partial)

1. Add extraction and chunking module for EPUB/PDF.
2. Add LanceDB table `book_chunks` and ingest pipeline.
3. Add or extend retrieve tool to search `book_chunks` and return passages with book_id, title, snippet.
4. Optional: filter by metadata (e.g. only search in certain tags) using book_id join.
