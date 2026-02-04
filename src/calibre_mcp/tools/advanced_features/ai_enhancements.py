"""AI-powered enhancements for CalibreMCP."""

import json
import logging
import os
from typing import Any

import httpx
from pydantic import BaseModel, Field, HttpUrl

# Compatibility shim for MCPTool (FastMCP 2.13 migration)
try:
    from fastmcp import MCPTool
except ImportError:
    from ..compat import MCPTool
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure structured logging
logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Base exception for AI service errors."""

    def __init__(self, message: str, status_code: int = None, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class AIServiceConfig(BaseModel):
    """Configuration for AI service."""

    api_key: str
    base_url: HttpUrl = "https://api.openai.com/v1"
    timeout: int = 30
    max_retries: int = 3


class BookRecommendation(BaseModel):
    """Model for book recommendations."""

    book_id: str
    title: str
    author: str
    score: float = Field(..., ge=0, le=1)
    reason: str
    metadata: dict[str, Any] | None = None


class AIEnhancementsTool(MCPTool):
    """AI-powered enhancements for the Calibre library."""

    name = "ai_enhancements"
    description = "AI-powered enhancements for the library"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ai_model = None
        self._embedding_model = None

    async def _run(self, action: str, **kwargs) -> dict:
        """Route to the appropriate AI enhancement handler."""
        handler = getattr(self, f"ai_{action}", None)
        if not handler:
            return {"error": f"Unknown AI action: {action}", "success": False}

        try:
            return await handler(**kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}

    async def ai_generate_metadata(
        self, book_id: int | str, fields: list[str] = None, library_path: str | None = None
    ) -> dict:
        """
        Generate missing metadata for a book using AI.

        Args:
            book_id: ID of the book to enhance
            fields: List of fields to generate (if None, all missing fields)
            library_path: Path to the Calibre library
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage
        from calibre_plugins.calibremcp.tools.metadata.update_metadata import UpdateMetadataTool

        storage = LocalStorage(library_path)
        metadata = await storage.get_metadata(book_id)

        if not metadata:
            return {"error": f"Book {book_id} not found", "success": False}

        # Determine which fields need to be generated
        if fields is None:
            fields = self._get_missing_fields(metadata)

        if not fields:
            return {"message": "No fields to generate", "success": True}

        # Generate metadata using AI
        generated_metadata = await self._generate_metadata(metadata, fields)

        # Update the book metadata
        update_tool = UpdateMetadataTool()
        update_result = await update_tool._run(
            book_ids=[book_id], metadata=generated_metadata, library_path=library_path
        )

        return {
            "success": True,
            "generated_fields": list(generated_metadata.keys()),
            "update_result": update_result,
        }

    async def ai_recommend_books(
        self, book_id: int | str, limit: int = 5, library_path: str | None = None
    ) -> dict:
        """
        Get book recommendations based on a book.

        Args:
            book_id: ID of the book to get recommendations for
            limit: Maximum number of recommendations to return
            library_path: Path to the Calibre library
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)
        metadata = await storage.get_metadata(book_id)

        if not metadata:
            return {"error": f"Book {book_id} not found", "success": False}

        # Get book embeddings
        query_embedding = await self._get_book_embedding(metadata)

        # Find similar books (in a real implementation, this would use a vector database)
        all_books = await storage.get_all_books()
        similarities = []

        for book in all_books:
            if str(book.id) == str(book_id):
                continue

            book_embedding = await self._get_book_embedding(book)
            similarity = self._cosine_similarity(query_embedding, book_embedding)
            similarities.append((book, similarity))

        # Sort by similarity and get top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_matches = similarities[:limit]

        # Format recommendations
        recommendations = []
        for book, score in top_matches:
            recommendations.append(
                BookRecommendation(
                    book_id=str(book.id),
                    title=book.title,
                    author=", ".join(book.authors) if book.authors else "Unknown",
                    score=score,
                    reason=f"Similar to {metadata.title}",
                    metadata=book.dict(),
                )
            )

        return {
            "success": True,
            "query_book": {
                "id": str(book_id),
                "title": metadata.title,
                "author": ", ".join(metadata.authors) if metadata.authors else "Unknown",
            },
            "recommendations": [rec.dict() for rec in recommendations],
        }

    async def ai_summarize_book(self, book_id: int | str, library_path: str | None = None) -> dict:
        """
        Generate a summary of a book's content.

        Args:
            book_id: ID of the book to summarize
            library_path: Path to the Calibre library
        """
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)
        book_path = storage.get_book_path(book_id)

        if not book_path or not book_path.exists():
            return {"error": f"Book file not found for ID {book_id}", "success": False}

        # In a real implementation, this would use an AI model to generate a summary
        # For now, return a mock response
        return {
            "success": True,
            "book_id": str(book_id),
            "summary": "This is a mock summary generated by the AI. In a real implementation, this would be a concise summary of the book's content, themes, and key points.",
            "key_points": [
                "Main theme of the book",
                "Key character or concept 1",
                "Key character or concept 2",
                "Major plot point or argument",
                "Conclusion or resolution",
            ],
            "tags": ["fiction", "adventure", "classic"],  # Example tags
        }

    async def ai_extract_quotes(
        self, book_id: int | str, max_quotes: int = 5, library_path: str | None = None
    ) -> dict:
        """
        Extract notable quotes from a book using AI.

        Args:
            book_id: ID of the book to extract quotes from
            max_quotes: Maximum number of quotes to return
            library_path: Path to the Calibre library
        """
        # This is a placeholder implementation
        # In a real implementation, this would use an AI model to analyze the book text

        return {
            "success": True,
            "book_id": str(book_id),
            "quotes": [
                {
                    "text": "This is an example quote from the book.",
                    "page": 42,
                    "chapter": "Chapter 3",
                    "context": "This quote appears during a key moment in the story.",
                    "tags": ["inspirational", "philosophy"],
                },
                # More quotes would be added here
            ],
        }

    # Helper methods
    def _get_missing_fields(self, metadata) -> list[str]:
        """Determine which metadata fields are missing or empty."""
        required_fields = ["title", "authors", "publisher", "published_date", "description"]
        missing = []

        for field in required_fields:
            value = getattr(metadata, field, None)
            if not value or (isinstance(value, (list, dict)) and not value):
                missing.append(field)

        return missing

    async def _init_ai_client(self) -> None:
        """Initialize the AI client with configuration."""
        if not hasattr(self, "_ai_client"):
            try:
                # Load configuration from environment or config file
                self._ai_config = AIServiceConfig(
                    api_key=os.getenv("OPENAI_API_KEY", ""),
                    base_url=os.getenv("AI_SERVICE_URL", "https://api.openai.com/v1"),
                )

                self._ai_client = httpx.AsyncClient(
                    base_url=str(self._ai_config.base_url),
                    headers={
                        "Authorization": f"Bearer {self._ai_config.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=self._ai_config.timeout,
                )

                logger.info(
                    "AI client initialized",
                    extra={
                        "service": "ai_enhancements",
                        "action": "client_initialized",
                        "base_url": str(self._ai_config.base_url),
                    },
                )

            except Exception as e:
                logger.error(
                    "Failed to initialize AI client",
                    extra={
                        "service": "ai_enhancements",
                        "action": "client_init_failed",
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )
                raise AIServiceError("Failed to initialize AI client") from e

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True
    )
    async def _generate_metadata(self, metadata, fields: list[str]) -> dict:
        """Generate metadata using AI.

        Args:
            metadata: Existing book metadata
            fields: List of fields to generate

        Returns:
            Dict containing generated metadata

        Raises:
            AIServiceError: If metadata generation fails
        """
        await self._init_ai_client()

        try:
            logger.info(
                "Generating metadata with AI",
                extra={
                    "service": "ai_enhancements",
                    "action": "generate_metadata_start",
                    "book_id": getattr(metadata, "id", "unknown"),
                    "fields": fields,
                },
            )

            # Prepare the prompt for the AI
            prompt = self._build_metadata_prompt(metadata, fields)

            # Call the AI service
            response = await self._ai_client.post(
                "/chat/completions",
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
            )

            if response.status_code != 200:
                error_data = response.json()
                logger.error(
                    "AI service returned error",
                    extra={
                        "service": "ai_enhancements",
                        "action": "generate_metadata_error",
                        "status_code": response.status_code,
                        "error": error_data,
                    },
                )
                raise AIServiceError(
                    "AI service error", status_code=response.status_code, details=error_data
                )

            # Parse the AI response
            result = response.json()
            generated_content = result["choices"][0]["message"]["content"]
            generated_metadata = self._parse_ai_response(generated_content, fields)

            logger.info(
                "Successfully generated metadata",
                extra={
                    "service": "ai_enhancements",
                    "action": "generate_metadata_success",
                    "book_id": getattr(metadata, "id", "unknown"),
                    "generated_fields": list(generated_metadata.keys()),
                },
            )

            return generated_metadata

        except httpx.RequestError as e:
            logger.error(
                "Request to AI service failed",
                extra={
                    "service": "ai_enhancements",
                    "action": "generate_metadata_error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise AIServiceError("Failed to connect to AI service") from e

    def _build_metadata_prompt(self, metadata, fields: list[str]) -> str:
        """Build a prompt for the AI to generate metadata."""
        prompt_parts = [
            "You are a helpful assistant that generates book metadata. "
            "Generate the following fields in JSON format:"
        ]

        field_descriptions = {
            "title": "Book title (string)",
            "authors": "List of author names (list of strings)",
            "description": "Detailed book description (string, 1-3 paragraphs)",
            "tags": "List of relevant tags (list of strings, 3-7 items)",
            "publisher": "Publisher name (string)",
            "published_date": "Publication date in YYYY-MM-DD format (string)",
            "identifiers": "Dictionary of identifiers like ISBN (dict)",
            "languages": "List of language codes (list of strings)",
            "series": "Series name (string, optional)",
            "series_index": "Position in series (float, optional)",
            "rating": "Rating from 0 to 5 (float, optional)",
        }

        # Add field descriptions for requested fields
        for field in fields:
            if field in field_descriptions:
                prompt_parts.append(f"- {field}: {field_descriptions[field]}")

        # Add existing metadata for context
        prompt_parts.append("\nUse the following existing metadata as context (do not repeat it):")
        for field, value in metadata.dict().items():
            if value and field in field_descriptions:
                prompt_parts.append(f"- {field}: {value}")

        prompt_parts.append("\nRespond with a JSON object containing only the requested fields.")
        return "\n".join(prompt_parts)

    def _parse_ai_response(self, content: str, fields: list[str]) -> dict:
        """Parse the AI response into a structured dictionary.

        Args:
            content: Raw content from the AI response
            fields: List of expected field names

        Returns:
            Dict containing only the requested fields

        Raises:
            AIServiceError: If parsing fails or response is invalid
        """
        try:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                # Fix: Properly handle markdown code blocks
                code_block = content.split("```")
                if len(code_block) > 1:
                    content = code_block[1].strip()
                    if content.startswith("json"):
                        content = content[4:].strip()

            # Parse the JSON content
            result = json.loads(content)

            # Validate that only requested fields are included
            return {k: v for k, v in result.items() if k in fields}

        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            logger.error(
                "Failed to parse AI response",
                extra={
                    "service": "ai_enhancements",
                    "action": "parse_ai_response_error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "content_sample": str(content)[:200],  # Log first 200 chars for debugging
                },
            )
            raise AIServiceError("Failed to parse AI response") from e

    async def _get_book_embedding(self, metadata) -> list[float]:
        """Get an embedding vector for a book's metadata.

        Args:
            metadata: Book metadata to generate embedding for

        Returns:
            List of floats representing the embedding

        Raises:
            AIServiceError: If embedding generation fails
        """
        await self._init_ai_client()

        try:
            logger.debug(
                "Generating book embedding",
                extra={
                    "service": "ai_enhancements",
                    "action": "generate_embedding_start",
                    "book_id": getattr(metadata, "id", "unknown"),
                },
            )

            # Prepare text for embedding
            text_parts = []
            for field in ["title", "authors", "description", "tags", "series"]:
                if hasattr(metadata, field) and getattr(metadata, field):
                    value = getattr(metadata, field)
                    if isinstance(value, list):
                        text_parts.append(", ".join(str(v) for v in value))
                    else:
                        text_parts.append(str(value))

            text = " ".join(text_parts)

            # Call the embedding API
            response = await self._ai_client.post(
                "/embeddings", json={"model": "text-embedding-3-small", "input": text}
            )

            if response.status_code != 200:
                error_data = response.json()
                logger.error(
                    "Embedding API returned error",
                    extra={
                        "service": "ai_enhancements",
                        "action": "generate_embedding_error",
                        "status_code": response.status_code,
                        "error": error_data,
                    },
                )
                raise AIServiceError(
                    "Embedding API error", status_code=response.status_code, details=error_data
                )

            result = response.json()
            embedding = result["data"][0]["embedding"]

            logger.debug(
                "Successfully generated embedding",
                extra={
                    "service": "ai_enhancements",
                    "action": "generate_embedding_success",
                    "book_id": getattr(metadata, "id", "unknown"),
                    "embedding_length": len(embedding),
                },
            )

            return embedding

        except Exception as e:
            logger.error(
                "Failed to generate embedding",
                extra={
                    "service": "ai_enhancements",
                    "action": "generate_embedding_error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise AIServiceError("Failed to generate embedding") from e

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np

        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
