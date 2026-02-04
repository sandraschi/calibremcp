"""Enhanced metadata and organization tools for CalibreMCP."""

import logging
import re
import string
import unicodedata
from typing import Any

try:
    from fastmcp import MCPTool
except ImportError:
    from ..compat import MCPTool
from pydantic import BaseModel, Field, HttpUrl


# Models
class MetadataEnhancementOptions(BaseModel):
    """Options for enhancing book metadata."""

    update_titles: bool = True
    update_authors: bool = True
    update_series: bool = True
    update_publisher: bool = False
    update_pubdate: bool = False
    update_identifiers: bool = True
    update_ratings: bool = False
    update_tags: bool = True
    update_comments: bool = False
    update_cover: bool = False
    dry_run: bool = True
    backup_before_changes: bool = True


class MetadataSource(BaseModel):
    """Configuration for a metadata source."""

    name: str
    priority: int = 0
    enabled: bool = True
    api_key: str | None = None
    url: HttpUrl | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class MetadataEnhancementResult(BaseModel):
    """Result of a metadata enhancement operation."""

    book_id: str
    changes: dict[str, dict[str, Any]] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    success: bool = True


class SeriesInfo(BaseModel):
    """Information about a book series."""

    name: str
    index: float | None = None
    total_books: int | None = None
    description: str | None = None


class AuthorInfo(BaseModel):
    """Enhanced author information."""

    name: str
    sort: str | None = None
    link: HttpUrl | None = None
    description: str | None = None


class MetadataStandardizationOptions(BaseModel):
    """Options for standardizing metadata."""

    title_case: bool = True
    title_remove_series: bool = True
    author_sort: bool = True
    author_invert_names: bool = True
    isbn_validate: bool = True
    isbn_convert_to_13: bool = True
    language_code: str = "eng"  # Default language code
    date_format: str = "%Y-%m-%d"
    remove_special_chars: bool = True
    normalize_unicode: bool = True
    deduplicate_tags: bool = True
    tag_separator: str = ","


