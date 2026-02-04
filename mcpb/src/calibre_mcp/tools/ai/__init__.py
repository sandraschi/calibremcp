"""
AI-powered tools for Calibre MCP server.

This module provides AI-powered tools for book recommendations,
content analysis, and reading insights.
"""

from .. import tool  # noqa: F401
from .content_analyzer import ContentAnalysisOptions, ContentAnalyzer, ReadingHabitOptions
from .llm_summarizer import (
    LLMConfig,
    check_llm_status,
    get_summarizer,
    summarize_book_content,
)
from .llm_summarizer import (
    query_books as llm_query_books,
)

# Import the AI tools
from .recommendation_engine import RecommendationEngine, RecommendationOptions

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
                "preferred_publishers": {"type": "array", "items": {"type": "string"}},
            },
        },
        "options": {
            "type": "object",
            "description": "Recommendation options",
            "properties": RecommendationOptions.schema()["properties"],
        },
    },
)
async def get_book_recommendations(*args, **kwargs):
    """Get book recommendations based on a book or user preferences."""
    if "book_id" in kwargs and kwargs["book_id"]:
        return await recommendation_engine.get_recommendations(**kwargs)
    elif "user_preferences" in kwargs and kwargs["user_preferences"]:
        return await recommendation_engine.get_personalized_recommendations(**kwargs)
    else:
        return {"success": False, "error": "Either book_id or user_preferences must be provided"}


@tool(
    name="train_recommendation_model",
    description="Train the recommendation model on the current library",
    parameters={
        "books": {
            "type": "array",
            "items": {"type": "object"},
            "description": "List of books to train the model on",
        }
    },
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
            "properties": ContentAnalysisOptions.schema()["properties"],
        },
    },
)
async def analyze_book_content(*args, **kwargs):
    """Analyze the content of a book using NLP."""
    return await content_analyzer.analyze_book_content(*args, **kwargs)


@tool(
    name="analyze_reading_habits",
    description="Analyze reading habits from reading history data",
    parameters={
        "reading_history": {
            "type": "array",
            "items": {"type": "object"},
            "description": "List of reading sessions",
        },
        "options": {
            "type": "object",
            "description": "Analysis options",
            "properties": ReadingHabitOptions.schema()["properties"],
        },
    },
)
async def analyze_reading_habits(*args, **kwargs):
    """Analyze reading habits from reading history data."""
    return await content_analyzer.analyze_reading_habits(*args, **kwargs)


# ============================================================================
# LLM-POWERED TOOLS - NotebookLM Killer!
# Uses local Ollama on 4090 - no cloud sees your Bullshit Library
# ============================================================================


@tool(
    name="llm_check_status",
    description="Check if local LLM (Ollama) is available and which models are loaded",
    parameters={},
)
async def llm_check_status():
    """Check local LLM availability.

    Returns status of Ollama and available models.
    Useful to verify 4090 is ready before heavy operations.
    """
    return await check_llm_status()


@tool(
    name="llm_summarize_book",
    description="Generate an academic summary of a book using local LLM. NotebookLM-killer feature!",
    parameters={
        "text": {
            "type": "string",
            "description": "Full text content of the book",
        },
        "title": {
            "type": "string",
            "description": "Book title",
        },
        "author": {
            "type": "string",
            "description": "Book author",
        },
        "target_pages": {
            "type": "integer",
            "description": "Target summary length in pages (default: 15)",
            "default": 15,
        },
        "citation": {
            "type": "string",
            "description": "Full citation for the book (optional)",
        },
        "model": {
            "type": "string",
            "description": "Override LLM model (default: llama3.1:70b-instruct-q4_K_M)",
        },
    },
)
async def llm_summarize_book(
    text: str,
    title: str,
    author: str,
    target_pages: int = 15,
    citation: str = None,
    model: str = None,
):
    """Generate academic-style book summary using local LLM.

    Uses map-reduce to handle 600+ page books:
    1. Chunks the text intelligently (respects chapters)
    2. Summarizes each chunk
    3. Synthesizes into final document

    Output includes proper citations and academic formatting.
    Perfect for sharing with friends to "rücke gerade" their understanding.

    Runs entirely on local 4090 - your Bullshit Library stays private!
    """
    return await summarize_book_content(
        text=text,
        title=title,
        author=author,
        target_pages=target_pages,
        citation=citation,
        model=model,
    )


@tool(
    name="llm_query_books",
    description="Ask questions across multiple books - RAG across your library!",
    parameters={
        "query": {
            "type": "string",
            "description": "Your question to answer using the books",
        },
        "book_contents": {
            "type": "object",
            "description": "Dict of {book_title: relevant_content} to query",
            "additionalProperties": {"type": "string"},
        },
    },
)
async def llm_cross_book_query(query: str, book_contents: dict):
    """Query across multiple books with citations.

    Example: "Compare German and Soviet tank doctrine in WWII"
    With contents from Guderian, Soviet military texts, academic analyses.

    Returns answer with citations to specific books.
    The 15k book RAG dream realized!
    """
    return await llm_query_books(query, book_contents)
