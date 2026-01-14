#!/usr/bin/env python3
"""Test FTS snippet extraction"""
import sys
sys.path.insert(0, 'src')

from calibre_mcp.utils.fts_utils import query_fts, find_fts_database
from pathlib import Path

fts_path = find_fts_database(Path(r'L:\Multimedia Files\Written Word\Calibre-Bibliothek\metadata.db'))
print(f'FTS Path: {fts_path}')

if fts_path:
    book_ids, total, snippets = query_fts(fts_path, 'to be or not to be', limit=3, include_snippets=True)
    print(f'\nFound {total} total matches')
    print(f'Returned {len(book_ids)} book IDs')
    print(f'Extracted {len(snippets)} snippets\n')
    
    for bid in book_ids[:3]:
        snippet = snippets.get(bid, 'No snippet')
        print(f'Book ID {bid}:')
        print(f'  Snippet: {snippet[:200]}...' if len(snippet) > 200 else f'  Snippet: {snippet}')
        print()
else:
    print('FTS database not found')
