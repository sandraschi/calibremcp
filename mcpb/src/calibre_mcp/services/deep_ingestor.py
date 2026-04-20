import logging
from pathlib import Path
from typing import Any

import ebooklib
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from ebooklib import epub

from calibre_mcp.rag.lancedb_vector_store import LanceVectorStore

logger = logging.getLogger(__name__)


class DeepIngestor:
    """Ingests full text from books into a separate LanceDB table.

    This splits EPUB and PDF files into manageable chunks for semantic searching
    deep within the text of the library.
    """

    def __init__(self, vector_store: LanceVectorStore) -> None:
        """
        Initialize the Deep Ingestor.

        Args:
            vector_store: LanceDB store (table ``calibre_fulltext``).
        """
        self.vector_store = vector_store
        # Target table name for full-text RAG
        self.table_name = "calibre_fulltext"

        # Ensure the vector store is pointing to the correct table
        self.vector_store.table_name = self.table_name

        self.chunk_size = 1000  # roughly 1000 chars per chunk
        self.chunk_overlap = 200

    def chunk_text(self, text: str) -> list[str]:
        """Simple character-based chunking with overlap."""
        chunks = []
        i = 0
        while i < len(text):
            chunks.append(text[i : i + self.chunk_size])
            i += self.chunk_size - self.chunk_overlap
        return chunks

    def parse_epub(self, file_path: str) -> list[dict[str, Any]]:
        """Parse EPUB chapters using ebooklib and BeautifulSoup."""
        book = epub.read_epub(file_path)
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

        extracted = []
        for i, item in enumerate(items):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text(separator="\n").strip()
            if text:
                extracted.append({"location": f"Chapter {i + 1}", "text": text})
        return extracted

    def parse_pdf(self, file_path: str) -> list[dict[str, Any]]:
        """Parse PDF pages using PyMuPDF (fitz)."""
        doc = fitz.open(file_path)
        extracted = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                extracted.append({"location": f"Page {page_num + 1}", "text": text})
        return extracted

    async def ingest_book_fulltext(
        self, book_id: str, title: str, file_path: str
    ) -> dict[str, Any]:
        """
        Extract and index the full text of a given book.

        Args:
            book_id: Calibre book ID
            title: Title of the book
            file_path: Absolute path to the EPUB/PDF file

        Returns:
            Dictionary with ingestion statistics or error status.
        """
        logger.info(f"Starting deep ingestion for '{title}' (ID: {book_id})")
        path = Path(file_path)
        if not path.exists():
            return {"status": "error", "error": f"File not found: {file_path}"}

        extracted_sections = []
        try:
            if path.suffix.lower() == ".epub":
                extracted_sections = self.parse_epub(str(path))
            elif path.suffix.lower() == ".pdf":
                extracted_sections = self.parse_pdf(str(path))
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported format for deep ingestion: {path.suffix}",
                }
        except Exception as e:
            logger.exception(f"Failed to parse {file_path}: {e}")
            return {"status": "error", "error": str(e)}

        documents = []
        chunk_index = 0
        for section in extracted_sections:
            chunks = self.chunk_text(section["text"])
            for chunk in chunks:
                doc = {
                    "id": f"calibre-deep-{book_id}-{chunk_index}",
                    "content": f"Book: {title}\nLocation: {section['location']}\n\n{chunk}",
                    "metadata": {
                        "source": "calibre_fulltext",
                        "book_id": book_id,
                        "title": title,
                        "location": section["location"],
                        "chunk_index": chunk_index,
                    },
                }
                documents.append(doc)
                chunk_index += 1

        if not documents:
            logger.warning(f"No text extracted for '{title}'")
            return {"status": "success", "count": 0, "message": "No text extracted"}

        try:
            self.vector_store.add_documents(documents, overwrite=False)
            logger.info(
                f"Successfully deep-ingested {len(documents)} chunks for '{title}' into {self.table_name}"
            )
            return {
                "status": "success",
                "count": len(documents),
                "message": f"Ingested {len(documents)} chunks",
            }
        except Exception as e:
            logger.exception(f"Failed to ingest fulltext chunks: {e}")
            return {"status": "error", "error": str(e)}
