"""
AI-powered portmanteau tool for Calibre MCP server.

Consolidates all AI operations into a single unified interface:
- Book recommendations and personalized suggestions
- Content analysis and NLP processing
- Reading habit analysis
- LLM-powered summarization and cross-book querying
"""

from typing import Any, Dict, List, Optional

from ...logging_config import get_logger
from ...server import mcp
from .content_analyzer import ContentAnalyzer
from .llm_summarizer import (
    check_llm_status,
    summarize_book_content,
)
from .llm_summarizer import (
    query_books as llm_query_books,
)

# Import AI tool implementations
from .recommendation_engine import RecommendationEngine

logger = get_logger("calibremcp.tools.ai")


@mcp.tool()
async def manage_ai_operations(
    operation: str,
    # Recommendation parameters
    book_id: str | None = None,
    user_preferences: dict[str, Any] | None = None,
    recommendation_options: dict[str, Any] | None = None,
    # Training parameters
    training_books: list[dict[str, Any]] | None = None,
    # Content analysis parameters
    book_content: str | None = None,
    content_analysis_options: dict[str, Any] | None = None,
    # Reading habit parameters
    reading_history: list[dict[str, Any]] | None = None,
    habit_analysis_options: dict[str, Any] | None = None,
    # LLM summarization parameters
    text: str | None = None,
    title: str | None = None,
    author: str | None = None,
    target_pages: int = 15,
    citation: str | None = None,
    model: str | None = None,
    # Cross-book query parameters
    query: str | None = None,
    book_contents: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Comprehensive AI operations portmanteau tool for Calibre MCP server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 7 related AI operations into single interface. Prevents tool explosion while maintaining
    full functionality. Enables unified AI workflow management across recommendations, analysis, and LLM operations.

    SUPPORTED OPERATIONS:
    - get_recommendations: Get book recommendations based on existing book or preferences
    - train_model: Train recommendation model on library data
    - analyze_content: Analyze book content using NLP techniques
    - analyze_habits: Analyze reading patterns and habits
    - check_llm_status: Verify local LLM availability and models
    - summarize_book: Generate academic book summaries using local LLM
    - query_books: Cross-book question answering with citations

    OPERATIONS DETAIL:

    get_recommendations:
    - Generate personalized book recommendations
    - Based on existing book similarity or user preferences
    - Supports collaborative filtering and content-based approaches
    - Parameters: book_id OR user_preferences (required), recommendation_options (optional)

    train_model:
    - Train recommendation algorithms on current library
    - Improves recommendation quality over time
    - Parameters: training_books (required)

    analyze_content:
    - Extract insights from book text using NLP
    - Sentiment analysis, topic modeling, readability metrics
    - Parameters: book_content (required), content_analysis_options (optional)

    analyze_habits:
    - Analyze reading patterns from history data
    - Identify preferences, reading speed, genre trends
    - Parameters: reading_history (required), habit_analysis_options (optional)

    check_llm_status:
    - Verify local LLM service availability
    - List loaded models and capabilities
    - No parameters required

    summarize_book:
    - Generate academic-style book summaries using local LLM
    - Map-reduce processing for long texts
    - Includes proper citations and formatting
    - Parameters: text, title, author (required), target_pages, citation, model (optional)

    query_books:
    - Answer questions across multiple books simultaneously
    - RAG implementation with source citations
    - Parameters: query, book_contents (required)

    Prerequisites:
        - For LLM operations: Local Ollama service running
        - For training: Sufficient library data available
        - For content analysis: Book text content accessible

    Returns:
        Dict with operation results, success status, and conversational messaging

    Examples:
        # Get recommendations for a specific book
        {"operation": "get_recommendations", "book_id": "123"}

        # Train recommendation model
        {"operation": "train_model", "training_books": [...]}

        # Summarize a book
        {"operation": "summarize_book", "text": "...", "title": "Book Title", "author": "Author Name"}
    """

    try:
        # Initialize AI components
        recommendation_engine = RecommendationEngine()
        content_analyzer = ContentAnalyzer()

        if operation == "get_recommendations":
            if book_id:
                return await recommendation_engine.get_recommendations(
                    book_id=book_id, options=recommendation_options
                )
            elif user_preferences:
                return await recommendation_engine.get_personalized_recommendations(
                    user_preferences=user_preferences, options=recommendation_options
                )
            else:
                return {
                    "success": False,
                    "error": "Either book_id or user_preferences must be provided for recommendations",
                    "message": "Please specify a book to base recommendations on, or provide user preferences.",
                }

        elif operation == "train_model":
            if not training_books:
                return {
                    "success": False,
                    "error": "training_books parameter required for model training",
                    "message": "Please provide a list of books to train the recommendation model on.",
                }
            return await recommendation_engine.train_model(books=training_books)

        elif operation == "analyze_content":
            if not book_content:
                return {
                    "success": False,
                    "error": "book_content parameter required for content analysis",
                    "message": "Please provide the text content of the book to analyze.",
                }
            return await content_analyzer.analyze_book_content(
                book_content=book_content, options=content_analysis_options
            )

        elif operation == "analyze_habits":
            if not reading_history:
                return {
                    "success": False,
                    "error": "reading_history parameter required for habit analysis",
                    "message": "Please provide reading history data to analyze patterns.",
                }
            return await content_analyzer.analyze_reading_habits(
                reading_history=reading_history, options=habit_analysis_options
            )

        elif operation == "check_llm_status":
            return await check_llm_status()

        elif operation == "summarize_book":
            if not all([text, title, author]):
                return {
                    "success": False,
                    "error": "text, title, and author parameters required for summarization",
                    "message": "Please provide the book text, title, and author for summarization.",
                }
            return await summarize_book_content(
                text=text,
                title=title,
                author=author,
                target_pages=target_pages,
                citation=citation,
                model=model,
            )

        elif operation == "query_books":
            if not query or not book_contents:
                return {
                    "success": False,
                    "error": "query and book_contents parameters required for cross-book querying",
                    "message": "Please provide a question and book contents to query across.",
                }
            return await llm_query_books(query=query, book_contents=book_contents)

        else:
            available_ops = [
                "get_recommendations",
                "train_model",
                "analyze_content",
                "analyze_habits",
                "check_llm_status",
                "summarize_book",
                "query_books",
            ]
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "message": f"Available operations: {', '.join(available_ops)}",
                "available_operations": available_ops,
            }

    except Exception as e:
        logger.error(f"AI operation '{operation}' failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"AI operation failed: {str(e)}",
            "operation": operation,
            "message": f"Sorry, the {operation.replace('_', ' ')} operation encountered an error. Please check the logs for details.",
        }
