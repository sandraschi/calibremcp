#!/usr/bin/env python3
"""
Test Helpers for Portmanteau Test Batteries

Provides utilities for creating and managing test libraries and books
to prevent destructive operations on real libraries.
"""

import shutil
import sys
import tempfile
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


class TestLibraryManager:
    """Manages test library lifecycle for safe destructive testing."""

    def __init__(self):
        self.test_library_path: Path | None = None
        self.test_library_name: str | None = None
        self.temp_dir: Path | None = None

    def create_test_library(self) -> tuple[str, Path]:
        """
        Create a temporary test library.

        Returns:
            Tuple of (library_name, library_path)
        """
        import time

        # Create temp directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="calibre_test_"))
        self.test_library_path = self.temp_dir / "test_library"
        self.test_library_path.mkdir(parents=True, exist_ok=True)

        # Create metadata.db
        from calibre_mcp.db.database import init_database

        metadata_db = self.test_library_path / "metadata.db"
        init_database(str(metadata_db), echo=False)

        # Create library structure
        (self.test_library_path / "cover").mkdir(exist_ok=True)

        self.test_library_name = f"test_lib_{int(time.time())}"

        print(f"[TEST_LIB] Created test library: {self.test_library_name}")
        print(f"[TEST_LIB] Path: {self.test_library_path}")

        return self.test_library_name, self.test_library_path

    def add_test_books(self, count: int = 3) -> list[int]:
        """
        Add test books to the test library.

        NOTE: This is a placeholder. Actual book addition should be done
        via manage_books(operation="add") after switching to the test library.

        Args:
            count: Number of test books to add (for reference)

        Returns:
            List of book IDs (empty for now - books must be added via manage_books)
        """
        if not self.test_library_path:
            raise ValueError("Test library not created. Call create_test_library() first.")

        print("[TEST_LIB] Test library ready for book addition via manage_books")
        print("[TEST_LIB] Use manage_books(operation='add', file_path=...) to add books")

        # Return empty list - books should be added via manage_books tool
        return []

    def cleanup(self):
        """Clean up test library and temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                print(f"[TEST_LIB] Cleaned up test library: {self.temp_dir}")
            except Exception as e:
                print(f"[WARN] Could not clean up test library: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - always cleanup."""
        self.cleanup()


def get_test_library_or_skip():
    """
    Get a test library for destructive operations, or return None to skip.

    Returns:
        Tuple of (library_name, library_path) or (None, None) to skip
    """
    try:
        manager = TestLibraryManager()
        lib_name, lib_path = manager.create_test_library()
        return manager, lib_name, lib_path
    except Exception as e:
        print(f"[WARN] Could not create test library: {e}")
        return None, None, None
