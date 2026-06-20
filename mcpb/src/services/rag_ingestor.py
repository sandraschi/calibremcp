import logging
import sqlite3
from typing import Any

from calibre_mcp.rag.lancedb_vector_store import LanceVectorStore

logger = logging.getLogger(__name__)


class CalibreIngestor:
    """Ingests Calibre library metadata into the LanceDB Vector Store."""

    def __init__(self, db_path: str, vector_store: LanceVectorStore) -> None:
        """
        Initialize the Calibre Ingestor.

        Args:
            db_path: Path to the Calibre metadata.db SQLite file.
            vector_store: LanceDB store (table ``calibre_media``).
        """
        self.db_path = db_path
        self.vector_store = vector_store

        # Table name for this specific data source
        self.table_name = "calibre_media"

    def _get_db_connection(self) -> sqlite3.Connection:
        """Get a read-only connection to the Calibre metadata.db."""
        uri = f"file:{self.db_path}?mode=ro"
        return sqlite3.connect(uri, uri=True)

    def extract_books(self) -> list[dict[str, Any]]:
        """
        Extract book metadata from the Calibre database.

        Returns:
            List of dictionaries containing book metadata.
        """
        books = []
        try:
            with self._get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Query to get essential book metadata
                query = """
                SELECT
                    b.id,
                    b.title,
                    b.author_sort as text_authors,
                    b.timestamp,
                    b.last_modified,
                    b.path,
                    b.series_index,
                    (SELECT name FROM series WHERE id = (SELECT series FROM books_series_link WHERE book = b.id)) as series,
                    (SELECT text FROM comments WHERE book = b.id) as blurbs
                FROM books b
                """

                cursor.execute(query)
                rows = cursor.fetchall()

                for row in rows:
                    book_id = row["id"]

                    # Fetch tags for the book
                    cursor.execute(
                        """
                        SELECT t.name
                        FROM tags t
                        JOIN books_tags_link btl ON t.id = btl.tag
                        WHERE btl.book = ?
                    """,
                        (book_id,),
                    )
                    tags = [t["name"] for t in cursor.fetchall()]

                    # Prepare the content string for embedding
                    title = row["title"] or ""
                    authors = row["text_authors"] or ""
                    series = row["series"] or ""
                    comments = row["blurbs"] or ""

                    content_parts = [f"Title: {title}", f"Author: {authors}"]
                    if series:
                        content_parts.append(f"Series: {series} (Index: {row['series_index']})")
                    if tags:
                        content_parts.append(f"Tags: {', '.join(tags)}")
                    if comments:
                        content_parts.append(f"Synopsis/Comments: {comments}")

                    content = "\n".join(content_parts)

                    books.append(
                        {
                            "id": f"calibre-{book_id}",
                            "title": title,
                            "content": content,
                            "metadata": {
                                "source": "calibre",
                                "book_id": book_id,
                                "title": title,
                                "authors": authors,
                                "series": series,
                                "tags": tags,
                                "library_path": self.db_path,
                                "book_path": row["path"],
                                "last_modified": row["last_modified"],
                            },
                        }
                    )

        except sqlite3.Error as e:
            logger.exception(f"Database error while extracting books: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error while extracting books: {e}")

        return books

    async def ingest_library(self) -> dict[str, Any]:
        """
        Extract all books and index them into the LanceDB vector store.

        Returns:
            Dictionary with ingestion statistics.
        """
        logger.info(f"Starting ingestion from {self.db_path}...")
        books = self.extract_books()

        if not books:
            logger.warning("No books extracted from Calibre database.")
            return {"status": "success", "count": 0, "message": "No books found"}

        logger.info(f"Extracted {len(books)} books. Preparing to index...")

        documents = []
        for b in books:
            doc = {"id": b["id"], "content": b["content"], "metadata": b["metadata"]}
            documents.append(doc)

        try:
            self.vector_store.add_documents(documents)
            logger.info(f"Successfully ingested {len(documents)} books into '{self.table_name}'")
            return {"status": "success", "count": len(documents)}
        except Exception as e:
            logger.exception(f"Failed to ingest library: {e}")
            return {"status": "error", "error": str(e)}
