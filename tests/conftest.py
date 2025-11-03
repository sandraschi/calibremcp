"""
Pytest configuration and fixtures for Calibre MCP tests.

Provides fixtures for test database and library setup.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calibre_mcp.db.database import init_database, close_database


@pytest.fixture(scope="session")
def test_library_path():
    """Path to the test library directory."""
    return Path(__file__).parent / "fixtures" / "test_library"


@pytest.fixture(scope="session")
def test_db_path(test_library_path):
    """Path to the test database."""
    db_path = test_library_path / "metadata.db"
    if not db_path.exists():
        pytest.fail(
            f"Test database not found at {db_path}. "
            f"Run 'python scripts/create_test_db.py' to create it."
        )
    return db_path


@pytest.fixture(scope="function")
def test_database(test_db_path):
    """
    Initialize and provide the test database.

    This fixture sets up the database connection for each test
    and cleans up afterwards.
    """
    # Initialize database
    init_database(str(test_db_path), echo=False)

    yield test_db_path

    # Cleanup
    close_database()


@pytest.fixture(scope="function")
def test_library(test_library_path, test_database):
    """
    Provide the full test library context (database + directory).

    This is the main fixture for integration tests.
    """
    yield {
        "path": test_library_path,
        "db_path": test_database,
        "metadata_db": test_database,
    }


@pytest.fixture(scope="function")
def sample_book_data():
    """Sample book data for testing."""
    return {
        "id": 1,
        "title": "A Study in Scarlet",
        "authors": [{"id": 1, "name": "Arthur Conan Doyle"}],
        "tags": [
            {"id": 1, "name": "mystery"},
            {"id": 2, "name": "detective"},
            {"id": 3, "name": "classic"},
        ],
        "series": {"id": 1, "name": "Sherlock Holmes"},
        "formats": [
            {
                "format": "EPUB",
                "filename": "1.epub",
                "path": str(
                    Path(__file__).parent
                    / "fixtures"
                    / "test_library"
                    / "Arthur Conan Doyle"
                    / "A Study in Scarlet (1)"
                    / "1.epub"
                ),
                "size": 245678,
            },
            {
                "format": "PDF",
                "filename": "1.pdf",
                "path": str(
                    Path(__file__).parent
                    / "fixtures"
                    / "test_library"
                    / "Arthur Conan Doyle"
                    / "A Study in Scarlet (1)"
                    / "1.pdf"
                ),
                "size": 456789,
            },
        ],
    }
