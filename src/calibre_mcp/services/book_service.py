"""
Service for handling book-related operations in the Calibre MCP application.
"""

import time
from pathlib import Path
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from ..db.database import DatabaseService
from ..db.models import (  # Use db.models for query models
    Author,
    Book,  # Use db.models.Book for queries (has series relationship)
    Comment,
    Rating,
    Series,
    Tag,
)
from ..logging_config import get_logger
from ..models.book import (
    BookCreate,
    BookResponse,
    BookUpdate,
)  # Use models.book for Pydantic schemas
from .base_service import BaseService, NotFoundError, ValidationError

logger = get_logger("calibremcp.services.book_service")


class BookSearchResult(BookResponse):
    """Model for book search results with additional metadata."""

    class Config(BookResponse.Config):
        fields = {
            "authors": {
                "exclude": {"books", "sort"},
            },
            "series": {
                "exclude": {"books"},
            },
            "tags": {
                "exclude": {"books"},
            },
        }


class BookService(BaseService[Book, BookCreate, BookUpdate, BookResponse]):
    """
    Service class for handling book-related operations.

    This class provides a high-level interface for performing CRUD operations
    on books, including managing relationships with authors, series, and tags.
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize the BookService with a database instance.

        Args:
            db: Database service instance
        """
        super().__init__(db, Book, BookResponse)
        self._library_path_cache = None

    def _get_library_base_path(self) -> str | None:
        """
        Get the base library path from the database connection URL.

        Returns:
            Library base path (directory containing metadata.db) or None if unavailable
        """
        if self._library_path_cache is not None:
            return self._library_path_cache

        try:
            # Get database URL from engine
            if self.db._engine is None:
                return None

            url = str(self.db._engine.url)

            # Extract path from SQLite URL (sqlite:///path/to/metadata.db)
            if url.startswith("sqlite:///"):
                db_path = url.replace("sqlite:///", "").replace("\\", "/")
                # Get parent directory (library root)
                library_path = str(Path(db_path).parent)
                self._library_path_cache = library_path
                return library_path
        except Exception:
            pass

        return None

    def get_by_id(self, book_id: int) -> dict[str, Any]:
        """
        Get a book by its ID with all related data.

        Args:
            book_id: The ID of the book to retrieve

        Returns:
            Dictionary containing book data

        Raises:
            NotFoundError: If the book is not found
        """
        with self._get_db_session() as session:
            book = (
                session.query(Book)
                .options(
                    joinedload(Book.authors),
                    joinedload(Book.tags),
                    joinedload(Book.series),
                    joinedload(Book.ratings),
                    joinedload(Book.comments),
                    joinedload(Book.data),
                    joinedload(Book.identifiers),
                    joinedload(Book.publishers),
                )
                .filter(Book.id == book_id)
                .first()
            )

            if not book:
                raise NotFoundError(f"Book with ID {book_id} not found")

            return self._to_response(book)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        title: str | None = None,  # NEW: Direct title search (bypasses general search)
        author_id: int | None = None,
        author_name: str | None = None,
        authors_list: list[str] | None = None,  # OR logic within list
        exclude_authors_list: list[str] | None = None,  # NOT logic - exclude these authors
        series_id: int | None = None,
        series_name: str | None = None,
        exclude_series_list: list[str] | None = None,  # NOT logic - exclude these series
        tag_id: int | None = None,
        tag_name: str | None = None,
        tags_list: list[str] | None = None,  # OR logic within list
        exclude_tags_list: list[str] | None = None,  # NOT logic - exclude these tags
        comment: str | None = None,
        has_cover: bool | None = None,
        sort_by: str = "title",
        sort_order: str = "asc",
        **filters: Any,
    ) -> dict[str, Any]:
        """
        Get a paginated list of books with optional filtering and sorting.

        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return (1-1000)
            search: Search term to filter books by title, author, or series
            title: Search specifically in book titles only (bypasses FTS for fast exact matching)
            author_id: Filter books by author ID
            author_name: Filter books by author name (case-insensitive partial match)
            series_id: Filter books by series ID
            series_name: Filter books by series name (case-insensitive partial match)
            tag_id: Filter books by tag ID
            tag_name: Filter books by tag name (case-insensitive partial match)
            comment: Search in book comments (case-insensitive partial match)
            has_cover: Filter books by cover availability
            sort_by: Field to sort by (title, author, series, rating, timestamp)
            sort_order: Sort order (asc or desc)
            **filters: Additional filter criteria

        Returns:
            Dictionary containing paginated results and metadata

        Raises:
            ValueError: If invalid parameters are provided
        """
        start_time = time.time()
        logger.info(
            "Starting get_all query",
            extra={
                "service": "book_service",
                "action": "get_all_start",
                "skip": skip,
                "limit": limit,
                "search": search,
                "author_name": author_name,
                "authors_list": authors_list,
                "tag_name": tag_name,
                "tags_list": tags_list,
                "series_name": series_name,
                "sort_by": sort_by,
                "sort_order": sort_order,
            },
        )

        # Validate inputs
        try:
            if limit < 1 or limit > 1000:
                logger.warning(
                    "Invalid limit parameter",
                    extra={"service": "book_service", "action": "validation_error", "limit": limit},
                )
                raise ValueError("Limit must be between 1 and 1000")

            if skip < 0:
                logger.warning(
                    "Invalid skip parameter",
                    extra={"service": "book_service", "action": "validation_error", "skip": skip},
                )
                raise ValueError("Skip cannot be negative")

            if sort_order.lower() not in ("asc", "desc"):
                logger.warning(
                    "Invalid sort_order parameter",
                    extra={
                        "service": "book_service",
                        "action": "validation_error",
                        "sort_order": sort_order,
                    },
                )
                raise ValueError("sort_order must be 'asc' or 'desc'")

            valid_sort_fields = {"title", "author", "series", "rating", "timestamp", "pubdate"}
            if sort_by.lower() not in valid_sort_fields:
                logger.warning(
                    "Invalid sort_by parameter",
                    extra={
                        "service": "book_service",
                        "action": "validation_error",
                        "sort_by": sort_by,
                        "valid_fields": valid_sort_fields,
                    },
                )
                raise ValueError(f"sort_by must be one of {valid_sort_fields}")
        except ValueError as ve:
            logger.error(
                "Input validation failed",
                extra={"service": "book_service", "action": "validation_failed", "error": str(ve)},
            )
            raise

        try:
            with self._get_db_session() as session:
                logger.debug(
                    "Database session acquired",
                    extra={"service": "book_service", "action": "session_acquired"},
                )
            # Start building the query
            # Only eager-load relationships for tables that definitely exist in Calibre schema
            # Many tables (identifiers, books_ratings_link, etc.) may not exist in all Calibre databases
            query = session.query(Book).options(
                joinedload(Book.authors),
                joinedload(Book.tags),
                joinedload(Book.series),  # db.models.Book has series as relationship
                joinedload(Book.data),  # Load format files for file paths
                # Note: ratings, comments, identifiers may not exist in all databases
                # Only eager-load if needed - for now, load lazily to avoid errors
                # joinedload(Book.comments),  # Optional - may not exist
                # joinedload(Book.identifiers),  # Optional - may not exist
            )

            # Apply title-specific filter (bypasses FTS for fast exact matching)
            if title:
                logger.debug(
                    "Filtering by title",
                    extra={"service": "book_service", "action": "filter_title", "title": title},
                )
                title_pattern = f"%{title}%"
                query = query.filter(Book.title.ilike(title_pattern)).distinct()
                logger.debug(
                    "Title filter applied",
                    extra={"service": "book_service", "action": "title_filter_applied"},
                )

            # Apply search filter (title, author, series, tags)
            # NOTE: The OR logic here is ONLY within the search parameter itself
            # (matches title OR author OR series OR tags). This is combined with AND
            # for any other filters (e.g., search AND publisher uses AND logic).

            # Initialize FTS variables BEFORE the search block (needed for later reference)
            fts_db_path = None
            book_ids = None
            fts_snippets = {}
            fts_succeeded = False

            # First check if FTS database is available
            if search:
                logger.debug(
                    "Processing search query",
                    extra={
                        "service": "book_service",
                        "action": "process_search",
                        "search_term": search,
                    },
                )
                from ..utils.fts_utils import find_fts_database, query_fts

                # Get metadata.db path from the database engine URL (not config)
                # The engine is already connected to the correct library
                metadata_db_path = None
                if self.db._engine:
                    # Extract file path from SQLite connection URL
                    # Format: sqlite:///C:/path/to/metadata.db or sqlite:///C:\\path\\to\\metadata.db
                    engine_url = str(self.db._engine.url)
                    logger.debug(
                        "Extracting metadata.db path from engine URL",
                        extra={
                            "service": "book_service",
                            "action": "extract_db_path",
                            "engine_url": engine_url,
                        },
                    )
                    if engine_url.startswith("sqlite:///"):
                        # Remove sqlite:/// prefix
                        db_path_str = engine_url.replace("sqlite:///", "")
                        # Handle both forward and backslashes (Windows can have either)
                        # Path() handles both correctly, so just create Path directly
                        metadata_db_path = Path(db_path_str)
                        logger.debug(
                            "Metadata DB path extracted",
                            extra={
                                "service": "book_service",
                                "action": "db_path_extracted",
                                "path": str(metadata_db_path),
                                "exists": metadata_db_path.exists(),
                            },
                        )

                # Reset FTS variables for this search (already initialized above)
                fts_db_path = None
                book_ids = None
                fts_snippets = {}
                fts_succeeded = False
                if metadata_db_path and metadata_db_path.exists():
                    logger.debug(
                        "Looking for FTS database",
                        extra={"service": "book_service", "action": "find_fts"},
                    )
                    fts_db_path = find_fts_database(metadata_db_path)
                    logger.debug(
                        "FTS database lookup complete",
                        extra={
                            "service": "book_service",
                            "action": "fts_found",
                            "fts_path": str(fts_db_path) if fts_db_path else None,
                        },
                    )

                    if fts_db_path:
                        logger.info(
                            "Using FTS search",
                            extra={
                                "service": "book_service",
                                "action": "fts_search",
                                "search_term": search,
                                "fts_path": str(fts_db_path),
                            },
                        )
                        # Use FTS search - get all matching IDs first (we'll paginate later)
                        # query_fts catches exceptions internally and returns ([], 0) on failure
                        # So we check if we got results - if not, fall back to LIKE
                        try:
                            book_ids, total_fts, fts_snippets = query_fts(
                                fts_db_path,
                                search,
                                limit=10000,  # Get all matches, we'll paginate in SQLAlchemy
                                offset=0,
                                include_snippets=True,
                            )
                            logger.info(
                                "FTS query completed",
                                extra={
                                    "service": "book_service",
                                    "action": "fts_complete",
                                    "book_ids_count": len(book_ids) if book_ids else 0,
                                    "total_fts": total_fts,
                                    "snippets_count": len(fts_snippets),
                                },
                            )
                        except Exception as fts_error:
                            logger.warning(
                                "FTS query failed, falling back to LIKE",
                                extra={
                                    "service": "book_service",
                                    "action": "fts_error",
                                    "error": str(fts_error),
                                    "error_type": type(fts_error).__name__,
                                },
                                exc_info=True,
                            )
                            book_ids = None
                            total_fts = 0
                            fts_snippets = {}  # Reset snippets on error

                        # If FTS returned results, use them
                        if book_ids:
                            # Filter query to only include FTS-matched book IDs
                            query = query.filter(Book.id.in_(book_ids))
                            # Don't need joins or ilike filters since FTS already found matches
                            # Note: Total count will be limited to the IDs we got from FTS
                            fts_succeeded = True
                            logger.debug(
                                "Applied FTS filter to query",
                                extra={
                                    "service": "book_service",
                                    "action": "fts_filter_applied",
                                    "book_ids_count": len(book_ids),
                                    "snippets_count": len(fts_snippets),
                                },
                            )
                        else:
                            logger.debug(
                                "FTS returned no results, will fall back to LIKE",
                                extra={"service": "book_service", "action": "fts_no_results"},
                            )
                        # else: FTS returned no results - could be no matches OR FTS failed
                        # We'll fall back to LIKE search to be safe (since we can't distinguish
                        # "no matches" from "FTS failed" when query_fts returns ([], 0))
                    else:
                        logger.debug(
                            "No FTS database found, will use LIKE search",
                            extra={"service": "book_service", "action": "no_fts"},
                        )

                # Fallback to LIKE search if FTS not available or failed
                # Only use LIKE if we didn't successfully use FTS
                if not fts_succeeded or book_ids is None:
                    logger.info(
                        "Using LIKE search (FTS not available or failed)",
                        extra={
                            "service": "book_service",
                            "action": "like_search",
                            "search_term": search,
                        },
                    )
                    search_pattern = f"%{search}%"
                    query = (
                        query.join(Book.authors, isouter=True)
                        .join(Book.series, isouter=True)
                        .join(Book.tags, isouter=True)
                        .filter(
                            or_(
                                Book.title.ilike(search_pattern),
                                Author.name.ilike(search_pattern),
                                Series.name.ilike(search_pattern),
                                Tag.name.ilike(search_pattern),
                            )
                        )
                        .distinct()
                    )
                    logger.debug(
                        "LIKE search filter applied",
                        extra={"service": "book_service", "action": "like_filter_applied"},
                    )

            # Apply author filters
            if author_id:
                logger.debug(
                    "Filtering by author_id",
                    extra={
                        "service": "book_service",
                        "action": "filter_author_id",
                        "author_id": author_id,
                    },
                )
                query = query.filter(Book.authors.any(Author.id == author_id))
            elif authors_list:
                logger.debug(
                    "Filtering by authors list (OR logic)",
                    extra={
                        "service": "book_service",
                        "action": "filter_authors_list",
                        "authors": authors_list,
                    },
                )
                # Multiple authors with OR logic (book by any of these authors)
                # Within each author name, require ALL words to be present (AND logic)
                author_conditions = []
                for author in authors_list:
                    author_words = author.split()
                    if author_words:
                        # For each author, create AND conditions for all their words
                        # This requires building a complex condition manually since SQLAlchemy
                        # doesn't easily support dynamic AND conditions in OR contexts
                        author_condition = None
                        for word in author_words:
                            word_pattern = f"%{word}%"
                            word_condition = Author.name.ilike(word_pattern)
                            if author_condition is None:
                                author_condition = word_condition
                            else:
                                author_condition = author_condition & word_condition

                        if author_condition is not None:
                            author_conditions.append(author_condition)

                if author_conditions:
                    # Between authors, use OR logic: match any of the specified authors
                    # Use INNER join (not outer) to ensure we only get books by these authors
                    query = query.join(Book.authors).filter(or_(*author_conditions)).distinct()
                    logger.debug(
                        "Authors list filter applied",
                        extra={"service": "book_service", "action": "authors_filter_applied"},
                    )
            elif author_name:
                logger.debug(
                    "Filtering by author name",
                    extra={
                        "service": "book_service",
                        "action": "filter_author_name",
                        "author_name": author_name,
                    },
                )
                # Single author - split into words and require ALL words to be present (AND logic)
                # This allows "Dickson Carr" to match "John Dickson Carr" but not "John Smith" or "Jane Doe"
                author_words = author_name.split()
                if author_words:
                    # Use INNER join to ensure we get books by this author
                    # Build a subquery that finds books matching all author name words
                    author_book_ids_subq = session.query(Book.id).join(Book.authors)
                    # Apply AND logic: author name must contain ALL search words
                    for word in author_words:
                        word_pattern = f"%{word}%"
                        author_book_ids_subq = author_book_ids_subq.filter(
                            Author.name.ilike(word_pattern)
                        )

                    author_book_ids_subq = author_book_ids_subq.distinct().subquery()
                    query = query.filter(Book.id.in_(session.query(author_book_ids_subq.c.id)))

                logger.debug(
                    "Author name filter applied",
                    extra={"service": "book_service", "action": "author_filter_applied"},
                )

            # Apply series filters
            if series_id:
                logger.debug(
                    "Filtering by series_id",
                    extra={
                        "service": "book_service",
                        "action": "filter_series_id",
                        "series_id": series_id,
                    },
                )
                query = query.filter(Book.series_id == series_id)

            if series_name:
                logger.debug(
                    "Filtering by series name",
                    extra={
                        "service": "book_service",
                        "action": "filter_series_name",
                        "series_name": series_name,
                    },
                )
                # Build a subquery that finds books matching the series name
                series_book_ids_subq = (
                    session.query(Book.id)
                    .join(Book.series)
                    .filter(Series.name.ilike(f"%{series_name}%"))
                    .distinct()
                    .subquery()
                )
                query = query.filter(Book.id.in_(session.query(series_book_ids_subq.c.id)))
                logger.debug(
                    "Series name filter applied",
                    extra={"service": "book_service", "action": "series_filter_applied"},
                )

            # Apply tag filters
            if tag_id:
                logger.debug(
                    "Filtering by tag_id",
                    extra={"service": "book_service", "action": "filter_tag_id", "tag_id": tag_id},
                )
                query = query.filter(Book.tags.any(Tag.id == tag_id))
            elif tags_list:
                logger.debug(
                    "Filtering by tags list (OR logic)",
                    extra={
                        "service": "book_service",
                        "action": "filter_tags_list",
                        "tags": tags_list,
                    },
                )
                # Multiple tags with OR logic (book with any of these tags)
                # Build a subquery to find books with any of the specified tags
                tag_conditions = []
                for tag in tags_list:
                    tag_pattern = f"%{tag}%"
                    tag_conditions.append(Tag.name.ilike(tag_pattern))
                if tag_conditions:
                    tag_book_ids_subq = (
                        session.query(Book.id)
                        .join(Book.tags)
                        .filter(or_(*tag_conditions))
                        .distinct()
                        .subquery()
                    )
                    query = query.filter(Book.id.in_(session.query(tag_book_ids_subq.c.id)))
                    logger.debug(
                        "Tags list filter applied",
                        extra={"service": "book_service", "action": "tags_filter_applied"},
                    )
            elif tag_name:
                logger.debug(
                    "Filtering by tag name",
                    extra={
                        "service": "book_service",
                        "action": "filter_tag_name",
                        "tag_name": tag_name,
                    },
                )
                # Single tag - use subquery for clean filtering
                tag_book_ids_subq = (
                    session.query(Book.id)
                    .join(Book.tags)
                    .filter(Tag.name.ilike(f"%{tag_name}%"))
                    .distinct()
                    .subquery()
                )
                query = query.filter(Book.id.in_(session.query(tag_book_ids_subq.c.id)))
                logger.debug(
                    "Tag name filter applied",
                    extra={"service": "book_service", "action": "tag_filter_applied"},
                )

            # Apply tag exclusions (NOT logic - exclude books with these tags)
            if exclude_tags_list:
                logger.debug(
                    "Applying tag exclusions",
                    extra={
                        "service": "book_service",
                        "action": "exclude_tags",
                        "exclude_tags": exclude_tags_list,
                    },
                )
                # Build list of book IDs to exclude (books that have any of the excluded tags)
                exclude_tag_conditions = []
                for exclude_tag in exclude_tags_list:
                    tag_pattern = f"%{exclude_tag}%"
                    exclude_tag_conditions.append(Tag.name.ilike(tag_pattern))

                if exclude_tag_conditions:
                    excluded_book_ids_subq = (
                        session.query(Book.id)
                        .join(Book.tags)
                        .filter(or_(*exclude_tag_conditions))
                        .distinct()
                        .subquery()
                    )
                    query = query.filter(~Book.id.in_(session.query(excluded_book_ids_subq.c.id)))
                    logger.debug(
                        "Tag exclusions applied",
                        extra={"service": "book_service", "action": "tags_excluded"},
                    )

            # Apply author exclusions (NOT logic - exclude books by these authors)
            if exclude_authors_list:
                logger.debug(
                    "Applying author exclusions",
                    extra={
                        "service": "book_service",
                        "action": "exclude_authors",
                        "exclude_authors": exclude_authors_list,
                    },
                )
                # Build list of book IDs to exclude (books by any of the excluded authors)
                # Use word-based matching with AND logic for better exclusion matching
                exclude_author_conditions = []
                for exclude_author in exclude_authors_list:
                    author_words = exclude_author.split()
                    if author_words:
                        # For each excluded author, create AND conditions for all their words
                        exclude_condition = None
                        for word in author_words:
                            word_pattern = f"%{word}%"
                            word_condition = Author.name.ilike(word_pattern)
                            if exclude_condition is None:
                                exclude_condition = word_condition
                            else:
                                exclude_condition = exclude_condition & word_condition

                        if exclude_condition is not None:
                            exclude_author_conditions.append(exclude_condition)

                if exclude_author_conditions:
                    excluded_book_ids_subq = (
                        session.query(Book.id)
                        .join(Book.authors)
                        .filter(or_(*exclude_author_conditions))
                        .distinct()
                        .subquery()
                    )
                    query = query.filter(~Book.id.in_(session.query(excluded_book_ids_subq.c.id)))
                    logger.debug(
                        "Author exclusions applied",
                        extra={"service": "book_service", "action": "authors_excluded"},
                    )

            # Apply series exclusions (NOT logic - exclude books in these series)
            if exclude_series_list:
                logger.debug(
                    "Applying series exclusions",
                    extra={
                        "service": "book_service",
                        "action": "exclude_series",
                        "exclude_series": exclude_series_list,
                    },
                )
                # Build list of book IDs to exclude (books in any of the excluded series)
                exclude_series_conditions = []
                for exclude_series in exclude_series_list:
                    series_pattern = f"%{exclude_series}%"
                    exclude_series_conditions.append(Series.name.ilike(series_pattern))

                if exclude_series_conditions:
                    excluded_book_ids_subq = (
                        session.query(Book.id)
                        .join(Book.series)
                        .filter(or_(*exclude_series_conditions))
                        .distinct()
                        .subquery()
                    )
                    query = query.filter(~Book.id.in_(session.query(excluded_book_ids_subq.c.id)))
                    logger.debug(
                        "Series exclusions applied",
                        extra={"service": "book_service", "action": "series_excluded"},
                    )

            # Apply comment search
            if comment:
                logger.debug(
                    "Filtering by comment",
                    extra={
                        "service": "book_service",
                        "action": "filter_comment",
                        "comment": comment,
                    },
                )
                comment_pattern = f"%{comment}%"
                query = (
                    query.join(Book.comments).filter(Comment.text.ilike(comment_pattern)).distinct()
                )
                logger.debug(
                    "Comment filter applied",
                    extra={"service": "book_service", "action": "comment_filter_applied"},
                )

            # Apply cover filter
            if has_cover is not None:
                logger.debug(
                    "Filtering by cover",
                    extra={
                        "service": "book_service",
                        "action": "filter_cover",
                        "has_cover": has_cover,
                    },
                )
                query = query.filter(Book.has_cover == has_cover)
                logger.debug(
                    "Cover filter applied",
                    extra={"service": "book_service", "action": "cover_filter_applied"},
                )

            # Apply rating filters (handle before general filter loop since it needs join)
            rating_value = filters.pop("rating", None)
            min_rating = filters.pop("min_rating", None)
            max_rating = filters.pop("max_rating", None)
            unrated = filters.pop("unrated", None)

            if (
                rating_value is not None
                or min_rating is not None
                or max_rating is not None
                or unrated
            ):
                # Rating is stored via Book.ratings relationship (many-to-many through books_ratings_link)
                if unrated:
                    # Unrated books don't have a rating entry - use outerjoin to include books without ratings
                    query = query.outerjoin(Book.ratings).filter(Rating.id.is_(None)).distinct()
                else:
                    # Filter by rating value - join to Rating table
                    query = query.join(Book.ratings)
                    if rating_value is not None:
                        query = query.filter(Rating.rating == rating_value)
                    if min_rating is not None:
                        query = query.filter(Rating.rating >= min_rating)
                    if max_rating is not None:
                        query = query.filter(Rating.rating <= max_rating)
                    query = query.distinct()

            # Apply date range filters (pubdate = edition date, timestamp = added date)
            pubdate_start = filters.pop("pubdate_start", None)
            pubdate_end = filters.pop("pubdate_end", None)
            added_after = filters.pop("added_after", None)
            added_before = filters.pop("added_before", None)

            def _parse_date(s: str):
                from datetime import datetime

                if not s or not isinstance(s, str):
                    return None
                raw = s.strip().split("T")[0][:10]
                for fmt, n in (("%Y-%m-%d", 10), ("%Y-%m", 7), ("%Y", 4)):
                    try:
                        return datetime.strptime(raw[:n], fmt)
                    except (ValueError, TypeError, IndexError):
                        continue
                return None

            if pubdate_start:
                dt = _parse_date(pubdate_start)
                if dt:
                    query = query.filter(Book.pubdate >= dt)
            if pubdate_end:
                dt = _parse_date(pubdate_end)
                if dt:
                    from datetime import datetime as dt_cls

                    end_of_day = dt_cls(dt.year, dt.month, dt.day, 23, 59, 59, 999999)
                    query = query.filter(Book.pubdate <= end_of_day)
            if added_after:
                dt = _parse_date(added_after)
                if dt:
                    query = query.filter(Book.timestamp >= dt)
            if added_before:
                dt = _parse_date(added_before)
                if dt:
                    from datetime import datetime as dt_cls

                    end_of_day = dt_cls(dt.year, dt.month, dt.day, 23, 59, 59, 999999)
                    query = query.filter(Book.timestamp <= end_of_day)

            # Apply additional filters from **filters
            # IMPORTANT: All filters are combined with AND logic
            # If you provide search="crime" AND publisher="shueisha",
            # you get books that match BOTH conditions (not OR)
            for field, value in filters.items():
                if field == "publisher":
                    # Publisher might be in identifiers table or custom columns
                    # Try identifiers first
                    from ..models.identifier import Identifier

                    if value:
                        publisher_filter = f"%{value}%"
                        query = (
                            query.join(Identifier, Book.identifiers)
                            .filter(Identifier.type == "publisher")
                            .filter(Identifier.val.ilike(publisher_filter))
                            .distinct()
                        )
                elif field == "publishers":
                    # Multiple publishers - OR within publishers list, AND with other filters
                    from ..models.identifier import Identifier

                    if value and isinstance(value, (list, tuple)):
                        publisher_conditions = []
                        for pub in value:
                            pub_filter = f"%{pub}%"
                            publisher_conditions.append(Identifier.val.ilike(pub_filter))
                        if publisher_conditions:
                            query = (
                                query.join(Identifier, Book.identifiers)
                                .filter(Identifier.type == "publisher")
                                .filter(or_(*publisher_conditions))
                                .distinct()
                            )
                elif field == "has_publisher":
                    from ..models.identifier import Identifier

                    if value is True:
                        # Has publisher
                        query = (
                            query.join(Identifier, Book.identifiers)
                            .filter(Identifier.type == "publisher")
                            .filter(Identifier.val.isnot(None))
                            .filter(Identifier.val != "")
                            .distinct()
                        )
                    elif value is False:
                        # No publisher - use subquery
                        subquery = (
                            session.query(Identifier)
                            .filter(
                                Identifier.book_id == Book.id,
                                Identifier.type == "publisher",
                                Identifier.val.isnot(None),
                                Identifier.val != "",
                            )
                            .exists()
                        )
                        query = query.filter(~subquery)
                elif hasattr(Book, field):
                    column = getattr(Book, field)
                    if isinstance(value, (list, tuple, set)):
                        query = query.filter(column.in_(value))
                    else:
                        query = query.filter(column == value)

            # Apply sorting
            logger.debug(
                "Applying sorting",
                extra={
                    "service": "book_service",
                    "action": "apply_sorting",
                    "sort_by": sort_by,
                    "sort_order": sort_order,
                },
            )
            # Note: In actual Calibre databases, rating might be stored differently.
            # Since books_ratings_link table doesn't exist in user's database,
            # we'll skip rating sort for now or use a workaround.
            sort_mapping = {
                "title": Book.title,
                "author": Author.sort,
                "series": Series.name,
                # Rating: books_ratings_link doesn't exist in actual Calibre schema
                # Skip rating sort or implement alternative access method
                "rating": Book.title,  # Fallback to title sort for now
                "timestamp": Book.timestamp,
                "pubdate": Book.pubdate,
            }

            sort_field = sort_mapping.get(sort_by.lower(), Book.title)
            if sort_order.lower() == "desc":
                sort_field = sort_field.desc()
            else:
                sort_field = sort_field.asc()

            # Special handling for author/series sorting to avoid duplicates
            if sort_by.lower() in ("author", "series"):
                query = query.order_by(sort_field, Book.sort)
            else:
                query = query.order_by(sort_field)
            logger.debug(
                "Sorting applied", extra={"service": "book_service", "action": "sorting_applied"}
            )

            # Get total count before pagination
            logger.debug(
                "Counting total results", extra={"service": "book_service", "action": "count_total"}
            )
            try:
                total = query.distinct().count()
                logger.debug(
                    "Total count retrieved",
                    extra={"service": "book_service", "action": "count_complete", "total": total},
                )
            except Exception as count_error:
                logger.error(
                    "Failed to count total results",
                    extra={
                        "service": "book_service",
                        "action": "count_error",
                        "error": str(count_error),
                        "error_type": type(count_error).__name__,
                    },
                    exc_info=True,
                )
                raise

            # Apply pagination
            logger.debug(
                "Applying pagination",
                extra={
                    "service": "book_service",
                    "action": "apply_pagination",
                    "skip": skip,
                    "limit": limit,
                },
            )
            try:
                books = query.offset(skip).limit(limit).all()
                logger.debug(
                    "Query executed successfully",
                    extra={
                        "service": "book_service",
                        "action": "query_executed",
                        "books_returned": len(books),
                    },
                )
            except Exception as query_error:
                logger.error(
                    "Query execution failed",
                    extra={
                        "service": "book_service",
                        "action": "query_error",
                        "error": str(query_error),
                        "error_type": type(query_error).__name__,
                    },
                    exc_info=True,
                )
                raise

            # Convert to response models
            logger.debug(
                "Converting books to response models",
                extra={"service": "book_service", "action": "convert_models"},
            )
            try:
                items = []
                for book in books:
                    book_dict = self._to_response(book)
                    # Add FTS snippet if available
                    if fts_succeeded and book.id in fts_snippets:
                        book_dict["search_snippet"] = fts_snippets[book.id]
                    items.append(book_dict)
                logger.debug(
                    "Models converted",
                    extra={
                        "service": "book_service",
                        "action": "models_converted",
                        "items_count": len(items),
                        "snippets_added": sum(1 for item in items if "search_snippet" in item),
                    },
                )
            except Exception as convert_error:
                logger.error(
                    "Failed to convert books to response models",
                    extra={
                        "service": "book_service",
                        "action": "convert_error",
                        "error": str(convert_error),
                        "error_type": type(convert_error).__name__,
                    },
                    exc_info=True,
                )
                raise

            duration = time.time() - start_time
            result = {
                "items": items,
                "total": total,
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "page_size": limit,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 1,
            }

            logger.info(
                "get_all query completed successfully",
                extra={
                    "service": "book_service",
                    "action": "get_all_complete",
                    "total": total,
                    "items_returned": len(items),
                    "page": result["page"],
                    "total_pages": result["total_pages"],
                    "duration_seconds": round(duration, 3),
                },
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "get_all query failed",
                extra={
                    "service": "book_service",
                    "action": "get_all_error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_seconds": round(duration, 3),
                },
                exc_info=True,
            )
            raise

    def create(self, book_data: BookCreate) -> dict[str, Any]:
        """
        Create a new book with the given data.

        Args:
            book_data: Data for creating the book

        Returns:
            Dictionary containing the created book data

        Raises:
            ValidationError: If the input data is invalid
        """
        with self._get_db_session() as session:
            # Create book instance
            book_dict = book_data.dict(
                exclude={"author_ids", "series_id", "tag_ids", "rating"}, exclude_unset=True
            )
            book = Book(**book_dict)

            # Handle relationships
            if book_data.author_ids:
                authors = session.query(Author).filter(Author.id.in_(book_data.author_ids)).all()
                if len(authors) != len(book_data.author_ids):
                    found_ids = {a.id for a in authors}
                    missing_ids = set(book_data.author_ids) - found_ids
                    raise ValidationError(f"Authors not found: {', '.join(map(str, missing_ids))}")
                book.authors = authors

            if book_data.series_id is not None:
                series = session.query(Series).get(book_data.series_id)
                if not series:
                    raise ValidationError(f"Series with ID {book_data.series_id} not found")
                book.series = [series]

            if book_data.tag_ids:
                tags = session.query(Tag).filter(Tag.id.in_(book_data.tag_ids)).all()
                if len(tags) != len(book_data.tag_ids):
                    found_ids = {t.id for t in tags}
                    missing_ids = set(book_data.tag_ids) - found_ids
                    raise ValidationError(f"Tags not found: {', '.join(map(str, missing_ids))}")
                book.tags = tags

            if book_data.rating is not None:
                rating = Rating(rating=book_data.rating, book=book)
                session.add(rating)

            session.add(book)
            session.commit()
            session.refresh(book)

            return self._to_response(book)

    def update(self, book_id: int, book_data: BookUpdate | dict[str, Any]) -> dict[str, Any]:
        """
        Update an existing book with the given data.

        Args:
            book_id: ID of the book to update
            book_data: Data for updating the book

        Returns:
            Dictionary containing the updated book data

        Raises:
            NotFoundError: If the book is not found
            ValidationError: If the input data is invalid
        """
        if isinstance(book_data, dict):
            update_data = book_data
        else:
            update_data = book_data.dict(exclude_unset=True)

        with self._get_db_session() as session:
            # Get the existing book
            book = session.query(Book).get(book_id)
            if not book:
                raise NotFoundError(f"Book with ID {book_id} not found")

            # Update simple fields
            for field, value in update_data.items():
                if hasattr(book, field) and field not in [
                    "author_ids",
                    "series_id",
                    "tag_ids",
                    "rating",
                ]:
                    setattr(book, field, value)

            # Handle relationships if provided
            if "author_ids" in update_data:
                authors = (
                    session.query(Author).filter(Author.id.in_(update_data["author_ids"])).all()
                )
                if len(authors) != len(update_data["author_ids"]):
                    found_ids = {a.id for a in authors}
                    missing_ids = set(update_data["author_ids"]) - found_ids
                    raise ValidationError(f"Authors not found: {', '.join(map(str, missing_ids))}")
                book.authors = authors

            if "series_id" in update_data:
                if update_data["series_id"] is not None:
                    series = session.query(Series).get(update_data["series_id"])
                    if not series:
                        raise ValidationError(
                            f"Series with ID {update_data['series_id']} not found"
                        )
                    book.series = [series]
                else:
                    book.series = []

            if "tag_ids" in update_data:
                tags = session.query(Tag).filter(Tag.id.in_(update_data["tag_ids"])).all()
                if len(tags) != len(update_data["tag_ids"]):
                    found_ids = {t.id for t in tags}
                    missing_ids = set(update_data["tag_ids"]) - found_ids
                    raise ValidationError(f"Tags not found: {', '.join(map(str, missing_ids))}")
                book.tags = tags

            if "rating" in update_data:
                # Update or create rating
                rating = session.query(Rating).filter(Rating.book_id == book.id).first()

                if update_data["rating"] is None and rating:
                    session.delete(rating)
                elif update_data["rating"] is not None:
                    if rating:
                        rating.rating = update_data["rating"]
                    else:
                        rating = Rating(rating=update_data["rating"], book=book)
                        session.add(rating)

            session.add(book)
            session.commit()
            session.refresh(book)

            return self._to_response(book)

    def delete(self, book_id: int) -> bool:
        """
        Delete a book by its ID.

        Args:
            book_id: ID of the book to delete

        Returns:
            True if the book was deleted successfully

        Raises:
            NotFoundError: If the book is not found
        """
        with self._get_db_session() as session:
            book = session.query(Book).get(book_id)
            if not book:
                raise NotFoundError(f"Book with ID {book_id} not found")

            session.delete(book)
            session.commit()
            return True

    def get_book_formats(self, book_id: int) -> list[dict[str, Any]]:
        """
        Get all available formats for a book.

        Args:
            book_id: ID of the book

        Returns:
            List of dictionaries containing format information

        Raises:
            NotFoundError: If the book is not found
        """
        with self._get_db_session() as session:
            book = session.query(Book).options(joinedload(Book.data)).get(book_id)
            if not book:
                raise NotFoundError(f"Book with ID {book_id} not found")

            return [
                {
                    "format": data.format.upper(),
                    "size": data.uncompressed_size,
                    "name": data.name,
                    "mtime": data.mtime.isoformat() if data.mtime else None,
                }
                for data in book.data
            ]

    def get_book_cover(self, book_id: int) -> bytes | None:
        """
        Get the cover image for a book.

        Args:
            book_id: ID of the book

        Returns:
            Bytes of the cover image, or None if no cover exists

        Raises:
            NotFoundError: If the book is not found
        """
        with self._get_db_session() as session:
            book = session.query(Book).get(book_id)
            if not book:
                raise NotFoundError(f"Book with ID {book_id} not found")

            if not book.has_cover:
                return None

            # This assumes you have a method to retrieve the cover data
            # You'll need to implement this based on your storage solution
            return self._get_cover_data(book_id)

    def _get_cover_data(self, book_id: int) -> bytes | None:
        """
        Internal method to retrieve cover data for a book.

        This is a placeholder that should be implemented based on your
        specific storage solution for book covers.

        Args:
            book_id: ID of the book

        Returns:
            Bytes of the cover image, or None if no cover exists
        """
        # TODO: Implement cover data retrieval based on your storage solution
        # This could read from the filesystem, a blob store, etc.
        return None

    def _to_response(self, book: Book) -> dict[str, Any]:
        """
        Convert a Book model instance to a response dictionary.

        Args:
            book: The Book instance to convert

        Returns:
            Dictionary containing the book data in the response format
        """
        # Build response dictionary manually to avoid relationship access issues
        # Pydantic V2 model_validate will try to access all attributes including relationships
        # which can cause issues with lazy-loaded relationships or column name mismatches
        book_dict = {
            "id": book.id,
            "title": book.title,
            "sort": book.sort,
            "timestamp": book.timestamp,
            "pubdate": book.pubdate,
            "series_index": book.series_index,
            "author_sort": book.author_sort,
            "isbn": book.isbn,
            "lccn": book.lccn,
            "path": book.path,
            "has_cover": bool(book.has_cover),
            "uuid": book.uuid,
            "last_modified": book.last_modified,
        }

        # Handle relationships manually to avoid lazy-loading issues
        book_dict["authors"] = [
            {"id": a.id, "name": a.name} for a in (book.authors if hasattr(book, "authors") else [])
        ]
        book_dict["tags"] = [
            {"id": t.id, "name": t.name} for t in (book.tags if hasattr(book, "tags") else [])
        ]
        # Handle series - db.models.Book has series as relationship
        if hasattr(book, "series") and book.series:
            book_dict["series"] = (
                {"id": book.series[0].id, "name": book.series[0].name} if book.series else None
            )
        else:
            book_dict["series"] = None

        # Rating from ratings relationship
        if hasattr(book, "ratings") and book.ratings:
            book_dict["rating"] = (
                book.ratings[0].rating if hasattr(book.ratings[0], "rating") else None
            )
        else:
            book_dict["rating"] = None

        # Publisher from publishers relationship
        if hasattr(book, "publishers") and book.publishers:
            book_dict["publisher"] = ", ".join(
                p.name for p in book.publishers if getattr(p, "name", None)
            )
        else:
            book_dict["publisher"] = None

        # Identifiers from identifiers relationship
        if hasattr(book, "identifiers") and book.identifiers:
            book_dict["identifiers"] = {
                ident.type: ident.val
                for ident in book.identifiers
                if getattr(ident, "type", None) and getattr(ident, "val", None)
            }
        else:
            book_dict["identifiers"] = {}

        # Handle comments - may not exist in all databases
        try:
            if hasattr(book, "comments") and book.comments:
                book_dict["comments"] = book.comments.text if book.comments.text else ""
            else:
                book_dict["comments"] = ""
        except Exception as e:
            # Comments relationship may not exist or be accessible
            logger.debug(f"Could not load comments for book {book.id}: {e}")
            book_dict["comments"] = ""

        # Add cover URL if cover exists
        if book.has_cover and book.path:
            # Generate a relative cover path that can be used with the API
            book_dict["cover_url"] = f"/api/v1/books/{book.id}/cover"
            logger.debug(f"Added cover_url for book {book.id}: {book_dict['cover_url']}")
        else:
            book_dict["cover_url"] = None

        # Build formats list with file paths
        # Calibre stores files using either:
        # 1. Descriptive filename from data.name if available
        # 2. Numeric format {data.id}.{format.lower()} if data.name is empty
        formats = []
        if hasattr(book, "data") and book.data:
            # Get library base path from database URL
            library_path = self._get_library_base_path()
            for data in book.data:
                # Use descriptive filename if available, otherwise use numeric format
                if data.name and data.name.strip():
                    # Descriptive filename: name may include extension, or we add it
                    if data.name.lower().endswith(f".{data.format.lower()}"):
                        filename = data.name
                    else:
                        filename = f"{data.name}.{data.format.lower()}"
                else:
                    # Numeric filename format
                    filename = f"{data.id}.{data.format.lower()}"

                relative_path = f"{book.path}/{filename}" if book.path else filename
                full_path = (
                    str(Path(library_path) / relative_path) if library_path else relative_path
                )

                formats.append(
                    {
                        "format": data.format.upper(),
                        "filename": filename,
                        "path": full_path,
                        "size": data.uncompressed_size if hasattr(data, "uncompressed_size") else 0,
                    }
                )
        book_dict["formats"] = formats

        # For debugging - return raw dict instead of validated model
        # return BookResponse.model_validate(book_dict).model_dump()
        return book_dict


# Create a singleton instance of the service
book_service = BookService(DatabaseService())
