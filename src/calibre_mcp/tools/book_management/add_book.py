"""
Add Book Tool

This module provides functionality to add new books to the Calibre library.
Uses calibredb CLI to properly integrate with Calibre's directory structure and database.
"""

import asyncio
import shutil
from pathlib import Path
from typing import Any

from ...config import CalibreConfig
from ...logging_config import get_logger
from ...server import current_library
from ...tools.compat import MCPServerError

logger = get_logger("calibremcp.tools.book_management")


def _find_calibredb() -> str | None:
    """
    Find calibredb executable in PATH.

    Returns:
        Path to calibredb executable or None if not found
    """
    calibredb_names = ["calibredb", "calibredb.exe"]

    for name in calibredb_names:
        calibredb_path = shutil.which(name)
        if calibredb_path:
            logger.debug(f"Found calibredb at: {calibredb_path}")
            return calibredb_path

    logger.warning("calibredb not found in PATH")
    return None


_ADD_TIMEOUT_SECONDS = 180

# calibredb stderr markers meaning "another program holds the library"
# (GUI / calibre-server). In that case --library-path always fails and the
# only supported route is --with-library against the content server.
_LIBRARY_LOCK_MARKERS = (
    "another calibre program",
    "is running",
    "database is locked",
    "could not lock",
)


def _content_server_target() -> tuple[str | None, str | None, str | None]:
    """Content-server URL + credentials from config (.env).

    Returns (url, username, password); url is None when not configured.
    """
    try:
        config = CalibreConfig.load_config()
        url = (config.server_url or "").rstrip("/")
        if not url:
            return None, None, None
        return url, config.username, config.password
    except Exception as e:
        logger.debug(f"Could not load content-server config: {e}")
        return None, None, None


async def _run_calibredb_add(cmd: list[str]) -> tuple[int, str, str]:
    """Run one calibredb add invocation. Returns (returncode, stdout, stderr)."""
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=_ADD_TIMEOUT_SECONDS)
    except TimeoutError as e:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        raise MCPServerError(
            f"calibredb add timed out after {_ADD_TIMEOUT_SECONDS}s. "
            "The library may be on a slow/network drive or under heavy load."
        ) from e
    return (
        process.returncode or 0,
        stdout.decode("utf-8", errors="replace") if stdout else "",
        stderr.decode("utf-8", errors="replace") if stderr else "",
    )


def _get_library_path(library_path: str | None = None) -> Path:
    """
    Get the active Calibre library path.

    Args:
        library_path: Optional explicit library path

    Returns:
        Path to the Calibre library directory

    Raises:
        MCPServerError: If library path cannot be determined
    """

    config = CalibreConfig.load_config()

    # Priority: 1) explicit library_path, 2) config.local_library_path, 3) discovered libraries
    if library_path:
        lib_path = Path(library_path)
        if lib_path.exists() and (lib_path / "metadata.db").exists():
            return lib_path
        raise MCPServerError(f"Invalid library path: {library_path} (metadata.db not found)")

    if config.local_library_path and (config.local_library_path / "metadata.db").exists():
        return config.local_library_path

    # Try to find library from discovered libraries
    if config.discovered_libraries:
        # Use current_library if available, otherwise use first discovered
        library_name = (
            current_library
            if current_library in config.discovered_libraries
            else list(config.discovered_libraries.keys())[0]
        )
        lib_info = config.discovered_libraries[library_name]
        lib_path = Path(lib_info.path)
        if lib_path.exists() and (lib_path / "metadata.db").exists():
            return lib_path

    raise MCPServerError(
        "Cannot determine library path. Please specify library_path parameter or configure a library in CalibreConfig."
    )


