"""AI-powered content analysis for CalibreMCP."""

from typing import Dict, List
import logging
import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import spacy

try:
    from fastmcp import MCPTool
except ImportError:
    from ..compat import MCPTool
from pydantic import BaseModel, Field

# Load the English language model for NLP
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If the model is not found, download it
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


class ContentAnalyzer(MCPTool):
    """AI-powered content analysis for books and reading habits."""

    name = "content_analyzer"
    description = "AI-powered content analysis for books and reading habits"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.nlp = nlp
        self.cached_analyses = {}

    async def analyze_book_content(
        self,
        book_content: str,
        analyze_entities: bool = True,
        analyze_sentiment: bool = True,
        analyze_themes: bool = True,
    ) -> Dict:
        """
        Analyze the content of a book using NLP.

        Args:
            book_content: The text content of the book
            analyze_entities: Whether to identify named entities
            analyze_sentiment: Whether to perform sentiment analysis
            analyze_themes: Whether to identify key themes and topics

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Create a hash of the content for caching
            content_hash = hashlib.md5(book_content.encode("utf-8")).hexdigest()

            # Check if we have a cached analysis
            if content_hash in self.cached_analyses:
                return self.cached_analyses[content_hash]

            # Process the text with spaCy
            doc = self.nlp(book_content)

            result = {
                "success": True,
                "content_hash": content_hash,
                "statistics": self._get_text_statistics(doc),
                "entities": {},
                "sentiment": {},
                "themes": {},
            }

            # Analyze named entities
            if analyze_entities:
                result["entities"] = self._extract_entities(doc)

            # Perform sentiment analysis
            if analyze_sentiment:
                result["sentiment"] = self._analyze_sentiment(doc)

            # Extract key themes and topics
            if analyze_themes:
                result["themes"] = self._extract_themes(doc)

            # Cache the results
            self.cached_analyses[content_hash] = result

            return result

        except Exception as e:
            self.logger.error(f"Error analyzing book content: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def analyze_reading_habits(
        self, reading_history: List[Dict], time_period: str = "all"
    ) -> Dict:
        """
        Analyze reading habits from reading history data.

        Args:
            reading_history: List of reading sessions
            time_period: Time period to analyze ('day', 'week', 'month', 'year', 'all')

        Returns:
            Dictionary containing reading habit analysis
        """
        try:
            if not reading_history:
                return {"success": False, "error": "No reading history provided"}

            # Filter by time period if needed
            if time_period != "all":
                now = datetime.now()
                if time_period == "day":
                    cutoff = now - timedelta(days=1)
                elif time_period == "week":
                    cutoff = now - timedelta(weeks=1)
                elif time_period == "month":
                    cutoff = now - timedelta(days=30)
                elif time_period == "year":
                    cutoff = now - timedelta(days=365)
                else:
                    return {"success": False, "error": f"Invalid time period: {time_period}"}

                reading_history = [
                    session
                    for session in reading_history
                    if datetime.fromisoformat(session.get("start_time", "")) >= cutoff
                ]

            # Calculate basic statistics
            total_reading_time = sum(
                session.get("duration_minutes", 0) for session in reading_history
            )

            # Analyze reading patterns
            reading_times = self._analyze_reading_times(reading_history)

            # Get most read genres/authors
            genre_counter = Counter()
            author_counter = Counter()

            for session in reading_history:
                if "book" in session and session["book"]:
                    book = session["book"]
                    if "tags" in book and book["tags"]:
                        genre_counter.update(book["tags"])
                    if "authors" in book and book["authors"]:
                        author_counter.update(book["authors"])

            return {
                "success": True,
                "time_period": time_period,
                "total_sessions": len(reading_history),
                "total_reading_time_minutes": total_reading_time,
                "average_session_length": total_reading_time / len(reading_history)
                if reading_history
                else 0,
                "reading_times": reading_times,
                "top_genres": genre_counter.most_common(10),
                "top_authors": author_counter.most_common(10),
                "reading_consistency": self._calculate_consistency(reading_history),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing reading habits: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _get_text_statistics(self, doc) -> Dict:
        """Calculate basic text statistics."""
        sentences = list(doc.sents)
        words = [token.text for token in doc if not token.is_punct and not token.is_space]

        return {
            "char_count": len(doc.text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "unique_words": len(set(word.lower() for word in words)),
            "lexical_diversity": len(set(word.lower() for word in words)) / len(words)
            if words
            else 0,
        }

    def _extract_entities(self, doc) -> Dict:
        """Extract named entities from the document."""
        entities = defaultdict(list)

        for ent in doc.ents:
            entities[ent.label_].append(
                {
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "label": ent.label_,
                }
            )

        # Count entities by type
        entity_counts = {label: len(ents) for label, ents in entities.items()}

        return {
            "entities": dict(entities),
            "entity_counts": entity_counts,
            "total_entities": sum(entity_counts.values()),
        }

    def _analyze_sentiment(self, doc) -> Dict:
        """Perform basic sentiment analysis on the document."""
        # This is a simplified sentiment analysis
        # In a production system, you might want to use a pre-trained sentiment analysis model

        positive_words = {"good", "great", "excellent", "wonderful", "amazing", "love", "loved"}
        negative_words = {"bad", "terrible", "awful", "worst", "hate", "hated"}

        positive_count = 0
        negative_count = 0

        for token in doc:
            lower_token = token.text.lower()
            if lower_token in positive_words:
                positive_count += 1
            elif lower_token in negative_words:
                negative_count += 1

        total_words = len([token for token in doc if not token.is_punct and not token.is_space])

        sentiment_score = (positive_count - negative_count) / total_words if total_words > 0 else 0

        return {
            "positive_words": positive_count,
            "negative_words": negative_count,
            "sentiment_score": sentiment_score,
            "sentiment": "positive"
            if sentiment_score > 0.01
            else "negative"
            if sentiment_score < -0.01
            else "neutral",
        }

    def _extract_themes(self, doc) -> Dict:
        """Extract key themes and topics from the document."""
        # Extract noun chunks as potential themes
        noun_chunks = list(doc.noun_chunks)

        # Count noun chunks
        chunk_counter = Counter(chunk.text.lower() for chunk in noun_chunks)

        # Get most common noun chunks as themes
        themes = [
            {"theme": theme, "count": count} for theme, count in chunk_counter.most_common(20)
        ]

        # Extract named entities as potential themes
        entities = [{"theme": ent.text, "type": ent.label_, "count": 1} for ent in doc.ents]

        return {"themes": themes, "named_entities": entities}

    def _analyze_reading_times(self, reading_history: List[Dict]) -> Dict:
        """Analyze reading times and patterns."""
        if not reading_history:
            return {}

        # Group by time of day
        time_of_day = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}

        # Group by day of week
        days_of_week = {
            "Monday": 0,
            "Tuesday": 0,
            "Wednesday": 0,
            "Thursday": 0,
            "Friday": 0,
            "Saturday": 0,
            "Sunday": 0,
        }

        for session in reading_history:
            if "start_time" not in session:
                continue

            try:
                dt = datetime.fromisoformat(session["start_time"])

                # Categorize by time of day
                hour = dt.hour
                if 5 <= hour < 12:
                    time_of_day["morning"] += session.get("duration_minutes", 0)
                elif 12 <= hour < 17:
                    time_of_day["afternoon"] += session.get("duration_minutes", 0)
                elif 17 <= hour < 22:
                    time_of_day["evening"] += session.get("duration_minutes", 0)
                else:
                    time_of_day["night"] += session.get("duration_minutes", 0)

                # Track by day of week
                day_name = dt.strftime("%A")
                days_of_week[day_name] += session.get("duration_minutes", 0)

            except (ValueError, TypeError):
                continue

        return {
            "time_of_day": time_of_day,
            "days_of_week": days_of_week,
            "preferred_reading_time": max(time_of_day.items(), key=lambda x: x[1])[0]
            if any(time_of_day.values())
            else "unknown",
            "preferred_reading_day": max(days_of_week.items(), key=lambda x: x[1])[0]
            if any(days_of_week.values())
            else "unknown",
        }

    def _calculate_consistency(self, reading_history: List[Dict]) -> Dict:
        """Calculate reading consistency metrics."""
        if not reading_history:
            return {}

        # Get all unique dates with reading activity
        reading_dates = set()
        for session in reading_history:
            if "start_time" in session:
                try:
                    dt = datetime.fromisoformat(session["start_time"])
                    reading_dates.add(dt.date())
                except (ValueError, TypeError):
                    continue

        if not reading_dates:
            return {}

        # Calculate streak information
        dates = sorted(reading_dates)
        current_streak = 1
        max_streak = 1

        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1

        # Calculate current streak (recent consecutive days)
        current_streak = 0
        today = datetime.now().date()
        check_date = today

        while check_date in reading_dates:
            current_streak += 1
            check_date -= timedelta(days=1)

        return {
            "total_days_read": len(reading_dates),
            "current_streak_days": current_streak,
            "longest_streak_days": max_streak,
            "reading_frequency": len(reading_dates) / ((max(dates) - min(dates)).days + 1)
            if len(dates) > 1
            else 1.0,
        }


class ContentAnalysisOptions(BaseModel):
    """Options for content analysis."""

    analyze_entities: bool = Field(True, description="Whether to identify named entities")
    analyze_sentiment: bool = Field(True, description="Whether to perform sentiment analysis")
    analyze_themes: bool = Field(True, description="Whether to identify key themes and topics")

    class Config:
        schema_extra = {
            "example": {"analyze_entities": True, "analyze_sentiment": True, "analyze_themes": True}
        }


class ReadingHabitOptions(BaseModel):
    """Options for reading habit analysis."""

    time_period: str = Field(
        "all", description="Time period to analyze ('day', 'week', 'month', 'year', 'all')"
    )

    class Config:
        schema_extra = {"example": {"time_period": "month"}}
