"""
Utility functions for Calibre MCP server.
"""

import mimetypes
import os
import tempfile

try:
    import magic
except ImportError:
    magic = None  # Optional dependency
import hashlib
from pathlib import Path

# Optional dependencies - imported only when needed
try:
    import aiofiles

    try:
        import aiofiles.os
    except AttributeError:
        # Windows compatibility: aiofiles.os fails on Windows due to missing statvfs
        # We still have aiofiles for file operations, just not aiofiles.os
        pass
except ImportError:
    aiofiles = None  # Optional dependency

try:
    from io import BytesIO

    from PIL import Image, ImageOps
except ImportError:
    Image = None  # Optional dependency

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # Optional dependency

try:
    from ebooklib import epub
except ImportError:
    epub = None  # Optional dependency

try:
    from calibre.ebooks.conversion import initialize_converters
    from calibre.ebooks.metadata import get_metadata
except ImportError:
    get_metadata = None
    initialize_converters = None  # Optional dependency

# Only initialize converters if available
if initialize_converters is not None:
    initialize_converters()

# Import models with error handling
try:
    # Try importing from models.py (flat structure)
    from ..models import BookFormat, BookIdentifier, BookMetadata  # type: ignore
except ImportError:
    try:
        # Try importing from models package
        from .models import BookFormat, BookIdentifier, BookMetadata  # type: ignore
    except ImportError:
        # Models not available - define minimal types
        from enum import Enum

        class BookFormat(Enum):  # type: ignore
            EPUB = "epub"
            PDF = "pdf"

        BookMetadata = None  # type: ignore
        BookIdentifier = None  # type: ignore

# Configure MIME type detection
if magic is not None:
    mime = magic.Magic(mime=True)
else:
    mime = None  # Fallback to mimetypes module

# Add custom MIME type mappings
mimetypes.add_type("application/x-cbz", ".cbz")
mimetypes.add_type("application/x-cbr", ".cbr")
mimetypes.add_type("application/x-mobi", ".mobi")
mimetypes.add_type("application/x-azw3", ".azw3")


class FileTypeNotSupportedError(Exception):
    """Raised when a file type is not supported."""

    pass


class FileProcessingError(Exception):
    """Raised when there is an error processing a file."""

    pass


