"""
MCP tools for book-related operations.
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from ..services.book_service import BookSearchResult, BookDetail, book_service
from .base_tool import BaseTool, mcp_tool
from ..logging_config import get_logger
import json

logger = get_logger("calibremcp.tools.book_tools")

class BookSearchInput(BaseModel):
    """Input model for advanced book search with fuzzy matching and relevance scoring."""
    text: Optional[str] = Field(
        None,
        description="Search text to look for in the specified fields. Supports quoted phrases for exact matches."
    )
    fields: Optional[Union[str, List[str]]] = Field(
        ["title^3", "authors^2", "tags^2", "series^1.5", "comments^1", "publisher^1.5"],
        description="""Fields to search in with optional boosting (e.g., "title^3" boosts title matches).
        Available fields: title, authors, tags, series, comments, publisher.
        Can be a JSON array or comma-separated string."""
    )
    operator: Optional[str] = Field(
        "OR",
        description="Search operator (AND, OR, or FUZZY)",
        regex="^(?i)(AND|OR|FUZZY)$"
    )
    fuzziness: Optional[Union[int, str]] = Field(
        "AUTO",
        description="""Fuzziness level for fuzzy search. Can be:
        - 'AUTO': automatic fuzziness based on term length
        - 0-2: fixed fuzziness level
        - '0': exact match only"""
    )
    min_score: Optional[float] = Field(
        0.1,
        description="Minimum relevance score (0-1) for results to be included",
        ge=0.0,
        le=1.0
    )
    highlight: Optional[bool] = Field(
        False,
        description="Whether to include highlighted snippets of matching text in results"
    )
    suggest: Optional[bool] = Field(
        False,
        description="Whether to include search suggestions for misspelled queries"
    )
    author: Optional[str] = Field(
        None,
        description="Filter by author name (case-insensitive partial match)"
    )
    tag: Optional[str] = Field(
        None,
        description="Filter by tag name (case-insensitive partial match)"
    )
    series: Optional[str] = Field(
        None,
        description="Filter by series name (case-insensitive partial match)"
    )
    comment: Optional[str] = Field(
        None,
        description="Search in book comments (case-insensitive partial match)"
    )
    has_empty_comments: Optional[bool] = Field(
        None,
        description="Filter books with empty (True) or non-empty (False) comments"
    )
    rating: Optional[int] = Field(
        None,
        description="Filter by exact star rating (1-5)",
        ge=1,
        le=5
    )
    min_rating: Optional[int] = Field(
        None,
        description="Filter by minimum star rating (1-5)",
        ge=1,
        le=5
    )
    unrated: Optional[bool] = Field(
        None,
        description="Filter for books with no rating when True"
    )
    publisher: Optional[str] = Field(
        None,
        description="Filter by publisher name (case-insensitive partial match)"
    )
    publishers: Optional[List[str]] = Field(
        None,
        description="Filter by multiple publishers (OR condition)"
    )
    has_publisher: Optional[bool] = Field(
        None,
        description="Filter books with (True) or without (False) a publisher"
    )
    pubdate_start: Optional[str] = Field(
        None,
        description="Filter by publication date (YYYY-MM-DD format), inclusive start date"
    )
    pubdate_end: Optional[str] = Field(
        None,
        description="Filter by publication date (YYYY-MM-DD format), inclusive end date"
    )
    added_after: Optional[str] = Field(
        None,
        description="Filter by date added (YYYY-MM-DD format), inclusive start date"
    )
    added_before: Optional[str] = Field(
        None,
        description="Filter by date added (YYYY-MM-DD format), inclusive end date"
    )
    min_size: Optional[int] = Field(
        None,
        description="Minimum file size in bytes",
        ge=0
    )
    max_size: Optional[int] = Field(
        None,
        description="Maximum file size in bytes",
        ge=0
    )
    formats: Optional[Union[str, List[str]]] = Field(
        None,
        description="Filter by file formats (e.g., 'EPUB,PDF' or ['EPUB', 'PDF'])"
    )
    limit: int = Field(
        50,
        description="Maximum number of results to return",
        ge=1,
        le=1000
    )
    offset: int = Field(
        0,
        description="Number of results to skip for pagination",
        ge=0
    )
    
    @validator('fields', pre=True)
    def parse_fields(cls, v):
        if isinstance(v, str):
            try:
                # Try to parse as JSON array first
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, split by comma and strip whitespace
                return [field.strip() for field in v.split(',') if field.strip()]
        return v
        
    @validator('formats', pre=True)
    def parse_formats(cls, v):
        if isinstance(v, str):
            try:
                # Try to parse as JSON array first
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, split by comma and strip whitespace, convert to uppercase
                return [fmt.strip().upper() for fmt in v.split(',') if fmt.strip()]
        elif isinstance(v, list):
            # Ensure all formats are uppercase
            return [fmt.upper() if isinstance(fmt, str) else str(fmt).upper() for fmt in v]
        return v
    
    class Config:
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }

class BookSearchResultOutput(BookSearchResult):
    """Output model for book search results."""
    class Config:
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }

class BookSearchOutput(BaseModel):
    """Output model for paginated book search results."""
    items: List[BookSearchResultOutput] = Field(
        ...,
        description="List of matching books"
    )
    total: int = Field(
        ...,
        description="Total number of matching books"
    )
    page: int = Field(
        ...,
        description="Current page number"
    )
    per_page: int = Field(
        ...,
        description="Number of items per page"
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages"
    )

class BookDetailOutput(BookDetail):
    """Output model for book details."""
    class Config:
        json_encoders = {
            'datetime': lambda v: v.isoformat() if v else None
        }

class BookTools(BaseTool):
    """MCP tools for book-related operations."""
    
    @mcp_tool(
        name="search_books",
        description="""Advanced book search with fuzzy matching, relevance scoring, and faceted filtering.
        
        Features:
        - Field-specific boosting (e.g., title^3 boosts title matches more)
        - Fuzzy search with configurable fuzziness
        - Phrase search with quoted terms
        - Relevance scoring and result highlighting
        - Search suggestions for misspelled queries
        - Faceted filtering by author, tag, series, etc.
        """,
        input_model=BookSearchInput,
        output_model=BookSearchOutput
    )
    async def search_books(
        self,
        text: Optional[str] = None,
        fields: Optional[Union[str, List[str]]] = None,
        operator: str = "OR",
        fuzziness: Union[int, str] = "AUTO",
        min_score: float = 0.1,
        highlight: bool = False,
        suggest: bool = False,
        query: Optional[str] = None,  # For backward compatibility
        author: Optional[str] = None,
        tag: Optional[str] = None,
        series: Optional[str] = None,
        comment: Optional[str] = None,
        has_empty_comments: Optional[bool] = None,
        rating: Optional[int] = None,
        min_rating: Optional[int] = None,
        unrated: Optional[bool] = None,
        publisher: Optional[str] = None,
        publishers: Optional[List[str]] = None,
        has_publisher: Optional[bool] = None,
        pubdate_start: Optional[str] = None,
        pubdate_end: Optional[str] = None,
        added_after: Optional[str] = None,
        added_before: Optional[str] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        formats: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search and list books with various filters.
        
        This tool allows searching through the entire library with flexible filtering
        by title, author, tags, series, dates, file size, and formats. Results are 
        paginated for efficient browsing of large libraries.
        
        Example:
            # Search for books about Python
            list_books(query="python")
            
            # Get books by a specific author
            list_books(author="Martin Fowler")
            
            # Get books in a series
            list_books(series="The Lord of the Rings")
            
            # Get books published in 2023
            list_books(pubdate_start="2023-01-01", pubdate_end="2023-12-31")
            
            # Get books added in the last 30 days
            from datetime import datetime, timedelta
            last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            list_books(added_after=last_month, added_before=today)
            
            # Get books between 1MB and 10MB in size
            list_books(min_size=1048576, max_size=10485760)  # 1MB to 10MB
            
            # Get books in specific formats
            list_books(formats=["EPUB", "PDF"])
            
            # Find books with empty comments
            list_books(has_empty_comments=True)
            
            # Find highly rated books
            list_books(min_rating=4)
            
            # Find unrated books
            list_books(unrated=True)
            
            # Find books by publisher
            list_books(publisher="O'Reilly Media")
            
            # Find books by multiple publishers
            list_books(publishers=["O'Reilly Media", "No Starch Press"])
            
            # Find books without a publisher
            list_books(has_publisher=False)
            
        Args:
            query: Search term to filter books by title, author, series, or tags
            author: Filter books by author name (case-insensitive partial match)
            tag: Filter books by tag name (case-insensitive partial match)
            series: Filter books by series name (case-insensitive partial match)
            comment: Search in book comments (case-insensitive partial match)
            has_empty_comments: Filter books with empty (True) or non-empty (False) comments
            rating: Filter by exact star rating (1-5)
            min_rating: Filter by minimum star rating (1-5)
            unrated: Filter for books with no rating when True
            publisher: Filter by publisher name (case-insensitive partial match)
            publishers: Filter by multiple publishers (OR condition)
            has_publisher: Filter books with (True) or without (False) a publisher
            pubdate_start: Filter by publication date (YYYY-MM-DD), inclusive start
            pubdate_end: Filter by publication date (YYYY-MM-DD), inclusive end
            added_after: Filter by date added (YYYY-MM-DD), inclusive start
            added_before: Filter by date added (YYYY-MM-DD), inclusive end
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes
            formats: List of file formats to include (e.g., ["EPUB", "PDF"])
            limit: Maximum number of results to return (1-1000)
            offset: Number of results to skip for pagination
            
        Returns:
            Dictionary containing paginated list of books and metadata:
            {
                "items": [book1, book2, ...],  # List of book objects
                "total": 42,                   # Total number of matching books
                "page": 1,                     # Current page number
                "per_page": 10,                # Number of items per page
                "total_pages": 5               # Total number of pages
            }
            
        Raises:
            ValueError: If input validation fails
            Exception: For other unexpected errors
        """
        logger.info("Listing books", extra={
            "service": "book_tools",
            "action": "list_books",
            "query": query,
            "author": author,
            "tag": tag,
            "series": series,
            "comment": comment,
            "has_empty_comments": has_empty_comments,
            "rating": rating,
            "min_rating": min_rating,
            "unrated": unrated,
            "publisher": publisher,
            "publishers": publishers,
            "has_publisher": has_publisher,
            "pubdate_start": pubdate_start,
            "pubdate_end": pubdate_end,
            "added_after": added_after,
            "added_before": added_before,
            "min_size": min_size,
            "max_size": max_size,
            "formats": formats,
            "limit": limit,
            "offset": offset
        })
        
        try:
            # Input validation
            if limit < 1 or limit > 1000:
                raise ValueError("Limit must be between 1 and 1000")
            if offset < 0:
                raise ValueError("Offset cannot be negative")
                
            # Convert filters to the format expected by book_service.get_all
            filters = {}
        
            # Process fields and boost factors
            field_boosts = {}
            if fields is None:
                fields = ["title^3", "authors^2", "tags^2", "series^1.5", "comments^1"]
            elif isinstance(fields, str):
                try:
                    fields = json.loads(fields)
                except json.JSONDecodeError:
                    fields = [f.strip() for f in fields.split(',') if f.strip()]
        
            # Parse field boosts (e.g., "title^3" -> {"title": 3.0})
            processed_fields = []
            for field in fields:
                if '^' in field:
                    field_name, boost = field.split('^', 1)
                    try:
                        field_boosts[field_name] = float(boost)
                        processed_fields.append(field_name)
                    except (ValueError, TypeError):
                        processed_fields.append(field)
                else:
                    processed_fields.append(field)
                
            # Handle text search across specified fields
            search_text = text or query  # Support both text and query parameters
            search_terms = []
            phrases = []
        
            if search_text:
                # Extract quoted phrases first
                import re
                phrases = re.findall(r'"(.*?)"', search_text)
                remaining_text = re.sub(r'"(.*?)"', '', search_text)
            
                # Get individual terms from remaining text
                search_terms = [term.strip() for term in remaining_text.split() if term.strip()]
            
                # If no fields specified, use all with default boosts
                if not processed_fields:
                    processed_fields = ["title", "authors", "tags", "series", "comments"]
            
                # Build field-specific queries with boosts
                search_queries = []
                
                # Handle exact phrase matches first
                for phrase in phrases:
                    if not phrase:
                        continue
                    phrase_queries = []
                    for field in processed_fields:
                        field_name = field.split('^')[0]  # Remove boost if present
                        if field_name in ["authors", "tags"]:
                            # For multi-value fields, use contains with quoted phrase
                            phrase_queries.append(f'{field_name}:"{phrase}"')
                        else:
                            phrase_queries.append(f'{field_name}:"{phrase}"')
                    
                    if phrase_queries:
                        search_queries.append(f"({' OR '.join(phrase_queries)})")
                
                # Handle individual terms with fuzzy matching
                if operator.upper() == "FUZZY":
                    fuzz_str = f"~{fuzziness}" if fuzziness != "AUTO" else "~"
                    for term in search_terms:
                        term_queries = []
                        for field in processed_fields:
                            field_name = field.split('^')[0]  # Remove boost if present
                            boost = field_boosts.get(field_name, 1.0)
                            boost_str = f"^{boost}" if boost != 1.0 else ""
                            term_queries.append(f"{field_name}:{term}{fuzz_str}{boost_str}")
                        
                        if term_queries:
                            search_queries.append(f"({' OR '.join(term_queries)})")
                
                elif operator.upper() == "AND":
                    # Require all terms to match (in any field)
                    for term in search_terms:
                        term_queries = []
                        for field in processed_fields:
                            field_name = field.split('^')[0]
                            boost = field_boosts.get(field_name, 1.0)
                            boost_str = f"^{boost}" if boost != 1.0 else ""
                            term_queries.append(f"{field_name}:{term}{boost_str}")
                        
                        if term_queries:
                            search_queries.append(f"({' OR '.join(term_queries)})")
                
                else:  # OR operator (default)
                    term_queries = []
                    for field in processed_fields:
                        field_name = field.split('^')[0]
                        boost = field_boosts.get(field_name, 1.0)
                        boost_str = f"^{boost}" if boost != 1.0 else ""
                        
                        # Add each term to this field with OR between them
                        field_terms = [f"{field_name}:{term}{boost_str}" for term in search_terms]
                        if field_terms:
                            term_queries.append(f"({' OR '.join(field_terms)})")
                    
                    if term_queries:
                        search_queries.extend(term_queries)
                
                # Combine all queries with the appropriate operator
                if search_queries:
                    join_operator = " AND " if operator.upper() in ["AND", "FUZZY"] else " OR "
                    filters['search'] = join_operator.join(search_queries)
                    
                    # Add minimum score filter if specified
                    if min_score > 0:
                        filters['min_score'] = min_score
                    
                    # Add highlighting if requested
                    if highlight:
                        filters['highlight'] = {
                            'fields': {field: {} for field in processed_fields if field not in ['authors', 'tags']},
                            'pre_tags': ['<mark>'],
                            'post_tags': ['</mark>']
                        }
        
            # Add other filters
            if author:
                filters['author_name'] = author
            if tag:
                filters['tag_name'] = tag
            if series:
                filters['series_name'] = series
            if comment is not None:
                filters['comment'] = comment
            
            if has_empty_comments is not None:
                filters['has_empty_comments'] = has_empty_comments
            
            if rating is not None:
                if rating < 1 or rating > 5:
                    raise ValueError("Rating must be between 1 and 5")
                filters['rating'] = rating
            
            if min_rating is not None:
                if min_rating < 1 or min_rating > 5:
                    raise ValueError("Minimum rating must be between 1 and 5")
                filters['min_rating'] = min_rating
            
            if unrated is not None:
                filters['unrated'] = unrated
            
            if publisher is not None:
                filters['publisher'] = publisher
            
            if publishers is not None:
                if isinstance(publishers, str):
                    try:
                        publishers = json.loads(publishers)
                    except json.JSONDecodeError:
                        publishers = [p.strip() for p in publishers.split(',') if p.strip()]
                if publishers:  # Only add if not empty
                    filters['publishers'] = publishers
            
            if has_publisher is not None:
                filters['has_publisher'] = has_publisher
            
            if pubdate_start:
                filters['pubdate_start'] = pubdate_start
            if pubdate_end:
                filters['pubdate_end'] = pubdate_end
            
            if added_after:
                filters['added_after'] = added_after
            if added_before:
                filters['added_before'] = added_before
            
            if min_size is not None:
                filters['min_size'] = min_size
            if max_size is not None:
                filters['max_size'] = max_size
            
            if formats is not None:
                if isinstance(formats, str):
                    try:
                        formats = json.loads(formats)
                    except json.JSONDecodeError:
                        formats = [f.strip().upper() for f in formats.split(',') if f.strip()]
                if formats:  # Only add if not empty
                    filters['formats'] = [f.upper() if isinstance(f, str) else str(f).upper() for f in formats]
            
            # Add search suggestions if requested and we have a query
            if suggest and search_text and len(search_terms) > 0:
                filters['suggest'] = {
                    'text': search_text,
                    'term': {
                        'field': '_all',
                        'sort': 'score',
                        'suggest_mode': 'popular'
                    }
                }
            
            # Get paginated results with relevance scoring
            result = book_service.search(
                query=filters.pop('search', None),
                filters={k: v for k, v in filters.items() if k != 'search'},
                offset=offset,
                limit=limit,
                highlight=highlight,
                min_score=min_score
            )
            
            # Convert to the expected output format
            response = {
                "items": [self._enhance_book_result(book, highlight) for book in result.get("items", [])],
                "total": result.get("total", 0),
                "page": (offset // limit) + 1 if limit > 0 else 1,
                "per_page": limit,
                "total_pages": (result.get("total", 0) + limit - 1) // limit if limit > 0 else 1,
                "suggestions": result.get("suggestions", []),
                "max_score": result.get("max_score", 0)
            }
            
        except ValueError as ve:
            logger.error("Invalid input parameters", extra={
                "service": "book_tools",
                "action": "list_books_error",
                "error": str(ve),
                "error_type": "validation_error"
            })
            raise
            
        except Exception as e:
            logger.error(f"Error searching books: {str(e)}", exc_info=True)
            # Return empty results with error information
            return {
                "items": [],
                "total": 0,
                "page": (offset // limit) + 1 if limit > 0 else 1,
                "per_page": limit,
                "total_pages": 0,
                "error": str(e),
                "suggestions": []
            }
    
    def _enhance_book_result(self, book: Any, highlight: bool = False) -> Dict[str, Any]:
        """Convert a book model to a dictionary with enhanced search results."""
        if not book:
            return {}
            
        result = {
            "id": book.id,
            "title": book.title,
            "authors": [a.name for a in book.authors] if hasattr(book, 'authors') else [],
            "series": book.series.name if hasattr(book, 'series') and book.series else None,
            "series_index": book.series_index if hasattr(book, 'series_index') else None,
            "publisher": book.publisher if hasattr(book, 'publisher') else None,
            "rating": book.rating if hasattr(book, 'rating') else None,
            "formats": [f.format for f in book.data] if hasattr(book, 'data') else [],
            "tags": [t.name for t in book.tags] if hasattr(book, 'tags') else [],
            "comments": book.comments[0].text if hasattr(book, 'comments') and book.comments else None,
            "pubdate": book.pubdate.isoformat() if hasattr(book, 'pubdate') and book.pubdate else None,
            "added_at": book.timestamp.isoformat() if hasattr(book, 'timestamp') and book.timestamp else None,
            "size": sum(d.size for d in book.data) if hasattr(book, 'data') and book.data else 0,
            "score": getattr(book, '_score', None)  # Add relevance score if available
        }
        
        # Add highlighted snippets if available
        if highlight and hasattr(book, '_highlight'):
            result['highlight'] = book._highlight
            
        return result
    
    @mcp_tool(
        name="get_book",
        description="Get detailed information about a book by ID",
        output_model=BookDetailOutput
    )
    async def get_book(self, book_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific book.
        
        This tool retrieves comprehensive information about a book, including
        all metadata, formats, and related entities like authors, series, and tags.
        
        Args:
            book_id: The unique identifier of the book
            
        Returns:
            Detailed book information or None if not found
            
        Example:
            # Get details for book with ID 123
            get_book(book_id=123)
        """
        book = self.book_service.get_book(book_id)
        return book.dict() if book else None
    
    @mcp_tool(
        name="get_recent_books",
        description="Get recently added books",
        output_model=List[BookSearchResultOutput]
    )
    async def get_recent_books(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get a list of the most recently added books.
        
        This is useful for displaying a "recently added" section in the UI.
        
        Args:
            limit: Maximum number of recent books to return (default: 10)
            
        Returns:
            List of recently added books
            
        Example:
            # Get 5 most recently added books
            get_recent_books(limit=5)
        """
        books = self.book_service.get_recent_books(limit=limit)
        return [book.dict() for book in books]
    
    @mcp_tool(
        name="get_books_by_series",
        description="Get all books in a series",
        output_model=List[BookSearchResultOutput]
    )
    async def get_books_by_series(self, series_id: int) -> List[Dict[str, Any]]:
        """
        Get all books that belong to a specific series.
        
        Books are returned in series order (based on series_index).
        
        Args:
            series_id: The ID of the series
            
        Returns:
            List of books in the series, ordered by series index
            
        Example:
            # Get all books in series with ID 42
            get_books_by_series(series_id=42)
        """
        books = self.book_service.get_books_by_series(series_id)
        return [book.dict() for book in books]
    
    @mcp_tool(
        name="get_books_by_author",
        description="Get all books by a specific author",
        output_model=List[BookSearchResultOutput]
    )
    async def get_books_by_author(
        self, 
        author_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get all books written by a specific author.
        
        Results are paginated for efficient browsing of large collections.
        
        Args:
            author_id: The ID of the author
            limit: Maximum number of results to return (default: 50)
            offset: Number of results to skip (for pagination)
            
        Returns:
            Paginated list of books by the author
            
        Example:
            # Get first page of books by author with ID 42
            get_books_by_author(author_id=42, limit=10, offset=0)
            
            # Get next page
            get_books_by_author(author_id=42, limit=10, offset=10)
        """
        return self.author_service.get_books_by_author(
            author_id=author_id,
            limit=limit,
            offset=offset
        )
