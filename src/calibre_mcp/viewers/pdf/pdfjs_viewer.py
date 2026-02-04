"""
Enhanced PDF Viewer using PDF.js for CalibreMCP.
"""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Bookmark(BaseModel):
    """Represents a bookmark in a PDF."""

    id: str
    title: str
    page_number: int
    parent_id: str | None = None
    children: list["Bookmark"] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    custom_data: dict[str, Any] = Field(default_factory=dict)


class PDFMetadata(BaseModel):
    """PDF metadata extracted from the document."""

    title: str | None = None
    author: str | None = None
    subject: str | None = None
    keywords: str | None = None
    creator: str | None = None
    producer: str | None = None
    creation_date: datetime | None = None
    modification_date: datetime | None = None
    page_count: int = 0
    file_size: int = 0
    file_path: str
    file_hash: str


class PDFViewerState(BaseModel):
    """Current state of the PDF viewer."""

    current_page: int = 0
    zoom_level: float = 1.0
    scroll_position: tuple[float, float] = (0, 0)
    view_mode: str = "single"  # single, double, continuous
    rotation: int = 0  # 0, 90, 180, 270
    bookmarks: list[Bookmark] = Field(default_factory=list)
    toc: list[dict[str, Any]] = Field(default_factory=list)
    annotations: list[dict[str, Any]] = Field(default_factory=list)


