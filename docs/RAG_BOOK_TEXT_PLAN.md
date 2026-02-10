# Plan: Heavy RAG Over Book Text (FOSS)

**Goal:** Enable semantic search over book content and use retrieved chunks to augment LLM answers (RAG). All components FOSS.

**Status:** Plan only. Not yet implemented.

**Example query:** "Book in our collection where somebody was stabbed with an icicle" — the point of the icicle (or ice bullet) trope is that the weapon *melts and vanishes* (no evidence). Semantic search finds that trope; keyword search for "ice pick" would miss it (different trope: weapon stays).

---

## 1. Pipeline Overview

```
[Book text] → [Chunk] → [Embed] → [Vector store] → [Retrieve] → [LLM]
     ↑            ↑          ↑            ↑              ↑
  Source      Split     Encode      Persist       Query + top-k
```

- **Source:** Reuse Calibre `full-text-search.db` → `books_text.searchable_text` (already extracted per book/format). Text is "precooked" by Calibre, so we avoid re-extracting from EPUB/PDF and get a single, consistent index. Optional: re-extract only if you need finer chunk boundaries (e.g. by chapter).
- **Chunk:** Split into overlapping segments (e.g. 512 tokens, 64 overlap); keep metadata (book_id, format, position).
- **Embed:** Encode each chunk with a local embedding model.
- **Store:** Vector DB keyed by (library_id, optional scope) for fast similarity search.
- **Retrieve:** Embed user query, run similarity search, optional rerank, return top-k chunks + metadata.
- **LLM:** Existing chat API; add a "RAG context" path that injects retrieved chunks into the system/user message.

---

## 2. SOTA FOSS Tools (all FOSS)

### 2.1 Embeddings

| Tool / Model | License | Notes |
|--------------|---------|--------|
| **sentence-transformers** (Python) | Apache 2.0 | All-MiniLM, BGE, E5; CPU/GPU, easy to use. |
| **FastEmbed** (Rust/Python) | MIT | Lightweight, fast CPU; small models (e.g. `BAAI/bge-small-en-v1.5`). |
| **Ollama** (nomic-embed, mxbai-embed) | MIT | Reuse existing Ollama; no extra Python embedding stack. |
| **BGE** (BAAI/bge-*) | MIT | SOTA quality; use via sentence-transformers or FastEmbed. |

**Recommendation:** Start with **Ollama + nomic-embed** (no new deps; same stack as chat). Fallback: **FastEmbed** or **sentence-transformers** for headless/API-only.

### 2.2 Vector Stores

| Tool | License | Notes |
|------|---------|--------|
| **Chroma** | Apache 2.0 | Embedded, file-based, simple API; good for single-process. |
| **LanceDB** | Apache 2.0 | Embedded, columnar, optional remote; good for large scale. |
| **Qdrant** | Apache 2.0 | Server; best if you want a dedicated vector service. |
| **pgvector** (PostgreSQL) | PostgreSQL License | Use if you already run Postgres. |
| **FAISS** | MIT (Facebook) | In-memory; no built-in persistence (need to save/load index). |
| **sqlite-vec** | MIT | SQLite extension; keeps everything in one DB. |

**Recommendation:** **Chroma** (embedded, minimal ops) or **LanceDB** (if you expect very large libraries). Both FOSS, no server required.

### 2.3 RAG / Orchestration (optional)

| Tool | License | Notes |
|------|---------|--------|
| **LlamaIndex** | MIT | RAG-focused; loaders, chunking, vector stores, query engines. |
| **Haystack** | Apache 2.0 | Pipelines, document stores, FOSS. |
| **LangChain** | MIT | Heavy; use only if you need its ecosystem. |
| **DIY** | - | Minimal: chunk → embed → store in Chroma; query → embed → search → format context → call existing chat. |

**Recommendation:** **DIY** first (chunk + embed + Chroma + existing chat). Add LlamaIndex later if you want advanced retrieval (hybrid, reranking, etc.).

### 2.4 Reranking (optional, improves quality)

| Tool | License | Notes |
|------|---------|--------|
| **BGE reranker** (BAAI) | MIT | Cross-encoder; use after vector search to rerank top-N. |
| **Cohere rerank** | API (not FOSS) | Skip if strict FOSS. |
| **Jina reranker** | Apache 2.0 | FOSS; can run self-hosted. |

**Recommendation:** Optional phase 2; start without reranker.

---

## 3. What We Have vs What We Need

| Component | Have | Need |
|-----------|------|------|
| Book text | Calibre FTS `books_text.searchable_text` (and `search_fulltext` tool) | Chunking + metadata (book_id, format, start/end) |
| Embeddings | - | Ollama embed and/or FastEmbed/sentence-transformers |
| Vector store | - | Chroma (or LanceDB) + index per library (or per library+scope) |
| Retrieval API | - | Endpoint: query → top-k chunks + book_id, snippet, score |
| Chat | Webapp LLM chat (Ollama/LM Studio) | Optional “Ask library” mode that runs retrieval then chat with context |

