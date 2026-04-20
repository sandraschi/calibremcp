"""
Setup complete test fixtures: database + files.

Run this to create both the test database and all test files.
"""

import sys
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir.parent))

from create_test_db import create_test_database  # noqa: E402
from create_test_files import create_test_files  # noqa: E402

if __name__ == "__main__":

    # Create database first
    create_test_database()

    # Then create files
    create_test_files()

