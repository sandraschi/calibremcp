"""Advanced search functionality for CalibreMCP."""
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
import re
import math
from collections import defaultdict

from fastmcp import MCPTool, Param

# Models
class SearchFilter(BaseModel):
    """A single search filter condition."""
    field: str
    operator: str  # '=', '!=', '>', '<', '>=', '<=', 'contains', 'not_contains', 'starts_with', 'ends_with', 'regex', 'in', 'not_in', 'exists', 'not_exists'
    value: Any
    
    @validator('operator')
    def validate_operator(cls, v):
        valid_operators = ['=', '!=', '>', '<', '>=', '<=', 'contains', 'not_contains', 
                          'starts_with', 'ends_with', 'regex', 'in', 'not_in', 'exists', 'not_exists']
        if v not in valid_operators:
            raise ValueError(f"Invalid operator. Must be one of {valid_operators}")
        return v

class SearchQuery(BaseModel):
    """A complete search query with multiple conditions."""
    query: Optional[str] = None  # Full-text search query
    filters: List[Union[Dict, SearchFilter]] = Field(default_factory=list)
    must_match_all: bool = True  # If False, use OR logic between filters
    fields: List[str] = Field(default_factory=list)  # Fields to return
    highlight: bool = False  # Whether to include highlighted snippets
    highlight_size: int = 200  # Approximate size of highlight snippets in characters
    highlight_tag: str = "em"  # HTML tag to use for highlighting
    
    @validator('filters', pre=True)
    def convert_dicts_to_filters(cls, v):
        if v is None:
            return []
        return [f if isinstance(f, SearchFilter) else SearchFilter(**f) for f in v]

class SearchResult(BaseModel):
    """A single search result."""
    id: str
    score: float
    highlights: Dict[str, List[str]] = Field(default_factory=dict)
    document: Dict[str, Any] = Field(default_factory=dict)

class SearchResults(BaseModel):
    """Paginated search results."""
    total: int
    took_ms: float
    page: int
    page_size: int
    results: List[SearchResult]
    facets: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    
    @property
    def total_pages(self) -> int:
        """Calculate the total number of pages."""
        return math.ceil(self.total / self.page_size) if self.page_size > 0 else 0
    
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

