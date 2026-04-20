#!/usr/bin/env python
"""
Export Calibre library metadata to JSON for external RAG / backup pipelines.

Run with Calibre's embedded Python only — not with system python:

    calibre-debug -e scripts/export_metadata_for_rag.py -- --library "D:\\path\\to\\Calibre Library" --output calibre_rag_data.json

On Windows, ensure calibre-debug is on PATH (standard Calibre install).

Uses Calibre's internal DB API (fast; includes comments — primary semantic signal for many libraries).

When this repo is on ``PYTHONPATH`` (dev checkout below ``src``), HTML stripping matches
``calibre_mcp.rag.text_utils.strip_html_for_embedding``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if _SRC.is_dir():
    sys.path.insert(0, str(_SRC))


def _strip_html(text: str) -> str:
    try:
        from calibre_mcp.rag.text_utils import strip_html_for_embedding

        return strip_html_for_embedding(text)
    except ImportError:
        import html
        import re

        _TAG_RE = re.compile(r"<[^>]+>")
        if not text:
            return ""
        s = html.unescape(text)
        s = _TAG_RE.sub(" ", s)
        return " ".join(s.split())


def export_metadata(library_path: str, *, strip_html: bool) -> list[dict[str, Any]]:
    from calibre.library import db  # type: ignore[import-untyped]

    cache = db(library_path).new_api
    books: list[dict[str, Any]] = []

    for book_id in cache.all_book_ids():
        metadata = cache.get_proxy_metadata(book_id)
        raw_comments = metadata.comments or ""
        comments = _strip_html(raw_comments) if strip_html else raw_comments

        book_data: dict[str, Any] = {
            "id": book_id,
            "title": metadata.title,
            "authors": list(metadata.authors),
            "tags": list(metadata.tags),
            "series": metadata.series,
            "series_index": metadata.series_index,
            "publisher": metadata.publisher,
            "comments": comments,
            "formats": cache.formats(book_id),
            "path": cache.get_book_path(book_id),
        }
        books.append(book_data)

    return books


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export Calibre metadata to JSON (run via calibre-debug -e)."
    )
    parser.add_argument(
        "--library",
        default=os.environ.get("CALIBRE_LIBRARY_PATH", "."),
        help="Calibre library folder (directory containing metadata.db). Default: CALIBRE_LIBRARY_PATH or cwd.",
    )
    parser.add_argument(
        "--output",
        default="calibre_rag_data.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--strip-html",
        action="store_true",
        help="Strip HTML tags from comments for cleaner embedding text.",
    )
    args = parser.parse_args()

    library_path = os.path.abspath(args.library)
    books = export_metadata(library_path, strip_html=args.strip_html)

    out_path = os.path.abspath(args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)



if __name__ == "__main__":
    main()
