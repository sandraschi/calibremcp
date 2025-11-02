"""
Data models for Calibre MCP server.
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum
from pathlib import Path
import os
from pydantic import BaseModel, Field, HttpUrl, field_validator


class BookFormat(str, Enum):
    """Supported book formats."""

    EPUB = "epub"
    PDF = "pdf"
    MOBI = "mobi"
    AZW3 = "azw3"
    CBZ = "cbz"
    CBR = "cbr"
    DOCX = "docx"
    FB2 = "fb2"
    HTML = "html"
    LIT = "lit"
    LRF = "lrf"
    ODT = "odt"
    PDB = "pdb"
    PML = "pml"
    RB = "rb"
    RTF = "rtf"
    SNB = "snb"
    TCR = "tcr"
    TXT = "txt"
    TXTZ = "txtz"


class BookStatus(str, Enum):
    """Book reading status."""

    UNREAD = "unread"
    READING = "reading"
    FINISHED = "finished"
    ABANDONED = "abandoned"
    WISHLIST = "wishlist"


class BookIdentifier(BaseModel):
    """Book identifier (ISBN, Goodreads, etc.)."""

    type: str
    value: str


class BookMetadata(BaseModel):
    """Book metadata model."""

    title: str
    authors: List[str] = []
    identifiers: List[BookIdentifier] = []
    formats: List[BookFormat] = []
    languages: List[str] = []
    publisher: Optional[str] = None
    pubdate: Optional[date] = None
    series: Optional[str] = None
    series_index: Optional[float] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    tags: List[str] = []
    description: Optional[str] = None
    comments: Optional[str] = None
    cover_url: Optional[HttpUrl] = None
    thumbnail_url: Optional[HttpUrl] = None
    status: BookStatus = BookStatus.UNREAD
    progress: float = Field(0.0, ge=0.0, le=100.0)
    last_read: Optional[datetime] = None
    date_added: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    size: Optional[int] = None  # in bytes
    file_path: Optional[Path] = None
    custom_fields: Dict[str, Any] = {}

    @field_validator("authors", "tags", "languages")
    @classmethod
    def normalize_list_fields(cls, v):
        """Normalize list fields by removing empty strings and duplicates."""
        if v is None:
            return []
        return list(dict.fromkeys([item.strip() for item in v if item and item.strip()]))

    @field_validator("title", "publisher", "series", "description", "comments")
    @classmethod
    def normalize_string_fields(cls, v):
        """Normalize string fields by stripping whitespace."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class Book(BookMetadata):
    """Book model with ID."""

    id: int


class BookListResponse(BaseModel):
    """Response model for listing books."""

    books: List[Book]
    total_count: int
    offset: int
    limit: int


class BookAddRequest(BaseModel):
    """Request model for adding a new book."""

    file_path: Optional[Path] = None
    file_data: Optional[bytes] = None  # For direct file uploads
    format: Optional[BookFormat] = None
    metadata: Optional[BookMetadata] = None
    fetch_metadata: bool = True

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v):
        """Validate that the file exists and is readable."""
        if v is not None:
            if not v.exists():
                raise ValueError(f"File not found: {v}")
            if not v.is_file():
                raise ValueError(f"Not a file: {v}")
            if not os.access(v, os.R_OK):
                raise ValueError(f"Cannot read file: {v}")
        return v


class BookUpdateRequest(BaseModel):
    """Request model for updating book metadata."""

    metadata: BookMetadata
    update_file: bool = False
    file_path: Optional[Path] = None
    file_data: Optional[bytes] = None
    format: Optional[BookFormat] = None


class SearchQuery(BaseModel):
    """Search query model."""

    query: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = []
    series: Optional[str] = None
    publisher: Optional[str] = None
    format: Optional[BookFormat] = None
    language: Optional[str] = None
    status: Optional[BookStatus] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    max_rating: Optional[float] = Field(None, ge=0, le=5)
    added_after: Optional[date] = None
    added_before: Optional[date] = None
    modified_after: Optional[date] = None
    modified_before: Optional[date] = None
    read_status: Optional[BookStatus] = None
    has_cover: Optional[bool] = None
    has_description: Optional[bool] = None
    sort_by: str = "title"
    sort_desc: bool = False


class UserRole(str, Enum):
    """User roles for access control."""

    ADMIN = "admin"
    EDITOR = "editor"
    READER = "reader"
    GUEST = "guest"


class User(BaseModel):
    """User model."""

    id: int
    username: str
    email: str
    role: UserRole = UserRole.READER
    is_active: bool = True
    last_login: Optional[datetime] = None
    date_joined: datetime = Field(default_factory=datetime.utcnow)
    preferences: Dict[str, Any] = {}


class Collection(BaseModel):
    """Book collection model."""

    id: int
    name: str
    description: Optional[str] = None
    books: List[int] = []  # List of book IDs
    is_public: bool = False
    created_by: int  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Annotation(BaseModel):
    """Book annotation model."""

    id: int
    book_id: int
    user_id: int
    content: str
    location: Optional[str] = None  # Page number, location, etc.
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    color: Optional[str] = None  # For highlights
    is_public: bool = False
