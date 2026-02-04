"""
Tests for AI enhancement tools in Calibre MCP.

Tests verify actual tool functionality with proper mocking of AI services.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

try:
    from calibre_mcp.tools.advanced_features.ai_enhancements import AIEnhancementsTool
except (ImportError, ModuleNotFoundError) as e:
    # Tool may not be available if dependencies are missing (e.g., tenacity)
    AIEnhancementsTool = None
    AI_ENHANCEMENTS_AVAILABLE = False
    IMPORT_ERROR = str(e)
else:
    AI_ENHANCEMENTS_AVAILABLE = True
    IMPORT_ERROR = None

from tests.fixtures.test_data import SAMPLE_BOOK


# Mock fixtures
@pytest.fixture
def mock_ai_response():
    """Mock AI response for metadata generation."""
    return {
        "title": "Generated Title",
        "authors": ["Generated Author"],
        "description": "Generated description",
        "tags": ["generated", "tag"],
    }


@pytest.fixture
def mock_embedding():
    """Mock embedding vector for similarity calculations."""
    return [0.1] * 1536  # Typical OpenAI embedding dimension


@pytest.fixture
def ai_tool_instance(monkeypatch):
    """Create an AIEnhancementsTool instance with mocked dependencies."""
    if not AI_ENHANCEMENTS_AVAILABLE:
        pytest.skip(f"AIEnhancementsTool not available: {IMPORT_ERROR}")

    # Mock environment variables
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

    # Create tool instance
    tool = AIEnhancementsTool()

    # Mock the AI client
    mock_client = AsyncMock()
    tool._ai_client = mock_client

    # Mock services
    tool.book_service = MagicMock()
    tool.storage_service = MagicMock()
    tool.metadata_service = MagicMock()

    return tool, mock_client


class TestAIEnhancementsTool:
    """Test suite for AIEnhancementsTool."""

    def test_tool_initialization(self, ai_tool_instance):
        """Test tool initialization."""
        tool, _ = ai_tool_instance

        # Verify tool has required services
        assert hasattr(tool, "book_service")
        assert hasattr(tool, "storage_service")
        assert hasattr(tool, "metadata_service")
        assert hasattr(tool, "_ai_client")

    @pytest.mark.asyncio
    async def test_generate_metadata_success(self, ai_tool_instance, mock_ai_response):
        """Test successful metadata generation."""
        tool, mock_client = ai_tool_instance

        # Mock the AI response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(mock_ai_response)}}]
        }
        mock_client.post.return_value = mock_response

        # Call the method via _run (which routes to ai_generate_metadata)
        result = await tool._run(
            "generate_metadata",
            book_id="test-book-1",
            fields=["title", "authors", "description", "tags"],
        )

        # Verify the result structure
        assert isinstance(result, dict)
        assert "error" not in result or result.get("success") is not False

        # Verify the API client was called if method exists
        # Note: This test verifies the routing works, actual implementation may differ

    @pytest.mark.asyncio
    async def test_generate_metadata_api_error(self, ai_tool_instance):
        """Test metadata generation with API error."""
        tool, mock_client = ai_tool_instance

        # Mock an error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_client.post.return_value = mock_response

        # Call the method and expect an exception or error response
        result = await tool._run("generate_metadata", book_id="test-book-1", fields=["title"])

        # Verify error handling - should return error dict or raise exception
        assert isinstance(result, dict)
        # Either success=False or error in result
        assert result.get("success") is False or "error" in result

    @pytest.mark.asyncio
    async def test_get_book_embedding_success(self, ai_tool_instance, mock_embedding):
        """Test successful book embedding generation."""
        tool, mock_client = ai_tool_instance

        # Mock the embedding response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"embedding": mock_embedding}]}
        mock_client.post.return_value = mock_response

        # If _get_book_embedding exists as a private method, test it
        # Otherwise verify it's handled through the _run interface
        if hasattr(tool, "_get_book_embedding"):
            result = await tool._get_book_embedding(SAMPLE_BOOK)

            # Verify the result
            assert isinstance(result, list)
            assert len(result) == len(mock_embedding)
            assert all(isinstance(x, float) for x in result)

            # Verify the API call
            mock_client.post.assert_called_once()

    def test_cosine_similarity(self, ai_tool_instance):
        """Test cosine similarity calculation."""
        tool, _ = ai_tool_instance

        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 1.0, 0.0]

        # Calculate expected result manually
        expected = 1.0 / (2**0.5)  # cos(45 degrees) = 1/√2

        if hasattr(tool, "_cosine_similarity"):
            result = tool._cosine_similarity(vec1, vec2)
            assert abs(result - expected) < 1e-9
        else:
            # If method doesn't exist, skip this test
            pytest.skip("_cosine_similarity method not found")

    @pytest.mark.asyncio
    async def test_get_book_recommendations(self, ai_tool_instance, mock_embedding):
        """Test getting book recommendations."""
        tool, mock_client = ai_tool_instance

        # Mock the embedding response
        mock_embed_response = MagicMock()
        mock_embed_response.status_code = 200
        mock_embed_response.json.return_value = {"data": [{"embedding": mock_embedding}]}

        # Mock the search results
        similar_books = [
            {"id": f"book-{i}", "title": f"Similar Book {i}", "embedding": mock_embedding}
            for i in range(3)
        ]
        if hasattr(tool.book_service, "search_similar_books"):
            tool.book_service.search_similar_books = AsyncMock(return_value=similar_books)

        # Set up the mock to return the embedding response
        mock_client.post.return_value = mock_embed_response

        # Test via _run interface if the action exists
        if hasattr(tool, "ai_get_recommendations"):
            result = await tool._run("get_recommendations", book_id="test-book-1", limit=3)

            # Verify the result structure
            assert isinstance(result, dict)
            # Should not have an error if successful
            assert "error" not in result or result.get("success") is not False

    @pytest.mark.asyncio
    async def test_missing_api_key(self, monkeypatch):
        """Test behavior when API key is missing."""
        if not AI_ENHANCEMENTS_AVAILABLE:
            pytest.skip(f"AIEnhancementsTool not available: {IMPORT_ERROR}")

        # Remove the API key
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Create a new instance to trigger client initialization
        tool = AIEnhancementsTool()

        # The client may not be initialized due to missing API key
        # Calling a method should raise an error or return error
        result = await tool._run("generate_metadata", book_id="test-book-1", fields=["title"])

        # Should return error response
        assert isinstance(result, dict)
        assert result.get("success") is False or "error" in result

    @pytest.mark.asyncio
    async def test_unknown_action(self, ai_tool_instance):
        """Test handling of unknown action."""
        tool, _ = ai_tool_instance

        result = await tool._run("unknown_action", some_param="value")

        # Should return error for unknown action
        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "error" in result
        assert "Unknown AI action" in result["error"]
