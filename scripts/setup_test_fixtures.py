"""
Setup complete test fixtures: database + files.

Run this to create both the test database and all test files.
"""
from pathlib import Path
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir.parent))

from create_test_db import create_test_database
from create_test_files import create_test_files

if __name__ == "__main__":
    print("=" * 60)
    print("Setting up test fixtures for CalibreMCP")
    print("=" * 60)
    print()
    
    # Create database first
    print("Step 1: Creating test database...")
    create_test_database()
    print()
    
    # Then create files
    print("Step 2: Creating test book files...")
    create_test_files()
    print()
    
    print("=" * 60)
    print("✓ Test fixtures setup complete!")
    print("=" * 60)
    print()
    print("You can now run tests with:")
    print("  pytest tests/ -v")
    print()

