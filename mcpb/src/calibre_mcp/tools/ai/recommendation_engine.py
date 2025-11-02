"""AI-powered book recommendation engine for CalibreMCP."""

from typing import Dict, List, Optional, Any
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from fastmcp import MCPTool
except ImportError:
    from ..compat import MCPTool
from pydantic import BaseModel, Field


class RecommendationEngine(MCPTool):
    """AI-powered book recommendation system."""

    name = "recommendation_engine"
    description = "AI-powered book recommendation system using content-based filtering"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.book_vectors = None
        self.book_ids = []

    async def train_model(self, books: List[Dict]) -> Dict:
        """Train the recommendation model on the current library."""
        try:
            # Prepare text data for each book
            texts = []
            self.book_ids = []

            for book in books:
                if not isinstance(book, dict):
                    continue

                # Combine relevant text fields
                text_parts = []
                for field in ["title", "authors", "tags", "series", "publisher", "comments"]:
                    if field in book and book[field]:
                        if isinstance(book[field], list):
                            text_parts.append(" ".join(str(x) for x in book[field] if x))
                        else:
                            text_parts.append(str(book[field]))

                text = " ".join(text_parts)
                if text.strip():
                    texts.append(text)
                    self.book_ids.append(book.get("id"))

            # Train TF-IDF vectorizer
            if texts:
                self.book_vectors = self.vectorizer.fit_transform(texts)
                return {"success": True, "books_processed": len(texts)}
            else:
                return {"success": False, "error": "No valid book data provided"}

        except Exception as e:
            self.logger.error(f"Error training recommendation model: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def get_recommendations(
        self, book_id: str, max_results: int = 5, exclude_read: bool = True
    ) -> Dict:
        """Get book recommendations based on a given book ID."""
        try:
            if self.book_vectors is None:
                return {"success": False, "error": "Model not trained. Call train_model first."}

            if book_id not in self.book_ids:
                return {"success": False, "error": f"Book ID {book_id} not found in training data"}

            # Get the index of the target book
            target_idx = self.book_ids.index(book_id)

            # Calculate similarity scores
            similarity_scores = cosine_similarity(
                self.book_vectors[target_idx : target_idx + 1], self.book_vectors
            ).flatten()

            # Get top N similar books (excluding the book itself)
            similar_indices = np.argsort(similarity_scores)[-max_results - 1 : -1][::-1]

            recommendations = []
            for idx in similar_indices:
                if self.book_ids[idx] != book_id:  # Don't recommend the same book
                    recommendations.append(
                        {
                            "book_id": self.book_ids[idx],
                            "similarity_score": float(similarity_scores[idx]),
                        }
                    )

            return {"success": True, "recommendations": recommendations}

        except Exception as e:
            self.logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def get_personalized_recommendations(
        self, user_preferences: Dict[str, Any], max_results: int = 10
    ) -> Dict:
        """Get personalized recommendations based on user preferences."""
        try:
            if self.book_vectors is None:
                return {"success": False, "error": "Model not trained. Call train_model first."}

            # Convert user preferences to a query vector
            query_text = self._preferences_to_text(user_preferences)
            query_vector = self.vectorizer.transform([query_text])

            # Calculate similarity scores
            similarity_scores = cosine_similarity(query_vector, self.book_vectors).flatten()

            # Get top N recommendations
            similar_indices = np.argsort(similarity_scores)[-max_results:][::-1]

            recommendations = []
            for idx in similar_indices:
                recommendations.append(
                    {
                        "book_id": self.book_ids[idx],
                        "relevance_score": float(similarity_scores[idx]),
                    }
                )

            return {"success": True, "recommendations": recommendations}

        except Exception as e:
            self.logger.error(
                f"Error getting personalized recommendations: {str(e)}", exc_info=True
            )
            return {"success": False, "error": str(e)}

    def _preferences_to_text(self, preferences: Dict[str, Any]) -> str:
        """Convert user preferences to a text query."""
        text_parts = []

        # Add favorite authors
        if "favorite_authors" in preferences and preferences["favorite_authors"]:
            text_parts.append(" ".join(str(a) for a in preferences["favorite_authors"]))

        # Add favorite genres/tags
        if "favorite_genres" in preferences and preferences["favorite_genres"]:
            text_parts.append(" ".join(str(g) for g in preferences["favorite_genres"]))

        # Add reading history
        if "recently_read" in preferences and preferences["recently_read"]:
            for book in preferences["recently_read"]:
                if isinstance(book, dict):
                    text_parts.append(book.get("title", ""))
                    if "authors" in book and book["authors"]:
                        text_parts.append(" ".join(book["authors"]))

        # Add preferred publishers
        if "preferred_publishers" in preferences and preferences["preferred_publishers"]:
            text_parts.append(" ".join(str(p) for p in preferences["preferred_publishers"]))

        return " ".join(text_parts)


class RecommendationOptions(BaseModel):
    """Options for generating recommendations."""

    max_results: int = Field(
        5, ge=1, le=50, description="Maximum number of recommendations to return"
    )
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating threshold")
    exclude_read: bool = Field(True, description="Exclude already read books")
    include_tags: Optional[List[str]] = Field(
        None, description="Only include books with these tags"
    )
    exclude_tags: Optional[List[str]] = Field(None, description="Exclude books with these tags")

    class Config:
        schema_extra = {
            "example": {
                "max_results": 5,
                "min_rating": 4.0,
                "exclude_read": True,
                "include_tags": ["science fiction", "fantasy"],
                "exclude_tags": ["horror"],
            }
        }