# Main tool
class AdvancedSearchTool(MCPTool):
    """Advanced search functionality for the Calibre library."""
    
    name = "advanced_search"
    description = "Advanced search with full-text and faceted filtering"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = None  # In-memory index (replace with a real search engine in production)
    
    async def _run(self, action: str, **kwargs) -> Dict:
        """Route to the appropriate search handler."""
        handler = getattr(self, f"search_{action}", None)
        if not handler:
            return {"error": f"Unknown search action: {action}", "success": False}
        
        try:
            return await handler(**kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}
    
    # Search Operations
    async def search_books(self, 
                         query: Optional[Union[str, Dict]] = None,
                         page: int = 1,
                         page_size: int = 20,
                         sort: Optional[str] = None,
                         sort_desc: bool = True,
                         library_path: Optional[str] = None) -> Dict:
        """
        Search books with advanced query capabilities.
        
        Args:
            query: Search query (string or structured query object)
            page: Page number (1-based)
            page_size: Number of results per page
            sort: Field to sort by
            sort_desc: Sort in descending order
            library_path: Path to the Calibre library
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage
        
        # Parse query
        search_query = self._parse_query(query)
        
        # Get all books (in a real implementation, this would use an index)
        storage = LocalStorage(library_path)
        all_books = await storage.get_all_books()
        
        # Convert to dict for easier manipulation
        books = [book.dict() for book in all_books]
        
        # Apply filters
        filtered_books = self._apply_filters(books, search_query.filters, search_query.must_match_all)
        
        # Apply full-text search if query is provided
        if search_query.query:
            filtered_books = self._apply_fulltext_search(filtered_books, search_query.query)
        
        # Sort results
        if sort:
            filtered_books = self._sort_results(filtered_books, sort, sort_desc)
        
        # Apply pagination
        total = len(filtered_books)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = filtered_books[start_idx:end_idx]
        
        # Format results
        results = []
        for book in paginated:
            result = {
                "id": book.get("id"),
                "score": book.get("_score", 1.0),
                "document": {}
            }
            
            # Include requested fields
            if search_query.fields:
                for field in search_query.fields:
                    if field in book:
                        result["document"][field] = book[field]
            else:
                result["document"] = book
            
            # Add highlights if requested
            if search_query.highlight and "_highlights" in book:
                result["highlights"] = book["_highlights"]
            
            results.append(SearchResult(**result).dict())
        
        # Calculate facets (in a real implementation, this would be more efficient)
        facets = self._calculate_facets(filtered_books)
        
        return SearchResults(
            total=total,
            took_ms=0,  # In a real implementation, measure execution time
            page=page,
            page_size=page_size,
            results=results,
            facets=facets
        ).dict()
    
    async def search_similar(self, 
                           book_id: str,
                           fields: List[str] = ["title", "authors", "tags", "comments"],
                           limit: int = 10,
                           library_path: Optional[str] = None) -> Dict:
        """
        Find books similar to the specified book.
        
        Args:
            book_id: ID of the book to find similar books for
            fields: Fields to consider for similarity
            limit: Maximum number of similar books to return
            library_path: Path to the Calibre library
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage
        
        # Get the target book
        storage = LocalStorage(library_path)
        target_book = await storage.get_metadata(book_id)
        
        if not target_book:
            return {"error": f"Book {book_id} not found", "success": False}
        
        # Get all other books
        all_books = await storage.get_all_books()
        other_books = [b for b in all_books if str(b.id) != str(book_id)]
        
        # Calculate similarity scores
        similarities = []
        target_text = self._get_book_text(target_book, fields)
        
        for book in other_books:
            book_text = self._get_book_text(book, fields)
            similarity = self._calculate_similarity(target_text, book_text)
            similarities.append((book, similarity))
        
        # Sort by similarity and get top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_matches = similarities[:limit]
        
        # Format results
        results = []
        for book, score in top_matches:
            results.append({
                "id": str(book.id),
                "title": book.title,
                "authors": book.authors,
                "score": score,
                "cover_url": f"/api/books/{book.id}/cover" if book.has_cover else None
            })
        
        return {
            "success": True,
            "query_book": {
                "id": str(target_book.id),
                "title": target_book.title,
                "authors": target_book.authors
            },
            "results": results,
            "total": len(results)
        }
    
    # Helper Methods
    def _parse_query(self, query: Optional[Union[str, Dict]]) -> SearchQuery:
        """Parse a query into a SearchQuery object."""
        if query is None:
            return SearchQuery()
        
        if isinstance(query, str):
            return SearchQuery(query=query)
        
        if isinstance(query, dict):
            return SearchQuery(**query)
        
        raise ValueError("Invalid query format. Must be a string or dictionary.")
    
    def _apply_filters(self, books: List[Dict], filters: List[SearchFilter], must_match_all: bool = True) -> List[Dict]:
        """Apply filters to a list of books."""
        if not filters:
            return books
        
        filtered = []
        
        for book in books:
            matches = []
            
            for filter_ in filters:
                field_value = book.get(filter_.field)
                matches.append(self._evaluate_filter(field_value, filter_.operator, filter_.value))
            
            if must_match_all and all(matches):
                filtered.append(book)
            elif not must_match_all and any(matches):
                filtered.append(book)
        
        return filtered
    
    def _evaluate_filter(self, field_value: Any, operator: str, filter_value: Any) -> bool:
        """Evaluate a single filter condition."""
        try:
            if operator == '=':
                return field_value == filter_value
            elif operator == '!=':
                return field_value != filter_value
            elif operator == '>':
                return field_value > filter_value
            elif operator == '<':
                return field_value < filter_value
            elif operator == '>=':
                return field_value >= filter_value
            elif operator == '<=':
                return field_value <= filter_value
            elif operator == 'contains':
                if field_value is None:
                    return False
                if isinstance(field_value, str):
                    return filter_value.lower() in field_value.lower()
                if isinstance(field_value, (list, set)):
                    return any(filter_value.lower() in str(v).lower() for v in field_value)
                return False
            elif operator == 'not_contains':
                if field_value is None:
                    return True
                if isinstance(field_value, str):
                    return filter_value.lower() not in field_value.lower()
                if isinstance(field_value, (list, set)):
                    return all(filter_value.lower() not in str(v).lower() for v in field_value)
                return True
            elif operator == 'starts_with':
                if not field_value:
                    return False
                return str(field_value).lower().startswith(str(filter_value).lower())
            elif operator == 'ends_with':
                if not field_value:
                    return False
                return str(field_value).lower().endswith(str(filter_value).lower())
            elif operator == 'regex':
                if not field_value:
                    return False
                return bool(re.search(filter_value, str(field_value), re.IGNORECASE))
            elif operator == 'in':
                if not field_value:
                    return False
                if isinstance(filter_value, (list, set, tuple)):
                    if isinstance(field_value, (list, set, tuple)):
                        return any(f in filter_value for f in field_value)
                    return field_value in filter_value
                return str(field_value) == str(filter_value)
            elif operator == 'not_in':
                if not field_value:
                    return True
                if isinstance(filter_value, (list, set, tuple)):
                    if isinstance(field_value, (list, set, tuple)):
                        return all(f not in filter_value for f in field_value)
                    return field_value not in filter_value
                return str(field_value) != str(filter_value)
            elif operator == 'exists':
                return field_value is not None and field_value != ""
            elif operator == 'not_exists':
                return field_value is None or field_value == ""
            
            return False
        except Exception:
            return False
    
    def _apply_fulltext_search(self, books: List[Dict], query: str) -> List[Dict]:
        """Apply full-text search to a list of books."""
        # In a real implementation, this would use a proper search engine
        # For now, do a simple case-insensitive search in title, authors, and tags
        
        query_terms = query.lower().split()
        
        for book in books:
            score = 0.0
            highlights = {}
            
            # Search in title
            if "title" in book and book["title"]:
                title = book["title"].lower()
                for term in query_terms:
                    if term in title:
                        score += 2.0  # Higher weight for title matches
                        
                        # Add highlight
                        if "title" not in highlights:
                            highlights["title"] = []
                        
                        # Simple highlighting (in a real implementation, use a proper highlighter)
                        highlighted = book["title"].replace(term, f"<{self._highlight_tag}>{term}</{self._highlight_tag}>")
                        highlights["title"].append(highlighted)
            
            # Search in authors
            if "authors" in book and book["authors"]:
                for author in book["authors"]:
                    author_lower = author.lower()
                    for term in query_terms:
                        if term in author_lower:
                            score += 1.5  # Slightly lower weight for author matches
                            
                            # Add highlight
                            if "authors" not in highlights:
                                highlights["authors"] = []
                            
                            highlighted = author.replace(term, f"<{self._highlight_tag}>{term}</{self._highlight_tag}>")
                            if highlighted not in highlights["authors"]:
                                highlights["authors"].append(highlighted)
            
            # Search in tags
            if "tags" in book and book["tags"]:
                for tag in book["tags"]:
                    tag_lower = tag.lower()
                    for term in query_terms:
                        if term in tag_lower:
                            score += 1.0  # Lower weight for tag matches
                            
                            # Add highlight
                            if "tags" not in highlights:
                                highlights["tags"] = []
                            
                            highlighted = tag.replace(term, f"<{self._highlight_tag}>{term}</{self._highlight_tag}>")
                            if highlighted not in highlights["tags"]:
                                highlights["tags"].append(highlighted)
            
            # Search in comments/description
            if "comments" in book and book["comments"]:
                comments = book["comments"].lower()
                for term in query_terms:
                    if term in comments:
                        score += 0.5  # Lower weight for content matches
                        
                        # Add highlight with context
                        if "comments" not in highlights:
                            highlights["comments"] = []
                        
                        # Simple snippet extraction (in a real implementation, use a proper highlighter)
                        start = max(0, comments.find(term) - 50)
                        end = min(len(comments), comments.find(term) + len(term) + 50)
                        snippet = book["comments"][start:end]
                        
                        # Add ellipsis if not at start/end
                        if start > 0:
                            snippet = "..." + snippet[3:]  # Remove first 3 chars to make room for ellipsis
                        if end < len(comments):
                            snippet = snippet[:-3] + "..."  # Remove last 3 chars to make room for ellipsis
                        
                        # Highlight term
                        snippet = snippet.replace(term, f"<{self._highlight_tag}>{term}</{self._highlight_tag}>")
                        highlights["comments"].append(snippet)
            
            # Store score and highlights
            book["_score"] = score
            if highlights:
                book["_highlights"] = highlights
        
        # Filter out books with zero score and sort by score
        scored_books = [b for b in books if b.get("_score", 0) > 0]
        scored_books.sort(key=lambda x: x.get("_score", 0), reverse=True)
        
        return scored_books
    
    def _sort_results(self, books: List[Dict], field: str, descending: bool = True) -> List[Dict]:
        """Sort search results by a field."""
        if not books:
            return []
        
        # Handle special fields
        if field == "relevance" and "_score" in books[0]:
            key = lambda x: x.get("_score", 0)
        elif field == "date_added" and "timestamp" in books[0]:
            key = lambda x: x.get("timestamp") or datetime.min
        else:
            key = lambda x: x.get(field, "")
        
        # Sort with None values at the end
        def sort_key(x):
            val = key(x)
            return (val is None, val) if descending else (val is not None, val)
        
        return sorted(books, key=sort_key, reverse=descending)
    
    def _calculate_facets(self, books: List[Dict]) -> Dict[str, Dict[str, int]]:
        """Calculate facets for search results."""
        if not books:
            return {}
        
        # Define which fields to facet on
        facet_fields = ["authors", "tags", "publisher", "languages", "series"]
        facets = {}
        
        for field in facet_fields:
            counter = Counter()
            
            for book in books:
                value = book.get(field)
                if value is None:
                    continue
                    
                if isinstance(value, (list, set, tuple)):
                    for item in value:
                        counter[item] += 1
                else:
                    counter[value] += 1
            
            if counter:
                facets[field] = dict(counter.most_common(10))  # Top 10 values
        
        return facets
    
    def _get_book_text(self, book, fields: List[str]) -> str:
        """Extract text from a book for similarity comparison."""
        text_parts = []
        
        for field in fields:
            value = getattr(book, field, None)
            if not value:
                continue
                
            if isinstance(value, (list, set, tuple)):
                text_parts.extend(str(v) for v in value)
            else:
                text_parts.append(str(value))
        
        return " ".join(text_parts).lower()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings."""
        # Simple Jaccard similarity for demonstration
        # In a real implementation, use a more sophisticated method like TF-IDF or embeddings
        
        if not text1 or not text2:
            return 0.0
        
        set1 = set(text1.split())
        set2 = set(text2.split())
        
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
