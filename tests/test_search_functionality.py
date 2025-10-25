"""Tests for search functionality in Calibre MCP."""
import pytest
from unittest.mock import MagicMock

from calibre_mcp.tools.book_tools import BookTools
from calibre_mcp.services.book_service import BookService
from calibre_mcp.models.book import Book

# Sample test data
SAMPLE_BOOKS = [
    Book(
        id="book1",
        title="Python Programming",
        authors=["John Doe", "Jane Smith"],
        tags=["programming", "python", "development"],
        comments="A comprehensive guide to Python programming",
        series="Python Series",
        publisher="Tech Books Inc.",
        published_date="2023-01-15"
    ),
    Book(
        id="book2",
        title="Advanced Python",
        authors=["John Doe"],
        tags=["advanced", "python", "algorithms"],
        comments="Advanced Python patterns and algorithms",
        series="Python Series",
        publisher="Code Masters"
    ),
    Book(
        id="book3",
        title="JavaScript Essentials",
        authors=["Alice Johnson"],
        tags=["javascript", "web", "frontend"],
        comments="Learn JavaScript from scratch",
        publisher="Web Wizards"
    )
]

class TestSearchFunctionality:
    """Test suite for search functionality."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # Create a mock book service
        self.book_service = MagicMock(spec=BookService)
        
        # Setup mock responses
        self.book_service.get_all.return_value = {
            "items": SAMPLE_BOOKS,
            "total": len(SAMPLE_BOOKS),
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
        
        # Create the tool with the mocked service
        self.tool = BookTools(book_service=self.book_service)
    
    @pytest.mark.asyncio
    async def test_search_by_title(self):
        """Test searching books by title."""
        # Search for a book by title
        result = await self.tool.list_books(query="Python Programming")
        
        # Verify the service was called with the correct parameters
        self.book_service.get_all.assert_called_once_with(
            skip=0,
            limit=50,
            search="Python Programming"
        )
        
        # Verify the results
        assert len(result["items"]) > 0
        assert any(book.title == "Python Programming" for book in result["items"])
    
    @pytest.mark.asyncio
    async def test_search_by_author(self):
        """Test searching books by author."""
        # Search for books by author
        result = await self.tool.list_books(author="John Doe")
        
        # Verify the service was called with the correct parameters
        self.book_service.get_all.assert_called_once_with(
            skip=0,
            limit=50,
            author_name="John Doe"
        )
        
        # Verify the results
        assert len(result["items"]) > 0
        assert all("John Doe" in book.authors for book in result["items"])
    
    @pytest.mark.asyncio
    async def test_search_by_tag(self):
        """Test searching books by tag."""
        # Search for books by tag
        result = await self.tool.list_books(tag="python")
        
        # Verify the service was called with the correct parameters
        self.book_service.get_all.assert_called_once_with(
            skip=0,
            limit=50,
            tag_name="python"
        )
        
        # Verify the results
        assert len(result["items"]) > 0
        assert all("python" in [t.lower() for t in book.tags] for book in result["items"])
    
    @pytest.mark.asyncio
    async def test_search_by_comment(self):
        """Test searching books by comment content."""
        # Search for books by comment
        result = await self.tool.list_books(comment="comprehensive guide")
        
        # Verify the service was called with the correct parameters
        self.book_service.get_all.assert_called_once_with(
            skip=0,
            limit=50,
            comment="comprehensive guide"
        )
        
        # Verify the results
        assert len(result["items"]) > 0
        assert any("comprehensive guide" in book.comments.lower() for book in result["items"])
    
    @pytest.mark.asyncio
    async def test_search_combined_filters(self):
        """Test searching with multiple filters."""
        from datetime import datetime, timedelta
        
        # Define date ranges
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Search with multiple filters
        result = await self.tool.list_books(
            query="Python",
            author="John Doe",
            tag="programming",
            pubdate_start=start_date,
            pubdate_end=end_date,
            added_after=start_date,
            added_before=end_date,
            min_size=1024,  # 1KB
            max_size=10485760,  # 10MB
            formats=["EPUB", "PDF"]
        )
        
        # Verify the service was called with the correct parameters
        self.book_service.get_all.assert_called_once_with(
            skip=0,
            limit=50,
            search="Python",
            author_name="John Doe",
            tag_name="programming",
            pubdate_start=start_date,
            pubdate_end=end_date,
            timestamp_start=start_date,
            timestamp_end=end_date,
            min_size=1024,
            max_size=10485760,
            formats=["EPUB", "PDF"]
        )
    
    @pytest.mark.asyncio
    async def test_search_by_date_ranges(self):
        """Test searching by publication date and entry date ranges."""
        from datetime import datetime, timedelta
        
        # Define date ranges
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Test publication date range
        await self.tool.list_books(
            pubdate_start=start_date,
            pubdate_end=end_date
        )
        
        # Verify publication date filter
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            pubdate_start=start_date,
            pubdate_end=end_date
        )
        
        # Test entry date range
        await self.tool.list_books(
            added_after=start_date,
            added_before=end_date
        )
        
        # Verify entry date filter
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            timestamp_start=start_date,
            timestamp_end=end_date
        )
    
    @pytest.mark.asyncio
    async def test_search_by_size_range(self):
        """Test searching by file size range."""
        # Test minimum size
        await self.tool.list_books(min_size=1048576)  # 1MB
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            min_size=1048576
        )
        
        # Test maximum size
        await self.tool.list_books(max_size=5242880)  # 5MB
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            max_size=5242880
        )
        
        # Test both min and max size
        await self.tool.list_books(min_size=1048576, max_size=5242880)
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            min_size=1048576,
            max_size=5242880
        )
    
    @pytest.mark.asyncio
    async def test_search_by_file_type(self):
        """Test searching by file format."""
        # Test single format
        await self.tool.list_books(formats=["EPUB"])
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            formats=["EPUB"]
        )
        
        # Test multiple formats
        await self.tool.list_books(formats=["EPUB", "PDF", "MOBI"])
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            formats=["EPUB", "PDF", "MOBI"]
        )
    
    @pytest.mark.asyncio
    async def test_search_by_empty_comments(self):
        """Test filtering books with empty/non-empty comments."""
        # Test books with empty comments
        await self.tool.list_books(has_empty_comments=True)
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            has_empty_comments=True
        )
        
        # Test books with non-empty comments
        await self.tool.list_books(has_empty_comments=False)
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            has_empty_comments=False
        )
    
    @pytest.mark.asyncio
    async def test_search_by_rating(self):
        """Test filtering books by star rating."""
        # Test exact rating
        await self.tool.list_books(rating=5)
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            rating=5
        )
        
        # Test minimum rating
        await self.tool.list_books(min_rating=4)
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            min_rating=4
        )
        
        # Test unrated books
        await self.tool.list_books(unrated=True)
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            unrated=True
        )
    
    @pytest.mark.asyncio
    async def test_search_by_publisher(self):
        """Test filtering books by publisher."""
        # Test single publisher
        await self.tool.list_books(publisher="O'Reilly Media")
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            publisher="O'Reilly Media"
        )
        
        # Test multiple publishers (OR condition)
        await self.tool.list_books(publishers=["O'Reilly Media", "No Starch Press"])
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            publishers=["O'Reilly Media", "No Starch Press"]
        )
        
        # Test empty publisher
        await self.tool.list_books(has_publisher=False)
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            has_publisher=False
        )
    
    @pytest.mark.asyncio
    async def test_search_pagination(self):
        """Test search results pagination."""
        # Test pagination
        result = await self.tool.list_books(
            query="Python",
            limit=1,
            offset=1
        )
        
        # Verify the service was called with the correct pagination parameters
        self.book_service.get_all.assert_called_once_with(
            skip=1,
            limit=1,
            search="Python"
        )
        
        # Verify pagination metadata
        assert result["page"] == 2  # page = (offset // limit) + 1
        assert result["per_page"] == 1
        assert result["total_pages"] > 0
    
    @pytest.mark.asyncio
    async def test_search_empty_results(self):
        """Test search with no results."""
        # Setup empty results
        self.book_service.get_all.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "page_size": 10,
            "total_pages": 0
        }
        
        # Search for non-existent book
        result = await self.tool.list_books(query="Nonexistent Book")
        
        # Verify the results
        assert len(result["items"]) == 0
        assert result["total"] == 0
