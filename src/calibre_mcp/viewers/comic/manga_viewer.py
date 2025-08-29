"""
Manga/Comic viewer for CalibreMCP with support for CBZ, CBR, and other formats.
"""
import os
import io
import json
import zipfile
import rarfile
import hashlib
import sqlite3
import tempfile
from pathlib import Path
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Union, BinaryIO, Any, Generator
from datetime import datetime
from PIL import Image, ImageOps

class ReadingDirection(Enum):
    """Reading direction for manga/comics."""
    LEFT_TO_RIGHT = "ltr"
    RIGHT_TO_LEFT = "rtl"
    VERTICAL = "vertical"

class PageLayout(Enum):
    """Page layout mode."""
    SINGLE = "single"
    DOUBLE = "double"
    AUTO = "auto"

class ZoomMode(Enum):
    """Zoom mode for the viewer."""
    FIT_WIDTH = "fit-width"
    FIT_HEIGHT = "fit-height"
    FIT_BOTH = "fit-both"
    ORIGINAL = "original"
    CUSTOM = "custom"

class ComicMetadata(BaseModel):
    """Comic book metadata."""
    title: str = ""
    series: str = ""
    volume: str = ""
    number: str = ""
    summary: str = ""
    publisher: str = ""
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    page_count: int = 0
    file_path: str = ""
    file_hash: str = ""
    file_size: int = 0
    file_extension: str = ""
    is_manga: bool = False

class ComicViewerState(BaseModel):
    """Current state of the comic viewer."""
    current_page: int = 0
    reading_direction: ReadingDirection = ReadingDirection.RIGHT_TO_LEFT
    page_layout: PageLayout = PageLayout.SINGLE
    zoom_mode: ZoomMode = ZoomMode.FIT_WIDTH
    zoom_level: float = 1.0
    scroll_position: Tuple[float, float] = (0, 0)
    bookmarks: List[Dict[str, Any]] = []
    last_read: Optional[datetime] = None
    reading_progress: float = 0.0
    show_controls: bool = True
    show_thumbnails: bool = True
    show_page_numbers: bool = True
    background_color: str = "#000000"
    custom_css: str = ""

class MangaViewer:
    """Manga/Comic viewer with support for CBZ, CBR, and other formats."""
    
    SUPPORTED_FORMATS = ['cbz', 'cbr', 'zip', 'rar']
    IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}
    
    def __init__(self, db_path: Optional[str] = None):
        self._file_path: Optional[Path] = None
        self._metadata = ComicMetadata()
        self._state = ComicViewerState()
        self._db_path = db_path or ":memory:"
        self._db_conn = None
        self._archive = None
        self._pages: List[Dict[str, Any]] = []
        self._temp_dir = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize the SQLite database for bookmarks and reading progress."""
        self._db_conn = sqlite3.connect(self._db_path, check_same_thread=False)
        cursor = self._db_conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id TEXT PRIMARY KEY,
            file_hash TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reading_progress (
            file_hash TEXT PRIMARY KEY,
            page_number INTEGER NOT NULL,
            percentage REAL NOT NULL,
            last_read TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reading_direction TEXT NOT NULL DEFAULT 'rtl',
            page_layout TEXT NOT NULL DEFAULT 'single',
            zoom_mode TEXT NOT NULL DEFAULT 'fit-width',
            zoom_level REAL NOT NULL DEFAULT 1.0
        )
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_bookmarks_file_hash 
        ON bookmarks(file_hash)
        """)
        
        self._db_conn.commit()
    
    def _get_file_hash(self, file_path: Union[str, Path]) -> str:
        """Calculate a hash of the file for identification."""
        file_path = Path(file_path)
        hasher = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
                
        return hasher.hexdigest()
    
    def load(self, file_path: Union[str, Path]) -> None:
        """Load a comic/manga file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.close()  # Close any previously opened file
        
        # Set up metadata
        self._file_path = file_path
        file_hash = self._get_file_hash(file_path)
        file_ext = file_path.suffix.lower()[1:]
        
        self._metadata = ComicMetadata(
            file_path=str(file_path),
            file_hash=file_hash,
            file_size=file_path.stat().st_size,
            file_extension=file_ext,
            title=file_path.stem,
            is_manga=self._is_likely_manga(file_path)
        )
        
        # Open the archive
        self._open_archive(file_path, file_ext)
        
        # Load bookmarks and reading progress
        self._load_bookmarks(file_hash)
        self._load_reading_progress(file_hash)
    
    def _is_likely_manga(self, file_path: Path) -> bool:
        """Determine if the file is likely a manga based on filename and path."""
        manga_terms = {'manga', 'raw', 'japanese', 'jp', 'jpn', 'jap'}
        path_lower = str(file_path).lower()
        return any(term in path_lower for term in manga_terms)
    
    def _open_archive(self, file_path: Path, file_ext: str) -> None:
        """Open the comic archive file."""
        self._temp_dir = tempfile.TemporaryDirectory(prefix="calibremcp_manga_")
        
        try:
            if file_ext in ('cbz', 'zip'):
                self._archive = zipfile.ZipFile(file_path, 'r')
                self._load_zip_pages()
            elif file_ext in ('cbr', 'rar'):
                self._archive = rarfile.RarFile(file_path, 'r')
                self._load_rar_pages()
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
            # Sort pages by filename
            self._pages.sort(key=lambda x: x['index'])
            self._metadata.page_count = len(self._pages)
            
        except Exception as e:
            self.close()
            raise RuntimeError(f"Failed to open archive: {e}")
    
    def _load_zip_pages(self) -> None:
        """Load pages from a ZIP archive."""
        self._pages = []
        
        for idx, filename in enumerate(self._archive.namelist()):
            if not self._is_image_file(filename):
                continue
                
            try:
                with self._archive.open(filename) as f:
                    data = f.read()
                    
                    # Verify it's a valid image
                    try:
                        img = Image.open(io.BytesIO(data))
                        img.verify()
                        
                        self._pages.append({
                            'index': idx,
                            'name': os.path.basename(filename),
                            'data': data,
                            'width': img.width,
                            'height': img.height,
                            'format': img.format
                        })
                    except (IOError, OSError):
                        continue
                        
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    def _load_rar_pages(self) -> None:
        """Load pages from a RAR archive."""
        self._pages = []
        
        for idx, file_info in enumerate(self._archive.infolist()):
            if not self._is_image_file(file_info.filename):
                continue
                
            try:
                with self._archive.open(file_info) as f:
                    data = f.read()
                    
                    # Verify it's a valid image
                    try:
                        img = Image.open(io.BytesIO(data))
                        img.verify()
                        
                        self._pages.append({
                            'index': idx,
                            'name': os.path.basename(file_info.filename),
                            'data': data,
                            'width': img.width,
                            'height': img.height,
                            'format': img.format
                        })
                    except (IOError, OSError):
                        continue
                        
            except Exception as e:
                print(f"Error processing {file_info.filename}: {e}")
    
    def _is_image_file(self, filename: str) -> bool:
        """Check if a filename has an image extension."""
        ext = os.path.splitext(filename)[1].lower()[1:]
        return ext in self.IMAGE_EXTENSIONS
    
    def _load_bookmarks(self, file_hash: str) -> None:
        """Load bookmarks from the database."""
        if not self._db_conn:
            return
            
        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            SELECT id, page_number, name, created_at
            FROM bookmarks
            WHERE file_hash = ?
            ORDER BY created_at
            """,
            (file_hash,)
        )
        
        self._state.bookmarks = [
            {
                'id': row[0],
                'page_number': row[1],
                'name': row[2],
                'created_at': row[3]
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
            SELECT page_number, percentage, last_read, 
                   reading_direction, page_layout, zoom_mode, zoom_level
            FROM reading_progress
            WHERE file_hash = ?
            """,
            (file_hash,)
        )
        
        row = cursor.fetchone()
        if row:
            self._state.current_page = max(0, min(row[0], len(self._pages) - 1)) if self._pages else 0
            self._state.reading_progress = row[1] or 0.0
            self._state.last_read = row[2]
            
            # Load reading settings if available
            if row[3]:
                try:
                    self._state.reading_direction = ReadingDirection(row[3])
                except ValueError:
                    pass
            
            if row[4]:
                try:
                    self._state.page_layout = PageLayout(row[4])
                except ValueError:
                    pass
            
            if row[5]:
                try:
                    self._state.zoom_mode = ZoomMode(row[5])
                except ValueError:
                    pass
            
            if row[6] is not None:
                self._state.zoom_level = max(0.1, min(row[6], 5.0))
    
    def save_reading_progress(self) -> None:
        """Save the current reading progress to the database."""
        if not self._metadata or not self._db_conn or not self._pages:
            return
            
        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            INSERT INTO reading_progress (
                file_hash, page_number, percentage, last_read,
                reading_direction, page_layout, zoom_mode, zoom_level
            )
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?)
            ON CONFLICT(file_hash) DO UPDATE SET
                page_number = excluded.page_number,
                percentage = excluded.percentage,
                last_read = excluded.last_read,
                reading_direction = excluded.reading_direction,
                page_layout = excluded.page_layout,
                zoom_mode = excluded.zoom_mode,
                zoom_level = excluded.zoom_level
            """,
            (
                self._metadata.file_hash,
                self._state.current_page,
                self._state.reading_progress,
                self._state.reading_direction.value,
                self._state.page_layout.value,
                self._state.zoom_mode.value,
                self._state.zoom_level
            )
        )
        
        self._db_conn.commit()
    
    def add_bookmark(self, page_number: int, name: str = "") -> Dict[str, Any]:
        """Add a new bookmark."""
        if not self._metadata or not self._db_conn or not self._pages:
            raise RuntimeError("No comic file loaded")
            
        if page_number < 0 or page_number >= len(self._pages):
            raise ValueError("Invalid page number")
            
        bookmark_id = f"bm_{hashlib.sha256(f'{self._metadata.file_hash}:{page_number}'.encode()).hexdigest()[:16]}"
        
        # Create the bookmark
        bookmark = {
            'id': bookmark_id,
            'page_number': page_number,
            'name': name or f"Page {page_number + 1}",
            'created_at': datetime.utcnow()
        }
        
        # Save to database
        cursor = self._db_conn.cursor()
        cursor.execute(
            """
            INSERT INTO bookmarks (id, file_hash, page_number, name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name
            """,
            (
                bookmark_id,
                self._metadata.file_hash,
                page_number,
                name or f"Page {page_number + 1}"
            )
        )
        
        self._db_conn.commit()
        
        # Add to in-memory state if not already present
        if not any(bm['id'] == bookmark_id for bm in self._state.bookmarks):
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
            self._state.bookmarks = [bm for bm in self._state.bookmarks if bm['id'] != bookmark_id]
            
        return deleted
    
    def get_page(self, page_number: int) -> Optional[Dict[str, Any]]:
        """Get a page by index."""
        if not self._pages or page_number < 0 or page_number >= len(self._pages):
            return None
            
        return self._pages[page_number]
    
    def get_page_image(self, page_number: int, max_size: Optional[Tuple[int, int]] = None) -> Optional[bytes]:
        """Get a page image, optionally resized."""
        page = self.get_page(page_number)
        if not page:
            return None
            
        try:
            img = Image.open(io.BytesIO(page['data']))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # Resize if needed
            if max_size and (img.width > max_size[0] or img.height > max_size[1]):
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=85)
            return img_byte_arr.getvalue()
            
        except Exception as e:
            print(f"Error processing page {page_number}: {e}")
            return None
    
    def get_cover_image(self) -> Optional[bytes]:
        """Get the cover image."""
        if not self._pages:
            return None
            
        return self.get_page_image(0, max_size=(800, 1200))
    
    def navigate(self, direction: int) -> bool:
        """Navigate to the next or previous page."""
        if not self._pages:
            return False
            
        new_page = self._state.current_page + direction
        
        # Handle page boundaries
        if new_page < 0:
            new_page = 0
        elif new_page >= len(self._pages):
            new_page = len(self._pages) - 1
        
        if new_page != self._state.current_page:
            self._state.current_page = new_page
            
            # Update reading progress
            self._state.reading_progress = (new_page + 1) / len(self._pages) * 100
            self.save_reading_progress()
            
            return True
            
        return False
    
    def set_reading_direction(self, direction: Union[str, ReadingDirection]) -> None:
        """Set the reading direction."""
        if isinstance(direction, str):
            direction = ReadingDirection(direction.lower())
            
        if direction != self._state.reading_direction:
            self._state.reading_direction = direction
            self.save_reading_progress()
    
    def set_page_layout(self, layout: Union[str, PageLayout]) -> None:
        """Set the page layout mode."""
        if isinstance(layout, str):
            layout = PageLayout(layout.lower())
            
        if layout != self._state.page_layout:
            self._state.page_layout = layout
            self.save_reading_progress()
    
    def set_zoom_mode(self, zoom_mode: Union[str, ZoomMode]) -> None:
        """Set the zoom mode."""
        if isinstance(zoom_mode, str):
            zoom_mode = ZoomMode(zoom_mode.lower())
            
        if zoom_mode != self._state.zoom_mode:
            self._state.zoom_mode = zoom_mode
            self.save_reading_progress()
    
    def set_zoom_level(self, zoom_level: float) -> None:
        """Set the zoom level (1.0 = 100%)."""
        zoom_level = max(0.1, min(zoom_level, 5.0))  # Clamp between 0.1x and 5.0x
        
        if zoom_level != self._state.zoom_level:
            self._state.zoom_level = zoom_level
            self._state.zoom_mode = ZoomMode.CUSTOM
            self.save_reading_progress()
    
    def get_metadata(self) -> ComicMetadata:
        """Get the comic metadata."""
        return self._metadata
    
    def get_state(self) -> ComicViewerState:
        """Get the current viewer state."""
        return self._state
    
    def close(self) -> None:
        """Clean up resources."""
        if self._archive:
            try:
                self._archive.close()
            except:
                pass
            self._archive = None
            
        if self._temp_dir:
            try:
                self._temp_dir.cleanup()
            except:
                pass
            self._temp_dir = None
            
        if self._db_conn:
            try:
                self._db_conn.close()
            except:
                pass
            self._db_conn = None
            
        self._file_path = None
        self._metadata = ComicMetadata()
        self._state = ComicViewerState()
        self._pages = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manga/Comic Viewer")
    parser.add_argument("file", help="Path to the comic/manga file (CBZ, CBR, ZIP, RAR)")
    args = parser.parse_args()
    
    with MangaViewer() as viewer:
        viewer.load(args.file)
        print(f"Loaded: {viewer.get_metadata().title}")
        print(f"Pages: {len(viewer._pages)}")
        print(f"Reading direction: {viewer.get_state().reading_direction}")
