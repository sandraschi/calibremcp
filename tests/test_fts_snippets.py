#!/usr/bin/env python3
"""Test FTS snippet extraction"""

import sys

sys.path.insert(0, "src")

from pathlib import Path

from calibre_mcp.utils.fts_utils import find_fts_database, query_fts

fts_path = find_fts_database(
    Path(r"L:\Multimedia Files\Written Word\Calibre-Bibliothek\metadata.db")
)

if fts_path:
    book_ids, total, snippets = query_fts(
        fts_path, "to be or not to be", limit=3, include_snippets=True
    )

    for bid in book_ids[:3]:
        snippet = snippets.get(bid, "No snippet")
else:
    pass