class PDFViewer:
    """Enhanced PDF viewer using PDF.js with bookmark and TOC support."""

    SUPPORTED_FORMATS = ["pdf"]

    def __init__(self, db_path: str | None = None):
        """Initialize the PDF viewer.

        Args:
            db_path: Path to the SQLite database for storing bookmarks and annotations.
                     If None, uses in-memory storage.
        """
        self._file_path: Path | None = None
        self._metadata: PDFMetadata | None = None
        self._state = PDFViewerState()
        self._db_path = db_path or ":memory:"
        self._db_conn = None
        self._initialize_database()

    @classmethod
    def supports_format(cls, file_extension: str) -> bool:
        """Check if this viewer supports the given file format."""
        return file_extension.lower() in cls.SUPPORTED_FORMATS

    def _initialize_database(self) -> None:
        """Initialize the SQLite database for bookmarks and annotations."""
        self._db_conn = sqlite3.connect(self._db_path, check_same_thread=False)
        cursor = self._db_conn.cursor()

        # Create bookmarks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id TEXT PRIMARY KEY,
            file_hash TEXT NOT NULL,
            title TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            parent_id TEXT,
            custom_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES bookmarks (id) ON DELETE CASCADE
        )
        """)

        # Create annotations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS annotations (
            id TEXT PRIMARY KEY,
            file_hash TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            type TEXT NOT NULL,  -- highlight, underline, note, etc.
            content TEXT,
            position TEXT,  -- JSON string with position data
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_file_hash ON bookmarks(file_hash)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_annotations_file_hash ON annotations(file_hash)"
        )

        self._db_conn.commit()

    def _get_file_hash(self, file_path: str | Path) -> str:
        """Calculate a hash of the file for identification."""
        file_path = Path(file_path)
        hasher = hashlib.sha256()

        with open(file_path, "rb") as f:
            while chunk := f.read(65536):  # 64KB chunks
                hasher.update(chunk)

        return hasher.hexdigest()

    def load(self, file_path: str) -> None:
        """Load a PDF file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        self._file_path = file_path
        file_hash = self._get_file_hash(file_path)

        # Extract basic metadata
        self._metadata = PDFMetadata(
            file_path=str(file_path), file_hash=file_hash, file_size=file_path.stat().st_size
        )

        # Load bookmarks and annotations from the database
        self._load_bookmarks(file_hash)
        self._load_annotations(file_hash)

        # Extract PDF metadata (title, author, etc.)
        self._extract_pdf_metadata()

        # Extract TOC
        self._extract_toc()

    def _extract_pdf_metadata(self) -> None:
        """Extract metadata from the PDF file."""
        try:
            import fitz  # PyMuPDF

            with fitz.open(self._file_path) as doc:
                metadata = doc.metadata

                if self._metadata:
                    self._metadata.title = metadata.get("title", "").strip() or self._file_path.stem
                    self._metadata.author = metadata.get("author", "").strip()
                    self._metadata.subject = metadata.get("subject", "").strip()
                    self._metadata.keywords = metadata.get("keywords", "").strip()
                    self._metadata.creator = metadata.get("creator", "").strip()
                    self._metadata.producer = metadata.get("producer", "").strip()

                    # Parse dates
                    for date_field in ["creation_date", "modification_date"]:
                        if date_str := metadata.get(date_field):
                            try:
                                # Try to parse the PDF date format
                                # This is a simplified version - in a real app, you'd need a proper PDF date parser
                                if "D:" in date_str:
                                    date_str = date_str[2:]  # Remove 'D:' prefix
                                    date_obj = datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")
                                    setattr(self._metadata, date_field, date_obj)
                            except (ValueError, TypeError):
                                pass

                    self._metadata.page_count = len(doc)
        except ImportError:
            # Fallback if PyMuPDF is not available
            pass

    def _extract_toc(self) -> None:
        """Extract table of contents from the PDF."""
        try:
            import fitz  # PyMuPDF

            with fitz.open(self._file_path) as doc:
                toc = doc.get_toc(simple=False)
                self._state.toc = self._process_toc(toc)

                # If no TOC found, create a simple page list
                if not self._state.toc and self._metadata:
                    self._state.toc = [
                        {"title": f"Page {i + 1}", "page": i, "level": 1}
                        for i in range(self._metadata.page_count)
                    ]
        except ImportError:
            # Fallback if PyMuPDF is not available
            if self._metadata:
                self._state.toc = [
                    {"title": f"Page {i + 1}", "page": i, "level": 1}
                    for i in range(self._metadata.page_count)
                ]

    def _process_toc(
        self, toc_items: list[tuple[int, str, int, dict[str, Any]]]
    ) -> list[dict[str, Any]]:
        """Process the raw TOC items into a hierarchical structure."""

        def build_hierarchy(items, level=1):
            result = []
            i = 0

            while i < len(items):
                item = items[i]
                current_level, title, page, _ = item

                if current_level < level:
                    # Move back up in the hierarchy
                    break

                if current_level > level:
                    # Skip or handle malformed TOC
                    i += 1
                    continue

                # Create the node
                node = {
                    "title": title,
                    "page": page - 1,  # Convert to 0-based
                    "level": level,
                    "children": [],
                }

                # Process children
                i += 1
                if i < len(items) and items[i][0] > level:
                    node["children"], i = build_hierarchy(items[i:], level + 1)

                result.append(node)

            return result, i

        result, _ = build_hierarchy(toc_items)
        return result

    def _load_bookmarks(self, file_hash: str) -> None:
        """Load bookmarks from the database."""
        if not self._db_conn:
            return

        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            SELECT id, title, page_number, parent_id, custom_data, created_at, modified_at
            FROM bookmarks
            WHERE file_hash = ?
            ORDER BY created_at
            """,
            (file_hash,),
        )

        # Build a flat list of bookmarks
        bookmarks = []
        bookmark_map = {}

        for row in cursor.fetchall():
            bookmark = Bookmark(
                id=row[0],
                title=row[1],
                page_number=row[2],
                parent_id=row[3],
                custom_data=json.loads(row[4] or "{}"),
                created_at=row[5],
                modified_at=row[6],
            )
            bookmarks.append(bookmark)
            bookmark_map[bookmark.id] = bookmark

        # Build the hierarchy
        root_bookmarks = []

        for bookmark in bookmarks:
            if bookmark.parent_id:
                parent = bookmark_map.get(bookmark.parent_id)
                if parent:
                    parent.children.append(bookmark)
            else:
                root_bookmarks.append(bookmark)

        self._state.bookmarks = root_bookmarks

    def _load_annotations(self, file_hash: str) -> None:
        """Load annotations from the database."""
        if not self._db_conn:
            return

        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            SELECT id, page_number, type, content, position, created_at, modified_at
            FROM annotations
            WHERE file_hash = ?
            ORDER BY created_at
            """,
            (file_hash,),
        )

        self._state.annotations = [
            {
                "id": row[0],
                "page_number": row[1],
                "type": row[2],
                "content": row[3],
                "position": json.loads(row[4] or "{}"),
                "created_at": row[5],
                "modified_at": row[6],
            }
            for row in cursor.fetchall()
        ]

    def add_bookmark(
        self,
        title: str,
        page_number: int,
        parent_id: str | None = None,
        custom_data: dict[str, Any] | None = None,
    ) -> Bookmark:
        """Add a new bookmark."""
        if not self._metadata or not self._db_conn:
            raise RuntimeError("No PDF file loaded")

        bookmark_id = f"bm_{hashlib.sha256(f'{self._metadata.file_hash}:{title}:{page_number}'.encode()).hexdigest()[:16]}"

        # Create the bookmark
        bookmark = Bookmark(
            id=bookmark_id,
            title=title,
            page_number=page_number,
            parent_id=parent_id,
            custom_data=custom_data or {},
        )

        # Save to database
        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            INSERT INTO bookmarks (id, file_hash, title, page_number, parent_id, custom_data)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                page_number = excluded.page_number,
                parent_id = excluded.parent_id,
                custom_data = excluded.custom_data,
                modified_at = CURRENT_TIMESTAMP
            """,
            (
                bookmark_id,
                self._metadata.file_hash,
                title,
                page_number,
                parent_id,
                json.dumps(custom_data or {}),
            ),
        )

        self._db_conn.commit()

        # Add to in-memory state
        if parent_id:
            # Find the parent and add as a child
            def find_parent(bookmarks):
                for bm in bookmarks:
                    if bm.id == parent_id:
                        return bm
                    if bm.children:
                        if found := find_parent(bm.children):
                            return found
                return None

            if parent := find_parent(self._state.bookmarks):
                parent.children.append(bookmark)
        else:
            self._state.bookmarks.append(bookmark)

        return bookmark

    def remove_bookmark(self, bookmark_id: str) -> bool:
        """Remove a bookmark by ID."""
        if not self._metadata or not self._db_conn:
            return False

        # Delete from database (cascades to children)
        cursor = self._db_conn.cursor()
        cursor.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        deleted = cursor.rowcount > 0
        self._db_conn.commit()

        # Remove from in-memory state
        def remove_from_list(bookmarks):
            for i, bm in enumerate(bookmarks):
                if bm.id == bookmark_id:
                    bookmarks.pop(i)
                    return True
                if bm.children and remove_from_list(bm.children):
                    return True
            return False

        if deleted:
            remove_from_list(self._state.bookmarks)

        return deleted

    def get_bookmarks(self) -> list[Bookmark]:
        """Get all bookmarks."""
        return self._state.bookmarks

    def get_toc(self) -> list[dict[str, Any]]:
        """Get the table of contents."""
        return self._state.toc

    def get_metadata(self) -> PDFMetadata | None:
        """Get PDF metadata."""
        return self._metadata

    def get_state(self) -> PDFViewerState:
        """Get the current viewer state."""
        return self._state

    def close(self) -> None:
        """Clean up resources."""
        if self._db_conn:
            self._db_conn.close()
            self._db_conn = None

        self._file_path = None
        self._metadata = None
        self._state = PDFViewerState()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
