# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-04

### Added
- **MCPB Packaging**: Successfully implemented MCPB bundle packaging for one-click installation
- **Build Staging**: Optimized packaging workflow using dedicated `dist/` and staging patterns

### Fixed
- **Startup Reliability**: Fixed server startup by standardizing on system Python (`python -m calibre_mcp`)
- **Dependency Resolution**: Fixed missing `fastmcp` and other core dependencies in system environment
- **Import Logic**: Resolved relative import issues in server initialization

## [Unreleased]

### Added
- **Logs API** - Backend `/api/logs` with tail, filter, level; reads calibremcp.log or webapp.log
- **Logs page** - Log file viewer with filtering, live tail (polling with exponential backoff), system status view
- **Chat personalities** - Default, Librarian, Casual preprompt presets
- **Webapp file logging** - Backend writes to logs/webapp.log with rotation (10MB, 5 backups)

### Fixed
- **getSystemStatus URL** - Use getBaseUrl() for absolute URL (fixes "Failed to parse URL" in logs page)
- **Books API publisher** - Added missing `publisher` query parameter to list_books
- **Book modal metadata** - Direct BookService path for full metadata (rating, publisher, identifiers, comments/description)
- **Export enhancements** - Stats (CSV/JSON/HTML), detail_level (minimal/standard/full), html_style (catalog/gallery/dashboard)
- **manage_import portmanteau** - annas_search (Anna's Archive), from_url (download and add), from_path (local file)
- **Anna's Archive client** - Search with configurable mirrors (ANNAS_MIRRORS env); docs in `docs/ANNAS_ARCHIVE_CONFIG.md`
- **Tool preload verification test** - `tests/test_tool_preload.py` parametrized test for all MCP tools
- **Webapp loading states** - Root and books loading.tsx; ErrorBanner component for consistent error display
- **manage_system help** - help_helper and all helpers; HELP_DOCS with portmanteau tools (basic/intermediate/advanced/expert)
- **Webapp help page** - Static content for Calibre, Calibre MCP, Webapp; no backend dependency
- **Webapp Full UI** - Retractable sidebar, all nav pages
  - Overview dashboard with library stats
  - Authors, Series, Tags list pages with search and drill-down
  - Import (add by path), Export (CSV/JSON with filters)
  - Logs (system status), Help, Settings
- **Webapp AI Chat** - Ollama, LM Studio, OpenAI-compatible
  - Settings page: provider, base URL, model list
  - Chat page with model selection
  - Backend `/api/llm/models`, `/api/llm/chat`
- **Author Wikipedia Links** - Click author in book modal opens Wikipedia search
- **Series API** - Backend `/api/series`, frontend series list and detail pages
- **Book Detail Route** - `/book/[id]` for direct book links from series
- **Webapp Docker** - Full Docker Compose for backend + frontend
  - `webapp/Dockerfile.backend`, `webapp/Dockerfile.frontend`
  - `webapp/docker-compose.yml` - backend:13000, frontend:13001
  - Mount Calibre library, persist user data volume
  - `webapp/docker-up.ps1`, `webapp/.env.docker.example`
- **Calibre Plugin** - GUI integration for Calibre
  - Extended metadata panel: Edit first_published, translator, user comments (Ctrl+Shift+M)
  - Direct SQLite sync with calibre_mcp_data.db (no MCP process required)
  - Virtual library from query: Create Calibre saved searches from webapp backend search
  - Config: Override user data dir, webapp backend URL (default port 13000)
  - Bulk enrich placeholder (shows backend status)
  - Install: `calibre-customize -b calibre_plugin` or `calibre-customize -a calibre_mcp_integration.zip`
- **Calibre Plugin Documentation**
  - `docs/integrations/CALIBRE_PLUGIN_DESIGN.md` - Architecture, features, data flow
  - `docs/integrations/CALIBRE_PLUGIN_IMPLEMENTATION_NOTES.md` - Implementation checklist, code snippets
  - `docs/integrations/CALIBRE_INTEGRATION_GUIDE.md` - Updated with plugin section

### Fixed
- **manage_analysis **kwargs** - FastMCP incompatible; replaced with explicit optional params; removed unimplemented summarize/analyze_themes/sentiment_analysis
- **export_books preload** - Added export_books.py re-export for MCP client module path

### Changed
- Config default MCP HTTP URL: 8765 -> 13000 (Calibre webapp backend port)
- `docs/integrations/CALIBRE_INTEGRATION_GUIDE.md` - Added Calibre plugin section
- `docs/DOCUMENTATION_INDEX.md` - Added Calibre Integrations section
- `README.md` - Added Calibre plugin to features and library access methods

## [1.1.0] - 2026-01-22

### Added
- **Natural Language Search** - Intelligent query parsing with FastMCP 2.14.3 sampling
  - Automatic parsing of conversational queries ("books by harari" → author search)
  - Fallback LLM sampling for ambiguous queries
  - Support for multiple query patterns (author, tag, title, date, genre)
- **Auto-Open Books** - Seamless book reading experience
  - Unique search results automatically launch in system viewer
  - Support for EPUB, PDF, MOBI, AZW3, CBZ, CBR, TXT, HTML, RTF formats
  - Cross-platform viewer launching (Windows `os.startfile`, macOS `open`, Linux `xdg-open`)
- **Title-Specific Search** - Fast, exact title matching
  - New `title` parameter bypasses full-text search for precise title queries
  - Much faster than general text search for title-specific lookups
- **Enhanced Query Books Tool** - Improved search capabilities
  - Added `auto_open` and `auto_open_format` parameters
  - Comprehensive parameter documentation with examples
  - Better error handling and user feedback

### Changed
- **Documentation Updates** - Comprehensive README overhaul
  - Added natural language search examples
  - Documented auto-open functionality
  - Updated feature list and usage examples
  - Improved parameter documentation in docstrings

## [Unreleased] - 2026-01-14

### Fixed
- **FastMCP 2.14.1+ Compliance** - Complete server modernization
  - Updated `pyproject.toml` to require `fastmcp>=2.14.1,<2.15.0`
  - Added `lifespan=server_lifespan` parameter to FastMCP constructor
  - Implemented proper server lifespan for initialization/cleanup (FastMCP 2.13+ requirement)
  - Fixed server startup method (deprecated `run_standalone()` → `run_stdio_async()`)
  - Added FastMCP persistent storage backend (py-key-value-aio[disk])
- **Import System Overhaul** - Fixed relative import failures
  - Converted all relative imports to absolute imports (`from .module` → `from calibre_mcp.module`)
  - Enabled direct script execution without package context issues
  - Maintained backward compatibility for module imports
- **Cursor MCP Configuration** - Fixed IDE integration
  - Updated Cursor MCP config to use absolute paths instead of relative
  - Corrected entry point to `src/calibre_mcp/server.py`
  - Added proper environment variables (`PYTHONPATH`, `PYTHONUNBUFFERED`)
  - Removed conflicting launcher files (`run_server.py`, `server/server.py`)
- **Unicode Safety** - Eliminated encoding crashes
  - Removed all emoji characters from logger messages
  - Fixed Windows console encoding compatibility issues
  - Prevented `UnicodeEncodeError` crashes in IDE environments
- **Test Suite Compatibility** - Updated for FastMCP FunctionTool objects
  - Fixed circular import issues in test suite
  - Updated integration tests to work with new FastMCP tool registration
  - Added lazy import patterns for testing (`_get_mcp()`)
  - Comprehensive test coverage maintained

### Changed
- **Server Architecture** - Modernized to FastMCP 2.14.1+ standards
  - Eliminated non-standard launcher scripts
  - Direct execution capability (`python src/calibre_mcp/server.py`)
  - Proper async stdio transport implementation
  - Enhanced error handling and logging

### Added
- **Lifespan Management** - FastMCP 2.14.1+ server lifecycle
  - Proper initialization and cleanup procedures
  - Async context manager for server lifespan
  - Storage initialization with error recovery
- **Enhanced Logging** - Structured logging throughout server lifecycle
  - Phase-based initialization logging
  - Import success/failure tracking
  - Debug information for troubleshooting

### Added
- **Database Auto-Initialization** - Robust first-try reliability improvements
  - Server startup always initializes database or fails fast with clear errors
  - Tools auto-initialize database on first use if not initialized at startup
  - Library selection priority: persisted -> config -> active Calibre library -> first discovered
  - All searches now work on first try without manual library switching
- **Intelligent Query Parsing** - Natural language query understanding
  - Extracts author, tag, publication date, rating, series from natural language queries
  - Handles time expressions (last month, this week, etc.)
  - Content type hints (manga, comic, paper) trigger intelligent library selection
  - "books by X" always interpreted as author search
  - Quoted text for exact matching
- **Comments CRUD Portmanteau Tool** - `manage_comments` for dedicated comment management
  - Operations: create, read, update, delete, append, replace
  - Handles comment format normalization (string/list formats from Calibre API)
  - Comprehensive error handling and structured logging
  - Full unit test coverage (13 test cases)
- **Random Book Opening** - `manage_viewer(operation="open_random")` for serendipitous reading
  - Search for books by author/tag/series filters
  - Randomly select one matching book
  - Automatically open with system's default application
  - Supports format preference (EPUB, PDF, etc.)
  - Example: "open a dickson carr book now" → opens random Carr book
- **Metadata Display Tool** - `manage_metadata(operation="show")` for comprehensive book metadata viewing
  - Search for books by title or author
  - Retrieve and format comprehensive metadata
  - Display in formatted HTML popup (optional)
  - Returns formatted text representation
  - Example: "cal meta gormenghast" → shows metadata popup
- **Portmanteau Tool Refactoring Complete** - 18 consolidated tools (55% reduction from ~40+ tools)
  - `manage_comments` - Comment CRUD operations (create, read, update, delete, append, replace)
  - `manage_viewer` - Book viewer operations (open, get_page, get_metadata, get_state, update_state, close, open_file, open_random)
  - `manage_metadata` - Metadata operations (update, organize_tags, fix_issues, show)
  - `manage_specialized` - Specialized tools (japanese_organizer, it_curator, reading_recommendations)
- **Phase 3: Docstring Standardization** - 100% compliance with TOOL_DOCSTRING_STANDARD.md
  - All 18 portmanteau tools have PORTMANTEAU PATTERN RATIONALE sections
  - All tools have OPERATIONS DETAIL sections
  - Comprehensive parameter documentation
  - Operation-specific return structures
  - Usage examples for each operation

### Changed
- **Database initialization flow** - Unified priority logic between server startup and tool auto-initialization
- **Query parsing** - Centralized intelligent parsing in `tools/shared/query_parsing.py`
- **Error handling** - Enhanced with structured logging and actionable error messages
- **Standardized all portmanteau tool docstrings** - Following TOOL_DOCSTRING_STANDARD.md format
- **Updated documentation** - Migration plan, completion reports, usage guides
- **Improved tool discoverability** - Related operations grouped in portmanteau tools

### Fixed
- **Unicode encoding crashes** - Server startup failures on Windows due to Unicode emojis (✅, ❌, 📚)
  - Replaced all Unicode emojis with ASCII equivalents across codebase
  - Fixed undefined `_is_stdio_mode` variable in server initialization
  - Removed problematic `original_getLogger` reference
  - Server now starts successfully on Windows systems
- **Database initialization reliability** - Searches now work on first try without manual library switching
- **Query interpretation** - "books by X" correctly interpreted as author search
- **Library discovery** - Proper priority handling for library selection
- **Ruff linting issues** - All portmanteau tools now pass linting (0 errors)
- **Unused imports** - Cleaned up unused imports across portmanteau tools
- **Unused variables** - Fixed unused exception variables

## [1.0.0] - 2025-10-21

### Added
- Initial release
- Core functionality implemented
- Documentation created

### Changed
- N/A

### Fixed
- N/A

### Removed
- N/A

---

## How to Update This File

When making changes, add them under the appropriate section:
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes
