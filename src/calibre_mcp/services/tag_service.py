"""
Service for handling tag-related operations in the Calibre MCP application.
"""

from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import joinedload
from sqlalchemy import func, desc, asc, or_
from difflib import SequenceMatcher

from ..db.database import DatabaseService
from ..models.tag import Tag, TagCreate, TagUpdate, TagResponse
from ..models.book import Book
from .base_service import BaseService, NotFoundError, ValidationError


class TagService(BaseService[Tag, TagCreate, TagUpdate, TagResponse]):
    """
    Service class for handling tag-related operations.

    This class provides a high-level interface for performing CRUD operations
    on tags, including managing relationships with books and tag weeding.
    """

    def __init__(self, db: DatabaseService):
        """
        Initialize the TagService with a database instance.

        Args:
            db: Database service instance
        """
        super().__init__(db, Tag, TagResponse)

    def get_by_id(self, tag_id: int) -> Dict[str, Any]:
        """
        Get a tag by ID with related data.

        Args:
            tag_id: The ID of the tag to retrieve

        Returns:
            Dictionary containing tag data with book count

        Raises:
            NotFoundError: If the tag is not found
        """
        with self._get_db_session() as session:
            tag = session.query(Tag).options(joinedload(Tag.books)).filter(Tag.id == tag_id).first()

            if not tag:
                raise NotFoundError(f"Tag with ID {tag_id} not found")

            return self._to_response(tag)

    def get_by_name(self, tag_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a tag by name.

        Args:
            tag_name: The name of the tag to retrieve

        Returns:
            Dictionary containing tag data or None if not found
        """
        with self._get_db_session() as session:
            tag = (
                session.query(Tag)
                .options(joinedload(Tag.books))
                .filter(func.lower(Tag.name) == tag_name.lower())
                .first()
            )

            if not tag:
                return None

            return self._to_response(tag)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        min_book_count: Optional[int] = None,
        max_book_count: Optional[int] = None,
        unused_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Get a paginated list of tags with optional filtering and sorting.

        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            search: Search term to filter tags by name
            sort_by: Field to sort by (e.g., 'name', 'book_count')
            sort_order: Sort order ('asc' or 'desc')
            min_book_count: Minimum number of books using this tag
            max_book_count: Maximum number of books using this tag
            unused_only: If True, only return tags with 0 books

        Returns:
            Dictionary containing paginated list of tags and metadata
        """
        with self._get_db_session() as session:
            # Start with base query
            query = session.query(Tag)

            # Add subquery for book count
            book_count = (
                session.query(Tag.id.label("tag_id"), func.count(Book.id).label("book_count"))
                .join(Tag.books)
                .group_by(Tag.id)
                .subquery()
            )

            # Join with book count
            query = query.outerjoin(book_count, Tag.id == book_count.c.tag_id)

            # Apply filters
            if search:
                search_term = f"%{search}%"
                query = query.filter(Tag.name.ilike(search_term))

            if unused_only:
                query = query.filter(
                    or_(book_count.c.book_count.is_(None), book_count.c.book_count == 0)
                )

            if min_book_count is not None:
                query = query.filter(func.coalesce(book_count.c.book_count, 0) >= min_book_count)

            if max_book_count is not None:
                query = query.filter(func.coalesce(book_count.c.book_count, 0) <= max_book_count)

            # Apply sorting
            if sort_by == "book_count":
                if sort_order.lower() == "desc":
                    query = query.order_by(desc(func.coalesce(book_count.c.book_count, 0)))
                else:
                    query = query.order_by(asc(func.coalesce(book_count.c.book_count, 0)))
            else:
                sort_field = getattr(Tag, sort_by, Tag.name)
                if sort_order.lower() == "desc":
                    query = query.order_by(desc(sort_field))
                else:
                    query = query.order_by(asc(sort_field))

            # Get total count before pagination
            total = query.distinct().count()

            # Apply pagination and add book_count column for easy access
            tags = query.distinct().options(joinedload(Tag.books)).offset(skip).limit(limit).all()

            # Convert to response models with book counts
            items = []
            for tag in tags:
                tag_dict = self._to_response(tag)

                # Get book count from relationship (already loaded via joinedload)
                book_count_value = len(tag.books) if hasattr(tag, "books") and tag.books else 0
                tag_dict["book_count"] = book_count_value
                items.append(tag_dict)

            return {
                "items": items,
                "total": total,
                "page": (skip // limit) + 1,
                "per_page": limit,
                "total_pages": (total + limit - 1) // limit if total > 0 else 1,
            }

    def create(self, tag_data: TagCreate) -> Dict[str, Any]:
        """
        Create a new tag.

        Args:
            tag_data: Data for creating the tag

        Returns:
            Dictionary containing the created tag data

        Raises:
            ValidationError: If a tag with the same name already exists
        """
        with self._get_db_session() as session:
            # Normalize tag name
            normalized_name = self._normalize_tag_name(tag_data.name)

            # Check if tag with same name already exists
            existing = (
                session.query(Tag).filter(func.lower(Tag.name) == normalized_name.lower()).first()
            )

            if existing:
                raise ValidationError(f"Tag with name '{normalized_name}' already exists")

            # Create new tag
            tag = Tag(name=normalized_name)

            session.add(tag)
            session.commit()
            session.refresh(tag)

            return self._to_response(tag)

    def update(self, tag_id: int, tag_data: Union[TagUpdate, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update an existing tag (rename it).

        Args:
            tag_id: ID of the tag to update
            tag_data: Data for updating the tag

        Returns:
            Dictionary containing the updated tag data

        Raises:
            NotFoundError: If the tag is not found
            ValidationError: If the update data is invalid
        """
        if isinstance(tag_data, dict):
            update_data = tag_data
        else:
            update_data = tag_data.dict(exclude_unset=True)

        with self._get_db_session() as session:
            # Get the existing tag
            tag = session.query(Tag).get(tag_id)
            if not tag:
                raise NotFoundError(f"Tag with ID {tag_id} not found")

            # Check if name is being updated and if it conflicts with existing
            if "name" in update_data:
                normalized_name = self._normalize_tag_name(update_data["name"])
                if normalized_name != tag.name:
                    existing = (
                        session.query(Tag)
                        .filter(func.lower(Tag.name) == normalized_name.lower(), Tag.id != tag_id)
                        .first()
                    )
                    if existing:
                        raise ValidationError(f"Tag with name '{normalized_name}' already exists")

                    tag.name = normalized_name

            session.add(tag)
            session.commit()
            session.refresh(tag)

            return self._to_response(tag)

    def delete(self, tag_id: int, force: bool = False) -> bool:
        """
        Delete a tag by ID.

        Removes the tag from all books and deletes the tag itself.

        Args:
            tag_id: ID of the tag to delete
            force: If True, delete even if tag has books (removes tag from books)

        Returns:
            bool: True if deletion was successful

        Raises:
            NotFoundError: If the tag is not found
        """
        with self._get_db_session() as session:
            tag = session.query(Tag).options(joinedload(Tag.books)).filter(Tag.id == tag_id).first()

            if not tag:
                raise NotFoundError(f"Tag with ID {tag_id} not found")

            # Remove tag from all books (relationship is handled by SQLAlchemy)
            # The many-to-many relationship will be automatically cleaned up
            # when we delete the tag if the relationship is set up correctly

            session.delete(tag)
            session.commit()
            return True

    def find_duplicates(self, similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Find duplicate or similar tags that should be merged.

        Args:
            similarity_threshold: Similarity score threshold (0.0-1.0) for considering tags similar

        Returns:
            List of dictionaries containing groups of similar tags
        """
        with self._get_db_session() as session:
            tags = session.query(Tag).options(joinedload(Tag.books)).all()

            duplicates = []
            processed = set()

            for i, tag1 in enumerate(tags):
                if tag1.id in processed:
                    continue

                similar_tags = [tag1]

                for tag2 in tags[i + 1 :]:
                    if tag2.id in processed:
                        continue

                    similarity = SequenceMatcher(None, tag1.name.lower(), tag2.name.lower()).ratio()

                    if similarity >= similarity_threshold:
                        similar_tags.append(tag2)
                        processed.add(tag2.id)

                if len(similar_tags) > 1:
                    # Calculate book counts
                    tag_info = []
                    for tag in similar_tags:
                        book_count = len(tag.books) if hasattr(tag, "books") else 0
                        tag_info.append({"id": tag.id, "name": tag.name, "book_count": book_count})

                    # Sort by book count (descending) to suggest keeping the most-used one
                    tag_info.sort(key=lambda x: x["book_count"], reverse=True)

                    duplicates.append(
                        {
                            "tags": tag_info,
                            "suggested_name": tag_info[0]["name"],  # Use most popular as suggested
                            "total_books": sum(t["book_count"] for t in tag_info),
                        }
                    )

                    processed.add(tag1.id)

            return duplicates

    def merge_tags(self, source_tag_ids: List[int], target_tag_id: int) -> Dict[str, Any]:
        """
        Merge multiple source tags into a target tag.

        All books tagged with source tags will be retagged with the target tag.
        Source tags will be deleted after merging.

        Args:
            source_tag_ids: List of tag IDs to merge from
            target_tag_id: Tag ID to merge into

        Returns:
            Dictionary with merge results

        Raises:
            NotFoundError: If any tag is not found
            ValidationError: If target tag is in source list
        """
        if target_tag_id in source_tag_ids:
            raise ValidationError("Target tag cannot be in source tag list")

        with self._get_db_session() as session:
            # Get target tag
            target_tag = session.query(Tag).options(joinedload(Tag.books)).get(target_tag_id)
            if not target_tag:
                raise NotFoundError(f"Target tag with ID {target_tag_id} not found")

            # Get source tags
            source_tags = []
            books_affected = set()

            for source_id in source_tag_ids:
                source_tag = session.query(Tag).options(joinedload(Tag.books)).get(source_id)
                if not source_tag:
                    raise NotFoundError(f"Source tag with ID {source_id} not found")

                source_tags.append(source_tag)

                # Collect books that need retagging
                if hasattr(source_tag, "books"):
                    for book in source_tag.books:
                        books_affected.add(book)

            # Retag books: add target tag if not already present, remove source tags
            for book in books_affected:
                # Add target tag if not already tagged
                if target_tag not in book.tags:
                    book.tags.append(target_tag)

                # Remove source tags
                for source_tag in source_tags:
                    if source_tag in book.tags:
                        book.tags.remove(source_tag)

            # Delete source tags
            for source_tag in source_tags:
                session.delete(source_tag)

            session.commit()

            return {
                "success": True,
                "target_tag": self._to_response(target_tag),
                "merged_tags": [self._to_response(tag).get("name", "") for tag in source_tags],
                "books_affected": len(books_affected),
            }

    def get_unused_tags(self) -> List[Dict[str, Any]]:
        """
        Get all tags that are not assigned to any books.

        Returns:
            List of unused tag dictionaries
        """
        with self._get_db_session() as session:
            # Get tags with book counts
            unused_tags = (
                session.query(Tag)
                .outerjoin(Tag.books)
                .group_by(Tag.id)
                .having(func.count(Book.id) == 0)
                .all()
            )

            return [self._to_response(tag) for tag in unused_tags]

    def delete_unused_tags(self) -> Dict[str, Any]:
        """
        Delete all tags that are not assigned to any books.

        Returns:
            Dictionary with deletion results
        """
        unused_tags = self.get_unused_tags()

        with self._get_db_session() as session:
            deleted_count = 0
            for tag_dict in unused_tags:
                tag = session.query(Tag).get(tag_dict["id"])
                if tag:
                    session.delete(tag)
                    deleted_count += 1

            session.commit()

            return {
                "success": True,
                "deleted_count": deleted_count,
                "deleted_tags": [t["name"] for t in unused_tags],
            }

    def normalize_tag_name(self, tag_name: str) -> str:
        """
        Normalize a tag name (trim whitespace, standardize case).

        Args:
            tag_name: Tag name to normalize

        Returns:
            Normalized tag name
        """
        return self._normalize_tag_name(tag_name)

    @staticmethod
    def _normalize_tag_name(tag_name: str) -> str:
        """
        Normalize tag name: trim, lowercase first letter of each word.

        Args:
            tag_name: Tag name to normalize

        Returns:
            Normalized tag name
        """
        # Trim whitespace
        normalized = tag_name.strip()

        # Title case (first letter of each word capitalized)
        normalized = normalized.title()

        return normalized

    def get_tag_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about tags in the library.

        Returns:
            Dictionary containing tag statistics
        """
        with self._get_db_session() as session:
            # Total number of tags
            total_tags = session.query(func.count(Tag.id)).scalar()

            # Tags with book counts
            tag_counts = (
                session.query(Tag, func.count(Book.id).label("book_count"))
                .outerjoin(Tag.books)
                .group_by(Tag.id)
                .all()
            )

            unused_count = sum(1 for _, count in tag_counts if count == 0)

            # Top tags by book count
            top_tags = (
                session.query(Tag, func.count(Book.id).label("book_count"))
                .join(Tag.books)
                .group_by(Tag.id)
                .order_by(desc("book_count"))
                .limit(20)
                .all()
            )

            return {
                "total_tags": total_tags,
                "unused_tags_count": unused_count,
                "used_tags_count": total_tags - unused_count,
                "top_tags": [
                    {"id": tag.id, "name": tag.name, "book_count": book_count}
                    for tag, book_count in top_tags
                ],
                "average_books_per_tag": (
                    sum(count for _, count in tag_counts) / total_tags if total_tags > 0 else 0
                ),
            }


# Create a singleton instance of the service
tag_service = TagService(DatabaseService())
