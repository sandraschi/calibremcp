# Calibre MCP Test Suite

Comprehensive test suite for Calibre MCP search functionality and related features.

## Test Structure

```
tests/
├── conftest.py              # Shared pytest fixtures
├── unit/                    # Unit tests
│   ├── test_book_search.py  # Search functionality tests
│   ├── test_search_logging.py  # Logging tests
│   └── test_search_error_handling.py  # Error handling tests
├── integration/             # Integration tests
│   └── test_search_integration.py  # Full flow tests
└── fixtures/               # Test data
    └── test_library/       # Test Calibre library
```

## Running Tests

### Run all tests:
```powershell
pytest tests/
```

### Run specific test file:
```powershell
pytest tests/unit/test_book_search.py
```

### Run with coverage:
```powershell
pytest tests/ --cov=calibre_mcp --cov-report=html
```

### Run with verbose output:
```powershell
pytest tests/ -v
```

### Run specific test:
```powershell
pytest tests/unit/test_book_search.py::TestSearchBooksHelper::test_search_by_author
```

## Test Categories

### Unit Tests (`tests/unit/`)

- **test_book_search.py**: Core search functionality
  - Basic search operations
  - Filter combinations
  - Pagination
  - Edge cases
  - Performance tests

- **test_search_logging.py**: Logging verification
  - Log message presence
  - Structured logging format
  - Error logging
  - Timing information

- **test_search_error_handling.py**: Error handling
  - Database errors
  - Validation errors
  - Query execution errors
  - Error message quality

### Integration Tests (`tests/integration/`)

- **test_search_integration.py**: Full flow tests
  - End-to-end search flow
  - Database reconnection
  - Concurrent queries
  - Result structure validation

## Test Fixtures

### test_database
Provides an initialized test database for each test function.

### test_library
Provides full test library context (database + directory).

### sample_book_data
Sample book data structure for testing.

## Setup

Before running tests, ensure the test database exists:

```powershell
python scripts/create_test_db.py
```

This creates a minimal test Calibre library with sample books:
- 4 books (Sherlock Holmes, Pride and Prejudice, Tom Sawyer)
- 3 authors
- 5 tags
- 1 series

## Test Coverage

The test suite covers:

- ✅ Basic search operations (text, author, tag, series)
- ✅ Multiple filter combinations
- ✅ Exclusion filters (exclude_tags, exclude_authors)
- ✅ Pagination
- ✅ Sorting
- ✅ Format filtering
- ✅ Date range filtering
- ✅ Size filtering
- ✅ Error handling
- ✅ Logging
- ✅ Performance
- ✅ Edge cases (empty queries, special characters, SQL injection attempts)
- ✅ Case insensitivity
- ✅ Partial matching

## Writing New Tests

When adding new tests:

1. **Use appropriate fixtures**: Use `test_database` for database-dependent tests
2. **Follow naming conventions**: Test classes start with `Test`, test methods start with `test_`
3. **Use descriptive names**: Test names should clearly describe what they test
4. **Add docstrings**: Explain what the test verifies
5. **Use assertions**: Verify expected behavior, not just that code runs
6. **Test edge cases**: Include tests for boundary conditions and error cases

## Continuous Integration

Tests are automatically run in CI/CD pipelines. Ensure all tests pass before merging.

## Debugging Failed Tests

1. Run with verbose output: `pytest tests/ -v`
2. Run specific failing test: `pytest tests/path/to/test.py::TestClass::test_method -v`
3. Use pytest's debugging features: `pytest tests/ --pdb`
4. Check logs: Test logs are written to `logs/calibremcp.log`
