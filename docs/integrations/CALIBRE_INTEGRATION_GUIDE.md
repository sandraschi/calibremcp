# Calibre Integration Guide

## Overview

CalibreMCP provides comprehensive integration with Calibre ebook library management system. This guide covers all aspects of Calibre integration, from basic setup to advanced features and troubleshooting.

## Table of Contents

1. [Calibre Overview](#calibre-overview)
2. [Installation and Setup](#installation-and-setup)
3. [Library Structure](#library-structure)
4. [API Integration](#api-integration)
5. [Database Integration](#database-integration)
6. [File Management](#file-management)
7. [Metadata Handling](#metadata-handling)
8. [Advanced Features](#advanced-features)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

## Calibre Overview

### What is Calibre?

Calibre is a powerful, open-source ebook library management system that provides:

- **Library Management**: Organize and manage large ebook collections
- **Format Conversion**: Convert between various ebook formats
- **Metadata Management**: Rich metadata handling and editing
- **Content Server**: Web-based library access
- **Device Sync**: Synchronize with e-readers and mobile devices

### Key Features

- **Multi-format Support**: EPUB, PDF, MOBI, AZW3, FB2, TXT, RTF, HTML
- **Metadata Database**: SQLite-based metadata storage
- **Plugin System**: Extensible through plugins
- **Cross-platform**: Windows, macOS, Linux support
- **Content Server**: Web interface for library access

## Installation and Setup

### Prerequisites

- **Python 3.8+**: Required for CalibreMCP
- **Calibre**: Installed and configured
- **SQLite**: For database operations
- **Network Access**: For content server integration

### Calibre Installation

#### Windows
```bash
# Download from https://calibre-ebook.com/download
# Run installer with default settings
```

#### macOS
```bash
# Using Homebrew
brew install --cask calibre

# Or download from website
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install calibre

# CentOS/RHEL
sudo yum install calibre
```

### CalibreMCP Configuration

#### Automatic Library Discovery

CalibreMCP now automatically discovers Calibre libraries, making it universally useful:

```python
from calibre_mcp.config import CalibreConfig

# Auto-discovery enabled by default
config = CalibreConfig.load_config()

# Libraries are automatically discovered
print(f"Found {len(config.discovered_libraries)} libraries")
for name, library in config.discovered_libraries.items():
    print(f"- {name}: {library.path}")
```

#### Environment Variables

```bash
# Calibre Server Configuration
export CALIBRE_SERVER_URL="http://localhost:8080"
export CALIBRE_USERNAME="your_username"
export CALIBRE_PASSWORD="your_password"
export CALIBRE_TIMEOUT=30
export CALIBRE_DEFAULT_LIMIT=50

# Library Discovery (optional - auto-discovery handles most cases)
export CALIBRE_LIBRARY_PATH="/path/to/specific/library"
export CALIBRE_LIBRARIES="/path/lib1,/path/lib2,/path/lib3"
export CALIBRE_BASE_PATH="/path/to/library/parent/directory"
```

#### Configuration File

```python
# config.py
from pathlib import Path

class CalibreConfig:
    def __init__(self):
        self.server_url = "http://localhost:8080"
        self.username = "admin"
        self.password = "password"
        self.timeout = 30
        self.default_limit = 50
        self.local_library_path = Path("L:/Multimedia Files/Written Word")
```

## Library Structure

### Directory Organization

```
Base Library Directory/
├── metadata.db                    # SQLite metadata database
├── Author Name/                   # Author folder
│   └── Book Title (ID)/          # Book folder
│       ├── cover.jpg              # Cover image
│       ├── metadata.opf           # Metadata file
│       └── Book Title - Author.format  # Book file
└── ...
```

### Multi-Library Setup

```
L:/Multimedia Files/Written Word/
├── Calibre-Bibliothek/            # Main library
├── Calibre-Bibliothek IT/         # IT books
├── Calibre-Bibliothek Japanisch/ # Japanese content
├── Calibre-Bibliothek Manga/      # Manga collection
└── ...
```

### Database Schema

#### Books Table
```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    sort TEXT,
    timestamp TIMESTAMP,
    pubdate TIMESTAMP,
    series_index REAL,
    author_sort TEXT,
    isbn TEXT,
    lccn TEXT,
    path TEXT,
    flags INTEGER,
    uuid TEXT,
    has_cover BOOLEAN,
    last_modified TIMESTAMP
);
```

#### Authors Table
```sql
CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    sort TEXT,
    link TEXT
);
```

#### Series Table
```sql
CREATE TABLE series (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    sort TEXT
);
```

## API Integration

### Calibre Content Server API

CalibreMCP integrates with Calibre's Content Server API:

#### Base URL Structure
```
http://localhost:8080/
├── /ajax/                         # AJAX endpoints
├── /browse/                       # Browse library
├── /get/                          # Download files
├── /mobile/                       # Mobile interface
└── /opds/                         # OPDS feed
```

#### Key Endpoints

```python
# Library information
GET /ajax/library-info

# Book details
GET /ajax/book/{book_id}

# Search books
GET /ajax/search?query={query}&library_id={id}

# Download book
GET /get/{format}/{book_id}/{filename}
```

### Authentication

```python
import httpx
from calibre_mcp.config import CalibreConfig

class CalibreAPIClient:
    def __init__(self, config: CalibreConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            auth=(config.username, config.password),
            timeout=config.timeout
        )
    
    async def test_connection(self):
        """Test connection to Calibre server"""
        try:
            response = await self.client.get(f"{self.config.server_url}/ajax/library-info")
            return response.json()
        except Exception as e:
            raise CalibreAPIError(f"Connection failed: {e}")
```

## Database Integration

### Direct Database Access

For advanced operations, CalibreMCP can access the SQLite database directly:

```python
import sqlite3
from pathlib import Path

class CalibreDatabase:
    def __init__(self, library_path: Path):
        self.db_path = library_path / "metadata.db"
        self.connection = sqlite3.connect(str(self.db_path))
    
    def get_books(self, limit: int = 50):
        """Get books from database"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, title, author_sort, series_index, timestamp
            FROM books
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    
    def search_books(self, query: str):
        """Search books by title or author"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT b.id, b.title, b.author_sort, b.series_index
            FROM books b
            WHERE b.title LIKE ? OR b.author_sort LIKE ?
            ORDER BY b.title
        """, (f"%{query}%", f"%{query}%"))
        return cursor.fetchall()
```

### SQLAlchemy Integration

For more complex operations, use SQLAlchemy:

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_sort = Column(String)
    series_index = Column(Integer)
    timestamp = Column(DateTime)

class CalibreDatabaseService:
    def __init__(self, library_path: Path):
        self.engine = create_engine(f"sqlite:///{library_path}/metadata.db")
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()
```

## File Management

### File Operations

```python
from pathlib import Path
import shutil

class CalibreFileManager:
    def __init__(self, library_path: Path):
        self.library_path = library_path
    
    def get_book_path(self, book_id: int) -> Path:
        """Get book directory path"""
        # Implementation depends on Calibre's folder structure
        pass
    
    def get_book_file(self, book_id: int, format: str) -> Path:
        """Get specific format file for book"""
        book_path = self.get_book_path(book_id)
        for file in book_path.glob(f"*.{format.lower()}"):
            return file
        return None
    
    def download_book(self, book_id: int, format: str) -> bytes:
        """Download book file content"""
        book_file = self.get_book_file(book_id, format)
        if book_file and book_file.exists():
            return book_file.read_bytes()
        return None
```

### Format Conversion

```python
import subprocess
from pathlib import Path

class CalibreConverter:
    def __init__(self, calibre_path: Path = None):
        self.calibre_path = calibre_path or Path("calibre")
    
    async def convert_book(self, input_file: Path, output_format: str) -> Path:
        """Convert book to different format using Calibre"""
        output_file = input_file.with_suffix(f".{output_format.lower()}")
        
        cmd = [
            str(self.calibre_path),
            "ebook-convert",
            str(input_file),
            str(output_file),
            "--output-profile", "tablet"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return output_file
        else:
            raise Exception(f"Conversion failed: {result.stderr}")
```

## Metadata Handling

### Metadata Models

```python
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class BookMetadata(BaseModel):
    id: int
    title: str
    authors: List[str]
    series: Optional[str] = None
    series_index: Optional[float] = None
    rating: Optional[int] = None
    tags: List[str] = []
    comments: Optional[str] = None
    published: Optional[datetime] = None
    languages: List[str] = ["en"]
    formats: List[str] = []
    identifiers: Dict[str, str] = {}
    last_modified: Optional[datetime] = None

class AuthorMetadata(BaseModel):
    id: int
    name: str
    sort_name: str
    link: Optional[str] = None

class SeriesMetadata(BaseModel):
    id: int
    name: str
    sort_name: str
```

### Metadata Operations

```python
class MetadataManager:
    def __init__(self, db_service: CalibreDatabaseService):
        self.db = db_service
    
    async def update_book_metadata(self, book_id: int, updates: Dict[str, Any]):
        """Update book metadata"""
        session = self.db.get_session()
        try:
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                for key, value in updates.items():
                    if hasattr(book, key):
                        setattr(book, key, value)
                session.commit()
        finally:
            session.close()
    
    async def get_book_metadata(self, book_id: int) -> BookMetadata:
        """Get complete book metadata"""
        session = self.db.get_session()
        try:
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                return BookMetadata(
                    id=book.id,
                    title=book.title,
                    authors=[book.author_sort],
                    # ... other fields
                )
        finally:
            session.close()
```

## Advanced Features

### Library Analytics

```python
class LibraryAnalytics:
    def __init__(self, db_service: CalibreDatabaseService):
        self.db = db_service
    
    async def get_library_stats(self) -> Dict[str, Any]:
        """Get comprehensive library statistics"""
        session = self.db.get_session()
        try:
            total_books = session.query(Book).count()
            total_authors = session.query(Author).count()
            total_series = session.query(Series).count()
            
            # Get most common tags
            tag_counts = session.execute("""
                SELECT tag, COUNT(*) as count
                FROM books_tags bt
                JOIN tags t ON bt.tag = t.id
                GROUP BY tag
                ORDER BY count DESC
                LIMIT 10
            """).fetchall()
            
            return {
                "total_books": total_books,
                "total_authors": total_authors,
                "total_series": total_series,
                "most_common_tags": tag_counts
            }
        finally:
            session.close()
```

### Duplicate Detection

```python
from difflib import SequenceMatcher

class DuplicateDetector:
    def __init__(self, db_service: CalibreDatabaseService):
        self.db = db_service
    
    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    async def find_duplicates(self, threshold: float = 0.8) -> List[List[int]]:
        """Find potential duplicate books"""
        session = self.db.get_session()
        try:
            books = session.query(Book).all()
            duplicates = []
            processed = set()
            
            for i, book1 in enumerate(books):
                if book1.id in processed:
                    continue
                    
                group = [book1.id]
                for j, book2 in enumerate(books[i+1:], i+1):
                    if book2.id in processed:
                        continue
                    
                    # Check title similarity
                    title_sim = self.similarity(book1.title, book2.title)
                    if title_sim >= threshold:
                        group.append(book2.id)
                        processed.add(book2.id)
                
                if len(group) > 1:
                    duplicates.append(group)
                    processed.add(book1.id)
            
            return duplicates
        finally:
            session.close()
```

## Performance Optimization

### Database Optimization

```python
class DatabaseOptimizer:
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    def optimize_database(self):
        """Optimize SQLite database"""
        conn = sqlite3.connect(str(self.db_path))
        try:
            # Analyze database
            conn.execute("ANALYZE")
            
            # Vacuum database
            conn.execute("VACUUM")
            
            # Create indexes for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_books_title 
                ON books(title)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_books_author 
                ON books(author_sort)
            """)
            
            conn.commit()
        finally:
            conn.close()
```

### Caching Strategy

```python
from functools import lru_cache
import asyncio

class CalibreCache:
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
    
    @lru_cache(maxsize=100)
    def get_book_metadata(self, book_id: int) -> BookMetadata:
        """Cached book metadata retrieval"""
        # Implementation
        pass
    
    async def preload_popular_books(self, limit: int = 100):
        """Preload metadata for popular books"""
        # Implementation
        pass
```

## Troubleshooting

### Common Issues

#### Connection Problems
```python
# Test Calibre server connection
async def test_connection():
    try:
        client = httpx.AsyncClient()
        response = await client.get("http://localhost:8080/ajax/library-info")
        if response.status_code == 200:
            print("✓ Calibre server is running")
        else:
            print("✗ Calibre server returned error")
    except httpx.ConnectError:
        print("✗ Cannot connect to Calibre server")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
```

#### Database Issues
```python
# Check database integrity
def check_database_integrity(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result[0] == "ok":
            print("✓ Database integrity check passed")
        else:
            print(f"✗ Database integrity issues: {result[0]}")
    finally:
        conn.close()
```

#### File Access Issues
```python
# Check file permissions
def check_file_permissions(library_path: Path):
    try:
        # Test read access
        test_file = library_path / "metadata.db"
        if test_file.exists():
            test_file.read_bytes()
            print("✓ Read access OK")
        
        # Test write access
        test_write = library_path / "test_write.tmp"
        test_write.write_text("test")
        test_write.unlink()
        print("✓ Write access OK")
        
    except PermissionError:
        print("✗ Permission denied")
    except Exception as e:
        print(f"✗ File access error: {e}")
```

### Diagnostic Tools

```python
class CalibreDiagnostics:
    def __init__(self, config: CalibreConfig):
        self.config = config
    
    async def run_full_diagnostics(self):
        """Run comprehensive diagnostics"""
        print("🔍 Running CalibreMCP Diagnostics...")
        
        # Test server connection
        await self.test_server_connection()
        
        # Test database access
        self.test_database_access()
        
        # Test file permissions
        self.test_file_permissions()
        
        # Test library discovery
        self.test_library_discovery()
        
        print("✅ Diagnostics complete")
    
    async def test_server_connection(self):
        """Test Calibre server connection"""
        try:
            client = CalibreAPIClient(self.config)
            info = await client.test_connection()
            print(f"✓ Server: {info.get('server_url')}")
            print(f"✓ Version: {info.get('version')}")
        except Exception as e:
            print(f"✗ Server connection failed: {e}")
    
    def test_database_access(self):
        """Test database access"""
        db_path = self.config.local_library_path / "metadata.db"
        if db_path.exists():
            print(f"✓ Database found: {db_path}")
            print(f"✓ Size: {db_path.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            print(f"✗ Database not found: {db_path}")
    
    def test_file_permissions(self):
        """Test file system permissions"""
        try:
            test_path = self.config.local_library_path / "test.tmp"
            test_path.write_text("test")
            test_path.unlink()
            print("✓ File permissions OK")
        except Exception as e:
            print(f"✗ File permissions error: {e}")
    
    def test_library_discovery(self):
        """Test library discovery"""
        libraries = self.discover_libraries()
        print(f"✓ Found {len(libraries)} libraries:")
        for lib in libraries:
            print(f"  - {lib['name']}: {lib['book_count']} books")
```

## Best Practices

### Library Management

1. **Regular Backups**: Backup metadata databases regularly
2. **Consistent Naming**: Use consistent naming conventions
3. **Metadata Quality**: Maintain high-quality metadata
4. **Format Diversity**: Keep multiple formats for important books

### Performance

1. **Database Optimization**: Regular database maintenance
2. **Caching**: Implement appropriate caching strategies
3. **Batch Operations**: Use batch operations for bulk changes
4. **Connection Pooling**: Reuse database connections

### Security

1. **Authentication**: Use strong authentication for content server
2. **Network Security**: Secure network connections
3. **File Permissions**: Appropriate file system permissions
4. **Data Privacy**: Protect sensitive metadata

### Development

1. **Error Handling**: Comprehensive error handling
2. **Logging**: Structured logging for debugging
3. **Testing**: Unit and integration tests
4. **Documentation**: Keep documentation updated

---

*This integration guide is part of the CalibreMCP project and follows Austrian efficiency principles for comprehensive, clear, and actionable documentation.*
