# Calibre-debug metadata export and RAG alignment

**Status:** Implemented — script, env-driven comment cap, HTML stripping, MCP tool **`calibre_metadata_export_json`**, unit tests.

---

## LanceDB in calibre-mcp

| Lane | Location (under library folder) | Tools |
|------|----------------------------------|--------|
| **Metadata RAG** | `lancedb_metadata/` table `calibre_metadata` | `calibre_metadata_index_build`, `calibre_metadata_search` |
| **FTS chunk RAG** | `lancedb/` table `books_rag` | `rag_index_build`, `rag_retrieve` |
| **Portmanteau / Deep ingest** | `lancedb_calibre/` | `calibre_rag`, DeepIngestor |

See **[AGENTIC_AND_RAG.md](./AGENTIC_AND_RAG.md)** for the lane diagram. Fleet mirror: **mcp-central-docs** `projects/calibre-mcp/SEARCH_RAG_FTS.md`.

**Comments as RAG signal:** Metadata RAG embeds title, authors, series, tags, and **book comments**. Implementation: `rag/metadata_rag.py` (`_book_to_searchable_text`). HTML in comments is normalized with **`rag/text_utils.strip_html_for_embedding`** when **`CALIBRE_METADATA_STRIP_HTML`** is on (default).

### Environment variables (metadata RAG + JSON export)

| Variable | Default | Meaning |
|----------|---------|--------|
| **`CALIBRE_METADATA_COMMENT_MAX_CHARS`** | `20480` (20 KiB) | Max characters from each book’s Comments field in the **embedding text** (comments are not full book text). Clamped to `1..16777216` (16 MiB). Raise the env var if you need longer blurbs in the index. |
| **`CALIBRE_METADATA_STRIP_HTML`** | `1` | If `0`/`false`/`no`/`off`, keep raw HTML in comments for embeddings. |

After **bulk comment edits**, run **`calibre_metadata_index_build`** (or rebuild from the webapp) so LanceDB matches the library.

---

## Why `calibre-debug` for a JSON export

Calibre ships its **own Python** and internal modules (`calibre.library`, etc.). Run:

```text
calibre-debug -e path\to\export_metadata_for_rag.py -- --library "D:\path\to\Library" --output out.json
```

Use when you want Calibre’s **`new_api`** (same fields as the GUI), automation without the MCP server, or to compare with MCP’s SQL export.

---

## Three ways to get JSON

| Method | When to use |
|--------|-------------|
| **`calibre_metadata_export_json`** (MCP) | Server running; writes via `metadata.db`; default file `calibre_mcp_metadata_export.json` in the library folder. |
| **`scripts/export_metadata_for_rag.py`** + **`calibre-debug -e`** | Calibre’s embedded interpreter; dev checkout adds `src` to path so HTML strip matches **`text_utils`**. |
| External ingest | Pipe either JSON into your own LanceDB/Chroma pipeline (see cookbook note in **COOKBOOK.md**). |

---

## Implementation plan (completed)

### Phase A — Documentation and script

- [x] Lanes documented; **`scripts/export_metadata_for_rag.py`** with CLI.

### Phase B — Comment quality

- [x] **`CALIBRE_METADATA_COMMENT_MAX_CHARS`** + **`rag/text_utils.py`** (strip HTML, caps).
- [x] **`tests/unit/test_rag_text_utils.py`**.

### Phase C — MCP ergonomics

- [x] **`calibre_metadata_export_json`** in **`tools/rag/manage_rag.py`**.
- [x] Rebuild reminder in this doc + **AGENTIC_AND_RAG.md**.

### Phase D — External pipelines

- [x] Cookbook pointer (**COOKBOOK.md**).
- [x] Optional **Task Scheduler**: run `calibre-debug -e` on a schedule the same way as any `.py` (no special casing in-repo).

---

## See also

- [AGENTIC_AND_RAG.md](./AGENTIC_AND_RAG.md) — FTS vs RAG, `lancedb_*` layout  
- [CONTENT_SERVER.md](./CONTENT_SERVER.md) — when HTTP API is enough vs direct DB  
- **Fleet mirror:** `mcp-central-docs/projects/calibre-mcp/CALIBRE_DEBUG_EXPORT_AND_RAG_PLAN.md`
