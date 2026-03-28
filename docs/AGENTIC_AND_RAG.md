# Agentic Workflows and RAG

## Agentic workflows (FastMCP 3.1)

CalibreMCP supports **sampling** and **agentic** tool use: an MCP client (e.g. Claude Desktop) can chain multiple tools in one flow. Each tool returns `success`, `message`, and structured data so the next step can be chosen automatically.

**Typical flow:** List libraries → switch library → search (`query_books`, `calibre_metadata_search`, or `search_fulltext`) → open book or show metadata.

**Use in Chat:** Ask e.g. "Open a random unread science fiction book" or "Find programming books about Python and recommend one." The model will call the tools in sequence.

See **Skills** (webapp Skills page or `skills/` in repo) and the **calibre_mcp_guide** prompt for recommended workflows.

## Calibre FTS vs semantic RAG (use both)

| Source | Role | Tools / paths |
|--------|------|----------------|
| **Calibre `full-text-search.db`** | Keyword / phrase match in book body (exact, fast). Required JOIN: `books_text.id = books_fts.rowid`. | `search_fulltext`, `query_books` / `book_service` when FTS is present |
| **Metadata RAG** | Meaning over title, authors, tags, comments, series (no book body). | `calibre_metadata_index_build`, `calibre_metadata_search` → `lancedb_metadata/` |
| **FTS → LanceDB** | Semantic search over *chunks* of text from Calibre’s indexed `searchable_text`. | `rag_index_build`, `rag_retrieve` → `{library}/lancedb`, table `books_rag` |
| **Portmanteau ingest** | `calibre_media` / `calibre_fulltext` under `{library}/lancedb_calibre` (DeepIngestor, `calibre_rag`). | Separate from FTS chunk index |

**Recommendation:** Use **FTS** for quoted lines and rare phrases; use **metadata RAG** or **chunk RAG** for paraphrases and tropes. Run both when unsure.

Implementation detail: vector storage lives in **calibre-mcp** (`rag/lancedb_vector_store.py`); there is **no** runtime dependency on other repos for LanceDB embeddings.

## Metadata RAG (LanceDB)

**Semantic search over book metadata** (title, authors, tags, comments, series) without indexing full book text.

**Format:** **PDF and EPUB are treated the same** — metadata comes from `metadata.db` only, not from EPUB vs PDF rendering. PDF caveats apply to **content** (chunk) RAG and FTS body text, not here.

Comments are intentionally part of the embedding text (many libraries use the Comments field for blurbs and curated notes). The indexer applies **`CALIBRE_METADATA_COMMENT_MAX_CHARS`** (default **20480** = 20 KiB per book comment in the embedding blob; max **16777216**) and optional HTML stripping via **`CALIBRE_METADATA_STRIP_HTML`** (default on); see **`rag/text_utils.py`**. For JSON exports use **`calibre_metadata_export_json`** or the **`calibre-debug`** script — **[CALIBRE_DEBUG_EXPORT_AND_RAG_PLAN.md](./CALIBRE_DEBUG_EXPORT_AND_RAG_PLAN.md)**.

1. **Build index** (once per library, or after large changes):
   - MCP: `calibre_metadata_index_build(force_rebuild=False)` — starts in background; poll build status for progress.
   - Webapp: Semantic Search page → "Build index" or "Rebuild from scratch" — shows a **percentage progress bar** (gathering metadata, then embedding) until done.
2. **Search:** `calibre_metadata_search(query="...", top_k=10)` or use the Semantic Search page.

Index is stored under the library path in `lancedb_metadata/`. Uses fastembed (BAAI/bge-small-en-v1.5 by default). For large libraries (e.g. 10k books), build progress is written to `lancedb_metadata/.build_progress.json`; the webapp polls `GET /api/rag/metadata/build/status` to display current phase and percentage.

## Full-text search with phrase locations

`search_fulltext` supports **`resolve_locations=True`**. For each matching `books_text` row it returns:

- **`char_offset` / `char_end`** in Calibre’s `searchable_text` when the query matches literally (stem-only matches may omit offsets).
- **PDF:** `page_1based`, `page_0based`, `match_rect` via PyMuPDF.
- **EPUB:** `epub_href`, `epub_item_order` (first HTML document whose text contains the phrase).
- **`calibre_viewer`:** hints for Calibre’s **`ebook-viewer --open-at search:…`** (runs Find after open; see [ebook-viewer manual](https://manual.calibre-ebook.com/generated/en/ebook-viewer.html)).
- **PDF:** optional **`manage_viewer_get_page`** (`operation`, `book_id`, `file_path`, `page_number`) for `manage_viewer`.

Dependencies: `ebooklib`, `pymupdf` (declared in `pyproject.toml`).

## Full-text RAG design (longer-term)

Design notes for a unified `book_chunks` schema and optional `lancedb_fulltext` layout are in **docs/FULL_TEXT_RAG_DESIGN.md**. Partial implementation already exists via FTS-backed `rag_index_build`, portmanteau tables, and DeepIngestor; consolidation remains optional.

## HTTP transport: search and chat

When the server runs with **`--http`**, optional endpoints include semantic search proxy and **LLM chat** proxy (`LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_API_KEY`) — see `transport.py` and the webapp backend `llm` router for parity.

## See also

- [PROMPTS.md](./PROMPTS.md) — MCP prompt names × tools  
- [COOKBOOK.md](./COOKBOOK.md) — recipes (lane picker, chains)  
- [CALIBRE_DEBUG_EXPORT_AND_RAG_PLAN.md](./CALIBRE_DEBUG_EXPORT_AND_RAG_PLAN.md) — `calibre-debug` JSON export, LanceDB alignment, implementation phases  
- Bundled skill: `skill://calibre-expert/SKILL.md`
