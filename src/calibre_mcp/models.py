"""
Data models for Calibre MCP server.
"""

import os
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

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
    authors: list[str] = []
    identifiers: list[BookIdentifier] = []
    formats: list[BookFormat] = []
    languages: list[str] = []
    publisher: str | None = None
    pubdate: date | None = None
    series: str | None = None
    series_index: float | None = None
    rating: float | None = Field(None, ge=0, le=5)
    tags: list[str] = []
    description: str | None = None
    comments: str | None = None
    cover_url: HttpUrl | None = None
    thumbnail_url: HttpUrl | None = None
    status: BookStatus = BookStatus.UNREAD
    progress: float = Field(0.0, ge=0.0, le=100.0)
    last_read: datetime | None = None
    date_added: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    size: int | None = None  # in bytes
    file_path: Path | None = None
    custom_fields: dict[str, Any] = {}

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

    books: list[Book]
    total_count: int
    offset: int
    limit: int


class BookAddRequest(BaseModel):
    """Request model for adding a new book."""

    file_path: Path | None = None
    file_data: bytes | None = None  # For direct file uploads
    format: BookFormat | None = None
    metadata: BookMetadata | None = None
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
    file_path: Path | None = None
    file_data: bytes | None = None
    format: BookFormat | None = None


class SearchQuery(BaseModel):
    """Search query model."""

    query: str | None = None
    title: str | None = None
    author: str | None = None
    tags: list[str] = []
    series: str | None = None
    publisher: str | None = None
    format: BookFormat | None = None
    language: str | None = None
    status: BookStatus | None = None
    min_rating: float | None = Field(None, ge=0, le=5)
    max_rating: float | None = Field(None, ge=0, le=5)
    added_after: date | None = None
    added_before: date | None = None
    modified_after: date | None = None
    modified_before: date | None = None
    read_status: BookStatus | None = None
    has_cover: bool | None = None
    has_description: bool | None = None
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
    last_login: datetime | None = None
    date_joined: datetime = Field(default_factory=datetime.utcnow)
    preferences: dict[str, Any] = {}


class Collection(BaseModel):
    """Book collection model."""

    id: int
    name: str
    description: str | None = None
    books: list[int] = []  # List of book IDs
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
    location: str | None = None  # Page number, location, etc.
    note: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    color: str | None = None  # For highlights
    is_public: bool = False
