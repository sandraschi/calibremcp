# catalog_bookcase.py - CLI for the bookcase spine-cataloging pipeline.
#
# Photograph a bookcase, read the spines with a local vision LLM, match titles
# to OpenLibrary, write a CSV catalog. No cloud, no API keys.
#
# Usage:
#   uv run python scripts/catalog_bookcase.py D:/shelf1.jpg D:/shelf2.jpg -o D:/catalog.csv
#
# Env overrides: BOOKCASE_OLLAMA_URL (default http://localhost:11434),
#                BOOKCASE_VISION_MODEL (default qwen3.8:27b)

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


async def main() -> int:
    parser = argparse.ArgumentParser(description="Catalog a bookcase from photos")
    parser.add_argument("images", nargs="+", help="Paths to bookcase photo(s)")
    parser.add_argument("-o", "--output", default="bookcase-catalog.csv", help="Output CSV path")
    args = parser.parse_args()

    from calibre_mcp.services import bookcase_catalog

    result = await bookcase_catalog.catalog(args.images)
    if not result.get("success"):
        print(f"ERROR: {result.get('error')}", file=sys.stderr)
        return 1

    bookcase_catalog.write_csv(result.get("items", []), args.output)
    print(f"Identified {result['total_identified']} spines, "
          f"{result['matched_count']} matched OpenLibrary, "
          f"{result['unmatched_count']} unmatched.")
    for it in result.get("items", []):
        mark = "OK" if it["matched"] else "--"
        print(f"  [{mark}] {it['spine_title']} / {it['spine_author'] or '?'} "
              f"-> {it.get('title','')} ({it.get('year','')}) ISBN {it.get('isbn','-')}")
    for err in result.get("errors", []):
        print(f"WARN: {err}", file=sys.stderr)
    print(f"CSV written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
