# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.0] - 2026-04-18

### Industrialization & SOTA Hardening
- **Pydantic V2 Migration**: Completed mandatory upgrade from legacy `@validator` to `@field_validator(..., mode="after")` + `@classmethod` for all models. Standardized on `v2`-native validation patterns.
- **Ruff Linting Excellence**: Resolved over 100 manual linting violations (TRY400, B904, PTH, SIM, S110). Replaced silent `except: pass` with `contextlib.suppress`.
- **Backend Modernization**: Systematic migration from `os.path` to `pathlib.Path` in core service and server modules.
- **Structured Logging**: Standardized on `logger.exception` for diagnostic-rich error reporting across the MCP lifecycle.
- **Robustness**: Replaced deprecated `TimeoutError` aliases and established binary `stdio` hygiene for Windows compatibility.
- **Venv Repair**: Resolved environment corruption where site-packages were accidentally modified during bulk refactoring. Recreated `webapp/backend` venv with Python 3.12.9.

### Fixed
- **Query Tools Resilience**: Fixed major syntax and indentation errors in `book_tools.py` and `metadata_rag.py` introduced during automated industrialization.
- **Model Registration**: Fixed `PydanticUserError` runtime blockers in the book model registry.

## [1.7.0] - 2026-04-16

### Added

**`media_research_book` — Deep book research tool**

New MCP tool and REST endpoint `POST /api/rag/research/{book_id}`.

Given any book ID from your Calibre library, fetches and synthesises:
- Wikipedia article (book) — summary, plot, reception, adaptations, accolades
- Wikipedia article (author) — biography and bibliography context
- SF Encyclopedia — for SF/fantasy/space opera/cyberpunk tagged books
- TVTropes Literature page — for fiction (best-effort, graceful fallback)
- Anime News Network Encyclopedia — for manga/light novel/anime tagged books
- Open Library — for books with ISBN identifier

All sources fetched concurrently with per-source timeout and graceful failure.
Source routing is automatic based on Calibre tags/genres.

Local data combined into synthesis: your rating, series, personal notes from
`calibre_mcp_data.db`, and top RAG passages from content index if built.

Synthesised via LLM sampling into a structured markdown report with sections:
Overview, The Author, Plot & Content, Critical Reception, Themes & Tropes,
Adaptations & Related Media, If You Liked This, Your Library.

Requires sampling-capable MCP client (Claude Desktop / Cursor).

**Frontend: Research tab on RAG page**

Fourth tab on `/rag` page alongside Metadata / Passages / Synopsis.
- Book ID input with spoilers toggle
- Source attribution bar (green = fetched, grey = failed)
- Local data badges (rating stars, series, notes indicator, RAG passage count)
- Full report rendered in scrollable panel

**Spec documented at `docs/BOOK_RESEARCH_SPEC.md`**



### Added

**Calibre plugin — first working release**
- `calibre_plugin/` is now fully functional and tested. Install with `calibre-customize -b calibre_plugin` or from the pre-built ZIP.
- Extended metadata panel (`Ctrl+Shift+M`): First Published, Translator, personal notes — stored in `calibre_mcp_data.db`, shared with the MCP server. Works standalone with no webapp required.
- VL from Query: calls `/api/search`, retrieves book IDs, creates a Calibre saved search as a virtual library.
- Config dialog: server URL, DB path override.
- Full dev/test script at `scripts/calibre-plugin-test.ps1` with full Windows paths.
- Complete documentation at `calibre_plugin/README.md` and `docs/integrations/CALIBRE_INTEGRATION_GUIDE.md`.

**RAG API — new endpoints**
- `GET /api/rag/retrieve` — full-text passage retrieval via `rag_retrieve` (LanceDB content index)
- `POST /api/rag/content/build` — build/rebuild the content index (separate from metadata index)
- `POST /api/rag/search` — combined portmanteau search via `calibre_rag`
- `POST /api/rag/synopsis/{book_id}` — RAG-synthesised spoiler-aware synopsis via `media_synopsis`
- `POST /api/rag/critical-reception/{book_id}` — critical reception synthesis
- `POST /api/rag/deep-research` — cross-book thematic analysis
- `POST /api/rag/metadata/export` — JSON metadata export for external pipelines

**Series API — new endpoints**
- `GET /api/series/analysis?series_name=` — reading order + owned/missing breakdown for a named series
- `GET /api/series/completion` — library-wide series completion report

**Webapp frontend — RAG page overhaul**
- Three-tab interface: Metadata search / Passage retrieval / Synopsis generator
- Separate build controls for metadata index (fast) and content index (slow/large libraries)
- Passage results with `<mark>` snippet highlighting
- Synopsis panel with spoilers toggle

