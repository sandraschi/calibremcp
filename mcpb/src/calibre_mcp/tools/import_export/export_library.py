"""Tool for exporting Calibre library data and books."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from fastmcp import MCPTool, Param
except ImportError:
    from ..compat import MCPTool, Param


class ExportLibraryTool(MCPTool):
    """Export Calibre library data and books to a specified location."""

    name = "export_library"
    description = "Export Calibre library to a specified location"
    parameters = [
        Param("export_path", str, "Path where to export the library"),
        Param("library_path", str, "Path to the source Calibre library", required=False),
        Param("include_books", bool, "Whether to include book files in the export", default=True),
        Param("include_metadata", bool, "Whether to include metadata in the export", default=True),
        Param("include_covers", bool, "Whether to include book covers", default=True),
        Param(
            "book_ids",
            Optional[list[int | str]],
            "Specific book IDs to export (all if None)",
            default=None,
        ),
        Param("format", str, "Export format (directory, zip, calibre)", default="directory"),
        Param("progress_callback", Optional[str], "Callback for progress updates", required=False),
    ]

    async def _run(
        self,
        export_path: str,
        library_path: str | None = None,
        include_books: bool = True,
        include_metadata: bool = True,
        include_covers: bool = True,
        book_ids: list[int | str] | None = None,
        format: str = "directory",
        progress_callback: str | None = None,
    ) -> dict:
        """Export the library to the specified location."""
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)
        export_path = Path(export_path).resolve()

        # Create export directory if it doesn't exist
        export_path.mkdir(parents=True, exist_ok=True)

        # Get books to export
        if book_ids:
            books = []
            for book_id in book_ids:
                book = await storage.get_metadata(book_id)
                if book:
                    books.append(book)
        else:
            books = await storage.get_all_books()

        total_books = len(books)
        results = {
            "exported_books": 0,
            "exported_metadata": 0,
            "exported_covers": 0,
            "skipped_books": 0,
            "errors": [],
            "export_path": str(export_path),
            "exported_at": datetime.utcnow().isoformat(),
            "total_books": total_books,
            "included_book_ids": [str(book.id) for book in books],
        }

        # Create metadata directory
        metadata_dir = export_path / "metadata"
        metadata_dir.mkdir(exist_ok=True)

        # Export each book
        for i, book in enumerate(books, 1):
            try:
                self._update_progress(progress_callback, i, total_books, f"Exporting {book.title}")

                # Export metadata
                if include_metadata:
                    metadata_path = metadata_dir / f"{book.id}.json"
                    with open(metadata_path, "w", encoding="utf-8") as f:
                        json.dump(book.dict(), f, ensure_ascii=False, indent=2)
                    results["exported_metadata"] += 1

                # Export book files
                if include_books and book.formats:
                    book_dir = export_path / "books" / str(book.id)
                    book_dir.mkdir(parents=True, exist_ok=True)

                    for fmt in book.formats:
                        src_path = storage.get_book_path(book.id, fmt)
                        if src_path and src_path.exists():
                            dst_path = book_dir / f"{book.id}.{fmt.lower()}"
                            shutil.copy2(src_path, dst_path)
                            results["exported_books"] += 1

                # Export cover
                if include_covers and book.has_cover:
                    cover_path = storage.get_cover_path(book.id)
                    if cover_path and cover_path.exists():
                        cover_dir = export_path / "covers"
                        cover_dir.mkdir(exist_ok=True)
                        dst_path = cover_dir / f"{book.id}.jpg"
                        shutil.copy2(cover_path, dst_path)
                        results["exported_covers"] += 1

            except Exception as e:
                results["errors"].append(
                    {"book_id": str(book.id), "title": book.title, "error": str(e)}
                )

        # Create manifest
        manifest = {
            "version": "1.0",
            "export_date": results["exported_at"],
            "source_library": str(storage.library_path),
            "total_books": results["total_books"],
            "exported_books": results["exported_books"],
            "exported_metadata": results["exported_metadata"],
            "exported_covers": results["exported_covers"],
            "book_ids": [str(book.id) for book in books],
        }

        with open(export_path / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # Package if requested
        if format.lower() == "zip":
            self._update_progress(progress_callback, 0, 1, "Creating archive...")
            shutil.make_archive(str(export_path), "zip", export_path)
            shutil.rmtree(export_path)
            results["export_path"] = f"{export_path}.zip"

        self._update_progress(progress_callback, total_books, total_books, "Export complete!")
        return results

    def _update_progress(
        self, callback_url: str | None, current: int, total: int, message: str
    ) -> None:
        """Send progress updates if a callback URL is provided."""
        if not callback_url:
            return

        import requests

        try:
            requests.post(
                callback_url,
                json={
                    "current": current,
                    "total": total,
                    "message": message,
                    "progress": (current / total) * 100 if total > 0 else 0,
                },
                timeout=5,
            )
        except Exception:
            pass  # Don't fail the export if the callback fails
