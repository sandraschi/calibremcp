"""
PDF viewer module for CalibreMCP.
"""

from typing import List, Dict, Any
from pathlib import Path
import base64

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # Optional dependency


class PdfViewer:
    """Viewer for PDF files."""

    SUPPORTED_FORMATS = ["pdf"]

    def __init__(self):
        self._doc = None
        self._metadata = {}
        self._current_page = 0
        self._file_path = None

    @classmethod
    def supports_format(cls, file_extension: str) -> bool:
        """Check if this viewer supports the given file format."""
        return file_extension.lower() in cls.SUPPORTED_FORMATS

    def load(self, file_path: str) -> None:
        """Load a PDF file."""
        if fitz is None:
            raise ImportError("PyMuPDF (fitz) is required for PDF viewing. Install it with: pip install PyMuPDF")
        self._file_path = Path(file_path)
        self._doc = fitz.open(file_path)
        self._extract_metadata()

    def _extract_metadata(self) -> None:
        """Extract metadata from the PDF."""
        if not self._doc:
            return

        metadata = self._doc.metadata
        self._metadata = {
            "title": metadata.get("title", "").strip() or Path(self._file_path).stem,
            "author": metadata.get("author", "").strip(),
            "subject": metadata.get("subject", "").strip(),
            "keywords": metadata.get("keywords", "").strip(),
            "creator": metadata.get("creator", "").strip(),
            "producer": metadata.get("producer", "").strip(),
            "creation_date": metadata.get("creationDate", "").strip(),
            "modification_date": metadata.get("modDate", "").strip(),
            "page_count": len(self._doc) if self._doc else 0,
        }

    def render_page(self, page_number: int = 0, zoom: float = 1.5) -> Dict[str, Any]:
        """Render a specific page of the PDF."""
        if not self._doc or page_number < 0 or page_number >= len(self._doc):
            return {
                "content": "<p>Page not found</p>",
                "total_pages": len(self._doc) if self._doc else 0,
                "current_page": page_number,
                "metadata": self._metadata,
                "error": "Page not found",
            }

        try:
            # Get the page
            page = self._doc.load_page(page_number)

            # Render to an image
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Convert to base64 for HTML display
            img_data = pix.tobytes("png")
            img_base64 = base64.b64encode(img_data).decode("utf-8")

            # Extract text if available
            text = page.get_text()

            return {
                "content": f'<img src="data:image/png;base64,{img_base64}" style="max-width: 100%;" />',
                "text": text,
                "total_pages": len(self._doc),
                "current_page": page_number,
                "metadata": self._metadata,
                "navigation": {
                    "has_prev": page_number > 0,
                    "has_next": page_number < len(self._doc) - 1,
                    "toc": self._get_toc(),
                },
            }

        except Exception as e:
            return {
                "content": f"<p>Error rendering page: {str(e)}</p>",
                "total_pages": len(self._doc) if self._doc else 0,
                "current_page": page_number,
                "metadata": self._metadata,
                "error": str(e),
            }

    def _get_toc(self) -> List[Dict[str, Any]]:
        """Get the table of contents."""
        if not self._doc:
            return []

        toc = []
        for i in range(len(self._doc)):
            toc.append({"title": f"Page {i + 1}", "page": i})
        return toc

    def search_text(self, query: str) -> List[Dict[str, Any]]:
        """Search for text in the PDF."""
        if not self._doc:
            return []

        results = []
        for page_num in range(len(self._doc)):
            page = self._doc.load_page(page_num)
            text_instances = page.search_for(query)

            for inst in text_instances:
                results.append(
                    {
                        "page": page_num,
                        "rect": [inst.x0, inst.y0, inst.x1, inst.y1],
                        "text": page.get_text("text", clip=inst).strip(),
                    }
                )

        return results

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the PDF."""
        return self._metadata

    def close(self) -> None:
        """Clean up resources."""
        if self._doc:
            self._doc.close()
            self._doc = None
        self._metadata = {}
        self._current_page = 0
        self._file_path = None
