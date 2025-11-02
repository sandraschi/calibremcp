"""Advanced series management tools for CalibreMCP."""

from typing import Dict, List, Optional
import logging
from collections import defaultdict

try:
    from fastmcp import MCPTool
except ImportError:
    from ..compat import MCPTool
from pydantic import BaseModel, Field


class SeriesInfo(BaseModel):
    """Information about a book series."""

    name: str
    books: List[Dict] = Field(default_factory=list)
    total_books: Optional[int] = None
    description: Optional[str] = None
    is_complete: bool = False
    reading_order: Optional[List[str]] = None

    def add_book(self, book: Dict, index: Optional[float] = None):
        """Add a book to the series."""
        if not isinstance(book, dict) or "id" not in book:
            return False

        # Check if book is already in the series
        for existing in self.books:
            if existing.get("id") == book.get("id"):
                # Update the existing entry
                existing.update(book)
                if index is not None:
                    existing["series_index"] = index
                return True

        # Add new book to series
        book_data = book.copy()
        if index is not None:
            book_data["series_index"] = index
        self.books.append(book_data)
        return True

    def sort_books(self):
        """Sort books in the series by their series index."""
        self.books.sort(key=lambda x: float(x.get("series_index", 0)))

    def get_next_book(self, current_book_id: str) -> Optional[Dict]:
        """Get the next book in the series after the given book ID."""
        if not self.books:
            return None

        self.sort_books()

        # Find the current book
        current_idx = -1
        for i, book in enumerate(self.books):
            if book.get("id") == current_book_id:
                current_idx = i
                break

        # Return the next book if it exists
        if 0 <= current_idx < len(self.books) - 1:
            return self.books[current_idx + 1]
        return None


