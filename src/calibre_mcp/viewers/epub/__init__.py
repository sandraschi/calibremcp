"""
EPUB viewer module for CalibreMCP.
"""

from typing import List, Dict, Any
from pathlib import Path
import zipfile
from bs4 import BeautifulSoup


class EpubViewer:
    """Viewer for EPUB files."""

    SUPPORTED_FORMATS = ["epub"]

    def __init__(self):
        self._book_path = None
        self._zip_file = None
        self._opf_path = None
        self._spine_items = []
        self._manifest = {}
        self._metadata = {}
        self._current_page = 0

    @classmethod
    def supports_format(cls, file_extension: str) -> bool:
        """Check if this viewer supports the given file format."""
        return file_extension.lower() in cls.SUPPORTED_FORMATS

    def load(self, file_path: str) -> None:
        """Load an EPUB file."""
        self._book_path = Path(file_path)
        self._zip_file = zipfile.ZipFile(file_path, "r")
        self._parse_container()
        self._parse_opf()

    def _parse_container(self) -> None:
        """Parse the container.xml to find the OPF file."""
        container_data = self._zip_file.read("META-INF/container.xml")
        soup = BeautifulSoup(container_data, "xml")
        rootfile = soup.find("rootfile")
        if rootfile and "full-path" in rootfile.attrs:
            self._opf_path = rootfile["full-path"]

    def _parse_opf(self) -> None:
        """Parse the OPF file to get the book structure."""
        if not self._opf_path:
            raise ValueError("OPF file not found in EPUB")

        opf_data = self._zip_file.read(self._opf_path)
        opf_dir = str(Path(self._opf_path).parent) + "/"

        soup = BeautifulSoup(opf_data, "xml")

        # Parse metadata
        self._metadata = {}
        for meta in soup.find_all("meta"):
            if "name" in meta.attrs and "content" in meta.attrs:
                self._metadata[meta["name"]] = meta["content"]

        # Parse manifest
        self._manifest = {}
        manifest = soup.find("manifest")
        if manifest:
            for item in manifest.find_all("item"):
                if "id" in item.attrs and "href" in item.attrs:
                    # Make sure the path is relative to the OPF directory
                    href = item["href"]
                    if not href.startswith(("http:", "https:")):
                        href = opf_dir + href
                    self._manifest[item["id"]] = href

        # Parse spine
        self._spine_items = []
        spine = soup.find("spine")
        if spine:
            for itemref in spine.find_all("itemref"):
                if "idref" in itemref.attrs and itemref["idref"] in self._manifest:
                    self._spine_items.append(itemref["idref"])

    def render_page(self, page_number: int = 0) -> Dict[str, Any]:
        """Render a specific page of the EPUB."""
        if not self._spine_items or page_number >= len(self._spine_items):
            return {
                "content": "<p>Page not found</p>",
                "total_pages": len(self._spine_items) if self._spine_items else 0,
                "current_page": page_number,
                "metadata": self._metadata,
            }

        item_id = self._spine_items[page_number]
        item_path = self._manifest.get(item_id)

        if not item_path:
            return {
                "content": f"<p>Error: Could not find content for page {page_number}</p>",
                "total_pages": len(self._spine_items),
                "current_page": page_number,
                "metadata": self._metadata,
            }

        try:
            # Read the content
            content = self._zip_file.read(item_path).decode("utf-8")

            # Clean up the content (basic example, you might want to enhance this)
            soup = BeautifulSoup(content, "html.parser")

            # Make relative paths absolute
            for tag in soup.find_all(["img", "link", "script", "a"]):
                for attr in ["src", "href"]:
                    if tag.has_attr(attr) and not tag[attr].startswith(
                        ("http:", "https:", "data:")
                    ):
                        # Handle relative paths
                        base_dir = str(Path(item_path).parent) + "/"
                        tag[attr] = base_dir + tag[attr]

            return {
                "content": str(soup),
                "total_pages": len(self._spine_items),
                "current_page": page_number,
                "metadata": self._metadata,
                "navigation": {
                    "has_prev": page_number > 0,
                    "has_next": page_number < len(self._spine_items) - 1,
                    "toc": self._get_toc(),
                },
            }

        except Exception as e:
            return {
                "content": f"<p>Error rendering page: {str(e)}</p>",
                "total_pages": len(self._spine_items),
                "current_page": page_number,
                "metadata": self._metadata,
                "error": str(e),
            }

    def _get_toc(self) -> List[Dict[str, Any]]:
        """Generate a table of contents."""
        # This is a simplified version - a real implementation would parse the NCX or nav file
        return [{"title": f"Page {i + 1}", "page": i} for i in range(len(self._spine_items))]

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the book."""
        return self._metadata

    def close(self) -> None:
        """Clean up resources."""
        if self._zip_file:
            self._zip_file.close()
            self._zip_file = None
        self._book_path = None
        self._spine_items = []
        self._manifest = {}
        self._metadata = {}
        self._current_page = 0
