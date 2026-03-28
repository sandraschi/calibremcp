"""
Plain-text normalization for metadata RAG and JSON exports.

HTML in Calibre comments is common; embeddings and external RAG pipelines work better on stripped text.
"""

from __future__ import annotations

import html
import os
import re

_TAG_RE = re.compile(r"<[^>]+>")

# Default max characters from the Comments field included in the metadata embedding blob.
# Comments are blurbs/notes, not full book text; raise via CALIBRE_METADATA_COMMENT_MAX_CHARS if needed.
_DEFAULT_COMMENT_MAX = 20 * 1024  # 20 KiB
# Hard ceiling to avoid pathological memory use (still generous for curated notes).
_ABS_MAX_COMMENT = 16_777_216  # 16 MiB


def strip_html_for_embedding(text: str) -> str:
    """Unescape entities, remove tags, collapse whitespace."""
    if not text:
        return ""
    s = html.unescape(text)
    s = _TAG_RE.sub(" ", s)
    return " ".join(s.split())


def get_comment_max_chars() -> int:
    """
    Max characters from each book's Comments field used in metadata RAG searchable text.

    Environment: ``CALIBRE_METADATA_COMMENT_MAX_CHARS`` (integer).
    If unset or invalid, returns 20480 (20 KiB). Values are clamped to 1..16777216 (16 MiB).
    """
    raw = os.environ.get("CALIBRE_METADATA_COMMENT_MAX_CHARS", "").strip()
    if not raw:
        return _DEFAULT_COMMENT_MAX
    try:
        v = int(raw)
    except ValueError:
        return _DEFAULT_COMMENT_MAX
    if v < 1:
        return _DEFAULT_COMMENT_MAX
    return min(v, _ABS_MAX_COMMENT)


def should_strip_html_metadata() -> bool:
    """When False, keep raw comment HTML in the embedding text (default: strip). Env ``CALIBRE_METADATA_STRIP_HTML``."""
    val = os.environ.get("CALIBRE_METADATA_STRIP_HTML", "1").strip().lower()
    return val not in ("0", "false", "no", "off")
