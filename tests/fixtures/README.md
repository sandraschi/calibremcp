# Test Fixtures

This directory contains a minimal test Calibre library for automated testing and CI/CD.

## Structure

```
test_library/
├── metadata.db          # SQLite database with 4 test books
└── [author directories]/
    └── [book directories]/
        ├── [id].epub    # Minimal EPUB files
        ├── [id].pdf     # Minimal PDF files
        └── [id].cbz     # Minimal CBZ files (comics)
```

## Test Data

- **4 books**: A Study in Scarlet, The Sign of the Four, Pride and Prejudice, Tom Sawyer
- **3 authors**: Arthur Conan Doyle, Jane Austen, Mark Twain
- **5 tags**: mystery, detective, classic, romance, adventure
- **1 series**: Sherlock Holmes (2 books)
- **6 format files**: EPUB, PDF, and CBZ (total ~15KB)

## Setup

To create/update the test fixtures:

```bash
# Create both database and files
python scripts/setup_test_fixtures.py

# Or create separately:
python scripts/create_test_db.py      # Creates metadata.db
python scripts/create_test_files.py   # Creates EPUB/PDF/CBZ files
```

## Usage in Tests

Use the pytest fixtures from `tests/conftest.py`:

```python
def test_search_books(test_database):
    """Test uses the test database."""
    results = book_service.get_all(search="Conan Doyle")
    assert len(results["items"]) >= 2

def test_open_book_file(test_library):
    """Test uses full library (database + files)."""
    library_path = test_library["path"]
    # Files exist at library_path/[author]/[book]/[id].epub
```

## File Sizes

All test files are minimal but valid:
- EPUB: ~2-3 KB each
- PDF: ~0.6 KB each
- CBZ: ~0.5 KB each
- Database: ~20-30 KB

**Total fixture size: < 50 KB** (safe for GitHub)

## CI/CD

These fixtures are committed to GitHub and used in:
- GitHub Actions workflows
- Local pytest runs
- Integration tests without mocking

## Notes

- Files are valid but minimal (contain just enough structure to be valid)
- Database uses real Calibre schema structure
- All files should be committed (not in .gitignore)
- Update fixtures if schema changes significantly