# Main tool
class EnhancedMetadataTools(MCPTool):
    """Enhanced metadata and organization tools for CalibreMCP."""

    name = "enhanced_metadata_tools"
    description = "Advanced metadata enhancement and organization tools"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self._metadata_sources = self._load_default_metadata_sources()

    # Metadata Enhancement
    async def enhance_metadata(
        self,
        library_path: str,
        book_ids: list[str] | None = None,
        options: dict | None = None,
    ) -> dict:
        """Enhance metadata for one or more books."""
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)
        opts = MetadataEnhancementOptions(**(options or {}))

        if book_ids is None:
            # Get all book IDs if none specified
            books = await storage.get_all_books()
            book_ids = [book["id"] for book in books if "id" in book]

        results = []

        for book_id in book_ids:
            result = MetadataEnhancementResult(book_id=book_id)

            try:
                book = await storage.get_book(book_id)
                if not book:
                    result.errors.append(f"Book {book_id} not found")
                    result.success = False
                    results.append(result.dict())
                    continue

                # Backup if requested
                if opts.backup_before_changes and not opts.dry_run:
                    await self._backup_book_metadata(storage, book)

                # Apply enhancements
                updated = False

                if opts.update_titles:
                    updated |= await self._enhance_title(book, result, opts)

                if opts.update_authors:
                    updated |= await self._enhance_authors(book, result, opts)

                if opts.update_series:
                    updated |= await self._enhance_series(book, result, opts)

                if opts.update_publisher:
                    updated |= await self._enhance_publisher(book, result, opts)

                if opts.update_identifiers:
                    updated |= await self._enhance_identifiers(book, result, opts)

                if opts.update_tags:
                    updated |= await self._enhance_tags(book, result, opts)

                if opts.update_cover:
                    updated |= await self._enhance_cover(book, result, opts)

                # Save changes if any were made and we're not in dry-run mode
                if updated and not opts.dry_run:
                    await storage.update_book(book_id, book)

                result.success = True

            except Exception as e:
                self.logger.error(
                    f"Error enhancing metadata for book {book_id}: {str(e)}", exc_info=True
                )
                result.errors.append(f"Error: {str(e)}")
                result.success = False

            results.append(result.dict())

        return {
            "success": True,
            "results": results,
            "total_books": len(results),
            "books_updated": sum(1 for r in results if r.get("changes") and not opts.dry_run),
            "dry_run": opts.dry_run,
        }

    async def standardize_metadata(
        self,
        library_path: str,
        book_ids: list[str] | None = None,
        options: dict | None = None,
    ) -> dict:
        """Standardize metadata across books according to specified rules."""
        from calibre_plugins.calibremcp.storage.local import LocalStorage

        storage = LocalStorage(library_path)
        opts = MetadataStandardizationOptions(**(options or {}))

        if book_ids is None:
            # Get all book IDs if none specified
            books = await storage.get_all_books()
            book_ids = [book["id"] for book in books if "id" in book]

        results = []

        for book_id in book_ids:
            result = {
                "book_id": book_id,
                "changes": {},
                "warnings": [],
                "errors": [],
                "success": True,
            }

            try:
                book = await storage.get_book(book_id)
                if not book:
                    result["errors"].append("Book not found")
                    result["success"] = False
                    results.append(result)
                    continue

                book.copy()

                # Standardize title
                if "title" in book and book["title"]:
                    new_title = book["title"]

                    if opts.title_case:
                        new_title = self._title_case(new_title)

                    if opts.title_remove_series and "series" in book and book["series"]:
                        # Remove series name from title if present
                        series_pattern = re.compile(
                            rf"\s*\(?i:{re.escape(book['series'])}[^)]*\)", re.IGNORECASE
                        )
                        new_title = series_pattern.sub("", new_title).strip()

                    if opts.remove_special_chars:
                        new_title = self._remove_special_chars(new_title)

                    if opts.normalize_unicode:
                        new_title = unicodedata.normalize("NFKC", new_title)

                    if new_title != book["title"]:
                        result["changes"]["title"] = {"old": book["title"], "new": new_title}
                        book["title"] = new_title

                # Standardize authors
                if "authors" in book and book["authors"]:
                    new_authors = []

                    for author in book["authors"]:
                        if not author:
                            continue

                        # Clean up author name
                        clean_author = author.strip()

                        if opts.author_invert_names:
                            # Simple inversion of "Last, First" to "First Last"
                            if "," in clean_author:
                                parts = [p.strip() for p in clean_author.split(",", 1)]
                                if len(parts) == 2:
                                    clean_author = f"{parts[1]} {parts[0]}"

                        if opts.remove_special_chars:
                            clean_author = self._remove_special_chars(clean_author)

                        if opts.normalize_unicode:
                            clean_author = unicodedata.normalize("NFKC", clean_author)

                        new_authors.append(clean_author)

                    # Remove duplicates while preserving order
                    seen = set()
                    new_authors = [a for a in new_authors if not (a in seen or seen.add(a))]

                    if new_authors != book["authors"]:
                        result["changes"]["authors"] = {"old": book["authors"], "new": new_authors}
                        book["authors"] = new_authors

                # Standardize series
                if "series" in book and book["series"]:
                    clean_series = book["series"].strip()

                    if opts.remove_special_chars:
                        clean_series = self._remove_special_chars(clean_series)

                    if opts.normalize_unicode:
                        clean_series = unicodedata.normalize("NFKC", clean_series)

                    if clean_series != book["series"]:
                        result["changes"]["series"] = {"old": book["series"], "new": clean_series}
                        book["series"] = clean_series

                # Standardize tags
                if "tags" in book and book["tags"]:
                    new_tags = []

                    for tag in book["tags"]:
                        if not tag:
                            continue

                        clean_tag = tag.strip()

                        if opts.remove_special_chars:
                            clean_tag = self._remove_special_chars(clean_tag)

                        if opts.normalize_unicode:
                            clean_tag = unicodedata.normalize("NFKC", clean_tag)

                        # Convert to title case (first letter of each word)
                        clean_tag = " ".join(word.capitalize() for word in clean_tag.split())

                        new_tags.append(clean_tag)

                    # Remove duplicates while preserving order
                    seen = set()
                    new_tags = [t for t in new_tags if not (t in seen or seen.add(t))]

                    if new_tags != book["tags"]:
                        result["changes"]["tags"] = {"old": book["tags"], "new": new_tags}
                        book["tags"] = new_tags

                # Standardize publisher
                if "publisher" in book and book["publisher"]:
                    clean_publisher = book["publisher"].strip()

                    if opts.remove_special_chars:
                        clean_publisher = self._remove_special_chars(clean_publisher)

                    if opts.normalize_unicode:
                        clean_publisher = unicodedata.normalize("NFKC", clean_publisher)

                    # Convert to title case (first letter of each word)
                    clean_publisher = " ".join(
                        word.capitalize() for word in clean_publisher.split()
                    )

                    if clean_publisher != book["publisher"]:
                        result["changes"]["publisher"] = {
                            "old": book["publisher"],
                            "new": clean_publisher,
                        }
                        book["publisher"] = clean_publisher

                # Standardize identifiers
                if "identifiers" in book and book["identifiers"]:
                    new_identifiers = {}
                    changed = False

                    for id_type, id_value in book["identifiers"].items():
                        if not id_value:
                            continue

                        clean_id = id_value.strip()

                        # Special handling for ISBNs
                        if id_type.lower() == "isbn":
                            # Remove all non-alphanumeric characters
                            clean_id = re.sub(r"[^0-9Xx]", "", clean_id.upper())

                            # Convert ISBN-10 to ISBN-13 if requested
                            if opts.isbn_convert_to_13 and len(clean_id) == 10:
                                clean_id = self._convert_isbn10_to_isbn13(clean_id)

                            # Validate ISBN if requested
                            if opts.isbn_validate and not self._is_valid_isbn(clean_id):
                                result["warnings"].append(f"Invalid ISBN: {clean_id}")
                                # Keep the invalid ISBN but don't modify it
                                clean_id = id_value

                        new_identifiers[id_type] = clean_id

                        if clean_id != id_value:
                            changed = True

                    if changed:
                        result["changes"]["identifiers"] = {
                            "old": book["identifiers"],
                            "new": new_identifiers,
                        }
                        book["identifiers"] = new_identifiers

                # Save changes if any were made
                if result.get("changes"):
                    if not opts.dry_run:
                        await storage.update_book(book_id, book)
                else:
                    result["message"] = "No changes needed"

            except Exception as e:
                self.logger.error(
                    f"Error standardizing metadata for book {book_id}: {str(e)}", exc_info=True
                )
                result["errors"].append(f"Error: {str(e)}")
                result["success"] = False

            results.append(result)

        return {
            "success": True,
            "results": results,
            "total_books": len(results),
            "books_updated": sum(1 for r in results if r.get("changes") and not opts.dry_run),
            "dry_run": opts.dry_run,
        }

    # Helper Methods
    async def _enhance_title(
        self, book: dict, result: MetadataEnhancementResult, options: MetadataEnhancementOptions
    ) -> bool:
        """Enhance book title metadata."""
        # This is a placeholder for actual title enhancement logic
        # In a real implementation, this would query external sources
        return False

    async def _enhance_authors(
        self, book: dict, result: MetadataEnhancementResult, options: MetadataEnhancementOptions
    ) -> bool:
        """Enhance author metadata."""
        # This is a placeholder for actual author enhancement logic
        return False

    async def _enhance_series(
        self, book: dict, result: MetadataEnhancementResult, options: MetadataEnhancementOptions
    ) -> bool:
        """Enhance series metadata."""
        # This is a placeholder for actual series enhancement logic
        return False

    async def _enhance_publisher(
        self, book: dict, result: MetadataEnhancementResult, options: MetadataEnhancementOptions
    ) -> bool:
        """Enhance publisher metadata."""
        # This is a placeholder for actual publisher enhancement logic
        return False

    async def _enhance_identifiers(
        self, book: dict, result: MetadataEnhancementResult, options: MetadataEnhancementOptions
    ) -> bool:
        """Enhance book identifiers (ISBN, etc.)."""
        # This is a placeholder for actual identifier enhancement logic
        return False

    async def _enhance_tags(
        self, book: dict, result: MetadataEnhancementResult, options: MetadataEnhancementOptions
    ) -> bool:
        """Enhance book tags."""
        # This is a placeholder for actual tag enhancement logic
        return False

    async def _enhance_cover(
        self, book: dict, result: MetadataEnhancementResult, options: MetadataEnhancementOptions
    ) -> bool:
        """Enhance book cover."""
        # This is a placeholder for actual cover enhancement logic
        return False

    async def _backup_book_metadata(self, storage, book: dict) -> bool:
        """Create a backup of the book's metadata."""
        # This is a placeholder for actual backup logic
        return True

    def _load_default_metadata_sources(self) -> list[MetadataSource]:
        """Load default metadata sources."""
        return [
            MetadataSource(
                name="calibre", priority=0, enabled=True, config={"prefer_embedded_metadata": True}
            )
        ]

    def _title_case(self, text: str) -> str:
        """Convert text to title case with proper handling of small words."""
        if not text:
            return text

        # List of small words to keep lowercase unless they're the first/last word
        small_words = {
            "a",
            "an",
            "and",
            "as",
            "at",
            "but",
            "by",
            "for",
            "if",
            "in",
            "of",
            "on",
            "or",
            "the",
            "to",
            "with",
            "vs",
            "vs.",
            "v",
            "v.",
        }

        words = text.split()
        if not words:
            return text

        # Always capitalize the first and last words
        result = [words[0].capitalize()]

        for word in words[1:-1]:
            lower_word = word.lower()
            if lower_word in small_words:
                result.append(lower_word)
            else:
                result.append(word.capitalize())

        # Handle the last word
        if len(words) > 1:
            result.append(words[-1].capitalize())

        return " ".join(result)

    def _remove_special_chars(self, text: str, keep: str = "-' ") -> str:
        """Remove special characters from text, keeping only letters, numbers, and specified characters."""
        if not text:
            return text

        # Keep letters, numbers, and specified characters
        allowed = f"{string.ascii_letters}{string.digits}{keep}"
        return "".join(c for c in text if c in allowed or c.isspace()).strip()

    def _convert_isbn10_to_isbn13(self, isbn10: str) -> str:
        """Convert an ISBN-10 to ISBN-13."""
        if (
            len(isbn10) != 10
            or not isbn10[:-1].isdigit()
            or not (isbn10[-1].isdigit() or isbn10[-1].upper() == "X")
        ):
            return isbn10  # Not a valid ISBN-10, return as-is

        # Convert to ISBN-13 by prefixing with 978 and removing the old check digit
        isbn12 = "978" + isbn10[:-1]

        # Calculate the check digit for ISBN-13
        total = 0
        for i, c in enumerate(isbn12):
            digit = int(c)
            # Multiply by 1 or 3 based on position (1-based index)
            total += digit * (1 if i % 2 == 0 else 3)

        check_digit = (10 - (total % 10)) % 10
        return f"{isbn12}{check_digit}"

    def _is_valid_isbn(self, isbn: str) -> bool:
        """Check if a string is a valid ISBN-10 or ISBN-13."""
        if not isbn:
            return False

        isbn = isbn.upper()

        # Check ISBN-10
        if len(isbn) == 10:
            if not (isbn[:-1].isdigit() and (isbn[-1].isdigit() or isbn[-1] == "X")):
                return False

            total = 0
            for i, c in enumerate(isbn):
                if i < 9:
                    total += int(c) * (10 - i)
                else:
                    total += 10 if c == "X" else int(c)

            return total % 11 == 0

        # Check ISBN-13
        elif len(isbn) == 13 and isbn.isdigit():
            total = 0
            for i, c in enumerate(isbn):
                digit = int(c)
                # Multiply by 1 or 3 based on position (1-based index)
                total += digit * (1 if i % 2 == 0 else 3)

            return total % 10 == 0

        return False