**Webapp frontend — Series Analysis page**
- New page at `/series/analysis`
- Named series lookup with progress bar (owned/total ratio)
- Reading order list with Owned/Missing badges, links to book pages
- Accessible from sidebar and from the Series list page header

### Fixed
- All stale port 13000 references corrected to 10720 throughout plugin, webapp backend config, and MCP client.
- CORS origins corrected from port 13001 to 10721.
- `config_widget.py` fallback URL was writing 13000 back on empty save — fixed.
- Archived stale `CALIBRE_PLUGIN_IMPLEMENTATION_NOTES.md` (January 2025 checklist, superseded).
- Replaced 22KB boilerplate `CALIBRE_INTEGRATION_GUIDE.md` with accurate architecture doc.


### Added
- **SOTA 2026 Industrialization**: Fleet-wide modernization for April 2026 standards.
- **FastMCP 3.2.0 Parity**: Full integration of native prompts, skills, and sampling features.
- **Biome Integration**: High-fidelity linting and formatting toolchain for the web dashboard.
- **Universal Connect Pattern**: Support for multiple simultaneous clients via stdio and HTTP transports.
- **Concurrency Safety**: Thread-safe database operations preventing race conditions in multi-client environments.

### Changed
- **Codebase Hardening**: Purged all executable `print` statements to ensure strict JSON-RPC protocol compliance.
- **Ruff Standard**: Aligned with 120-character line length and expanded SOTA linting rules. 
- **Webapp Performance**: Optimized Next.js dashboard with adjacent port assignments (10722).

### Fixed
- **FastAPI Routing Error**: Removed legacy decorators to align with FastMCP 3.2+ architecture.
- **Database Concurrency**: Implemented thread-safe operations with row-level locking.
### Added
- **Import Hub Stabilization**: Comprehensive hardening of automated book ingestion sources.
- **Anna's Archive UX Optimization**:
    - Automatic detection of interactive "landing pages" (CAPTCHAs and timers).
    - Improved mirror management with support for custom mirrors via `ANNAS_MIRRORS` environment variable.
    - Specialized error code `MANUAL_INTERACTION_REQUIRED` for mirrors requiring browser fallback.
- **arXiv Reliability**:
    - Exponential backoff retry logic (5 attempts) to mitigate `HTTP 429` rate limiting.
    - Custom User-Agent string to comply with arXiv API usage guidelines.
- **Global Import Settings**:
    - Persistent UI settings for target library selection.
    - Automated tag injection (e.g., "automated-import") and series assignment for incoming books.
- **Documentation**: New [DOWNLOAD_SITES.md](docs/DOWNLOAD_SITES.md) guide detailing mirror configurations and technical requirements.

## [1.4.0] - 2026-03-27
### Added
- **MCPB — mcp-central-docs alignment:** `mcpb/manifest.json` v0.2 with `python -m calibre_mcp`, `tools` as `{name, description}` list, `user_config`, compatibility.
- **docs/PROMPTS.md** — MCP `@mcp.prompt()` catalog with suggested tool pairings.
- **docs/COOKBOOK.md** — Goal-oriented recipes (FTS vs RAG lanes, workflows).
- **skill://calibre-expert** — Bundled expert skill for library management.
- **Self-contained LanceDB vector store** — Decoupled RAG logic for easier maintenance.
- **Metadata RAG build progress** — Background build with percentage gauge and status polling for large libraries.
### Changed
- **GitHub Actions:** Unified `ci.yml` and released-based `ci-cd.yml` with PyPI publishing.
- **Webapp startup SOTA** — Port reservoir 10720/10721; `start.ps1` with zombie clear.
- **FastMCP 3.1 Tool Preloading** — Fixed issues with module resolution on Windows.
### Fixed
- **Book isbn/lccn AttributeError** — Fixed ORM mapping for identifiers.
- **Webapp layout** — Standardized 3-column layout and improved topbar accessibility.

## [1.3.0] - 2026-02-26
### Added
- **Neural Media RAG Portmanteau**: Unified semantic search and Q&A tool powered by LanceDB.
- **DeepIngestor**: Full-text parsing and semantic chunking for high-density embeddings.
- **Agentic Synthesis API**: Expanded webapp backend with search/chat endpoints for central docs integration.

## [1.2.0] - 2026-02-04
### Added
- **MCPB Packaging**: Support for bundle-based installation.
### Fixed
- **Startup Reliability**: Standardized on system Python and fixed dependency resolution.

## [1.1.0] - 2026-01-22
### Added
- **Natural Language Search**: Intelligent query parsing with FastMCP sampling.
- **Auto-Open Books**: Unique search results automatically launch in system viewer.
- **Title-Specific Search**: Precise title matching bypassing FTS.

## [1.0.0] - 2025-10-21
### Added
- Initial release with core library management tools.
