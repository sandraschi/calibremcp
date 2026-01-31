"""
Server response models - extracted to break circular import.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class LibrarySearchResponse(BaseModel):
    model_config = {"from_attributes": True}
    results: List[Dict[str, Any]]
    total_found: int
    query_used: Optional[str] = None
    search_time_ms: int = 0
    library_searched: str = "main"


class BookDetailResponse(BaseModel):
    model_config = {"from_attributes": True}
    book_id: int
    title: str
    authors: List[str]
    series: Optional[str] = None
    series_index: Optional[float] = None
    rating: Optional[float] = None
    tags: List[str] = []
    comments: Optional[str] = None
    published: Optional[str] = None
    languages: List[str] = ["en"]
    formats: List[str] = []
    identifiers: Dict[str, str] = {}
    last_modified: Optional[str] = None
    cover_url: Optional[str] = None
    download_links: Dict[str, str] = {}
    library_name: str = "main"


class ConnectionTestResponse(BaseModel):
    model_config = {"from_attributes": True}
    connected: bool
    server_url: str
    server_version: Optional[str] = None
    library_count: int = 0
    total_books: int = 0
    response_time_ms: int = 0
    error_message: Optional[str] = None


class LibraryListResponse(BaseModel):
    model_config = {"from_attributes": True}
    libraries: List[Dict[str, Any]]
    current_library: str
    total_libraries: int


class LibraryStatsResponse(BaseModel):
    model_config = {"from_attributes": True}
    library_name: str
    total_books: int
    total_authors: int
    total_series: int
    total_tags: int
    format_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    rating_distribution: Dict[str, int]
    last_modified: Optional[str] = None


class MetadataUpdateRequest(BaseModel):
    model_config = {"from_attributes": True}
    book_id: int
    field: str
    value: Any


class ConversionRequest(BaseModel):
    model_config = {"from_attributes": True}
    book_id: int
    source_format: str
    target_format: str
    quality: str = "high"


class ConversionResponse(BaseModel):
    model_config = {"from_attributes": True}
    book_id: int
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None


class MetadataUpdateResponse(BaseModel):
    model_config = {"from_attributes": True}
    updated_books: List[int]
    failed_updates: List[Dict[str, Any]]
    success_count: int


class TagStatsResponse(BaseModel):
    model_config = {"from_attributes": True}
    total_tags: int
    unique_tags: int
    duplicate_tags: List[Dict[str, Any]]
    unused_tags: List[str]
    suggestions: List[Dict[str, Any]]
