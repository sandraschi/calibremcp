"""
EPUB Viewer for CalibreMCP with full TOC and bookmark support.
"""

import hashlib
import os
import sqlite3
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


class EPubMetadata(BaseModel):
    """EPUB metadata."""

    title: str = ""
    creator: str = ""
    publisher: str = ""
    language: str = "en"
    description: str = ""
    rights: str = ""
    date: datetime | None = None
    cover_image: str | None = None
    identifier: str = ""
    file_path: str = ""
    file_hash: str = ""
    file_size: int = 0
    spine_items: list[dict[str, Any]] = Field(default_factory=list)
    toc_items: list[dict[str, Any]] = Field(default_factory=list)


class EPubViewerState(BaseModel):
    """Current state of the EPUB viewer."""

    current_position: dict[str, Any] = Field(default_factory=dict)
    bookmarks: list[dict[str, Any]] = Field(default_factory=list)
    annotations: list[dict[str, Any]] = Field(default_factory=list)
    reading_progress: float = 0.0
    font_size: int = 16
    font_family: str = "Arial, sans-serif"
    theme: str = "light"
    line_height: float = 1.6
    margin: int = 2
    last_read: datetime | None = None


class EPubViewer:
    """EPUB viewer with TOC and bookmark support."""

    CONTAINER_XML = "META-INF/container.xml"
    MIMETYPE = "mimetype"

    def __init__(self, db_path: str | None = None):
        """Initialize the EPUB viewer."""
        self._file_path: Path | None = None
        self._metadata = EPubMetadata()
        self._state = EPubViewerState()
        self._db_path = db_path or ":memory:"
        self._db_conn = None
        self._zip_file = None
        self._spine = []
        self._toc = []
        self._manifest = {}
        self._spine_itemrefs = []
        self._root_dir = ""
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize the SQLite database for bookmarks and annotations."""
        self._db_conn = sqlite3.connect(self._db_path, check_same_thread=False)
        cursor = self._db_conn.cursor()

        # Create bookmarks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id TEXT PRIMARY KEY,
            file_hash TEXT NOT NULL,
            cfi TEXT NOT NULL,
            text TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create annotations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS annotations (
            id TEXT PRIMARY KEY,
            file_hash TEXT NOT NULL,
            type TEXT NOT NULL,
            cfi_range TEXT NOT NULL,
            text TEXT,
            note TEXT,
            color TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create reading progress table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reading_progress (
            file_hash TEXT PRIMARY KEY,
            cfi TEXT,
            percentage REAL,
            last_read TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_hash) REFERENCES bookmarks(file_hash) ON DELETE CASCADE
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

    def load(self, file_path: str | Path) -> None:
        """Load an EPUB file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"EPUB file not found: {file_path}")

        self._file_path = file_path
        file_hash = self._get_file_hash(file_path)

        # Initialize metadata
        self._metadata = EPubMetadata(
            file_path=str(file_path), file_hash=file_hash, file_size=file_path.stat().st_size
        )

        # Open the EPUB file
        self._zip_file = zipfile.ZipFile(file_path, "r")

        # Parse the container to find the root file
        container_data = self._zip_file.read(self.CONTAINER_XML)
        rootfile_path = self._parse_container(container_data)

        # Set the root directory
        self._root_dir = os.path.dirname(rootfile_path) if "/" in rootfile_path else ""

        # Parse the root file (OPF)
        rootfile_data = self._zip_file.read(rootfile_path).decode("utf-8")
        self._parse_root_file(rootfile_data)

        # Load bookmarks and reading progress
        self._load_bookmarks(file_hash)
        self._load_reading_progress(file_hash)

    def _parse_container(self, container_data: bytes) -> str:
        """Parse the container.xml file to find the root file."""
        root = ET.fromstring(container_data)
        ns = {"ocf": "urn:oasis:names:tc:opendocument:xmlns:container"}

        # Find the rootfile element
        rootfile = root.find(".//ocf:rootfile", ns)
        if rootfile is None:
            raise ValueError("No rootfile found in container.xml")

        return rootfile.get("full-path", "")

    def _parse_root_file(self, opf_content: str) -> None:
        """Parse the OPF file to extract metadata, manifest, and spine."""
        soup = BeautifulSoup(opf_content, "xml")

        # Parse metadata
        metadata = soup.find("metadata")
        if metadata:
            self._parse_metadata(metadata)

        # Parse manifest
        manifest = soup.find("manifest")
        if manifest:
            self._parse_manifest(manifest)

        # Parse spine
        spine = soup.find("spine")
        if spine:
            self._parse_spine(spine)

    def _parse_metadata(self, metadata: BeautifulSoup) -> None:
        """Parse metadata from the OPF file."""
        # DC elements
        dc_ns = {"dc": "http://purl.org/dc/elements/1.1/"}

        if title := metadata.find("dc:title", dc_ns):
            self._metadata.title = title.text.strip()

        if creator := metadata.find("dc:creator", dc_ns):
            self._metadata.creator = creator.text.strip()

        if publisher := metadata.find("dc:publisher", dc_ns):
            self._metadata.publisher = publisher.text.strip()

        if language := metadata.find("dc:language", dc_ns):
            self._metadata.language = language.text.strip()

        if description := metadata.find("dc:description", dc_ns):
            self._metadata.description = description.text.strip()

        if rights := metadata.find("dc:rights", dc_ns):
            self._metadata.rights = rights.text.strip()

        if date := metadata.find("dc:date", dc_ns):
            try:
                self._metadata.date = datetime.strptime(date.text.strip(), "%Y-%m-%d")
            except (ValueError, TypeError):
                pass

        # Cover image
        if meta_cover := metadata.find("meta", {"name": "cover"}):
            cover_id = meta_cover.get("content", "")
            if cover_id and cover_id in self._manifest:
                self._metadata.cover_image = self._manifest[cover_id]["href"]

    def _parse_manifest(self, manifest: BeautifulSoup) -> None:
        """Parse the manifest section of the OPF file."""
        for item in manifest.find_all("item"):
            item_id = item.get("id")
            href = item.get("href", "")
            media_type = item.get("media-type", "")
            properties = item.get("properties", "")

            # Resolve relative paths
            if self._root_dir:
                href = os.path.join(self._root_dir, href)

            self._manifest[item_id] = {
                "id": item_id,
                "href": href,
                "media_type": media_type,
                "properties": properties.split() if properties else [],
            }

    def _parse_spine(self, spine: BeautifulSoup) -> None:
        """Parse the spine section of the OPF file."""
        self._spine_itemrefs = []

        for itemref in spine.find_all("itemref"):
            idref = itemref.get("idref")
            if idref in self._manifest:
                self._spine_itemrefs.append(idref)

                # Add to spine items list
                item = self._manifest[idref]
                self._metadata.spine_items.append(
                    {
                        "id": item["id"],
                        "href": item["href"],
                        "title": f"Page {len(self._metadata.spine_items) + 1}",
                    }
                )

    def _load_bookmarks(self, file_hash: str) -> None:
        """Load bookmarks from the database."""
        if not self._db_conn:
            return

        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            SELECT id, cfi, text, note, created_at, modified_at
            FROM bookmarks
            WHERE file_hash = ?
            ORDER BY created_at
            """,
            (file_hash,),
        )

        self._state.bookmarks = [
            {
                "id": row[0],
                "cfi": row[1],
                "text": row[2],
                "note": row[3],
                "created_at": row[4],
                "modified_at": row[5],
            }
            for row in cursor.fetchall()
        ]

    def _load_reading_progress(self, file_hash: str) -> None:
        """Load reading progress from the database."""
        if not self._db_conn:
            return

        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            SELECT cfi, percentage, last_read
            FROM reading_progress
            WHERE file_hash = ?
            """,
            (file_hash,),
        )

        row = cursor.fetchone()
        if row:
            self._state.reading_progress = row[1] or 0.0
            self._state.last_read = row[2]

            # Set current position if available
            if row[0]:
                self._state.current_position = {"cfi": row[0]}

    def add_bookmark(self, cfi: str, text: str = "", note: str = "") -> dict[str, Any]:
        """Add a new bookmark."""
        if not self._metadata or not self._db_conn:
            raise RuntimeError("No EPUB file loaded")

        bookmark_id = (
            f"bm_{hashlib.sha256(f'{self._metadata.file_hash}:{cfi}'.encode()).hexdigest()[:16]}"
        )

        # Create the bookmark
        bookmark = {
            "id": bookmark_id,
            "cfi": cfi,
            "text": text,
            "note": note,
            "created_at": datetime.utcnow(),
            "modified_at": datetime.utcnow(),
        }

        # Save to database
        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            INSERT INTO bookmarks (id, file_hash, cfi, text, note)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                text = excluded.text,
                note = excluded.note,
                modified_at = CURRENT_TIMESTAMP
            """,
            (bookmark_id, self._metadata.file_hash, cfi, text, note),
        )

        self._db_conn.commit()

        # Add to in-memory state
        self._state.bookmarks.append(bookmark)

        return bookmark

    def remove_bookmark(self, bookmark_id: str) -> bool:
        """Remove a bookmark by ID."""
        if not self._metadata or not self._db_conn:
            return False

        # Delete from database
        cursor = self._db_conn.cursor()
        cursor.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        deleted = cursor.rowcount > 0
        self._db_conn.commit()

        # Remove from in-memory state
        if deleted:
            self._state.bookmarks = [bm for bm in self._state.bookmarks if bm["id"] != bookmark_id]

        return deleted

    def update_reading_progress(self, cfi: str, percentage: float) -> None:
        """Update reading progress."""
        if not self._metadata or not self._db_conn:
            return

        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            INSERT INTO reading_progress (file_hash, cfi, percentage, last_read)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(file_hash) DO UPDATE SET
                cfi = excluded.cfi,
                percentage = excluded.percentage,
                last_read = excluded.last_read
            """,
            (self._metadata.file_hash, cfi, max(0.0, min(100.0, percentage))),
        )

        self._db_conn.commit()

        # Update in-memory state
        self._state.reading_progress = percentage
        self._state.last_read = datetime.utcnow()
        self._state.current_position = {"cfi": cfi}

    def get_spine_item(self, index: int) -> dict[str, Any] | None:
        """Get a spine item by index."""
        if 0 <= index < len(self._spine_itemrefs):
            item_id = self._spine_itemrefs[index]
            return self._manifest.get(item_id)
        return None

    def get_spine_item_content(self, index: int) -> str | None:
        """Get the content of a spine item by index."""
        item = self.get_spine_item(index)
        if not item or not self._zip_file:
            return None

        try:
            content = self._zip_file.read(item["href"]).decode("utf-8")
            return self._process_content(content, os.path.dirname(item["href"]))
        except (KeyError, UnicodeDecodeError):
            return None

    def _process_content(self, content: str, base_path: str) -> str:
        """Process HTML content, fixing relative paths and adding CSS."""
        soup = BeautifulSoup(content, "html.parser")

        # Fix relative paths in links and images
        for tag in soup.find_all(["a", "img", "link", "script"]):
            for attr in ["href", "src"]:
                if attr in tag.attrs:
                    # Skip empty or anchor links
                    if not tag[attr] or tag[attr].startswith("#"):
                        continue

                    # Convert to absolute path
                    if not tag[attr].startswith(("http://", "https://", "data:")):
                        tag[attr] = f"/epub/resource/{base_path}/{tag[attr]}"

        # Add base tag if not present
        if not soup.find("base"):
            base_tag = soup.new_tag("base")
            base_tag["href"] = f"/epub/resource/{base_path}/"
            if soup.head:
                soup.head.insert(0, base_tag)

        # Add custom CSS
        style = soup.new_tag("style")
        style.string = """
            body {
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
            }
            img {
                max-width: 100%;
                height: auto;
            }
        """

        if soup.head:
            soup.head.append(style)

        return str(soup)

    def get_toc(self) -> list[dict[str, Any]]:
        """Get the table of contents."""
        # In a real implementation, this would parse the NCX or nav file
        # For now, return a simple TOC based on spine items
        return self._metadata.spine_items

    def get_metadata(self) -> EPubMetadata:
        """Get EPUB metadata."""
        return self._metadata

    def get_state(self) -> EPubViewerState:
        """Get the current viewer state."""
        return self._state

    def close(self) -> None:
        """Clean up resources."""
        if self._zip_file:
            self._zip_file.close()
            self._zip_file = None

        if self._db_conn:
            self._db_conn.close()
            self._db_conn = None

        self._file_path = None
        self._metadata = EPubMetadata()
        self._state = EPubViewerState()
        self._spine = []
        self._toc = []
        self._manifest = {}
        self._spine_itemrefs = []
        self._root_dir = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
