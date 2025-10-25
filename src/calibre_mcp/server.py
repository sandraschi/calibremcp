"""
CalibreMCP Phase 2 - FastMCP 2.12 Server for Calibre E-book Library Management

Austrian efficiency for Sandra's 1000+ book collection across multiple libraries.
Now with 23 comprehensive tools including multi-library, Japanese weeb optimization,
and IT book curation. All tools properly categorized and FastMCP 2.12 compliant.

Phase 2 adds 19 additional tools:
- Multi-Library Management (4 tools)
- Advanced Organization & Analysis (5 tools) 
- Metadata & Database Operations (4 tools)
- File Operations (3 tools)
- Austrian Efficiency Specials (3 tools)
"""

from typing import Optional, List, Dict, Any
from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel
from rich.console import Console
from dotenv import load_dotenv

# Import structured logging
from .logging_config import get_logger, log_operation, log_error

# Standard imports - no fallbacks needed
from .calibre_api import CalibreAPIClient
from .config import CalibreConfig

# Load environment variables
load_dotenv()

# Initialize console for logging
console = Console()
logger = get_logger("calibremcp.server")

# Initialize FastMCP server  
mcp = FastMCP("CalibreMCP Phase 2")

# Global API client and database connections (initialized on startup)
api_client: Optional[CalibreAPIClient] = None
current_library: str = "main"
available_libraries: Dict[str, str] = {}


# ==================== RESPONSE MODELS ====================

class LibrarySearchResponse(BaseModel):
    """Response model for library search operations"""
    results: List[Dict[str, Any]]
    total_found: int
    query_used: Optional[str] = None
    search_time_ms: int = 0
    library_searched: str = "main"


class BookDetailResponse(BaseModel):
    """Response model for detailed book information"""
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
    """Response model for connection testing"""
    connected: bool
    server_url: str
    server_version: Optional[str] = None
    library_count: int = 0
    total_books: int = 0
    response_time_ms: int = 0
    error_message: Optional[str] = None


class LibraryListResponse(BaseModel):
    """Response model for library listing"""
    libraries: List[Dict[str, Any]]
    current_library: str
    total_libraries: int


class LibraryStatsResponse(BaseModel):
    """Response model for library statistics"""
    library_name: str
    total_books: int
    total_authors: int
    total_series: int
    total_tags: int
    format_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    rating_distribution: Dict[str, int]
    last_modified: Optional[str] = None


class TagStatsResponse(BaseModel):
    """Response model for tag statistics"""
    total_tags: int
    unique_tags: int
    duplicate_tags: List[Dict[str, Any]]
    unused_tags: List[str]
    suggestions: List[Dict[str, Any]]


class DuplicatesResponse(BaseModel):
    """Response model for duplicate detection"""
    duplicate_groups: List[Dict[str, Any]]
    total_duplicates: int
    confidence_scores: Dict[str, float]


class SeriesAnalysisResponse(BaseModel):
    """Response model for series analysis"""
    incomplete_series: List[Dict[str, Any]]
    reading_order_suggestions: List[Dict[str, Any]]
    series_statistics: Dict[str, Any]


class LibraryHealthResponse(BaseModel):
    """Response model for library health analysis"""
    health_score: float
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]
    database_integrity: bool


class UnreadPriorityResponse(BaseModel):
    """Response model for unread priority list"""
    prioritized_books: List[Dict[str, Any]]
    priority_reasons: Dict[str, str]
    total_unread: int


class MetadataUpdateRequest(BaseModel):
    """Request model for metadata updates"""
    book_id: int
    field: str
    value: Any


class MetadataUpdateResponse(BaseModel):
    """Response model for metadata updates"""
    updated_books: List[int]
    failed_updates: List[Dict[str, Any]]
    success_count: int


class ReadingStats(BaseModel):
    """Response model for reading statistics"""
    total_books_read: int
    average_rating: float
    favorite_genres: List[str]
    reading_patterns: Dict[str, Any]


class ConversionRequest(BaseModel):
    """Request model for format conversion"""
    book_id: int
    source_format: str
    target_format: str
    quality: str = "high"


class ConversionResponse(BaseModel):
    """Response model for format conversion"""
    book_id: int
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None


class JapaneseBookOrganization(BaseModel):
    """Response model for Japanese book organization"""
    manga_series: List[Dict[str, Any]]
    light_novels: List[Dict[str, Any]]
    language_learning: List[Dict[str, Any]]
    reading_recommendations: List[str]


class ITBookCuration(BaseModel):
    """Response model for IT book curation"""
    programming_languages: Dict[str, List[Dict[str, Any]]]
    outdated_books: List[Dict[str, Any]]
    learning_paths: List[Dict[str, Any]]


class ReadingRecommendations(BaseModel):
    """Response model for reading recommendations"""
    recommendations: List[Dict[str, Any]]
    reasoning: Dict[str, str]
    confidence_scores: Dict[str, float]


# ==================== HELPER FUNCTIONS ====================

async def get_api_client() -> CalibreAPIClient:
    """Get or create API client instance"""
    global api_client
    if api_client is None:
        config = CalibreConfig()
        api_client = CalibreAPIClient(config)
        await api_client.initialize()
    return api_client


async def discover_libraries() -> Dict[str, str]:
    """Discover available Calibre libraries"""
    global available_libraries
    
    if available_libraries:
        return available_libraries
    
    config = CalibreConfig()
    libraries = {}
    
    # Check configured library path
    if config.local_library_path and config.local_library_path.exists():
        libraries["main"] = str(config.local_library_path)
    
    # Discover additional libraries
    base_dir = Path("L:/Multimedia Files/Written Word")
    if base_dir.exists():
        for item in base_dir.iterdir():
            if item.is_dir() and (item / "metadata.db").exists():
                libraries[item.name] = str(item)
    
    available_libraries = libraries
    return libraries


# ==================== SERVER INITIALIZATION ====================

def create_app() -> FastMCP:
    """Create and configure the FastMCP application"""
    return mcp


async def main():
    """Main server entry point"""
    try:
        # Initialize logging
        log_operation(logger, "server_startup", level="INFO",
                     version="1.0.0", collection_size="1000+ books")
        
        # Discover libraries
        libraries = await discover_libraries()
        log_operation(logger, "library_discovery", level="INFO",
                     discovered_libraries=list(libraries.keys()),
                     current_library=current_library)
        
        # Run the FastMCP server
        mcp.run()
        
    except Exception as e:
        log_error(logger, "server_startup_error", e)
        raise


if __name__ == "__main__":
    main()
