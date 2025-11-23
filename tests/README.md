# CalibreMCP Test Suite

**Status:** ✅ Modernized for Portmanteau Tools  
**Date:** 2025-11-22  
**Structure:** Unit tests + Integration tests

---

## Test Structure

```
tests/
├── unit/                          # Unit tests (mocked dependencies)
│   ├── test_portmanteau_books.py      # manage_books tests
│   ├── test_portmanteau_query_books.py # query_books tests
│   ├── test_portmanteau_libraries.py  # manage_libraries tests
│   └── test_portmanteau_viewer.py     # manage_viewer tests
│
├── integration/                   # Integration tests (real database)
│   └── test_portmanteau_integration.py # Full workflow tests
│
├── fixtures/                      # Test fixtures and data
│   └── test_library/              # Test Calibre library
│
├── conftest.py                    # Pytest configuration and fixtures
├── test_basic.py                  # Core functionality tests
├── test_api.py                    # API client tests
├── test_mcp_server.py             # MCP server tests
├── test_mcp_compliance.py         # MCP protocol compliance
├── test_server_integration.py     # Server integration tests
└── test_stdio_integration.py      # STDIO integration tests
```

---

## Running Tests

### Run All Tests

```bash
# Using uv (recommended)
uv run pytest tests/ -v

# Using pytest directly
pytest tests/ -v
```

### Run Unit Tests Only

```bash
uv run pytest tests/unit/ -v
```

### Run Integration Tests Only

```bash
uv run pytest tests/integration/ -v
```

### Run Specific Test File

```bash
uv run pytest tests/unit/test_portmanteau_books.py -v
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=src/calibre_mcp --cov-report=html --cov-report=term-missing
```

---

## Test Categories

### Unit Tests (`tests/unit/`)

**Purpose:** Test portmanteau tools with mocked dependencies

**Characteristics:**
- Fast execution
- No database required
- Isolated testing
- Mocked helper functions

**Files:**
- `test_portmanteau_books.py` - Tests `manage_books` operations (add, get, update, delete)
- `test_portmanteau_query_books.py` - Tests `query_books` operations (search, list, by_author, by_series)
- `test_portmanteau_libraries.py` - Tests `manage_libraries` operations (list, switch, stats, search)
- `test_portmanteau_viewer.py` - Tests `manage_viewer` operations (open, get_page, get_state, etc.)

### Integration Tests (`tests/integration/`)

**Purpose:** Test portmanteau tools with real database connections

**Characteristics:**
- Real database connections
- Full workflow testing
- End-to-end validation
- Uses test fixtures

**Files:**
- `test_portmanteau_integration.py` - Full workflow tests using multiple portmanteau tools

### Core Tests (Root `tests/`)

**Purpose:** Test core functionality, API, server, and compliance

**Files:**
- `test_basic.py` - Core imports and initialization
- `test_api.py` - API client functionality
- `test_mcp_server.py` - MCP server functionality
- `test_mcp_compliance.py` - MCP protocol compliance
- `test_server_integration.py` - Server integration
- `test_stdio_integration.py` - STDIO protocol integration

---

## Test Fixtures

### Available Fixtures

- `test_library_path` - Path to test library directory
- `test_db_path` - Path to test database file
- `test_database` - Initialized test database (function-scoped)
- `test_library` - Full test library context (database + directory)
- `sample_book_data` - Sample book data structure
- `portmanteau_test_data` - Test data for portmanteau tools

### Usage

```python
@pytest.mark.asyncio
async def test_example(test_library, sample_book_data):
    """Example test using fixtures."""
    # test_library provides database and path
    # sample_book_data provides sample book structure
    pass
```

---

## Portmanteau Tool Testing

### Testing Pattern

All portmanteau tools follow a consistent testing pattern:

1. **Operation Testing** - Test each operation (add, get, update, delete, etc.)
2. **Parameter Validation** - Test required/optional parameters
3. **Error Handling** - Test invalid operations and missing parameters
4. **Return Structure** - Verify return value structure

### Example Test

```python
@pytest.mark.asyncio
async def test_manage_books_get(mock_book_helpers):
    """Test manage_books get operation."""
    result = await manage_books(
        operation="get",
        book_id="123",
        include_metadata=True
    )
    
    assert result["id"] == "123"
    assert "title" in result
    mock_book_helpers["get"].assert_called_once()
```

---

## Deleted Stale Tests

The following stale tests were removed (they tested old individual tools):

- ❌ `test_book_tools.py` - Tested old `search_books` tool
- ❌ `test_query_books_search.py` - Tested old `search_books_helper`
- ❌ `test_query_books_integration.py` - Tested old service directly
- ❌ `test_search_functionality.py` - Tested old `search_books` tool
- ❌ `test_fts_search.py` - Tested old `search_books_helper`
- ❌ `test_integration.py` - Tested old individual tools
- ❌ `test_open_book_file.py` - Tested old viewer tools

**Replaced by:**
- ✅ `tests/unit/test_portmanteau_*.py` - Unit tests for portmanteau tools
- ✅ `tests/integration/test_portmanteau_integration.py` - Integration tests

---

## Test Coverage Goals

- **Unit Tests:** 80%+ coverage for portmanteau tools
- **Integration Tests:** Critical workflows covered
- **Core Tests:** 100% coverage for core functionality

---

## Writing New Tests

### Unit Test Template

```python
"""
Unit tests for [tool_name] portmanteau tool.
"""

import pytest
from unittest.mock import patch
from calibre_mcp.tools.[module].[tool] import [tool_name]


@pytest.fixture
def mock_helpers():
    """Mock helper functions."""
    with patch("...") as mock:
        mock.return_value = {...}
        yield {"helper": mock}


@pytest.mark.asyncio
async def test_[tool]_[operation](mock_helpers):
    """Test [tool] [operation] operation."""
    result = await [tool_name](
        operation="[operation]",
        # parameters
    )
    
    assert result[...] == ...
    mock_helpers["helper"].assert_called_once()
```

### Integration Test Template

```python
"""
Integration test for [tool_name].
"""

import pytest
from calibre_mcp.tools.[module].[tool] import [tool_name]
from calibre_mcp.db.database import init_database, close_database


@pytest.mark.asyncio
async def test_[tool]_integration(test_library):
    """Integration test for [tool]."""
    init_database(str(test_library["db_path"]), echo=False)
    
    try:
        result = await [tool_name](
            operation="[operation]",
            # parameters
        )
        
        assert "result" in result or "error" in result
        
    finally:
        close_database()
```

---

## CI/CD Integration

Tests run automatically in CI/CD:

- **Pre-commit:** Unit tests run locally before commit
- **CI Pipeline:** All tests run on push/PR
- **Coverage:** Codecov integration for coverage tracking

---

## Troubleshooting

### Tests Fail with Database Errors

```bash
# Create test database
python scripts/create_test_db.py
```

### Import Errors

```bash
# Ensure src is in path (handled by conftest.py)
# If issues persist, check PYTHONPATH
```

### Mock Issues

- Ensure mocks match actual function signatures
- Check that patches target correct import paths
- Verify return values match expected structure

---

## Related Documentation

- [Portmanteau Tools](../../docs/development/PORTMANTEAU_REFACTORING_SUMMARY.md)
- [CI/CD Setup](../../docs/development/CI_CD_STATUS.md)
- [Development Workflow](../../docs/MCP_DEVELOPMENT_WORKFLOW.md)

---

*Test Suite Documentation*  
*Last Updated: 2025-11-22*  
*Status: ✅ Modernized for Portmanteau Tools*

