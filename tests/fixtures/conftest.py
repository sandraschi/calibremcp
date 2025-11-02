"""Shared pytest fixtures for Calibre MCP tests."""

import pytest


@pytest.fixture
def mock_ai_response():
    """Mock AI response for metadata generation."""
    return {
        "title": "Generated Title",
        "authors": ["Generated Author"],
        "description": "This is a generated description.",
        "tags": ["ai-generated", "test"],
        "publisher": "Generated Publisher",
        "published_date": "2023-01-01",
    }


@pytest.fixture
def mock_embedding():
    """Mock embedding vector."""
    return [0.1 * i for i in range(1536)]  # 1536 dimensions for text-embedding-3-small