class SeriesManager(MCPTool):
    """Advanced series management tools for CalibreMCP."""

    name = "series_manager"
    description = "Advanced tools for managing book series"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.series_cache = {}

    async def analyze_series(self, library_path: str, update_metadata: bool = False) -> Dict:
        """
        Analyze all series in the library.

        Args:
            library_path: Path to the Calibre library
            update_metadata: Whether to update book metadata with series information

        Returns:
            Dictionary with series analysis results
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)
        books = await storage.get_all_books()

        # Group books by series
        series_books = defaultdict(list)
        for book in books:
            if "series" in book and book["series"]:
                series_name = book["series"]
                series_books[series_name].append(book)

        # Analyze each series
        results = {}
        for series_name, books_in_series in series_books.items():
            series_info = await self._analyze_series(series_name, books_in_series)
            results[series_name] = series_info.dict()

            # Update book metadata if requested
            if update_metadata:
                await self._update_series_metadata(storage, series_info)

        return {"success": True, "total_series": len(results), "series": results}

    async def fix_series_metadata(self, library_path: str, dry_run: bool = True) -> Dict:
        """
        Fix common series metadata issues.

        Args:
            library_path: Path to the Calibre library
            dry_run: If True, only show what would be changed

        Returns:
            Dictionary with results of the operation
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)
        books = await storage.get_all_books()

        changes = []

        # Group books by series
        series_books = defaultdict(list)
        for book in books:
            if "series" in book and book["series"]:
                series_name = book["series"]
                series_books[series_name].append(book)

        # Process each series
        for series_name, books_in_series in series_books.items():
            # Fix 1: Ensure consistent series name (trim whitespace, etc.)
            clean_series_name = series_name.strip()
            if clean_series_name != series_name:
                for book in books_in_series:
                    change = {
                        "book_id": book["id"],
                        "field": "series",
                        "old_value": book["series"],
                        "new_value": clean_series_name,
                    }
                    changes.append(change)
                    if not dry_run:
                        book["series"] = clean_series_name
                        await storage.update_book(book["id"], book)

            # Fix 2: Ensure series_index is set and is a number
            for book in books_in_series:
                if "series_index" not in book or not isinstance(book["series_index"], (int, float)):
                    change = {
                        "book_id": book["id"],
                        "field": "series_index",
                        "old_value": book.get("series_index"),
                        "new_value": 1.0,  # Default value
                    }
                    changes.append(change)
                    if not dry_run:
                        book["series_index"] = 1.0
                        await storage.update_book(book["id"], book)

            # Fix 3: Detect and fix duplicate series indices
            index_map = {}
            for book in books_in_series:
                idx = book.get("series_index", 0)
                if idx in index_map:
                    # Found duplicate index, increment the second one
                    new_idx = idx + 0.1
                    change = {
                        "book_id": book["id"],
                        "field": "series_index",
                        "old_value": idx,
                        "new_value": new_idx,
                        "reason": f"Duplicate series index with book {index_map[idx]}",
                    }
                    changes.append(change)
                    if not dry_run:
                        book["series_index"] = new_idx
                        await storage.update_book(book["id"], book)
                else:
                    index_map[idx] = book["id"]

            # Fix 4: Ensure series_index is sequential
            books_in_series.sort(key=lambda x: x.get("series_index", 0))
            for i, book in enumerate(books_in_series, 1):
                if book.get("series_index") != i:
                    change = {
                        "book_id": book["id"],
                        "field": "series_index",
                        "old_value": book.get("series_index"),
                        "new_value": i,
                        "reason": "Make series indices sequential",
                    }
                    changes.append(change)
                    if not dry_run:
                        book["series_index"] = i
                        await storage.update_book(book["id"], book)

        return {
            "success": True,
            "changes": changes,
            "total_changes": len(changes),
            "dry_run": dry_run,
        }

    async def merge_series(
        self, library_path: str, source_series: str, target_series: str, dry_run: bool = True
    ) -> Dict:
        """
        Merge one series into another.

        Args:
            library_path: Path to the Calibre library
            source_series: Name of the series to merge from
            target_series: Name of the series to merge into
            dry_run: If True, only show what would be changed

        Returns:
            Dictionary with results of the merge operation
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        if source_series == target_series:
            return {"success": False, "error": "Source and target series cannot be the same"}

        storage = LocalStorage(library_path)
        books = await storage.get_all_books()

        # Find books in both series
        source_books = []
        target_books = []

        for book in books:
            if "series" in book:
                if book["series"] == source_series:
                    source_books.append(book)
                elif book["series"] == target_series:
                    target_books.append(book)

        if not source_books:
            return {"success": False, "error": f"No books found in source series: {source_series}"}

        # Calculate the offset for series indices
        offset = 0
        if target_books:
            max_index = max(book.get("series_index", 0) for book in target_books)
            offset = max_index + 1

        # Prepare changes
        changes = []

        for book in source_books:
            old_series = book.get("series")
            old_index = book.get("series_index", 0)
            new_index = old_index + offset

            changes.append(
                {
                    "book_id": book["id"],
                    "title": book.get("title", "Unknown"),
                    "old_series": old_series,
                    "new_series": target_series,
                    "old_index": old_index,
                    "new_index": new_index,
                }
            )

            if not dry_run:
                book["series"] = target_series
                book["series_index"] = new_index
                await storage.update_book(book["id"], book)

        return {
            "success": True,
            "source_series": source_series,
            "target_series": target_series,
            "books_moved": len(changes),
            "changes": changes,
            "dry_run": dry_run,
        }

    async def _analyze_series(self, series_name: str, books: List[Dict]) -> SeriesInfo:
        """Analyze a single series."""
        series_info = SeriesInfo(name=series_name)

        # Add all books to the series
        for book in books:
            series_info.add_book(book)

        # Sort books by series index
        series_info.sort_books()

        # Calculate statistics
        series_info.total_books = len(series_info.books)

        # Check for gaps in series indices
        indices = [float(b.get("series_index", 0)) for b in series_info.books]
        if indices:
            expected_indices = set(range(1, int(max(indices)) + 1))
            actual_indices = set(int(i) for i in indices if i == int(i))
            missing_indices = expected_indices - actual_indices

            if missing_indices:
                series_info.description = f"Missing books at positions: {sorted(missing_indices)}"
            elif all(i == int(i) for i in indices) and max(indices) == len(indices):
                series_info.is_complete = True

        return series_info

    async def _update_series_metadata(self, storage, series_info: SeriesInfo) -> int:
        """Update book metadata with series information."""
        updated = 0

        for book in series_info.books:
            # Check if any updates are needed
            needs_update = False

            if book.get("series") != series_info.name:
                book["series"] = series_info.name
                needs_update = True

            # Check if series_index needs updating
            current_idx = book.get("series_index")
            if current_idx is None or current_idx != book.get("series_index"):
                book["series_index"] = book.get("series_index", 0)
                needs_update = True

            # Save changes if needed
            if needs_update:
                await storage.update_book(book["id"], book)
                updated += 1

        return updated


class SeriesMergeOptions(BaseModel):
    """Options for merging series."""

    dry_run: bool = Field(True, description="If True, only show what would be changed")

    class Config:
        schema_extra = {"example": {"dry_run": True}}
