# About AI Workflows

calibre-mcp supports **agentic AI workflows** — chains of tool calls where an LLM decides the next step based on each result. This enables zero-training natural-language library interaction.

## Agentic orchestration (SEP-1577)

FastMCP 3.2 injects a sampling context (`ctx.sample()`) that lets the server ask the client LLM to make decisions mid-tool-call. This is used for:

- **Natural language to SQL** — Convert "unread Banks novels from the 90s" into a structured query
- **Query disambiguation** — If a search is ambiguous, ask the LLM to clarify
- **Result ranking** — Rank search results by relevance to a conversational query

```
User: "Find me something like The Culture series but darker"
  ↓
calibre_metadata_search("dark sci-fi similar to The Culture")
  ↓ returns 15 candidates
LLM samples results → ranks by "darkness" score
  ↓ returns top 3
Claude shows: "Top match: Blindsight by Peter Watts"
```

## RAG (Retrieval-Augmented Generation)

calibre-mcp has **two RAG pipelines**, both using LanceDB with fastembed (BAAI/bge-small-en-v1.5).

### Metadata RAG

Semantic search over **title, authors, tags, comments, and series** — not book body text.

| Step | Tool | What happens |
|------|------|-------------|
| Build | `calibre_metadata_index_build()` | Embeds all metadata into LanceDB (`lancedb_metadata/`) |
| Search | `calibre_metadata_search(query="...")` | Returns top-k books by semantic similarity |
| Export | `calibre_metadata_export_json()` | Full library metadata as JSON |

### Full-text chunk RAG

Semantic search over **chunks of book content** extracted from Calibre's FTS index.

| Step | Tool | What happens |
|------|------|-------------|
| Build | `rag_index_build(library="...")` | Chunks FTS text, embeds into LanceDB (`{library}/lancedb`) |
| Search | `rag_retrieve(query="...", top_k=10)` | Returns relevant text chunks with book context |
| Portmanteau | `calibre_rag(query="...")` | Unified RAG via DeepIngestor pipeline |

## FTS (Full-Text Search) with phrase locations

Calibre's built-in FTS5 index is the fastest way to find exact phrases. `search_fulltext(resolve_locations=True)` returns:

- Character offsets in Calibre's `searchable_text`
- PDF pages (via PyMuPDF) and screen rectangles
- EPUB spine references (`epub_href`, `epub_item_order`)
- Calibre `ebook-viewer --open-at search:...` hints

**Recommendation:** Use FTS for quoted lines and exact phrases. Use RAG for meaning-based queries ("books about post-human identity"). Run both when unsure.

## Skills

Pre-built reusable workflows that Claude can invoke:

| Skill | Purpose |
|-------|---------|
| `reading_recommendations` | Generate personalized book suggestions based on reading history |
| `library_health` | Analyze library for duplicates, missing metadata, series gaps |
| `semantic_search` | Multi-step semantic search with result refinement |
| `agentic_workflow` | Guide for chaining tools in the correct sequence |
| `calibre-expert` | Bundled expertise skill shipped with the MCP server |

Skills are MCP resources (`skill://calibre-expert/SKILL.md`) registered at server startup and loadable by any MCP client.

## Prompts

Registered MCP prompts provide ready-to-use conversation templates:

- `calibre_mcp_guide` — System prompt that teaches the AI how to use calibre-mcp tools
- 24 prompt assets in `assets/prompts/` — `author_analysis.md`, `book_discovery.md`, `library_health.md`, `reading_recommendations.md`, etc.

Full prompt catalog: [PROMPTS.md](PROMPTS.md)

## Webapp AI chat

The webapp frontend includes an AI chat interface with support for:
- **Ollama** (local, default) — llama3, mistral, etc.
- **LM Studio** — any GGUF model
- **OpenAI-compatible** APIs — cloud or local (vLLM, tabbyAPI)

The chat has access to the full tool surface and can execute the same agentic workflows as Claude Desktop.

## RAG + Agentic = The full picture

```
User query
  ↓
1. Agentic sampling → disambiguate / plan query
2. Metadata RAG → find candidate books by meaning
3. FTS → verify exact phrases if needed
4. Chunk RAG → retrieve relevant passages
5. Tool chaining → open book, show metadata, export results
  ↓
Natural language answer + structured actions
```

Full workflow docs: [AGENTIC_AND_RAG.md](AGENTIC_AND_RAG.md) | RAG design: [FULL_TEXT_RAG_DESIGN.md](FULL_TEXT_RAG_DESIGN.md)

> **Back:** [About MCP Tools](ABOUT_MCP_TOOLS.md) | **Start:** [README](../README.md)
