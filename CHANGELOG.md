# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
