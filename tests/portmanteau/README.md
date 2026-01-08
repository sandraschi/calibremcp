# Portmanteau Test Batteries

This directory contains comprehensive test batteries for all portmanteau tools in Calibre-MCP.

## Test Files

Each portmanteau tool has its own dedicated test battery file:

1. **test_manage_libraries.py** - Tests library management operations (list, switch, stats, search)
2. **test_manage_books.py** - Tests book CRUD operations (add, get, details, update, delete)
3. **test_query_books.py** - Tests book query/search operations (search, list, recent, by_author, by_series)
4. **test_manage_authors.py** - Tests author management (list, get, get_books, stats, by_letter)
5. **test_manage_tags.py** - Tests tag management (list, get, create, update, delete, find_duplicates, merge, get_unused, statistics)
6. **test_manage_comments.py** - Tests comment operations (create, read, update, delete, append, replace)
7. **test_manage_metadata.py** - Tests metadata operations (update, organize_tags, fix_issues)
8. **test_manage_files.py** - Tests file operations (convert, download, bulk)
9. **test_manage_smart_collections.py** - Tests smart collections/virtual libraries (create, get, update, delete, list, query)
10. **test_manage_analysis.py** - Tests analysis operations (tag_statistics, duplicate_books, series_analysis, library_health, unread_priority, reading_stats)
11. **test_manage_specialized.py** - Tests specialized operations (japanese_organizer, it_curator, reading_recommendations)
12. **test_manage_system.py** - Tests system operations (help, status, tool_help, list_tools, hello_world, health_check)
13. **test_manage_bulk_operations.py** - Tests bulk operations (update_metadata, export, delete, convert)
14. **test_manage_content_sync.py** - Tests content sync operations (register_device, update_device, get_device, start, status, cancel)
15. **test_manage_users.py** - Tests user management (create_user, update_user, delete_user, list_users, get_user, login, verify_token)
16. **test_manage_viewer.py** - Tests viewer operations (open, get_page, get_metadata, get_state, update_state, close, open_file)
17. **test_export_books.py** - Tests export operations (csv, json, html, pandoc)

## Running Tests

### Run Individual Test Battery

```powershell
python tests/portmanteau/test_manage_libraries.py
```

### Run All Test Batteries

```powershell
python tests/portmanteau/run_all_tests.py
```

## Test Structure

Each test battery follows a consistent structure:

1. **Setup**: Initialize database and library
2. **Tests**: Run multiple test cases for each operation
3. **Cleanup**: Remove test data (where applicable)
4. **Summary**: Print test results summary

## Test Coverage

Each test battery covers:
- All operations supported by the portmanteau tool
- Error handling
- Edge cases (empty results, missing data, etc.)
- Cleanup of test data

## Requirements

- Calibre library must be configured
- Database must be accessible
- Some tests may require additional dependencies (e.g., Pandoc for export tests)

## Safety Notes

**CRITICAL: Tests are designed to protect real libraries and books from destruction.**

### Destructive Operations

- **Book Deletion**: Uses test library created specifically for testing. Test library is automatically cleaned up.
- **Library Deletion**: Not tested (manage_libraries doesn't support delete operation).
- **Tag Deletion**: Safe - only removes metadata, not books. Test tags are cleaned up.
- **Comment Deletion**: Safe - only removes metadata, not books.
- **Collection Deletion**: Safe - only removes metadata, not books.
- **Bulk Delete**: Skipped in tests (would require test library setup).

### Test Library Lifecycle

For destructive operations (like book deletion), tests follow this pattern:

1. **Create** test library in temporary directory
2. **Add** test books to test library
3. **Perform** destructive operations on test library
4. **Cleanup** test library (automatic)

### Non-Destructive Operations

Most operations (get, list, search, update metadata) use real libraries safely:
- Read operations are always safe
- Update operations modify metadata only (ratings, tags, etc.)
- No books or libraries are deleted from real libraries

## Notes

- Tests use the actual library data for non-destructive operations
- Results may vary based on library contents
- Test libraries are created in system temp directory and cleaned up automatically
