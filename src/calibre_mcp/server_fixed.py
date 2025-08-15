"""
FIXED CalibreMCP server - corrected list_books to use local database when available

Key fixes:
1. list_books now checks for local database access first
2. Falls back to web API only if local database not available
3. Proper error handling and response formatting
4. All tools have correct @mcp.tool() decorators
"""

import asyncio
import os
import sqlite3
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from rich.console import Console
from dotenv import load_dotenv

# Hybrid imports - work both as module and direct script
try:
    # Try relative imports first (when running as module)
    from .calibre_api import CalibreAPIClient, CalibreAPIError
    from .config import CalibreConfig
except ImportError:
    # Fall back to absolute imports (when running script directly)
    try:
        from calibre_mcp.calibre_api import CalibreAPIClient, CalibreAPIError
        from calibre_mcp.config import CalibreConfig
    except ImportError:
        # Last resort - add current directory to path
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from calibre_api import CalibreAPIClient, CalibreAPIError
        from config import CalibreConfig

# Load environment variables
load_dotenv()

# Initialize console for logging
console = Console()

# Initialize FastMCP server  
mcp = FastMCP("CalibreMCP Phase 2 - FIXED")

# Global API client and database connections (initialized on startup)
api_client: Optional[CalibreAPIClient] = None
current_library: str = "main"
available_libraries: Dict[str, str] = {}

# ==================== PYDANTIC MODELS (SAME AS ORIGINAL) ====================

class BookSearchResult(BaseModel):
    """Individual book result from library search"""
    book_id: int = Field(description="Calibre book ID")
    title: str = Field(description="Book title")
    authors: List[str] = Field(description="List of authors")
    series: Optional[str] = Field(default=None, description="Series name if part of series")
    series_index: Optional[float] = Field(default=None, description="Position in series")
    rating: Optional[int] = Field(default=None, description="User rating 1-5")
    tags: List[str] = Field(description="Book tags/categories")
    languages: List[str] = Field(description="Language codes")
    formats: List[str] = Field(description="Available formats (EPUB, PDF, etc)")
    last_modified: Optional[str] = Field(default=None, description="Last modification date")
    cover_url: Optional[str] = Field(default=None, description="Cover image URL")
    library_name: Optional[str] = Field(default=None, description="Library containing this book")


class LibrarySearchResponse(BaseModel):
    """Response from library search operations"""
    results: List[BookSearchResult] = Field(description="List of matching books")
    total_found: int = Field(description="Total books matching criteria")
    query_used: Optional[str] = Field(default=None, description="Search query that was executed")
    search_time_ms: int = Field(description="Time taken for search in milliseconds")
    library_searched: Optional[str] = Field(default=None, description="Library that was searched")


# ==================== UTILITY FUNCTIONS ====================

def get_local_library_path() -> Optional[str]:
    """Get local library path from environment"""
    return os.getenv('CALIBRE_LIBRARY_PATH')


def get_metadata_db_path(library_path: str) -> str:
    """Get path to metadata.db for direct database access"""
    return os.path.join(library_path, "metadata.db")


