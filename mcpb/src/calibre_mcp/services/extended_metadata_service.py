"""
Service for extended book metadata (translator, first_published).

Stored in CalibreMCP-owned SQLite. Calibre's metadata.db schema is not modified.
"""

from typing import Any

from ..db.user_data import BookExtendedMetadata, get_user_data_db
from ..logging_config import get_logger

logger = get_logger("calibremcp.services.extended_metadata")


class ExtendedMetadataService:
    """CRUD for translator and first_published on books."""

    def _get_library_path(self) -> str:
        """Get current library path (parent of metadata.db)."""
        try:
            from pathlib import Path

            from ..db.database import get_database

            db_path = get_database().get_current_path()
            if not db_path:
                return ""
            return str(Path(db_path).parent)
        except RuntimeError:
            return ""

    def get(
        self,
        book_id: int,
        library_path: str | None = None,
    ) -> dict[str, Any]:
        """Get extended metadata for a book."""
        lib_path = library_path or self._get_library_path()
        if not lib_path:
            return {
                "success": False,
                "error": "No library context. Load a library first.",
                "error_code": "NO_LIBRARY",
            }

        db = get_user_data_db()
        with db.session_scope() as session:
            rec = (
                session.query(BookExtendedMetadata)
                .filter(
                    BookExtendedMetadata.book_id == book_id,
                    BookExtendedMetadata.library_path == lib_path,
                )
                .first()
            )
            if not rec:
                return {
                    "success": True,
                    "book_id": book_id,
                    "library_path": lib_path,
                    "translator": None,
                    "first_published": None,
                    "has_data": False,
                }
            return {
                "success": True,
                "book_id": book_id,
                "library_path": lib_path,
                "translator": rec.translator or None,
                "first_published": rec.first_published or None,
                "has_data": bool(rec.translator or rec.first_published),
                "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
            }

    def set_translator(
        self,
        book_id: int,
        translator: str,
        library_path: str | None = None,
    ) -> dict[str, Any]:
        """Set or update translator for a book."""
        return self._upsert(
            book_id, translator=translator.strip() or None, library_path=library_path
        )

    def set_first_published(
        self,
        book_id: int,
        first_published: str,
        library_path: str | None = None,
    ) -> dict[str, Any]:
        """Set or update first published (e.g. '1599', '44 BC')."""
        return self._upsert(
            book_id, first_published=first_published.strip() or None, library_path=library_path
        )

    def upsert(
        self,
        book_id: int,
        translator: str | None = None,
        first_published: str | None = None,
        library_path: str | None = None,
    ) -> dict[str, Any]:
        """Create or update extended metadata. Partial updates supported."""
        return self._upsert(
            book_id,
            translator=translator.strip() if translator else None,
            first_published=first_published.strip() if first_published else None,
            library_path=library_path,
        )

    def _upsert(
        self,
        book_id: int,
        translator: str | None = None,
        first_published: str | None = None,
        library_path: str | None = None,
    ) -> dict[str, Any]:
        lib_path = library_path or self._get_library_path()
        if not lib_path:
            return {
                "success": False,
                "error": "No library context. Load a library first.",
                "error_code": "NO_LIBRARY",
            }

        db = get_user_data_db()
        with db.session_scope() as session:
            rec = (
                session.query(BookExtendedMetadata)
                .filter(
                    BookExtendedMetadata.book_id == book_id,
                    BookExtendedMetadata.library_path == lib_path,
                )
                .first()
            )
            if rec:
                if translator is not None:
                    rec.translator = translator or ""
                if first_published is not None:
                    rec.first_published = first_published or ""
                session.add(rec)
                return {
                    "success": True,
                    "book_id": book_id,
                    "library_path": lib_path,
                    "translator": rec.translator or None,
                    "first_published": rec.first_published or None,
                    "updated": True,
                }
            rec = BookExtendedMetadata(
                book_id=book_id,
                library_path=lib_path,
                translator=translator or "",
                first_published=first_published or "",
            )
            session.add(rec)
            session.flush()
            return {
                "success": True,
                "book_id": book_id,
                "library_path": lib_path,
                "translator": rec.translator or None,
                "first_published": rec.first_published or None,
                "created": True,
            }

    def delete(
        self,
        book_id: int,
        library_path: str | None = None,
    ) -> dict[str, Any]:
        """Remove extended metadata for a book."""
        lib_path = library_path or self._get_library_path()
        if not lib_path:
            return {
                "success": False,
                "error": "No library context. Load a library first.",
                "error_code": "NO_LIBRARY",
            }

        db = get_user_data_db()
        with db.session_scope() as session:
            deleted = (
                session.query(BookExtendedMetadata)
                .filter(
                    BookExtendedMetadata.book_id == book_id,
                    BookExtendedMetadata.library_path == lib_path,
                )
                .delete()
            )
            return {
                "success": True,
                "book_id": book_id,
                "library_path": lib_path,
                "deleted": deleted > 0,
            }


extended_metadata_service = ExtendedMetadataService()
