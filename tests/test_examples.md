# Test Examples and Usage

This document provides examples of how to use the test suite and write new tests.

## Running Tests

### Basic Usage

```powershell
# Run all tests
pytest tests/

# Run specific test file
pytest tests/unit/test_book_search.py

# Run specific test class
pytest tests/unit/test_book_search.py::TestSearchBooksHelper

# Run specific test method
pytest tests/unit/test_book_search.py::TestSearchBooksHelper::test_search_by_author
```

### With PowerShell Script

```powershell
# Run all tests
.\tests\run_tests.ps1

# Run with coverage
.\tests\run_tests.ps1 -Coverage

# Run verbose
.\tests\run_tests.ps1 -Verbose

# Run specific marker
.\tests\run_tests.ps1 -Marker "unit"

# Run specific test name pattern
.\tests\run_tests.ps1 -TestName "search_by_author"
```

### With Python Script

```powershell
# Run all tests
python tests/test_runner.py

# Run with coverage
python tests/test_runner.py --coverage

# Run verbose
python tests/test_runner.py --verbose

# Run specific marker
python tests/test_runner.py --marker unit

# Run specific test
python tests/test_runner.py --test "search_by_author"
```

## Writing New Tests

### Basic Test Structure

```python
import pytest
from calibre_mcp.tools.book_tools import search_books_helper

@pytest.mark.asyncio
async def test_my_new_feature(test_database):
    """Test description."""
    result = await search_books_helper(text="query", limit=10)
    
    assert "items" in result
    assert result["total"] >= 0
```

### Testing with Filters

```python
@pytest.mark.asyncio
async def test_search_with_multiple_filters(test_database):
    """Test search with multiple filters."""
    result = await search_books_helper(
        author="Conan Doyle",
        tag="mystery",
        min_rating=4,
        limit=10
    )
    
    assert result["total"] >= 0
    # Verify filters were applied
    for book in result["items"]:
        assert "Conan Doyle" in str(book.get("authors", []))
```

### Testing Error Cases

```python
@pytest.mark.asyncio
async def test_invalid_input(test_database):
    """Test error handling for invalid input."""
    with pytest.raises(ValueError) as exc_info:
        await search_books_helper(limit=0)
    
    assert "Limit must be between" in str(exc_info.value)
```

### Testing Logging

```python
import logging

@pytest.mark.asyncio
async def test_logging(test_database, caplog):
    """Test that operations are logged."""
    with caplog.at_level(logging.INFO):
        await search_books_helper(text="test", limit=10)
    
    # Check logs
    log_messages = [record.message for record in caplog.records]
    assert any("search" in msg.lower() for msg in log_messages)
```

### Testing Performance

```python
import time

@pytest.mark.asyncio
async def test_performance(test_database):
    """Test search performance."""
    start_time = time.time()
    result = await search_books_helper(text="test", limit=10)
    duration = time.time() - start_time
    
    assert duration < 1.0  # Should complete in under 1 second
    assert "items" in result
```

## Test Data

The test database includes:

- **Books**: 12+ books with diverse metadata
- **Authors**: 10+ authors including classics and modern authors
- **Tags**: 13+ tags covering various genres
- **Series**: 4+ series including popular book series
- **Formats**: Multiple formats (EPUB, PDF, MOBI, CBZ)
- **Comments**: Book descriptions and notes
- **Dates**: Various publication dates for date filtering tests

### Adding Test Data

To add more test data:

1. Run the base database creation:
   ```powershell
   python scripts/create_test_db.py
   ```

2. Add extensive test data:
   ```powershell
   python scripts/setup_extensive_test_data.py
   ```

## Test Categories

### Unit Tests

Test individual functions and methods in isolation:
- `tests/unit/test_book_search.py` - Search functionality
- `tests/unit/test_search_logging.py` - Logging verification
- `tests/unit/test_search_error_handling.py` - Error handling

### Integration Tests

Test the full flow from tool call to database:
- `tests/integration/test_search_integration.py` - End-to-end tests

## Common Patterns

### Testing Pagination

```python
@pytest.mark.asyncio
async def test_pagination(test_database):
    """Test pagination works correctly."""
    # Get first page
    page1 = await search_books_helper(limit=2, offset=0)
    
    # Get second page
    if page1["total"] > 2:
        page2 = await search_books_helper(limit=2, offset=2)
        
        # Verify no duplicates
        page1_ids = {book["id"] for book in page1["items"]}
        page2_ids = {book["id"] for book in page2["items"]}
        assert len(page1_ids & page2_ids) == 0
```

### Testing Case Insensitivity

```python
@pytest.mark.asyncio
async def test_case_insensitive(test_database):
    """Test that search is case-insensitive."""
    result1 = await search_books_helper(text="scarlet", limit=10)
    result2 = await search_books_helper(text="SCARLET", limit=10)
    
    assert result1["total"] == result2["total"]
```

### Testing Filter Combinations

```python
@pytest.mark.asyncio
async def test_filter_combinations(test_database):
    """Test multiple filter combinations."""
    # Test AND logic between different filter types
    result = await search_books_helper(
        author="Conan Doyle",
        tag="mystery",
        min_rating=1,
        formats=["EPUB"]
    )
    
    assert result["total"] >= 0
    # Verify all filters were applied
    for book in result["items"]:
        # Check author
        authors = [a.get("name", "") for a in book.get("authors", [])]
        assert any("Conan Doyle" in a for a in authors)
        
        # Check format
        formats = [f.get("format", "") for f in book.get("formats", [])]
        assert "EPUB" in formats or len(formats) == 0
```

## Debugging Failed Tests

1. **Run with verbose output**:
   ```powershell
   pytest tests/ -vv
   ```

2. **Run specific failing test**:
   ```powershell
   pytest tests/path/to/test.py::TestClass::test_method -vv
   ```

3. **Use pytest debugging**:
   ```powershell
   pytest tests/ --pdb
   ```

4. **Check logs**:
   Test logs are written to `logs/calibremcp.log` (structured JSON format)

5. **Print debug information**:
   ```python
   @pytest.mark.asyncio
   async def test_with_debug(test_database):
       result = await search_books_helper(text="test", limit=10)
       print(f"Result: {result}")  # Will show in test output
       assert "items" in result
   ```

## Best Practices

1. **Use descriptive test names**: Test names should clearly describe what they test
2. **One assertion per concept**: Test one thing at a time
3. **Use fixtures**: Leverage `test_database` and other fixtures
4. **Test edge cases**: Include boundary conditions and error cases
5. **Keep tests independent**: Tests should not depend on each other
6. **Clean up**: Use fixtures for setup/teardown
7. **Document complex tests**: Add docstrings explaining test logic
