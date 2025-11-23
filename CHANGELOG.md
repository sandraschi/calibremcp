# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-11-23

### Added
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
- **Standardized all portmanteau tool docstrings** - Following TOOL_DOCSTRING_STANDARD.md format
- **Updated documentation** - Migration plan, completion reports, usage guides
- **Improved tool discoverability** - Related operations grouped in portmanteau tools

### Fixed
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
