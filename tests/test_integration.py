"""Integration tests for Calibre MCP server and tools."""
import pytest
from unittest.mock import AsyncMock

from fastmcp import MCPClient

from calibre_mcp.mcp_server import CalibreMCPServer
from calibre_mcp.tools.advanced_features.ai_enhancements import AIEnhancementsTool

# Test configuration
TEST_LIBRARY_PATH = "/tmp/calibre_test_library"
TEST_DB_URL = "sqlite:///:memory:"

# Sample data
SAMPLE_BOOK = {
    "id": "test-book-1",
    "title": "Test Book",
    "authors": ["Test Author"],
    "description": "A test book description.",
    "tags": ["test", "fiction"],
    "series": "Test Series",
    "series_index": 1.0,
    "publisher": "Test Publisher",
    "published_date": "2023-01-01",
    "identifiers": {"isbn": "1234567890"},
    "languages": ["eng"],
    "rating": 4.5
}

class TestIntegration:
    """Integration test suite for Calibre MCP."""
    
    @pytest.fixture(autouse=True)
    async def setup(self, tmp_path):
        """Set up test environment."""
        # Create test library directory
        library_path = tmp_path / "test_library"
        library_path.mkdir()
        
        # Initialize test database
        self.db_url = f"sqlite:///{tmp_path}/test.db"
        
        # Create test server
        self.server = CalibreMCPServer(
            library_path=str(library_path),
            db_url=self.db_url
        )
        
        # Initialize server
        await self.server.initialize()
        
        # Create test client
        self.client = MCPClient("http://testserver")
        
        # Mock the AI service
        self.server.ai_enhancements = AsyncMock(spec=AIEnhancementsTool)
        
        yield
        
        # Cleanup
        await self.server.shutdown()
    
    @pytest.mark.asyncio
    async def test_book_lifecycle(self):
        """Test the complete book lifecycle (create, read, update, delete)."""
        # Create a book
        create_response = await self.client.call_tool(
            "book_tools.create_book",
            book_data={
                "title": "New Book",
                "authors": ["New Author"],
                "description": "New description",
                "tags": ["test"]
            }
        )
        
        assert "id" in create_response
        book_id = create_response["id"]
        
        # Get the book
        get_response = await self.client.call_tool(
            "book_tools.get_book",
            book_id=book_id
        )
        
        assert get_response["id"] == book_id
        assert get_response["title"] == "New Book"
        
        # Update the book
        update_response = await self.client.call_tool(
            "book_tools.update_book",
            book_id=book_id,
            book_data={"title": "Updated Title"}
        )
        
        assert update_response["title"] == "Updated Title"
        
        # Delete the book
        delete_response = await self.client.call_tool(
            "book_tools.delete_book",
            book_id=book_id
        )
        
        assert delete_response is True
        
        # Verify the book is deleted
        with pytest.raises(Exception):
            await self.client.call_tool(
                "book_tools.get_book",
                book_id=book_id
            )
    
    @pytest.mark.asyncio
    async def test_ai_enhancements(self):
        """Test AI enhancement features."""
        # Mock the AI service responses
        self.server.ai_enhancements.generate_metadata.return_value = {
            "title": "Enhanced Title",
            "description": "Enhanced description"
        }
        
        # Test metadata generation
        response = await self.client.call_tool(
            "ai_enhancements.generate_metadata",
            book_id="test-book-1",
            fields=["title", "description"]
        )
        
        assert "title" in response
        assert "description" in response
        assert response["title"] == "Enhanced Title"
        
        # Verify the AI service was called correctly
        self.server.ai_enhancements.generate_metadata.assert_called_once_with(
            book_id="test-book-1",
            fields=["title", "description"]
        )
    
    @pytest.mark.asyncio
    async def test_search_books(self):
        """Test searching for books."""
        # Add test data
        for i in range(10):
            await self.server.book_service.create(
                BookCreate(
                    title=f"Test Book {i}",
                    authors=[f"Author {i}"],
                    tags=["test"],
                    description=f"Description {i}"
                )
            )
        
        # Test search by title
        response = await self.client.call_tool(
            "book_tools.list_books",
            query="Test Book 1"
        )
        
        assert "items" in response
        assert len(response["items"]) > 0
        assert "Test Book 1" in [book["title"] for book in response["items"]]
        
        # Test pagination
        response = await self.client.call_tool(
            "book_tools.list_books",
            limit=5,
            offset=5
        )
        
        assert len(response["items"]) == 5
        assert response["page"] == 2
        assert response["total"] == 10
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling and validation."""
        # Test invalid book ID
        with pytest.raises(Exception) as exc_info:
            await self.client.call_tool(
                "book_tools.get_book",
                book_id="nonexistent"
            )
        
        assert "not found" in str(exc_info.value).lower()
        
        # Test invalid input
        with pytest.raises(Exception):
            await self.client.call_tool(
                "book_tools.create_book",
                book_data={"invalid": "data"}
            )
        
        # Test rate limiting (if implemented)
        # This is a placeholder for actual rate limiting tests
        pass
