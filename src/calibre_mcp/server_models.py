"""
Server response models - extracted to break circular import.
"""

from typing import Any

from pydantic import BaseModel


class LibrarySearchResponse(BaseModel):
    model_config = {"from_attributes": True}
    results: list[dict[str, Any]]
    total_found: int
    query_used: str | None = None
    search_time_ms: int = 0
    library_searched: str = "main"


class BookDetailResponse(BaseModel):
    model_config = {"from_attributes": True}
    book_id: int
    title: str
    authors: list[str]
    series: str | None = None
    series_index: float | None = None
    rating: float | None = None
    tags: list[str] = []
    comments: str | None = None
    published: str | None = None
    languages: list[str] = ["en"]
    formats: list[str] = []
    identifiers: dict[str, str] = {}
    last_modified: str | None = None
    cover_url: str | None = None
    download_links: dict[str, str] = {}
    library_name: str = "main"


class ConnectionTestResponse(BaseModel):
    model_config = {"from_attributes": True}
    connected: bool
    server_url: str
    server_version: str | None = None
    library_count: int = 0
    total_books: int = 0
    response_time_ms: int = 0
    error_message: str | None = None


class LibraryListResponse(BaseModel):
    model_config = {"from_attributes": True}
    libraries: list[dict[str, Any]]
    current_library: str
    total_libraries: int


class LibraryStatsResponse(BaseModel):
    model_config = {"from_attributes": True}
    library_name: str
    total_books: int
    total_authors: int
    total_series: int
    total_tags: int
    format_distribution: dict[str, int]
    language_distribution: dict[str, int]
    rating_distribution: dict[str, int]
    last_modified: str | None = None


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
    output_path: str | None = None
    error_message: str | None = None


class MetadataUpdateResponse(BaseModel):
    model_config = {"from_attributes": True}
    updated_books: list[int]
    failed_updates: list[dict[str, Any]]
    success_count: int


class TagStatsResponse(BaseModel):
    model_config = {"from_attributes": True}
    total_tags: int
    unique_tags: int
    duplicate_tags: list[dict[str, Any]]
    unused_tags: list[str]
    suggestions: list[dict[str, Any]]


class DuplicatesResponse(BaseModel):
    model_config = {"from_attributes": True}
    duplicate_groups: list[dict[str, Any]]
    total_duplicates: int
    confidence_scores: dict[str, float]


class SeriesAnalysisResponse(BaseModel):
    model_config = {"from_attributes": True}
    incomplete_series: list[dict[str, Any]]
    reading_order_suggestions: list[dict[str, Any]]
    series_statistics: dict[str, Any]


class LibraryHealthResponse(BaseModel):
    model_config = {"from_attributes": True}
    health_score: float
    issues_found: list[dict[str, Any]]
    recommendations: list[str]
    database_integrity: bool


class UnreadPriorityResponse(BaseModel):
    model_config = {"from_attributes": True}
    prioritized_books: list[dict[str, Any]]
    priority_reasons: dict[str, str]
    total_unread: int


class ReadingStats(BaseModel):
    model_config = {"from_attributes": True}
    total_books_read: int
    average_rating: float
    favorite_genres: list[str]
    reading_patterns: dict[str, Any]


class JapaneseBookOrganization(BaseModel):
    model_config = {"from_attributes": True}
    manga_series: list[dict[str, Any]]
    light_novels: list[dict[str, Any]]
    language_learning: list[dict[str, Any]]
    reading_recommendations: list[str]


class ITBookCuration(BaseModel):
    model_config = {"from_attributes": True}
    programming_languages: dict[str, list[dict[str, Any]]]
    outdated_books: list[dict[str, Any]]
    learning_paths: list[dict[str, Any]]


class ReadingRecommendations(BaseModel):
    model_config = {"from_attributes": True}
    recommendations: list[dict[str, Any]]
    reasoning: dict[str, str]
    confidence_scores: dict[str, float]
