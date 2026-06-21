"""Shared pytest fixtures for Calibre MCP tests."""

from pathlib import Path

import pytest


def get_test_db_path() -> Path:
    """Return the path to the shared test library metadata.db."""
    return Path(__file__).parent / "test_library" / "metadata.db"


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
