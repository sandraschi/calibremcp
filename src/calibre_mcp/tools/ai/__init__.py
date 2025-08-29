"""
AI-powered tools for Calibre MCP server.

This module provides AI-powered tools for book recommendations,
content analysis, and reading insights.
"""
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from ...models import Book, BookMetadata
from .. import tool

# Import the AI tools
from .recommendation_engine import RecommendationEngine, RecommendationOptions
from .content_analyzer import ContentAnalyzer, ContentAnalysisOptions, ReadingHabitOptions

# Initialize the tools
recommendation_engine = RecommendationEngine()
content_analyzer = ContentAnalyzer()

# Register the tools
@tool(
    name="get_book_recommendations",
    description="Get book recommendations based on a book or user preferences",
    parameters={
        "book_id": {"type": "string", "description": "ID of the book to get recommendations for"},
        "user_preferences": {
            "type": "object",
            "description": "User preferences for personalized recommendations",
            "properties": {
                "favorite_authors": {"type": "array", "items": {"type": "string"}},
                "favorite_genres": {"type": "array", "items": {"type": "string"}},
                "recently_read": {"type": "array", "items": {"type": "object"}},
                "preferred_publishers": {"type": "array", "items": {"type": "string"}}
            }
        },
        "options": {
            "type": "object",
            "description": "Recommendation options",
            "properties": RecommendationOptions.schema()["properties"]
        }
    }
)
async def get_book_recommendations(*args, **kwargs):
    """Get book recommendations based on a book or user preferences."""
    if 'book_id' in kwargs and kwargs['book_id']:
        return await recommendation_engine.get_recommendations(**kwargs)
    elif 'user_preferences' in kwargs and kwargs['user_preferences']:
        return await recommendation_engine.get_personalized_recommendations(**kwargs)
    else:
        return {"success": False, "error": "Either book_id or user_preferences must be provided"}

@tool(
    name="train_recommendation_model",
    description="Train the recommendation model on the current library",
    parameters={
        "books": {"type": "array", "items": {"type": "object"}, "description": "List of books to train the model on"}
    }
)
async def train_recommendation_model(*args, **kwargs):
    """Train the recommendation model on the current library."""
    return await recommendation_engine.train_model(*args, **kwargs)

@tool(
    name="analyze_book_content",
    description="Analyze the content of a book using NLP",
    parameters={
        "book_content": {"type": "string", "description": "The text content of the book"},
        "options": {
            "type": "object",
            "description": "Analysis options",
            "properties": ContentAnalysisOptions.schema()["properties"]
        }
    }
)
async def analyze_book_content(*args, **kwargs):
    """Analyze the content of a book using NLP."""
    return await content_analyzer.analyze_book_content(*args, **kwargs)

@tool(
    name="analyze_reading_habits",
    description="Analyze reading habits from reading history data",
    parameters={
        "reading_history": {"type": "array", "items": {"type": "object"}, "description": "List of reading sessions"},
        "options": {
            "type": "object",
            "description": "Analysis options",
            "properties": ReadingHabitOptions.schema()["properties"]
        }
    }
)
async def analyze_reading_habits(*args, **kwargs):
    """Analyze reading habits from reading history data."""
    return await content_analyzer.analyze_reading_habits(*args, **kwargs)