---

## 4. Implementation Plan (phased)

### Phase 1: Indexing and retrieval (backend only)

1. **Chunking**
   - Read from `full-text-search.db` → `books_text` (id, book, format, searchable_text).
   - Chunk strategy: by paragraph or fixed size (e.g. 512 tokens, 64 overlap); store book_id, format, chunk_index, start/end.
   - Output: list of `{ text, book_id, format, chunk_index }`.

2. **Embedding**
   - Option A: Ollama embedding API (e.g. `nomic-embed-text`) if available.
   - Option B: FastEmbed or sentence-transformers in a small Python service/script.
   - Batch embed chunks (e.g. 32–64 at a time), write vectors + metadata to store.

3. **Vector store**
   - Create Chroma collection per library (e.g. `calibre_rag_{library_id}`).
   - Documents: chunk text; metadata: book_id, format, chunk_index (and optionally title/author from metadata.db).
   - Persist Chroma DB under a known path (e.g. `{library_dir}/.calibre-rag/` or a configurable path).

4. **Indexing job**
   - Trigger: on-demand (e.g. “Build RAG index” in UI or MCP tool) and/or when library is switched and index missing.
   - Steps: open FTS DB → chunk all books_text → embed → upsert into Chroma. Progress logging; resume by book_id if interrupted.

5. **Retrieval API**
   - New backend endpoint, e.g. `POST /api/rag/retrieve`: body `{ query, top_k, library_id? }`.
   - Embed query, search Chroma, return `{ chunks: [{ text, book_id, format, chunk_index, score?, title?, author? }] }`.
   - Optional: filter by book_ids or format.

### Phase 2: Chat integration (“Ask the library”)

6. **RAG-aware chat**
   - New endpoint or flag, e.g. `POST /api/llm/chat-rag`: `{ messages, model, query_for_retrieval?, top_k? }`.
   - If `query_for_retrieval` is set: run retrieval, build context string from chunks, prepend to system or first user message.
   - Otherwise same as current chat. Reuse existing LLM (Ollama/LM Studio) and streaming.

7. **Webapp**
   - “Ask the library” input: free-text question; backend runs retrieve + chat with that question as retrieval query and as user message.
   - Show which books/chunks were used (e.g. “Based on: Book A (ch. 3), Book B (ch. 1)”).

### Phase 3: MCP and polish

8. **MCP tools**
   - `rag_index_build(library_id?, force?)` – build/rebuild RAG index.
   - `rag_retrieve(query, top_k, book_ids?)` – return chunks for a query (and optionally restrict to books).
   - Optional: `rag_chat(query, model?, top_k?)` – one-shot “ask library” that returns answer + sources.

9. **Reranking (optional)**
   - After vector search, rerank top-20 with BGE reranker (or Jina), return top-k. Improves answer quality.

10. **Config and docs**
    - Config: RAG index path, embedding model (Ollama vs FastEmbed), default top_k, optional reranker on/off.
    - Docs: how to enable RAG, how to run indexing, which models to pull (e.g. `nomic-embed-text`).

---

## 5. Dependencies (all FOSS)

- **chromadb** – vector store (Apache 2.0).
- **Embeddings:** either use existing **Ollama** (nomic-embed-text) or add **fastembed** (MIT) or **sentence-transformers** (Apache 2.0).
- No LangChain/LlamaIndex required for Phase 1–2; add later if needed.

---

## 6. File / Layout Sketch

- `src/calibre_mcp/rag/` (or `webapp/backend/app/rag/` if webapp-only first):
  - `chunking.py` – chunk logic from `books_text`.
  - `embedding.py` – Ollama or FastEmbed wrapper.
  - `store.py` – Chroma create/upsert/query.
  - `indexer.py` – full index build (chunk → embed → store).
  - `retriever.py` – query → embed → search → return chunks.
- Config: `CALIBRE_RAG_INDEX_PATH`, `CALIBRE_RAG_EMBED_MODEL` (e.g. `nomic-embed-text` or `fastembed/bge-small`).

---

## 7. Summary

| Step | Action | SOTA FOSS choice |
|------|--------|-------------------|
| 1 | Get book text | Calibre FTS `books_text` |
| 2 | Chunk | DIY (paragraph or token window + overlap) |
| 3 | Embed | Ollama (nomic-embed) or FastEmbed / sentence-transformers |
| 4 | Store | Chroma (or LanceDB) |
| 5 | Retrieve | Chroma similarity search; optional BGE reranker |
| 6 | LLM | Existing chat + inject retrieved context |
| 7 | MCP | Tools: index build, retrieve, optional rag_chat |

All components above are FOSS. Easiest start: **Ollama nomic-embed + Chroma + DIY chunking and retrieval**, then wire retrieval into the existing LLM chat and add “Ask the library” in the webapp.
