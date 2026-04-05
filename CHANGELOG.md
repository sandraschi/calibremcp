# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **FastMCP 3.2+ Upgrade**: Updated FastMCP dependency from 3.1.0 to 3.2.0 for universal connect pattern support
- **Database Concurrency**: Implemented thread-safe database operations with row-level locking for multi-client access
- **Transport Layer**: Removed invalid FastAPI app routing decorators to align with FastMCP 3.2+ architecture

### Added
- **Universal Connect Pattern**: Support for multiple simultaneous clients via stdio and HTTP transports
- **Concurrency Safety**: Thread-safe database operations preventing race conditions in multi-client environments
- **Database Locking**: Row-level locking for write operations to prevent data corruption
- **FastMCP 3.2 Features**: Access to new 3.2 functionality including codemode, prefabs, app providers, and transforms

### Fixed
- **FastAPI Routing Error**: Fixed `AttributeError: 'FastMCP' object has no attribute 'app'` by removing incorrect decorators
- **Database Access**: Implemented proper session management for concurrent database operations
- **Version Compatibility**: Ensured compatibility with latest FastMCP 3.2.0 features

## [1.5.0] - 2026-03-31
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
