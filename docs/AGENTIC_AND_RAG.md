# Agentic Workflows and RAG

## Agentic workflows (FastMCP 3.1)

CalibreMCP supports **sampling** and **agentic** tool use: an MCP client (e.g. Claude Desktop) can chain multiple tools in one flow. Each tool returns `success`, `message`, and structured data so the next step can be chosen automatically.

**Typical flow:** List libraries → switch library → search (query_books or calibre_metadata_search) → open book or show metadata.

**Use in Chat:** Ask e.g. "Open a random unread science fiction book" or "Find programming books about Python and recommend one." The model will call the tools in sequence.

See **Skills** (webapp Skills page or `skills/` in repo) and the **calibre_mcp_guide** prompt for recommended workflows.

## Metadata RAG (LanceDB)

**Semantic search over book metadata** (title, authors, tags, comments, series) without indexing full book text.

1. **Build index** (once per library, or after large changes):
   - MCP: `calibre_metadata_index_build(force_rebuild=False)` — starts in background; poll build status for progress.
   - Webapp: Semantic Search page → "Build index" or "Rebuild from scratch" — shows a **percentage progress bar** (gathering metadata, then embedding) until done.
2. **Search:** `calibre_metadata_search(query="...", top_k=10)` or use the Semantic Search page.

Index is stored under the library path in `lancedb_metadata/`. Uses fastembed (BAAI/bge-small-en-v1.5 by default). For large libraries (e.g. 10k books), build progress is written to `lancedb_metadata/.build_progress.json`; the webapp polls `GET /api/rag/metadata/build/status` to display current phase and percentage.

## Full-text RAG (future)

Design and schema for full-book text RAG (EPUB/PDF chunking, separate LanceDB table) are in **docs/FULL_TEXT_RAG_DESIGN.md**. Not implemented yet; current content RAG uses existing `rag_index_build` / `rag_retrieve` and Calibre FTS where available.
