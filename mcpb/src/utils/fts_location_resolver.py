"""
Map a phrase match in Calibre FTS text to concrete reader positions (PDF page, EPUB spine).

Also builds Calibre ``ebook-viewer --open-at search:...`` hints (see calibre manual).
"""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _sanitize_open_at_phrase(phrase: str, max_len: int = 180) -> str:
    """Phrase safe for Calibre ``search:`` / Windows command line."""
    s = re.sub(r"\s+", " ", phrase.strip())[:max_len]
    return s.replace('"', "")


def calibre_ebook_viewer_hints(file_path: str, phrase: str) -> dict[str, Any]:
    """
    Calibre's viewer supports ``--open-at search:text`` to search after opening.

    See: https://manual.calibre-ebook.com/generated/en/ebook-viewer.html
    """
    safe = _sanitize_open_at_phrase(phrase)
    if not safe:
        return {"available": False}
    open_at = f"search:{safe}"
    exe = shutil.which("ebook-viewer")
    return {
        "available": True,
        "open_at": open_at,
        "ebook_viewer_on_path": exe,
        "powershell_example": (
            f'& ebook-viewer --open-at "{open_at}" "{Path(file_path).as_posix()}"' if exe else None
        ),
        "note": "Use Calibre's ebook-viewer; --open-at search: runs Find after load.",
    }


def resolve_pdf_phrase(file_path: str, phrase: str) -> dict[str, Any]:
    """Find first page containing the phrase (PyMuPDF)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return {"resolved": False, "error": "pymupdf_not_installed"}

    path = Path(file_path)
    if not path.is_file():
        return {"resolved": False, "error": "file_not_found"}

    p = _sanitize_open_at_phrase(phrase, 500)
    if not p:
        return {"resolved": False, "error": "empty_phrase"}

    try:
        doc = fitz.open(str(path))
    except Exception as e:
        return {"resolved": False, "error": str(e)}

    try:
        # Try full phrase, then first ~50 chars (line breaks in PDF text)
        needles = [p]
        if len(p) > 20:
            needles.append(p[: min(50, len(p))].rsplit(" ", 1)[0])

        for page_idx in range(len(doc)):
            page = doc.load_page(page_idx)
            for needle in needles:
                if not needle.strip():
                    continue
                rects = page.search_for(needle)
                if rects:
                    r0 = rects[0]
                    return {
                        "resolved": True,
                        "format": "PDF",
                        "page_1based": page_idx + 1,
                        "page_0based": page_idx,
                        "match_rect": [r0.x0, r0.y0, r0.x1, r0.y1],
                        "matched_needle": needle,
                    }
        return {"resolved": False, "error": "phrase_not_found_in_pdf_text"}
    finally:
        doc.close()


def resolve_epub_phrase(file_path: str, phrase: str) -> dict[str, Any]:
    """Locate spine item (href) whose text contains the phrase."""
    try:
        import ebooklib
        from bs4 import BeautifulSoup
        from ebooklib import epub
    except ImportError:
        return {"resolved": False, "error": "ebooklib_or_bs4_missing"}

    path = Path(file_path)
    if not path.is_file():
        return {"resolved": False, "error": "file_not_found"}

    pq = phrase.strip()
    if not pq:
        return {"resolved": False, "error": "empty_phrase"}
    pq_lower = pq.lower()

    try:
        book = epub.read_epub(str(path))
    except Exception as e:
        return {"resolved": False, "error": str(e)}

    for order, item in enumerate(book.get_items_of_type(ebooklib.ITEM_DOCUMENT)):
        try:
            raw = item.get_content()
            soup = BeautifulSoup(raw, "html.parser")
            text = soup.get_text(separator="\n")
        except Exception as e:
            logger.debug("epub spine item skip: %s", e)
            continue
        if pq_lower in text.lower():
            name = item.get_name() or ""
            return {
                "resolved": True,
                "format": "EPUB",
                "epub_item_order": order,
                "epub_href": name,
                "preview_chars": 120,
            }

    return {"resolved": False, "error": "phrase_not_found_in_epub_html_text"}


def resolve_location_for_file(
    file_path: str,
    format_upper: str,
    phrase: str,
) -> dict[str, Any]:
    """Dispatch PDF vs EPUB; always attach Calibre viewer hints when possible."""
    fmt = (format_upper or "").upper()
    out: dict[str, Any] = {
        "file_path": str(Path(file_path).resolve()),
        "format": fmt,
    }

    if fmt == "PDF":
        pdf = resolve_pdf_phrase(file_path, phrase)
        out["pdf"] = pdf
        out["resolved"] = pdf.get("resolved", False)
    elif fmt in ("EPUB", "EPUB3"):
        ep = resolve_epub_phrase(file_path, phrase)
        out["epub"] = ep
        out["resolved"] = ep.get("resolved", False)
    else:
        out["resolved"] = False
        out["note"] = f"Position resolution not implemented for {fmt}; use Calibre search hint."

    out["calibre_viewer"] = calibre_ebook_viewer_hints(file_path, phrase)
    return out
