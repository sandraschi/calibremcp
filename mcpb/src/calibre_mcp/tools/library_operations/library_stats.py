"""Tool for retrieving statistics about the Calibre library."""

from collections import defaultdict
from datetime import datetime

try:
    from fastmcp import MCPTool, Param
except ImportError:
    from ..compat import MCPTool, Param


class LibraryStatsTool(MCPTool):
    """Get statistics about the Calibre library."""

    name = "library_stats"
    description = "Get statistics about the Calibre library"
    parameters = [
        Param("library_path", str, "Path to the Calibre library", required=False),
        Param("include_breakdown", bool, "Include detailed breakdowns", default=False),
    ]

    async def _run(self, library_path: str | None = None, include_breakdown: bool = False) -> dict:
        """Generate library statistics."""
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)

        # Get all books
        books = await storage.get_all_books()

        # Basic stats
        stats = {
            "total_books": len(books),
            "formats": defaultdict(int),
            "languages": defaultdict(int),
            "publishers": defaultdict(int),
            "series": defaultdict(int),
            "ratings": defaultdict(int),
            "publication_years": defaultdict(int),
            "added_dates": defaultdict(int),
            "file_sizes": {"total": 0, "average": 0},
            "tags": {},
            "authors": {},
        }

        # Calculate statistics
        total_size = 0

        for book in books:
            # Count formats
            for fmt in book.formats or []:
                stats["formats"][fmt.lower()] += 1

            # Count languages
            if book.languages:
                for lang in book.languages:
                    stats["languages"][lang] = stats["languages"].get(lang, 0) + 1

            # Count publishers
            if book.publisher:
                stats["publishers"][book.publisher] += 1

            # Count series
            if book.series:
                stats["series"][book.series] = stats["series"].get(book.series, 0) + 1

            # Count ratings
            if book.rating is not None:
                stats["ratings"][int(book.rating)] += 1

            # Count publication years
            if book.published_date:
                year = book.published_date.year
                stats["publication_years"][year] += 1

            # Count added dates
            if book.timestamp:
                date_str = book.timestamp.strftime("%Y-%m-%d")
                stats["added_dates"][date_str] += 1

            # Calculate file sizes
            if book.size:
                total_size += book.size

            # Count tags
            if book.tags:
                for tag in book.tags:
                    stats["tags"][tag] = stats["tags"].get(tag, 0) + 1

            # Count authors
            if book.authors:
                for author in book.authors:
                    stats["authors"][author] = stats["authors"].get(author, 0) + 1

        # Calculate file size statistics
        stats["file_sizes"]["total"] = total_size
        stats["file_sizes"]["average"] = total_size / len(books) if books else 0

        # Add human-readable sizes
        stats["file_sizes"]["total_human"] = self._human_readable_size(total_size)
        stats["file_sizes"]["average_human"] = self._human_readable_size(
            stats["file_sizes"]["average"]
        )

        # Sort the breakdowns
        for key in [
            "formats",
            "languages",
            "publishers",
            "series",
            "ratings",
            "publication_years",
            "added_dates",
            "tags",
            "authors",
        ]:
            if isinstance(stats[key], dict):
                stats[key] = dict(sorted(stats[key].items(), key=lambda x: (-x[1], x[0])))

        # Add timestamp
        stats["generated_at"] = datetime.utcnow().isoformat()

        return stats

    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert size in bytes to human-readable format."""
        if not size_bytes:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024
            i += 1

        return f"{size_bytes:.2f} {units[i]}"
