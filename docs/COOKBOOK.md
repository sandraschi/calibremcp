# CalibreMCP cookbook

Goal-oriented recipes. Parameter-level SQL and search construction also live in [SEARCH_QUERY_EXAMPLES.md](./SEARCH_QUERY_EXAMPLES.md). Architecture for RAG/FTS is in [AGENTIC_AND_RAG.md](./AGENTIC_AND_RAG.md). MCP prompt names and tool pairings are in [PROMPTS.md](./PROMPTS.md).

**Why Calibre (and thus CalibreMCP) at all:** If you have **very large** collections—**many thousands** of files, up to on the order of **100,000** EPUBs, PDFs, CBZ/CBR comics, manga, etc.—**Calibre** is the standard way to **organize, tag, search, and read** them **locally**, and to **expose** the same library via Calibre’s **Content server** (browser/OPDS on the LAN or beyond). CalibreMCP layers **agentic search and workflows** on top of that catalog (`metadata.db` + files).

---

## 1. “I remember a phrase from the book” (FTS first)

1. Use **`search_fulltext`** with the phrase (or keywords).  
2. If you need the exact place: set **`resolve_locations=True`** for PDF page / EPUB spine / Calibre viewer `ebook-viewer --open-at search:…` hints.  
3. Open the book with **`manage_viewer`** if the user wants to read immediately.

**Why not RAG first:** phrase and rare-word matches are what Calibre’s FTS index is for; metadata RAG does not search the full body.

---

## 2. “Books about X” by meaning (metadata)

1. Ensure index: **`calibre_metadata_index_build`** (webapp Semantic Search page can build/rebuild).  
2. **`calibre_metadata_search(query="…", top_k=…)`** over title, authors, tags, comments, series.  
3. Optional: open a result with **`manage_viewer`**.

---

## 3. “What happens in chapter Y / this theme in the text” (chunk RAG)

1. Build chunk index: **`rag_index_build`** (FTS-backed chunks → LanceDB `books_rag` under the library).  
2. **`rag_retrieve`** (or portmanteau **`calibre_rag`** per your deployment) for semantic passage retrieval.  
3. Combine with **`search_fulltext`** when the user gives exact wording.

See [AGENTIC_AND_RAG.md](./AGENTIC_AND_RAG.md) for `lancedb*` layout and DeepIngestor vs FTS chunk paths.

---

## 4. Open or find a book fast (structured query)

Use **`query_books`** with **`operation="search"`** — title, author, tag, text, date ranges, rating, format, `auto_open=True` for a unique hit. Natural-language phrasing is mapped by the client; examples in the root [README.md](../README.md) “Usage Examples”.

---

## 5. Multi-library workflow

1. **`manage_libraries(operation="list")`**  
2. **`manage_libraries(operation="switch", library_id=…)`**  
3. Run search / RAG / viewer as above.

---

## 6. Library health and duplicates (maintenance)

1. Prompts **`library_health`**, **`duplicate_detection`**, **`metadata_cleanup`** (see [PROMPTS.md](./PROMPTS.md)) set the intent.  
2. **`manage_analysis`** and **`manage_library_operations`** (per docstrings) for duplicates, stats, and cleanup actions your deployment exposes.

---

## 7. One-shot natural language (“organize my IT books and flag outdated”)

- With sampling: **`agentic_library_workflow(workflow_prompt="…")`**  
- Without sampling: decompose into steps 4–6 manually; use **`calibre_mcp_guide`** prompt or **`skill://calibre-expert/SKILL.md`** for heuristics.

---

## 8. HTTP-only helpers

With **`--http`**, optional **`/api/v1/chat`** proxies to a local or cloud LLM (`LLM_*` env) — same semantics as the webapp backend; see `transport.py` and [AGENTIC_AND_RAG.md](./AGENTIC_AND_RAG.md).

---

## Quick lane picker

| User goal | Start here |
|-----------|----------------|
| Exact quote / line | `search_fulltext` (+ `resolve_locations`) |
| Topic by title/tags/comments | `calibre_metadata_search` |
| Theme inside the text (paraphrase) | `rag_index_build` → `rag_retrieve` / `calibre_rag` |
| Known title/author | `query_books` |
