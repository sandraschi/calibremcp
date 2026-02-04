"""
Service for user comments (annotations on books).

Stored in CalibreMCP-owned SQLite, separate from Calibre's description/comment field.
"""

from typing import Any

from ..db.user_data import UserComment, get_user_data_db
from ..logging_config import get_logger

logger = get_logger("calibremcp.services.user_comment")


class UserCommentService:
    """CRUD operations for user comments on books."""

    def _get_library_path(self) -> str:
        """Get current library path for comment scope (parent of metadata.db)."""
        try:
            from pathlib import Path

            from ..db.database import get_database

            db_path = get_database().get_current_path()
            if not db_path:
                return ""
            return str(Path(db_path).parent)
        except RuntimeError:
            return ""

    def create_or_update(
        self,
        book_id: int,
        comment_text: str,
        library_path: str | None = None,
    ) -> dict[str, Any]:
        """Create or update user comment for a book."""
        lib_path = library_path or self._get_library_path()
        if not lib_path:
            return {
                "success": False,
                "error": "No library context. Load a library first.",
                "error_code": "NO_LIBRARY",
            }

        db = get_user_data_db()
        with db.session_scope() as session:
            existing = (
                session.query(UserComment)
                .filter(
                    UserComment.book_id == book_id,
                    UserComment.library_path == lib_path,
                )
                .first()
            )

            if existing:
                existing.comment_text = comment_text
                session.add(existing)
                return {
                    "success": True,
                    "id": existing.id,
                    "book_id": book_id,
                    "library_path": lib_path,
                    "comment_text": comment_text[:200] + "..."
                    if len(comment_text) > 200
                    else comment_text,
                    "updated": True,
                }
            else:
                uc = UserComment(
                    book_id=book_id,
                    library_path=lib_path,
                    comment_text=comment_text,
                )
                session.add(uc)
                session.flush()
                return {
                    "success": True,
                    "id": uc.id,
                    "book_id": book_id,
                    "library_path": lib_path,
                    "comment_text": comment_text[:200] + "..."
                    if len(comment_text) > 200
                    else comment_text,
                    "created": True,
                }

    def get(
        self,
        book_id: int,
        library_path: str | None = None,
    ) -> dict[str, Any]:
        """Get user comment for a book."""
        lib_path = library_path or self._get_library_path()
        if not lib_path:
            return {
                "success": False,
                "error": "No library context.",
                "error_code": "NO_LIBRARY",
            }

        db = get_user_data_db()
        with db.session_scope() as session:
            uc = (
                session.query(UserComment)
                .filter(
                    UserComment.book_id == book_id,
                    UserComment.library_path == lib_path,
                )
                .first()
            )

            if not uc:
                return {
                    "success": True,
                    "book_id": book_id,
                    "comment": None,
                    "has_comment": False,
                }

            return {
                "success": True,
                "book_id": book_id,
                "id": uc.id,
                "comment": uc.comment_text,
                "has_comment": True,
                "updated_at": uc.updated_at.isoformat() if uc.updated_at else None,
            }

    def delete(
        self,
        book_id: int,
        library_path: str | None = None,
    ) -> dict[str, Any]:
        """Delete user comment for a book."""
        lib_path = library_path or self._get_library_path()
        if not lib_path:
            return {
                "success": False,
                "error": "No library context.",
                "error_code": "NO_LIBRARY",
            }

        db = get_user_data_db()
        with db.session_scope() as session:
            uc = (
                session.query(UserComment)
                .filter(
                    UserComment.book_id == book_id,
                    UserComment.library_path == lib_path,
                )
                .first()
            )

            if uc:
                session.delete(uc)
                return {"success": True, "deleted": True, "book_id": book_id}

            return {"success": True, "deleted": False, "book_id": book_id}

    def append(
        self,
        book_id: int,
        text_to_append: str,
        library_path: str | None = None,
    ) -> dict[str, Any]:
        """Append text to existing user comment."""
        lib_path = library_path or self._get_library_path()
        if not lib_path:
            return {
                "success": False,
                "error": "No library context.",
                "error_code": "NO_LIBRARY",
            }

        db = get_user_data_db()
        with db.session_scope() as session:
            uc = (
                session.query(UserComment)
                .filter(
                    UserComment.book_id == book_id,
                    UserComment.library_path == lib_path,
                )
                .first()
            )

            if uc:
                uc.comment_text = (uc.comment_text or "") + "\n" + text_to_append
            else:
                uc = UserComment(
                    book_id=book_id,
                    library_path=lib_path,
                    comment_text=text_to_append,
                )
                session.add(uc)

            return {
                "success": True,
                "book_id": book_id,
                "comment_length": len(uc.comment_text or ""),
            }


user_comment_service = UserCommentService()
