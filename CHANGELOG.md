# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-12-22

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
- **Portmanteau Tool Refactoring Complete** - 18 consolidated tools (55% reduction from ~40+ tools)
  - `manage_comments` - Comment CRUD operations (create, read, update, delete, append, replace)
  - `manage_viewer` - Book viewer operations (open, get_page, get_metadata, get_state, update_state, close, open_file)
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