async def detect_file_type(file_path: str | Path) -> tuple[str, str]:
    """
    Detect the MIME type and file extension of a file.

    Args:
        file_path: Path to the file.

    Returns:
        Tuple of (mime_type, extension).

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.is_file():
        raise FileProcessingError(f"Not a file: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read file: {file_path}")

    # Get MIME type using python-magic or fallback to mimetypes
    if mime is not None:
        mime_type = mime.from_file(str(file_path))
    else:
        # Fallback to mimetypes module
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"

    # Get file extension
    extension = file_path.suffix.lower()
    if not extension and mime_type:
        # Try to get extension from MIME type
        extensions = mimetypes.guess_all_extensions(mime_type)
        extension = extensions[0] if extensions else ""

    return mime_type, extension


def get_book_format_from_extension(extension: str) -> BookFormat:
    """
    Get the book format from a file extension.

    Args:
        extension: File extension (with or without leading dot).

    Returns:
        BookFormat enum value.

    Raises:
        FileTypeNotSupportedError: If the extension is not a supported book format.
    """
    # Remove leading dot if present
    extension = extension.lstrip(".").lower()

    # Map extensions to BookFormat
    extension_map = {
        "epub": BookFormat.EPUB,
        "pdf": BookFormat.PDF,
        "mobi": BookFormat.MOBI,
        "azw3": BookFormat.AZW3,
        "cbz": BookFormat.CBZ,
        "cbr": BookFormat.CBR,
        "docx": BookFormat.DOCX,
        "fb2": BookFormat.FB2,
        "html": BookFormat.HTML,
        "lit": BookFormat.LIT,
        "lrf": BookFormat.LRF,
        "odt": BookFormat.ODT,
        "pdb": BookFormat.PDB,
        "pml": BookFormat.PML,
        "rb": BookFormat.RB,
        "rtf": BookFormat.RTF,
        "snb": BookFormat.SNB,
        "tcr": BookFormat.TCR,
        "txt": BookFormat.TXT,
        "txtz": BookFormat.TXTZ,
    }

    try:
        return extension_map[extension]
    except KeyError:
        raise FileTypeNotSupportedError(f"Unsupported book format: {extension}")


async def extract_metadata(file_path: str | Path) -> BookMetadata:
    """
    Extract metadata from a book file.

    Args:
        file_path: Path to the book file.

    Returns:
        BookMetadata object with extracted metadata.

    Raises:
        FileProcessingError: If there is an error extracting metadata.
    """
    file_path = Path(file_path)

    # Get file format
    try:
        _, extension = await detect_file_type(file_path)
        book_format = get_book_format_from_extension(extension)
    except (FileTypeNotSupportedError, FileNotFoundError, PermissionError) as e:
        raise FileProcessingError(f"Cannot process file {file_path}: {e}")

    # Initialize metadata with default values
    metadata = BookMetadata(
        title=file_path.stem,
        formats=[book_format],
    )

    try:
        # Extract metadata using Calibre
        with open(file_path, "rb") as f:
            calibre_metadata = get_metadata(f, mime_type=None, use_libprs_metadata=True)

        # Map Calibre metadata to our model
        if calibre_metadata.title:
            metadata.title = calibre_metadata.title

        if calibre_metadata.authors:
            metadata.authors = calibre_metadata.authors

        if calibre_metadata.publisher:
            metadata.publisher = calibre_metadata.publisher

        if calibre_metadata.pubdate:
            metadata.pubdate = calibre_metadata.pubdate.date()

        if calibre_metadata.series:
            metadata.series = calibre_metadata.series

        if calibre_metadata.series_index is not None:
            metadata.series_index = float(calibre_metadata.series_index)

        if calibre_metadata.rating is not None:
            metadata.rating = (
                float(calibre_metadata.rating) / 2.0
            )  # Convert from 10-point to 5-point scale

        if calibre_metadata.tags:
            metadata.tags = list(calibre_metadata.tags)

        if calibre_metadata.comments:
            metadata.description = calibre_metadata.comments

        # Extract identifiers (ISBN, etc.)
        if calibre_metadata.identifiers:
            for id_type, id_value in calibre_metadata.identifiers.items():
                if id_type and id_value:
                    metadata.identifiers.append(BookIdentifier(type=id_type, value=id_value))

        # Extract language
        if calibre_metadata.language:
            metadata.languages = [calibre_metadata.language]

        # Get file size
        metadata.size = file_path.stat().st_size

    except Exception:
        # If metadata extraction fails, just use the filename as title
        metadata.title = file_path.stem
        metadata.size = file_path.stat().st_size

    return metadata


async def generate_thumbnail(
    file_path: str | Path,
    size: tuple[int, int] = (200, 300),
    output_path: str | Path | None = None,
) -> Path | None:
    """
    Generate a thumbnail for a book.

    Args:
        file_path: Path to the book file.
        size: Size of the thumbnail as (width, height).
        output_path: Path to save the thumbnail. If None, a temporary file will be created.

    Returns:
        Path to the generated thumbnail, or None if no thumbnail could be generated.
    """
    file_path = Path(file_path)

    # Create output directory if it doesn't exist
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Create a temporary file
        temp_dir = Path(tempfile.mkdtemp(prefix="calibremcp_thumbnails_"))
        output_path = temp_dir / f"{file_path.stem}_thumb.jpg"

    try:
        # Get file format
        _, extension = await detect_file_type(file_path)
        book_format = get_book_format_from_extension(extension)

        if book_format in [BookFormat.PDF, BookFormat.CBZ, BookFormat.CBR]:
            # Handle PDF and comic book formats with PyMuPDF
            doc = fitz.open(str(file_path))
            if doc.page_count > 0:
                page = doc[0]
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img = ImageOps.pad(img, size, color="white")
                img.save(output_path, "JPEG", quality=85)
                return output_path

        elif book_format == BookFormat.EPUB:
            # Handle EPUB with EbookLib
            book = epub.read_epub(str(file_path))
            for item in book.get_items_of_type(epub.ITEM_IMAGE):
                if "cover" in item.get_name().lower() or "title" in item.get_name().lower():
                    img = Image.open(BytesIO(item.get_content()))
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    img = ImageOps.pad(img, size, color="white")
                    img.save(output_path, "JPEG", quality=85)
                    return output_path

        # If we get here, no thumbnail could be generated
        return None

    except Exception as e:
        # Log the error and return None
        import logging

        logging.warning(f"Failed to generate thumbnail for {file_path}: {e}")
        return None


async def convert_book(
    input_path: str | Path,
    output_format: BookFormat,
    output_path: str | Path | None = None,
    metadata: BookMetadata | None = None,
) -> Path:
    """
    Convert a book to another format.

    Args:
        input_path: Path to the input book file.
        output_format: Desired output format.
        output_path: Path to save the converted file. If None, a temporary file will be created.
        metadata: Optional metadata to embed in the converted file.

    Returns:
        Path to the converted file.

    Raises:
        FileProcessingError: If the conversion fails.
    """
    input_path = Path(input_path)

    # Create output directory if it doesn't exist
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Create a temporary file
        temp_dir = Path(tempfile.mkdtemp(prefix="calibremcp_converted_"))
        output_path = temp_dir / f"{input_path.stem}.{output_format.value}"

    try:
        # Use Calibre's conversion API
        from calibre.ebooks.conversion.cli import main as convert_cli

        # Prepare command line arguments for the converter
        args = [
            str(input_path),
            str(output_path),
            "--output-profile",
            "tablet",
            "--enable-heuristics",
        ]

        # Add metadata if provided
        if metadata:
            if metadata.title:
                args.extend(["--title", metadata.title])
            if metadata.authors:
                args.extend(["--authors", " & ".join(metadata.authors)])
            if metadata.publisher:
                args.extend(["--publisher", metadata.publisher])
            if metadata.tags:
                args.extend(["--tags", ",".join(metadata.tags)])
            if metadata.description:
                args.extend(["--comments", metadata.description])
            if metadata.series:
                args.extend(["--series", metadata.series])
            if metadata.series_index is not None:
                args.extend(["--series-index", str(metadata.series_index)])
            if metadata.rating is not None:
                args.extend(
                    ["--rating", str(int(metadata.rating * 2))]
                )  # Convert from 5-point to 10-point scale

        # Run the conversion
        convert_cli(args)

        # Verify the output file was created
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise FileProcessingError("Conversion failed: output file not created or empty")

        return output_path

    except Exception as e:
        # Clean up the output file if it was created but is invalid
        if output_path.exists():
            try:
                output_path.unlink()
            except OSError:
                pass
        raise FileProcessingError(f"Failed to convert {input_path} to {output_format.value}: {e}")


async def calculate_file_hash(file_path: str | Path, algorithm: str = "sha256") -> str:
    """
    Calculate the hash of a file.

    Args:
        file_path: Path to the file.
        algorithm: Hash algorithm to use (default: 'sha256').

    Returns:
        Hexadecimal string representation of the hash.
    """
    file_path = Path(file_path)
    hash_func = hashlib.new(algorithm)

    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(65536):  # 64KB chunks
            hash_func.update(chunk)

    return hash_func.hexdigest()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: The filename to sanitize.

    Returns:
        Sanitized filename.
    """
    # Replace invalid characters with underscore
    invalid_chars = '<>:"/\\|?*\0' + "".join(chr(i) for i in range(32))
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing spaces and dots
    filename = filename.strip(". ")

    # Ensure the filename is not empty
    if not filename:
        filename = "unnamed_file"

    # Truncate if too long (max 255 characters)
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        ext = ext[:10]  # Limit extension length
        name = name[: (max_length - len(ext) - 1)]
        filename = f"{name}{ext}"

    return filename