async def execute_sql_query(library_path: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute SQL query against library's metadata.db"""
    try:
        db_path = get_metadata_db_path(library_path)
        if not os.path.exists(db_path):
            raise CalibreAPIError(f"Database not found: {db_path}")
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
        
    except Exception as e:
        raise CalibreAPIError(f"Database query failed: {str(e)}")


async def search_local_library(
    library_path: str,
    query: Optional[str] = None,
    limit: int = 50,
    sort: str = "title"
) -> List[BookSearchResult]:
    """Search local Calibre library using direct database access"""
    try:
        # Build SQL query based on parameters
        base_query = """
        SELECT 
            b.id as book_id,
            b.title,
            b.series_index,
            b.timestamp as last_modified,
            GROUP_CONCAT(DISTINCT a.name, ' & ') as authors,
            s.name as series,
            (SELECT GROUP_CONCAT(t.name, ', ') FROM books_tags_link btl 
             JOIN tags t ON btl.tag = t.id WHERE btl.book = b.id) as tags,
            (SELECT GROUP_CONCAT(l.lang_code, ', ') FROM books_languages_link bll 
             JOIN languages l ON bll.lang_code = l.id WHERE bll.book = b.id) as languages,
            (SELECT GROUP_CONCAT(UPPER(d.format), ', ') FROM data d WHERE d.book = b.id) as formats,
            r.rating
        FROM books b
        LEFT JOIN books_authors_link bal ON b.id = bal.book
        LEFT JOIN authors a ON bal.author = a.id
        LEFT JOIN books_series_link bsl ON b.id = bsl.book
        LEFT JOIN series s ON bsl.series = s.id
        LEFT JOIN books_ratings_link brl ON b.id = brl.book
        LEFT JOIN ratings r ON brl.rating = r.id
        """
        
        where_conditions = []
        params = []
        
        # Add search conditions if query provided
        if query:
            # Simple text search across title, authors, and tags
            search_condition = """
            (b.title LIKE ? OR 
             EXISTS (SELECT 1 FROM books_authors_link bal2 
                     JOIN authors a2 ON bal2.author = a2.id 
                     WHERE bal2.book = b.id AND a2.name LIKE ?) OR
             EXISTS (SELECT 1 FROM books_tags_link btl2 
                     JOIN tags t2 ON btl2.tag = t2.id 
                     WHERE btl2.book = b.id AND t2.name LIKE ?))
            """
            where_conditions.append(search_condition)
            search_param = f"%{query}%"
            params.extend([search_param, search_param, search_param])
        
        # Add WHERE clause if needed
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        # Add GROUP BY to handle multiple authors/tags
        base_query += " GROUP BY b.id"
        
        # Add sorting
        sort_mapping = {
            "title": "b.title",
            "author": "authors",
            "rating": "r.rating DESC",
            "date": "b.timestamp DESC",
            "series": "s.name, b.series_index"
        }
        order_by = sort_mapping.get(sort, "b.title")
        base_query += f" ORDER BY {order_by}"
        
        # Add limit
        base_query += f" LIMIT {limit}"
        
        # Execute query
        results = await execute_sql_query(library_path, base_query, tuple(params))
        
        # Convert to BookSearchResult objects
        books = []
        for row in results:
            # Parse comma-separated values
            authors = row['authors'].split(' & ') if row['authors'] else []
            tags = row['tags'].split(', ') if row['tags'] else []
            languages = row['languages'].split(', ') if row['languages'] else ['en']
            formats = row['formats'].split(', ') if row['formats'] else []
            
            # Clean up any empty strings
            authors = [a.strip() for a in authors if a.strip()]
            tags = [t.strip() for t in tags if t.strip()]
            languages = [l.strip() for l in languages if l.strip()]
            formats = [f.strip() for f in formats if f.strip()]
            
            book = BookSearchResult(
                book_id=row['book_id'],
                title=row['title'] or 'Unknown Title',
                authors=authors,
                series=row['series'],
                series_index=row['series_index'],
                rating=row['rating'],
                tags=tags,
                languages=languages,
                formats=formats,
                last_modified=row['last_modified'],
                cover_url=f"http://localhost:8080/get/cover/{row['book_id']}" if row['book_id'] else None,
                library_name=current_library
            )
            books.append(book)
        
        return books
        
    except Exception as e:
        console.print(f"[red]Local library search failed: {e}[/red]")
        raise CalibreAPIError(f"Local search failed: {str(e)}")


async def get_api_client() -> CalibreAPIClient:
    """Get initialized API client, creating if needed"""
    global api_client
    if api_client is None:
        config = CalibreConfig()
        api_client = CalibreAPIClient(config)
    return api_client


# ==================== FIXED TOOLS ====================

@mcp.tool()
async def list_books(
    query: Optional[str] = None,
    limit: int = Field(50, description="Maximum number of books to return (1-200)"),
    sort: str = Field("title", description="Sort by: title, author, rating, date")
) -> LibrarySearchResponse:
    """
    Browse/search library with flexible filtering.
    
    Austrian efficiency tool for Sandra's 1000+ book collection.
    Supports natural language queries and various sorting options.
    
    Args:
        query: Optional search query (title, author, tags, series)
        limit: Maximum results to return (default 50, max 200)
        sort: Sort order - title, author, rating, date, series
        
    Returns:
        Structured library search results with metadata
        
    Example:
        list_books("programming python", limit=20, sort="rating")
    """
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Validate limit
        limit = max(1, min(200, limit))
        
        # Try local database access first
        local_library_path = get_local_library_path()
        
        if local_library_path and os.path.exists(local_library_path):
            console.print(f"[blue]Using local database: {local_library_path}[/blue]")
            
            # Use local database search
            books = await search_local_library(
                library_path=local_library_path,
                query=query,
                limit=limit,
                sort=sort
            )
            
            end_time = asyncio.get_event_loop().time()
            search_time_ms = int((end_time - start_time) * 1000)
            
            return LibrarySearchResponse(
                results=books,
                total_found=len(books),
                query_used=query or "all books",
                search_time_ms=search_time_ms,
                library_searched=f"{current_library} (local database)"
            )
        
        else:
            # Fall back to web API
            console.print("[yellow]Local database not available, trying web API[/yellow]")
            
            client = await get_api_client()
            
            # Perform search
            results = await client.search_library(
                query=query,
                limit=limit,
                sort=sort
            )
            
            end_time = asyncio.get_event_loop().time()
            search_time_ms = int((end_time - start_time) * 1000)
            
            # Convert to response format
            book_results = []
            for book in results:
                book_result = BookSearchResult(
                    book_id=book['id'],
                    title=book.get('title', 'Unknown'),
                    authors=book.get('authors', []),
                    series=book.get('series'),
                    series_index=book.get('series_index'),
                    rating=book.get('rating'),
                    tags=book.get('tags', []),
                    languages=book.get('languages', ['en']),
                    formats=book.get('formats', []),
                    last_modified=book.get('last_modified'),
                    cover_url=book.get('cover_url'),
                    library_name=current_library
                )
                book_results.append(book_result)
                
            return LibrarySearchResponse(
                results=book_results,
                total_found=len(book_results),
                query_used=query,
                search_time_ms=search_time_ms,
                library_searched=f"{current_library} (web API)"
            )
        
    except CalibreAPIError as e:
        console.print(f"[red]Calibre API error in list_books: {e}[/red]")
        return LibrarySearchResponse(
            results=[],
            total_found=0,
            query_used=query,
            search_time_ms=0,
            library_searched=current_library
        )
    except Exception as e:
        console.print(f"[red]Unexpected error in list_books: {e}[/red]")
        return LibrarySearchResponse(
            results=[],
            total_found=0,
            query_used=query,
            search_time_ms=0,
            library_searched=current_library
        )


@mcp.tool()
async def test_calibre_connection():
    """
    Test connection to Calibre server and get diagnostics.
    
    Verifies server connectivity, authentication, and retrieves
    basic server information and capabilities for troubleshooting.
    
    Returns:
        Connection status, server info, performance metrics, and capabilities
        
    Example:
        Use for debugging connection issues or verifying setup
    """
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Check local database first
        local_library_path = get_local_library_path()
        
        if local_library_path and os.path.exists(local_library_path):
            # Test local database access
            db_path = get_metadata_db_path(local_library_path)
            
            if os.path.exists(db_path):
                # Get basic stats from local database
                book_count_query = "SELECT COUNT(*) as total FROM books"
                results = await execute_sql_query(local_library_path, book_count_query)
                total_books = results[0]['total'] if results else 0
                
                end_time = asyncio.get_event_loop().time()
                response_time_ms = int((end_time - start_time) * 1000)
                
                return {
                    "connected": True,
                    "server_version": "Local Database",
                    "library_name": os.path.basename(local_library_path),
                    "total_books": total_books,
                    "response_time_ms": response_time_ms,
                    "error_message": None,
                    "server_capabilities": ["local_database", "search", "metadata", "direct_file_access"]
                }
            else:
                return {
                    "connected": False,
                    "server_version": None,
                    "library_name": None,
                    "total_books": None,
                    "response_time_ms": 0,
                    "error_message": f"metadata.db not found at {db_path}",
                    "server_capabilities": []
                }
        else:
            # Fall back to web API test
            client = await get_api_client()
            server_info = await client.test_connection()
            
            end_time = asyncio.get_event_loop().time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            return {
                "connected": True,
                "server_version": server_info.get('version'),
                "library_name": server_info.get('library_name', 'Default Library'),
                "total_books": server_info.get('total_books', 0),
                "response_time_ms": response_time_ms,
                "error_message": None,
                "server_capabilities": server_info.get('capabilities', [
                    'search', 'metadata', 'covers', 'downloads'
                ])
            }
        
    except Exception as e:
        end_time = asyncio.get_event_loop().time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        console.print(f"[red]Connection test failed: {e}[/red]")
        return {
            "connected": False,
            "server_version": None,
            "library_name": None,
            "total_books": None,
            "response_time_ms": response_time_ms,
            "error_message": str(e),
            "server_capabilities": []
        }


def main():
    """Main entry point for FIXED CalibreMCP server"""
    import sys
    
    print("Starting FIXED CalibreMCP - Local database priority mode", file=sys.stderr)
    print("Will use local database when available, fall back to web API", file=sys.stderr)
    
    # Check configuration
    local_path = get_local_library_path()
    if local_path:
        print(f"Local library path configured: {local_path}", file=sys.stderr)
        if os.path.exists(local_path):
            print("✅ Local library path exists", file=sys.stderr)
        else:
            print("❌ Local library path does not exist", file=sys.stderr)
    else:
        print("No local library path configured", file=sys.stderr)
    
    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()
