# Calibre-MCP: FastMCP 3.1, Sampling, Skills, Prompts, and Metadata RAG

**Status: Implemented.** This plan has been carried out. See README and docs/AGENTIC_AND_RAG.md for usage.

Original plan to bring calibre-mcp up to FastMCP 3.1 standard with sampling/agentic workflows, skills and prompts, and LanceDB-based RAG over Calibre metadata (with preparation for full-book text RAG).

---

## 1. Current state (brief)

- **FastMCP**: 2.14.4+; 21 portmanteau tools; prompts registered via `calibre_mcp.prompts`.
- **Data**: Direct SQLite access to Calibre `metadata.db`; optional RAG with chromadb + fastembed in `[rag]` extra.
- **Gaps**: No FastMCP 3.x; no LanceDB; no formal “skills” layer; RAG not wired to metadata.db; no path yet for full-text RAG.

---

## 2. FastMCP 3.1 upgrade

| Task | Details |
|------|--------|
| **Bump dependency** | `pyproject.toml`: `fastmcp>=3.1.0` (replace `>=2.14.5`). |
| **API compatibility** | Review 3.x changelog: any renames (e.g. `Context`), new required kwargs, or deprecated APIs; update server and tools. |
| **Transforms (optional)** | Consider `SearchTools` for large tool catalog; optionally `CodeMode` for agentic discovery. Add only if useful after 3.1 runs. |
| **Lifespan / startup** | Align with 3.1 lifespan patterns if they changed; keep stdio binary mode and logging suppression for MCP. |

**Outcome**: Server runs on FastMCP 3.1 with no regressions; optional transforms documented for later.

---

## 3. Sampling and agentic workflow

| Task | Details |
|------|--------|
| **Dialogic returns** | Ensure tool handlers return natural-language summaries plus structured data (already in place; verify with 3.1). |
| **Sampling (SEP-1577)** | Confirm tools are callable in sampling/agentic flows (no side effects that break multi-step calls); document “agentic use” in tool docstrings. |
| **Instructions** | Update `FastMCP(..., instructions=...)` to mention 3.1, sampling, and agentic use (e.g. “Supports sampling and multi-step agentic workflows”). |
| **Docs** | Short “Agentic workflow” section in README: how an agent can chain tools (search → filter → recommend → open). |

**Outcome**: Calibre-MCP is clearly documented and safe for sampling and agentic workflows.

---

## 4. Skills and prompts

| Task | Details |
|------|--------|
| **Prompts** | Keep and extend `calibre_mcp.prompts`: ensure all prompts are registered with 3.1 API; add any new prompts for RAG (“Semantic search over my library”, “Find books like this one”). |
| **Skills layer** | Introduce a “skills” concept: either (a) a small `skills/` dir with YAML + Markdown (name, description, steps) for “how to use Calibre-MCP” (e.g. “Library health”, “Reading recommendations”), or (b) prompts that explicitly invoke tool sequences. Prefer (a) for reusability and alignment with Claude Skills / central docs. |
| **Skill content** | Each skill: short description, list of tools/steps, optional example prompts. Expose via MCP prompts or a single `calibre_mcp_guide` prompt that references skills. |
| **Registration** | Register skills as prompts or as a resource so the client can discover “recommended workflows”. |

**Outcome**: Rich prompts plus a small set of named skills for common workflows (recommendations, health, discovery, metadata cleanup).

---

## 5. RAG with LanceDB over metadata.db

| Task | Details |
|------|--------|
| **Dependencies** | Add core: `lancedb>=0.17.0`, `fastembed>=0.4.0`. Move from optional `[rag]` chromadb to required (or optional) LanceDB. |
| **Schema (metadata only)** | Define a “book metadata” table in LanceDB: e.g. `book_id`, `title`, `authors` (concat), `tags` (concat), `comments` (snippet), `series`, `publisher`, `language`, `text` (single searchable blob: title + authors + tags + comments + series). One row per book. |
| **Ingestion from metadata.db** | Script/module: connect to Calibre `metadata.db` (SQLite), read `books`, `authors`, `series`, `tags`, `comments`, etc.; build the `text` field and optional structured fields; embed `text` with fastembed; write into LanceDB. |
| **Index location** | LanceDB table under library path or a fixed dir (e.g. `~/.calibre-mcp/lancedb` or next to `metadata.db`). Config flag for path. |
| **RAG tool(s)** | New tool(s), e.g. `calibre_semantic_search(query, library?, top_k)` that: embed query, search LanceDB, return book ids + snippets; optionally resolve ids to full metadata from SQLite. |
| **Sync / refresh** | On library change or on demand: re-run ingestion for changed books (or full refresh); keep LanceDB in sync with metadata.db. |

**Outcome**: Semantic search over Calibre metadata (title, authors, tags, comments, series) via LanceDB + fastembed, backed by metadata.db.

---

## 6. Preparation for full-book text RAG (no implementation yet)

| Task | Details |
|------|--------|
| **Design doc** | Add `docs/FULL_TEXT_RAG_DESIGN.md`: scope (EPUB/PDF), chunking (by section/paragraph, max tokens), storage (separate LanceDB table or namespace), embedding model, and how it will plug into existing RAG tool or a new “full-text search” tool. |
| **Schema placeholder** | In LanceDB design, reserve a future table or schema (e.g. `book_chunks`) and document fields: `book_id`, `format`, `chunk_index`, `text`, `embedding`, metadata (title, author) for filtering. |
| **Dependencies note** | Document future need for extraction (e.g. PyMuPDF, ebooklib) and any tokenization; no new deps in this phase. |

**Outcome**: Clear, implementable plan for full-book RAG when you’re ready; no code yet.

---

## 7. Implementation order

1. **FastMCP 3.1** – Bump, fix API, test all tools and prompts.
2. **Sampling / agentic** – Docs and instructions; no tool signature changes unless 3.1 requires.
3. **LanceDB + metadata RAG** – Dependencies, schema, ingestion from metadata.db, RAG tool(s), sync strategy.
4. **Skills** – Define skill format and 3–5 initial skills; register as prompts or guide.
5. **Prompts** – Add RAG-related prompts; tidy for 3.1.
6. **Full-text RAG design** – Write `FULL_TEXT_RAG_DESIGN.md` and schema placeholder only.

---

## 8. Files to touch (checklist)

- `pyproject.toml` – fastmcp>=3.1.0; lancedb, fastembed; optional [rag] cleanup.
- `src/calibre_mcp/server.py` – 3.1 API, instructions, optional transforms.
- `src/calibre_mcp/prompts.py` – 3.1 prompt API; new RAG prompts.
- New: `src/calibre_mcp/rag/` (or `src/calibre_mcp/lancedb_rag/`) – schema, ingestion from metadata.db, search API.
- New: `src/calibre_mcp/tools/rag_tools.py` (or extend portmanteau) – `calibre_semantic_search` (and optionally “find similar”).
- New: `skills/` – 3–5 skill YAML+Markdown files.
- New: `docs/FULL_TEXT_RAG_DESIGN.md` – design only.
- `README.md` – Agentic workflow section; RAG and skills mentioned.

---

## 9. Success criteria

- Server runs on FastMCP 3.1 with all existing tools and prompts.
- At least one RAG tool performs semantic search over metadata from metadata.db via LanceDB.
- Skills and prompts are discoverable and support “what should I read”, “library health”, “semantic search”.
- Design doc exists for full-book text RAG; no full-text implementation in this phase.
