# Quick Start Guide - Running Tests

## Setup (One-time)

1. **Create test database**:
   ```powershell
   python scripts/create_test_db.py
   ```

2. **Add extensive test data** (optional, for more comprehensive testing):
   ```powershell
   python scripts/setup_extensive_test_data.py
   ```

3. **Install test dependencies** (if not already installed):
   ```powershell
   pip install pytest pytest-asyncio pytest-cov
   ```

## Running Tests

### Quick Commands

```powershell
# Run all tests
pytest tests/

# Run with PowerShell script
.\tests\run_tests.ps1

# Run with Python script
python tests/test_runner.py
```

### Common Options

```powershell
# Verbose output
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_book_search.py

# Run specific test
pytest tests/unit/test_book_search.py::TestSearchBooksHelper::test_search_by_author

# Run with coverage
pytest tests/ --cov=calibre_mcp --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests matching pattern
pytest tests/ -k "search"

# Run tests in parallel (requires pytest-xdist)
pytest tests/ -n auto
```

## Test Files Overview

- **test_book_search.py**: Core search functionality (50+ tests)
- **test_search_logging.py**: Logging verification (10+ tests)
- **test_search_error_handling.py**: Error handling (15+ tests)
- **test_search_integration.py**: End-to-end tests (15+ tests)

**Total: 90+ test cases**

## What Gets Tested

✅ Basic search (text, author, tag, series)  
✅ Multiple filter combinations  
✅ Exclusion filters  
✅ Pagination  
✅ Sorting  
✅ Format filtering  
✅ Date filtering  
✅ Size filtering  
✅ Error handling  
✅ Logging  
✅ Performance  
✅ Edge cases  
✅ Case insensitivity  
✅ Partial matching  

## Troubleshooting

**Tests fail with "Database not found"**:
```powershell
python scripts/create_test_db.py
```

**Tests fail with import errors**:
```powershell
pip install -e .
```

**Want to see detailed output**:
```powershell
pytest tests/ -vv
```

**Want to debug a specific test**:
```powershell
pytest tests/path/to/test.py::TestClass::test_method --pdb
```

## Next Steps

- See `test_examples.md` for writing new tests
- See `README.md` for detailed documentation
- Check `logs/calibremcp.log` for test execution logs