async def add_book_helper(
    file_path: str,
    metadata: dict[str, Any] | None = None,
    fetch_metadata: bool = True,
    convert_to: str | None = None,
    library_path: str | None = None,
) -> dict[str, Any]:
    """
    Add a new book to the Calibre library using calibredb CLI.

    This function uses Calibre's calibredb command-line tool to properly:
    - Create Calibre's directory structure: {author_sort}/{title} ({id})/
    - Move the book file into the proper location
    - Write database entries to metadata.db
    - Extract and store metadata

    Args:
        file_path: Path to the book file to add
        metadata: Optional metadata to override extracted metadata
        fetch_metadata: Whether to fetch metadata from online sources (default: True)
        convert_to: Convert the book to this format before adding (optional)
        library_path: Path to the Calibre library (optional, auto-detected if not provided)

    Returns:
        Dictionary containing the added book's information with:
        - id: Book ID assigned by Calibre
        - title: Book title
        - authors: List of authors
        - formats: List of available formats
        - cover_url: URL to cover image (if available)
        - status: Reading status
        - progress: Reading progress (0.0-1.0)
        - date_added: ISO timestamp when book was added

    Raises:
        MCPServerError: If there's an error adding the book
    """
    try:
        # Validate input file
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise MCPServerError(f"File not found: {file_path}")

        if not file_path_obj.is_file():
            raise MCPServerError(f"Path is not a file: {file_path}")

        # Get library path
        lib_path = _get_library_path(library_path)
        logger.info(f"Adding book to library: {lib_path}")

        # Find calibredb executable
        calibredb = _find_calibredb()
        if not calibredb:
            raise MCPServerError(
                "calibredb not found in PATH. Please install Calibre and ensure calibredb is available. "
                "See: https://calibre-ebook.com/download"
            )

        # Shared add arguments (file + metadata flags). The library selector
        # (--library-path vs --with-library) is appended per route below.
        cmd = [
            calibredb,
            "add",
            str(file_path_obj),
            "--duplicates",  # Allow duplicates (Calibre will handle deduplication)
        ]

        # Add metadata overrides if provided
        if metadata:
            if "title" in metadata and metadata["title"]:
                cmd.extend(["--title", str(metadata["title"])])
            if "authors" in metadata and metadata["authors"]:
                # Calibre expects comma-separated authors
                authors_str = (
                    ", ".join(metadata["authors"])
                    if isinstance(metadata["authors"], list)
                    else str(metadata["authors"])
                )
                cmd.extend(["--authors", authors_str])
            if "tags" in metadata and metadata["tags"]:
                tags_str = ", ".join(metadata["tags"]) if isinstance(metadata["tags"], list) else str(metadata["tags"])
                cmd.extend(["--tags", tags_str])
            if "series" in metadata and metadata["series"]:
                cmd.extend(["--series", str(metadata["series"])])
            if "series_index" in metadata and metadata["series_index"] is not None:
                cmd.extend(["--series-index", str(metadata["series_index"])])
            if "publisher" in metadata and metadata["publisher"]:
                cmd.extend(["--publisher", str(metadata["publisher"])])
            if "rating" in metadata and metadata["rating"] is not None:
                cmd.extend(["--rating", str(metadata["rating"])])
            if "isbn" in metadata and metadata["isbn"]:
                cmd.extend(["--isbn", str(metadata["isbn"])])
            if "languages" in metadata and metadata["languages"]:
                lang_str = (
                    ", ".join(metadata["languages"])
                    if isinstance(metadata["languages"], list)
                    else str(metadata["languages"])
                )
                cmd.extend(["--languages", lang_str])

        # Disable metadata fetching if requested
        if not fetch_metadata:
            cmd.append("--dont-download-cover")
            cmd.append("--dont-read-metadata")

        # Add format conversion if requested
        if convert_to:
            cmd.extend(["--convert", convert_to.upper()])

        via = "direct"
        logger.debug(f"Executing calibredb command: {' '.join([*cmd, '--library-path', str(lib_path)])}")

        # Route 1: direct --library-path (fast; fails while the GUI/server
        # holds the library).
        returncode, stdout, stderr = await _run_calibredb_add([*cmd, "--library-path", str(lib_path)])

        if returncode != 0 and any(m in stderr.lower() for m in _LIBRARY_LOCK_MARKERS):
            # Route 2: content server (--with-library). This is the only
            # supported route while the GUI holds the library open.
            server_url, username, password = _content_server_target()
            if not server_url:
                logger.error(f"calibredb add failed (library locked, no content server configured): {stderr}")
                raise MCPServerError(
                    "Failed to add book: library is locked by another Calibre program and no "
                    "content server is configured. Set CALIBRE_SERVER_URL (plus CALIBRE_USERNAME/ "
                    f"CALIBRE_PASSWORD if the server needs auth). calibredb said: {stderr or 'Unknown error'}"
                )
            server_cmd = [calibredb, "--with-library", server_url]
            if username:
                server_cmd += ["--username", username]
            if password:
                server_cmd += ["--password", password]
            logger.info(f"Library locked by running Calibre; retrying add via content server {server_url}")
            via = "content_server"
            returncode, stdout, stderr = await _run_calibredb_add([*server_cmd, *cmd[1:]])

        if returncode != 0:
            error_msg = stderr or "Unknown error"
            logger.error(f"calibredb add failed with return code {returncode}: {error_msg}")
            raise MCPServerError(f"Failed to add book: {error_msg}")

        # Parse output to get book ID
        # calibredb add outputs: "Added book ids: 123" or "Added book id: 123"
        output = stdout.strip()
        logger.debug(f"calibredb output: {output}")

        # Extract book ID from output
        book_id = None
        for line in output.split("\n"):
            if "Added book id" in line or "Added book ids" in line:
                # Extract number(s) from line
                import re

                ids = re.findall(r"\d+", line)
                if ids:
                    book_id = int(ids[0])  # Use first ID if multiple
                    break

        if not book_id:
            logger.warning(f"Could not extract book ID from calibredb output: {output}")
            # Try to get the book by searching for the filename
            # This is a fallback - ideally calibredb should return the ID
            raise MCPServerError(f"Book was added but could not determine book ID. calibredb output: {output}")

        logger.info(f"Successfully added book with ID: {book_id}")

        # Retrieve the added book to return complete information
        from .get_book import get_book_helper

        try:
            book_data = await get_book_helper(
                book_id=str(book_id),
                include_metadata=True,
                include_formats=True,
                include_cover=False,
                library_path=str(lib_path),
            )

            return {
                "id": str(book_id),
                "title": book_data.get("title", "Unknown"),
                "authors": book_data.get("authors", []),
                "formats": book_data.get("formats", []),
                "cover_url": book_data.get("cover_url"),
                "status": book_data.get("status", "unread"),
                "progress": book_data.get("progress", 0.0),
                "date_added": book_data.get("timestamp"),
                "via": via,
            }
        except Exception as e:
            logger.warning(f"Could not retrieve book details after adding: {e}")
            # Return minimal response with book ID
            return {
                "id": str(book_id),
                "title": metadata.get("title", file_path_obj.stem) if metadata else file_path_obj.stem,
                "authors": metadata.get("authors", ["Unknown"]) if metadata else ["Unknown"],
                "formats": [file_path_obj.suffix[1:].upper()] if file_path_obj.suffix else [],
                "cover_url": None,
                "status": "unread",
                "progress": 0.0,
                "date_added": None,
                "via": via,
            }

    except MCPServerError:
        raise
    except Exception as e:
        logger.error(f"Error adding book: {e}", exc_info=True)
        raise MCPServerError(f"Failed to add book: {str(e)}") from e
