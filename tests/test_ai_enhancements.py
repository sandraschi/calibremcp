"""Tests for AI enhancement tools in Calibre MCP."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


from calibre_mcp.tools.advanced_features.ai_enhancements import (
    AIEnhancementsTool,
    AIServiceError,
    BookRecommendation
)

# Test data
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

# Fixtures
@pytest.fixture
def mock_ai_response():
    """Mock AI response for metadata generation."""
    return {
        "title": "Generated Title",
        "authors": ["Generated Author"],
        "description": "This is a generated description.",
        "tags": ["ai-generated", "test"],
        "publisher": "Generated Publisher",
        "published_date": "2023-01-01"
    }

@pytest.fixture
def mock_embedding():
    """Mock embedding vector."""
    return [0.1 * i for i in range(1536)]  # 1536 dimensions for text-embedding-3-small

# Test classes
class TestAIEnhancementsTool:
    """Test suite for AIEnhancementsTool."""
    
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """Setup test environment."""
        # Mock environment variables
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        
        # Create a test instance
        self.tool = AIEnhancementsTool()
        
        # Mock the AI client
        self.mock_client = AsyncMock()
        self.tool._ai_client = self.mock_client
        
        # Mock the book service
        self.tool.book_service = MagicMock()
        
        # Mock the storage service
        self.tool.storage_service = MagicMock()
        
        # Mock the metadata service
        self.tool.metadata_service = MagicMock()
        
        yield
        
        # Cleanup
        if hasattr(self.tool, '_ai_client') and hasattr(self.tool._ai_client, 'aclose'):
            self.tool._ai_client.aclose = AsyncMock()
            self.tool._ai_client.aclose.return_value = None
    
    # Test initialization
    def test_init(self):
        """Test tool initialization."""
        assert hasattr(self.tool, 'book_service')
        assert hasattr(self.tool, 'storage_service')
        assert hasattr(self.tool, 'metadata_service')
    
    # Test metadata generation
    @pytest.mark.asyncio
    async def test_generate_metadata_success(self, mock_ai_response):
        """Test successful metadata generation."""
        # Mock the AI response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(mock_ai_response)}}]
        }
        self.mock_client.post.return_value = mock_response
        
        # Call the method
        fields = ["title", "authors", "description", "tags"]
        result = await self.tool._generate_metadata(SAMPLE_BOOK, fields)
        
        # Verify the result
        assert all(field in result for field in fields)
        assert result["title"] == "Generated Title"
        assert "Generated Author" in result["authors"]
        
        # Verify the API call
        self.mock_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_metadata_api_error(self):
        """Test metadata generation with API error."""
        # Mock an error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        self.mock_client.post.return_value = mock_response
        
        # Call the method and expect an exception
        with pytest.raises(AIServiceError):
            await self.tool._generate_metadata(SAMPLE_BOOK, ["title"])
    
    # Test book embedding
    @pytest.mark.asyncio
    async def test_get_book_embedding_success(self, mock_embedding):
        """Test successful book embedding generation."""
        # Mock the embedding response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"embedding": mock_embedding}]
        }
        self.mock_client.post.return_value = mock_response
        
        # Call the method
        result = await self.tool._get_book_embedding(SAMPLE_BOOK)
        
        # Verify the result
        assert len(result) == len(mock_embedding)
        assert all(isinstance(x, float) for x in result)
        
        # Verify the API call
        self.mock_client.post.assert_called_once()
    
    # Test cosine similarity
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 1.0, 0.0]
        
        # Calculate expected result manually
        expected = 1.0 / (2 ** 0.5)  # cos(45 degrees)
        result = self.tool._cosine_similarity(vec1, vec2)
        
        assert abs(result - expected) < 1e-9
    
    # Test book recommendations
    @pytest.mark.asyncio
    async def test_get_book_recommendations(self, mock_embedding):
        """Test getting book recommendations."""
        # Mock the embedding response
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = {
            "data": [{"embedding": mock_embedding}]
        }
        
        # Mock the search results
        similar_books = [
            {"id": f"book-{i}", "title": f"Similar Book {i}", "embedding": mock_embedding}
            for i in range(3)
        ]
        self.tool.book_service.search_similar_books.return_value = similar_books
        
        # Set up the mock to return the embedding response
        self.mock_client.post.return_value = mock_embed_response
        
        # Call the method
        result = await self.tool.get_book_recommendations(
            book_id="test-book-1",
            limit=3
        )
        
        # Verify the result
        assert len(result) == 3
        assert all(isinstance(book, BookRecommendation) for book in result)
        assert all(book.score > 0 for book in result)
        
        # Verify the API call
        self.mock_client.post.assert_called_once()
    
    # Test error handling for missing API key
    @pytest.mark.asyncio
    async def test_missing_api_key(self, monkeypatch):
        """Test behavior when API key is missing."""
        # Remove the API key
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        # Create a new instance to trigger client initialization
        tool = AIEnhancementsTool()
        
        # The client should be None due to missing API key
        assert not hasattr(tool, '_ai_client')
        
        # Calling a method should raise an error
        with pytest.raises(AIServiceError):
            await tool._generate_metadata(SAMPLE_BOOK, ["title"])

# Test command-line interface
class TestCLI:
    """Test command-line interface for AI enhancements."""
    
    @pytest.fixture
    def mock_tool(self, monkeypatch):
        """Mock the AIEnhancementsTool for CLI tests."""
        mock = AsyncMock(spec=AIEnhancementsTool)
        mock._generate_metadata.return_value = {"title": "Generated Title"}
        
        # Patch the tool class to return our mock
        monkeypatch.setattr(
            "calibre_mcp.tools.advanced_features.ai_enhancements.AIEnhancementsTool",
            lambda *args, **kwargs: mock
        )
        
        return mock
    
    @pytest.mark.asyncio
    async def test_cli_generate_metadata(self, mock_tool, capsys):
        """Test the generate_metadata CLI command."""
        from calibre_mcp.tools.advanced_features.ai_enhancements import main
        
        # Mock command-line arguments
        test_args = [
            "generate-metadata",
            "--book-id", "test-book-1",
            "--fields", "title", "description"
        ]
        
        # Patch sys.argv
        with patch("sys.argv", ["test_script.py"] + test_args):
            await main()
        
        # Verify the tool was called correctly
        mock_tool._generate_metadata.assert_awaited_once()
        
        # Verify the output
        captured = capsys.readouterr()
        assert "Generated Title" in captured.out
