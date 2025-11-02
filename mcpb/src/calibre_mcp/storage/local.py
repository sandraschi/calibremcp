"""
Local storage backend for Calibre MCP.

Provides direct access to Calibre's SQLite database for local libraries.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Union

from ..models.book import Book
from ..models.library import LibraryInfo
from . import StorageBackend

logger = logging.getLogger(__name__)


class LocalStorage(StorageBackend):
    """Local storage backend using direct SQLite access"""

    def __init__(self, library_path: Optional[Path] = None):
        """
        Initialize local storage backend.

        Args:
            library_path: Path to the Calibre library directory
        """
        # Convert string path to Path object if needed
        if library_path and isinstance(library_path, str):
            library_path = Path(library_path)

        self.library_path = library_path
        self.db_path = self._find_metadata_db()

        if not self.db_path or not self.db_path.exists():
            error_msg = f"Could not find metadata.db in {self.library_path or 'default locations'}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Using Calibre library at: {self.db_path.parent}")

    def _find_metadata_db(self) -> Optional[Path]:
        """Locate the metadata.db file"""
        # First try the explicitly provided path
        if self.library_path:
            # Check if it's a direct path to metadata.db
            if self.library_path.name == "metadata.db" and self.library_path.exists():
                return self.library_path

            # Check if it's a library directory containing metadata.db
            db_path = self.library_path / "metadata.db"
            if db_path.exists():
                return db_path

            # Check if it's a parent directory containing library subdirectories
            for subdir in self.library_path.iterdir():
                if subdir.is_dir():
                    db_path = subdir / "metadata.db"
                    if db_path.exists():
                        return db_path

        # Try default locations if not found in specified path
        default_paths = [
            Path("L:/Multimedia Files/Written Word/Main Library/metadata.db"),
            Path.home() / "Calibre Library/metadata.db",
            Path("C:/Calibre Library/metadata.db"),
        ]

        for path in default_paths:
            if path.exists():
                return path

        logger.warning("Could not find metadata.db in any default location")
        return None

    def _get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)

    async def list_books(self, **filters) -> List[Book]:
        """List books with optional filtering"""
        query = """
        SELECT id, title, sort, timestamp, pubdate, series_index, author_sort, 
               path, has_cover, last_modified, uuid
        FROM books
        """

        params = []
        conditions = []

        # Add filter conditions
        if "author" in filters:
            conditions.append("""
                id IN (
                    SELECT book FROM authors a 
                    JOIN books_authors_link bal ON a.id = bal.author 
                    WHERE a.name LIKE ?
                )
            """)
            params.append(f"%{filters['author']}%")

        if "title" in filters:
            conditions.append("title LIKE ?")
            params.append(f"%{filters['title']}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Add sorting
        query += " ORDER BY sort"

        # Add limit if specified
        if "limit" in filters:
            query += " LIMIT ?"
            params.append(filters["limit"])

        books = []
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)

                for row in cursor.fetchall():
                    book = Book(
                        id=row["id"],
                        title=row["title"],
                        authors=row["author_sort"].split(", ") if row["author_sort"] else [],
                        timestamp=row["timestamp"],
                        pubdate=row["pubdate"],
                        series_index=row["series_index"],
                        path=str(self.library_path / row["path"]) if self.library_path else "",
                        has_cover=bool(row["has_cover"]),
                        last_modified=row["last_modified"],
                        uuid=row["uuid"],
                    )
                    books.append(book)

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise

        return books

    async def get_book(self, book_id: Union[int, str]) -> Optional[Book]:
        """Get a book by ID"""
        query = """
        SELECT id, title, sort, timestamp, pubdate, series_index, author_sort, 
               path, has_cover, last_modified, uuid
        FROM books
        WHERE id = ?
        """

        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, (str(book_id),))
                row = cursor.fetchone()

                if not row:
                    return None

                return Book(
                    id=row["id"],
                    title=row["title"],
                    authors=row["author_sort"].split(", ") if row["author_sort"] else [],
                    timestamp=row["timestamp"],
                    pubdate=row["pubdate"],
                    series_index=row["series_index"],
                    path=str(self.library_path / row["path"]) if self.library_path else "",
                    has_cover=bool(row["has_cover"]),
                    last_modified=row["last_modified"],
                    uuid=row["uuid"],
                )

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise

    async def get_library_info(self) -> LibraryInfo:
        """Get library metadata"""
        book_count = 0
        total_size = 0

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get book count
                cursor.execute("SELECT COUNT(*) FROM books")
                book_count = cursor.fetchone()[0]

                # Get total size of formats
                cursor.execute("""
                    SELECT SUM(size) FROM data
                    WHERE book IN (SELECT id FROM books)
                """)
                total_size = cursor.fetchone()[0] or 0

        except sqlite3.Error as e:
            logger.error(f"Failed to get library info: {e}")
            raise

        return LibraryInfo(
            name="Local Library",
            path=str(self.library_path) if self.library_path else "",
            book_count=book_count,
            total_size=total_size,
            is_local=True,
        )
