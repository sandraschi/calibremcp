"""Tests for book-related tools in Calibre MCP."""
import pytest
from unittest.mock import MagicMock


from calibre_mcp.tools.book_tools import BookTools
from calibre_mcp.services.book_service import BookService
from calibre_mcp.models.book import Book

# Test data
SAMPLE_BOOKS = [
    {
        "id": "book1",
        "title": "Test Book 1",
        "authors": ["Author 1"],
        "description": "Test description 1",
        "tags": ["test", "fiction"],
        "series": "Test Series 1",
        "series_index": 1.0,
        "publisher": "Test Publisher 1",
        "published_date": "2023-01-01",
        "identifiers": {"isbn": "1234567890"},
        "languages": ["eng"],
        "rating": 4.5
    },
    {
        "id": "book2",
        "title": "Test Book 2",
        "authors": ["Author 2"],
        "description": "Test description 2",
        "tags": ["test", "non-fiction"],
        "series": "Test Series 1",
        "series_index": 2.0,
        "publisher": "Test Publisher 2",
        "published_date": "2023-02-01",
        "identifiers": {"isbn": "0987654321"},
        "languages": ["eng"],
        "rating": 4.0
    }
]

class TestBookTools:
    """Test suite for BookTools."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # Create a test instance with mocked dependencies
        self.book_service = MagicMock(spec=BookService)
        self.tool = BookTools(book_service=self.book_service)
        
        # Setup mock return values
        self.book_service.get_all.return_value = {
            "items": [Book(**book) for book in SAMPLE_BOOKS],
            "total": len(SAMPLE_BOOKS),
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
        
        self.book_service.get.return_value = Book(**SAMPLE_BOOKS[0])
        self.book_service.create.return_value = Book(**SAMPLE_BOOKS[0])
        self.book_service.update.return_value = Book(**SAMPLE_BOOKS[0])
        self.book_service.delete.return_value = True
        
        yield
    
    # Test list_books
    @pytest.mark.asyncio
    async def test_list_books(self):
        """Test listing books with various filters."""
        # Test with no filters
        result = await self.tool.list_books()
        assert "items" in result
        assert len(result["items"]) == 2
        assert result["total"] == 2
        
        # Test with query filter
        result = await self.tool.list_books(query="Test Book 1")
        self.book_service.get_all.assert_called_with(
            skip=0, 
            limit=50,
            search="Test Book 1"
        )
        
        # Test with author filter
        result = await self.tool.list_books(author="Author 1")
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            author_name="Author 1"
        )
        
        # Test with tag filter
        result = await self.tool.list_books(tag="fiction")
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            tag_name="fiction"
        )
        
        # Test with series filter
        result = await self.tool.list_books(series="Test Series 1")
        self.book_service.get_all.assert_called_with(
            skip=0,
            limit=50,
            series_name="Test Series 1"
        )
        
        # Test pagination
        result = await self.tool.list_books(limit=10, offset=10)
        self.book_service.get_all.assert_called_with(
            skip=10,
            limit=10
        )
    
    # Test get_book
    @pytest.mark.asyncio
    async def test_get_book(self):
        """Test getting a single book by ID."""
        result = await self.tool.get_book(book_id="book1")
        assert result is not None
        assert result["id"] == "book1"
        self.book_service.get.assert_called_once_with("book1")
    
    # Test create_book
    @pytest.mark.asyncio
    async def test_create_book(self):
        """Test creating a new book."""
        book_data = {
            "title": "New Book",
            "authors": ["New Author"],
            "description": "New description",
            "tags": ["new", "test"]
        }
        
        result = await self.tool.create_book(book_data)
        assert result is not None
        self.book_service.create.assert_called_once()
        
        # Verify the book data was passed correctly
        call_args = self.book_service.create.call_args[0][0]
        assert call_args.title == "New Book"
        assert "New Author" in call_args.authors
    
    # Test update_book
    @pytest.mark.asyncio
    async def test_update_book(self):
        """Test updating an existing book."""
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        
        result = await self.tool.update_book(book_id="book1", book_data=update_data)
        assert result is not None
        self.book_service.update.assert_called_once()
        
        # Verify the update data was passed correctly
        call_args = self.book_service.update.call_args[0]
        assert call_args[0] == "book1"
        assert call_args[1].title == "Updated Title"
    
    # Test delete_book
    @pytest.mark.asyncio
    async def test_delete_book(self):
        """Test deleting a book."""
        result = await self.tool.delete_book(book_id="book1")
        assert result is True
        self.book_service.delete.assert_called_once_with("book1")
