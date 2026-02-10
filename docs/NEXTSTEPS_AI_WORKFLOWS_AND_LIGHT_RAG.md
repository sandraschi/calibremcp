# Next Steps: AI Workflows and Light RAG

**Timestamp**: 2026-02-10
**Status**: Planning
**Prerequisites**: FastMCP 2.14.4 SOTA complete (sampling, dialogic returns)

---

## Overview

Extend CalibreMCP with four AI workflow enhancements plus a light RAG layer. All leverage existing `ctx.sample()` and portmanteau tool infrastructure.

---

## 1. Intelligent Query Parsing via Sampling

**Goal**: Replace rule-based `intelligent_query_parsing` with `ctx.sample()` for ambiguous natural-language queries.

**Current**: `agentic_workflow.py` uses pattern matching (author, tag, time, title, genre) as fallback.

**Target**:
- Use `ctx.sample()` with a small schema/tool to parse queries like:
  - "recent sci-fi by women authors"
  - "books I added last month that I haven't read"
  - "something similar to sapiens but shorter"
- Return structured params: `{author?, tag?, pubdate?, added_after?, title?, limit?}`
- Fallback to existing rule-based parser when sampling unavailable

**Tasks**:
- [ ] Add `parse_query_sampling(ctx, query)` that calls `ctx.sample(messages=..., result_type=QueryParams)`
- [ ] Wire into `query_books` / search flow when ctx available
- [ ] Keep `intelligent_query_parsing` as fallback

**Files**: `src/calibre_mcp/tools/agentic_workflow.py`, `src/calibre_mcp/tools/book_management/query_books.py`, shared query parsing

---

## 2. Recommendation / Exploration Tool

**Goal**: Sampling-driven "explore related" and "suggest next read" with reasoning.

**Current**: AI tools exist (`get_book_recommendations`, `recommendation_engine`) but may not use sampling.

**Target**:
- New or enhanced tool: `explore_books(query, context, limit)` using `ctx.sample()` with tools:
  - `search_books`, `get_book_details`, `get_tags`, `get_authors`
- LLM orchestrates: search similar books, compare metadata, return suggestions with short reasoning
- Output: list of books + reasoning per suggestion

**Tasks**:
- [ ] Design tool signature: `explore_related(book_id?, tags?, author?, query?, limit=5, ctx?)`
- [ ] Implement sampling flow: pass search/get tools, prompt for "find similar and explain why"
- [ ] Integrate with light RAG (item 6) for semantic similarity when available

**Files**: `src/calibre_mcp/tools/ai/recommendation_engine.py`, new or extended tool

---

## 3. Metadata Enhancement via Sampling

**Goal**: LLM suggests tags, summaries, or categorization from book metadata and optionally content.

**Current**: Manual metadata tools exist; no AI-assisted suggestion flow.

**Target**:
- Tool: `suggest_metadata(book_id, fields=["tags","summary","genre"], ctx?)`
- Sampling tools: `get_book_details`, `search_books` (for similar books' metadata)
- LLM returns suggested tags, short summary, or genre based on title/authors/description

**Tasks**:
- [ ] Add `suggest_metadata` tool with ctx.sample()
- [ ] Define structured output: `{suggested_tags: list[str], suggested_summary?: str, suggested_genre?: str, confidence: float}`
- [ ] Optionally use light RAG for "similar books' tags" as context

**Files**: `src/calibre_mcp/tools/metadata/`, `src/calibre_mcp/tools/ai/`

---

## 4. Library Analysis / Reports

**Goal**: "Analyze my library and summarize" / "Identify gaps or themes" via sampling.

**Target**:
- Tool: `analyze_library(prompt, focus?, ctx?)` e.g. "What themes run through my library?" or "What gaps do I have in history books?"
- Sampling tools: `get_library_stats`, `list_books`, `get_tags`, `get_authors`, `search_books`
- LLM orchestrates multiple reads and returns structured report: themes, gaps, recommendations

**Tasks**:
- [ ] Add `analyze_library` tool with ctx.sample()
- [ ] Prompt engineering: instruct LLM to call stats, list, search, then synthesize
- [ ] Optional: structured output schema for themes/gaps/recommendations

**Files**: `src/calibre_mcp/tools/analysis/`, new `analyze_library.py` or extend `manage_analysis`

---

## 5. Light RAG Layer

**Goal**: Embed book metadata (title, authors, tags, description/comment) for semantic search. No full-text content embedding initially.

**Scope**:
- **Embed**: title + authors + tags + comment/description per book
- **Store**: Local vector store (Chroma, Qdrant, or FAISS)
- **Use cases**:
  - Semantic "find similar books"
  - Recommendation/exploration (item 2)
  - Metadata suggestions (item 3)
  - Theme/cluster analysis (item 4)

**Tasks**:
- [ ] Choose embedding model: sentence-transformers (e.g. all-MiniLM-L6-v2) or OpenAI/Anthropic embeddings
- [ ] Choose vector store: Chroma (simple, local) or Qdrant; FAISS for minimal deps
- [ ] Add indexing: `index_library()` or background sync when library changes
- [ ] Add tool: `semantic_search(query, limit=10)` returning book IDs + scores
- [ ] Integrate with items 2, 3, 4 as optional enhancement

**Dependencies**:
- `sentence-transformers` or API client for embeddings
- `chromadb` or `qdrant-client` or `faiss-cpu`

**Files**:
- New: `src/calibre_mcp/rag/` (or `src/calibre_mcp/services/embedding_service.py`)
- New: `src/calibre_mcp/tools/rag/semantic_search.py` (or portmanteau tool)

---

## Implementation Order

1. **Light RAG** (foundation for 2, 3, 4)
2. **Intelligent Query Parsing** (standalone, high impact)
3. **Recommendation/Exploration** (uses RAG + sampling)
4. **Metadata Enhancement** (uses RAG + sampling)
5. **Library Analysis** (uses RAG + sampling)

---

## Reference

- FastMCP sampling: https://gofastmcp.com/v2/servers/sampling
- SEP-1577: https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1577
- CalibreMCP agentic workflow: `docs/adn-notes/SEP-1577-in-Calibre-MCP-Agentic-Library-Orchestration.md`
