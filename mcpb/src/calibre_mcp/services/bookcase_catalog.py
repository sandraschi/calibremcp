"""
Bookcase cataloging: photograph a bookcase, read the spines with a local
vision LLM, match each title to OpenLibrary for ISBN/year/publisher, and emit
a catalog (JSON or CSV).

Local-first: the spine-reading runs on the configured Ollama vision model
(qwen3.8:27b by default) - no cloud, no API key. OpenLibrary metadata lookup is
a free public API with no key.

Env overrides:
  BOOKCASE_OLLAMA_URL   default http://localhost:11434
  BOOKCASE_VISION_MODEL default qwen3.8:27b
"""

from __future__ import annotations

import base64
import csv
import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("BOOKCASE_OLLAMA_URL", "http://localhost:11434").rstrip("/")
VISION_MODEL = os.getenv("BOOKCASE_VISION_MODEL", "qwen3.8:27b")
OPENLIBRARY_URL = "https://openlibrary.org/search.json"

_SPINE_PROMPT = """\
This is a photograph of a bookcase. Read the spines of the visible books and
list every book you can identify.
Return STRICT JSON only, no markdown, no prose:
{"books":[{"title":"...","author":"...","confidence":0.9}]}
Rules:
- Only include books whose spine text you can actually read; confidence 0.0-1.0.
- Skip books you cannot identify (blurred, worn, non-Latin spines).
- author may be an empty string if not visible.
- If you cannot read any spines, return {"books":[]}.
"""


def _encode_image(path: str) -> str:
    with open(path, "rb") as fh:
        raw = fh.read()
    ext = os.path.splitext(path)[1].lower().lstrip(".") or "jpeg"
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64," + base64.b64encode(raw).decode("ascii")


async def read_spines(image_path: str, timeout_s: int = 300) -> list[dict[str, Any]]:
    """Ask the local vision model to enumerate visible book spines."""
    data_uri = _encode_image(image_path)
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _SPINE_PROMPT},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            }
        ],
        "temperature": 0.2,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        resp = await client.post(f"{OLLAMA_BASE_URL}/v1/chat/completions", json=payload)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1:
        logger.warning("Vision model returned non-JSON for %s: %.200s", image_path, content)
        return []
    try:
        data = json.loads(content[start : end + 1])
    except json.JSONDecodeError:
        logger.warning("Vision model JSON parse failed for %s: %.200s", image_path, content)
        return []
    books = data.get("books", []) or []
    return [
        {
            "spine_title": str(b.get("title", "")).strip(),
            "spine_author": str(b.get("author", "") or "").strip(),
            "confidence": float(b.get("confidence", 0.0) or 0.0),
        }
        for b in books
        if str(b.get("title", "")).strip()
    ]


async def match_openlibrary(title: str, author: str = "") -> dict[str, Any] | None:
    """Best-effort metadata match via the OpenLibrary search API (no key)."""
    params = {"title": title, "limit": 5}
    if author:
        params["author"] = author
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(OPENLIBRARY_URL, params=params)
            resp.raise_for_status()
            docs = resp.json().get("docs", [])
        except Exception as e:
            logger.warning("OpenLibrary lookup failed for '%s': %s", title, e)
            return None
    if not docs:
        return None
    d = docs[0]
    isbn = None
    raw_isbn = d.get("isbn") or []
    for cand in raw_isbn:
        if len(str(cand)) in (10, 13) and str(cand).isdigit():
            isbn = str(cand)
            break
    return {
        "title": str(d.get("title", "")),
        "author": str((d.get("author_name") or [""])[0]),
        "year": d.get("first_publish_year"),
        "publisher": str((d.get("publisher") or [""])[0]) if d.get("publisher") else "",
        "isbn": isbn,
        "ol_key": str(d.get("key", "")),
    }


async def catalog(image_paths: list[str]) -> dict[str, Any]:
    """Run spine-reading + metadata matching across one or more bookcase photos."""
    if not image_paths:
        return {"success": False, "error": "No image paths provided", "items": [], "unmatched": []}

    spine_items: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in image_paths:
        if not os.path.isfile(path):
            errors.append(f"File not found: {path}")
            continue
        try:
            spine_items.extend(await read_spines(path))
        except Exception as e:
            errors.append(f"Vision pass failed for {path}: {e}")

    # Dedupe by lowercased title.
    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    for s in spine_items:
        key = s["spine_title"].lower()
        if key in seen:
            continue
        seen.add(key)
        match = await match_openlibrary(s["spine_title"], s["spine_author"])
        items.append(
            {
                "spine_title": s["spine_title"],
                "spine_author": s["spine_author"],
                "confidence": s["confidence"],
                "matched": bool(match),
                "title": (match or {}).get("title", ""),
                "author": (match or {}).get("author", ""),
                "year": (match or {}).get("year"),
                "publisher": (match or {}).get("publisher", ""),
                "isbn": (match or {}).get("isbn"),
                "ol_key": (match or {}).get("ol_key", ""),
            }
        )

    matched = [i for i in items if i["matched"]]
    unmatched = [i for i in items if not i["matched"]]
    return {
        "success": True,
        "total_identified": len(items),
        "matched_count": len(matched),
        "unmatched_count": len(unmatched),
        "items": items,
        "unmatched": unmatched,
        "errors": errors,
    }


def write_csv(items: list[dict[str, Any]], output_path: str) -> str:
    """Write the catalog to CSV (spine text + resolved metadata)."""
    fieldnames = [
        "spine_title",
        "spine_author",
        "confidence",
        "matched",
        "title",
        "author",
        "year",
        "publisher",
        "isbn",
        "ol_key",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for it in items:
            writer.writerow({k: it.get(k, "") for k in fieldnames})
    return output_path
