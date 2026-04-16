"""
media_agentic.py — Agentic media tools for CalibreMCP.

Tools:
  media_synopsis           — RAG-based synopsis from local full-text index
  media_critical_reception — Web-search-based critical reception essay
  media_deep_research      — Cross-book thematic analysis
  media_research_book      — Deep external research on a single book:
                             Wikipedia + SF Encyclopedia + TVTropes + ANN +
                             Open Library + local Calibre data, synthesised
                             via LLM sampling into a structured report.
"""

from __future__ import annotations

import asyncio
import logging
import re
import unicodedata
from typing import Any
from urllib.parse import quote, quote_plus

import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import Context

from calibre_mcp.server import mcp

logger = logging.getLogger(__name__)

# ── HTTP helpers ──────────────────────────────────────────────────────────────

_HEADERS = {
    "User-Agent": (
        "CalibreMCP/1.6 (https://github.com/sandraschi/calibre-mcp; "
        "research-tool/book-deep-research)"
    )
}
_FETCH_TIMEOUT = 12.0


async def _fetch(url: str, client: httpx.AsyncClient) -> str | None:
    """GET url, return text or None on any error."""
    try:
        r = await client.get(url, headers=_HEADERS, timeout=_FETCH_TIMEOUT,
                             follow_redirects=True)
        if r.status_code == 200:
            return r.text
        return None
    except Exception as e:
        logger.debug("fetch %s failed: %s", url, e)
        return None


async def _fetch_json(url: str, client: httpx.AsyncClient) -> dict | None:
    """GET url, return parsed JSON or None."""
    try:
        r = await client.get(url, headers=_HEADERS, timeout=_FETCH_TIMEOUT,
                             follow_redirects=True)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        logger.debug("fetch_json %s failed: %s", url, e)
        return None


# ── Slug helpers ──────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Basic slug: lowercase, spaces → underscores, strip punctuation."""
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s-]+", "_", text)


def _wiki_slug(text: str) -> str:
    """Wikipedia title slug: spaces → underscores, URL-encoded."""
    return quote(text.replace(" ", "_"), safe="_/")


def _sfe_slug(title: str) -> str:
    """SF Encyclopedia entry slug: lowercase, spaces → underscores, no punctuation."""
    t = re.sub(r"[^\w\s]", "", title).strip().lower()
    return re.sub(r"\s+", "_", t)


def _tvtropes_slug(title: str) -> str:
    """TVTropes CamelCase slug."""
    words = re.sub(r"[^\w\s]", "", title).split()
    return "".join(w.capitalize() for w in words)


# ── Source fetchers ───────────────────────────────────────────────────────────

async def _fetch_wikipedia_book(title: str, authors: list[str],
                                 client: httpx.AsyncClient) -> dict[str, str]:
    """Fetch Wikipedia summary + key sections for a book."""
    result: dict[str, str] = {}

    # Try title first, then "Title (novel)", then "Title by Author"
    slugs_to_try = [
        _wiki_slug(title),
        _wiki_slug(f"{title} (novel)"),
        _wiki_slug(f"{title} (book)"),
    ]

    summary_data = None
    used_slug = None
    for slug in slugs_to_try:
        d = await _fetch_json(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}", client
        )
        if d and d.get("type") not in ("disambiguation", None) and d.get("extract"):
            summary_data = d
            used_slug = slug
            break

    if not summary_data:
        return result

    result["summary"] = summary_data.get("extract", "")

    # Fetch full page sections for Reception, Plot, Adaptations, Accolades
    if used_slug:
        sections_data = await _fetch_json(
            f"https://en.wikipedia.org/api/rest_v1/page/sections/{used_slug}", client
        )
        if sections_data and "sections" in sections_data:
            want = {"plot", "reception", "critical reception", "adaptations",
                    "accolades", "awards", "legacy", "themes"}
            for sec in sections_data["sections"]:
                title_lower = sec.get("title", "").lower()
                if any(w in title_lower for w in want):
                    soup = BeautifulSoup(sec.get("content", ""), "html.parser")
                    text = soup.get_text(separator="\n").strip()
                    if text:
                        result[sec["title"]] = text[:2000]

    return result


async def _fetch_wikipedia_author(author: str,
                                   client: httpx.AsyncClient) -> dict[str, str]:
    """Fetch Wikipedia summary for the primary author."""
    result: dict[str, str] = {}
    slug = _wiki_slug(author)
    d = await _fetch_json(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}", client
    )
    if d and d.get("extract"):
        result["author_summary"] = d["extract"]
    return result


async def _fetch_sf_encyclopedia(title: str,
                                  client: httpx.AsyncClient) -> str | None:
    """Fetch SF Encyclopedia entry for a title."""
    slug = _sfe_slug(title)
    html = await _fetch(f"https://www.sf-encyclopedia.com/entry/{slug}", client)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    # SFE uses <div class="entry-content"> or similar
    content = soup.find("div", {"class": re.compile(r"entry.?content", re.I)})
    if not content:
        content = soup.find("article")
    if not content:
        return None
    text = content.get_text(separator="\n").strip()
    return text[:3000] if text else None


async def _fetch_tvtropes(title: str, client: httpx.AsyncClient) -> str | None:
    """Fetch TVTropes Literature page. Best-effort — graceful on failure."""
    slug = _tvtropes_slug(title)
    url = f"https://tvtropes.org/pmwiki/pmwiki.php/Literature/{slug}"
    html = await _fetch(url, client)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    # TVTropes main content is in div.page-content or div#main-article
    content = soup.find("div", {"id": "main-article"}) or \
              soup.find("div", {"class": "page-content"})
    if not content:
        return None
    # Extract description paragraph(s) — stop before the tropes list
    paragraphs = []
    for p in content.find_all("p"):
        text = p.get_text(separator=" ").strip()
        if len(text) > 50:
            paragraphs.append(text)
        if len(paragraphs) >= 4:
            break
    # Also grab a sample of trope names
    trope_links = content.find_all("a", {"class": re.compile(r"twikilink", re.I)})
    tropes = list({a.get_text(strip=True) for a in trope_links[:30]
                   if a.get_text(strip=True)})[:20]
    if not paragraphs and not tropes:
        return None
    out = "\n\n".join(paragraphs)
    if tropes:
        out += "\n\nNotable tropes: " + ", ".join(tropes)
    return out[:2500]


async def _fetch_anime_news_network(title: str,
                                     client: httpx.AsyncClient) -> str | None:
    """Fetch ANN encyclopedia entry for manga/anime titles."""
    search_url = (
        f"https://www.animenewsnetwork.com/search?q={quote_plus(title)}&type=manga"
    )
    html = await _fetch(search_url, client)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    first_result = soup.find("a", href=re.compile(r"/encyclopedia/manga\.php"))
    if not first_result:
        return None
    detail_url = "https://www.animenewsnetwork.com" + first_result["href"]
    detail_html = await _fetch(detail_url, client)
    if not detail_html:
        return None
    detail_soup = BeautifulSoup(detail_html, "html.parser")
    # ANN uses #content-zone with info boxes
    info = detail_soup.find("div", {"id": "content-zone"})
    if not info:
        return None
    text = info.get_text(separator="\n").strip()
    return text[:2000] if text else None


async def _fetch_open_library(isbn: str, client: httpx.AsyncClient) -> dict | None:
    """Fetch Open Library metadata for a given ISBN."""
    d = await _fetch_json(
        f"https://openlibrary.org/isbn/{isbn}.json", client
    )
    if not d:
        return None
    return {
        "first_publish_date": d.get("first_publish_date", ""),
        "subjects": d.get("subjects", [])[:20],
        "description": (d.get("description") or {}).get("value", "")
        if isinstance(d.get("description"), dict)
        else str(d.get("description", ""))[:500],
    }


# ── Local data helpers ────────────────────────────────────────────────────────

async def _get_book_metadata(book_id: int) -> dict[str, Any]:
    """Pull book metadata from Calibre via the MCP tool."""
    try:
        from calibre_mcp.tools.book_management.manage_books import manage_books
        result = await manage_books(operation="get", book_id=book_id)
        if isinstance(result, dict) and result.get("success"):
            return result.get("book", result)
        return {}
    except Exception as e:
        logger.warning("Could not fetch book metadata for %s: %s", book_id, e)
        return {}


async def _get_personal_notes(book_id: int, library_path: str) -> str:
    """Pull personal notes from calibre_mcp_data.db."""
    try:
        from calibre_mcp.db.user_data import get_user_comment
        return get_user_comment(book_id, library_path) or ""
    except Exception:
        return ""


async def _get_rag_passages(book_id: int, title: str,
                             n: int = 5) -> list[str]:
    """Pull thematically relevant RAG passages from the content index."""
    try:
        from calibre_mcp.tools.portmanteau.search import _get_vector_store
        store = _get_vector_store(table_name="calibre_fulltext")
        tbl = store.db.open_table(store.table_name)
        qemb = list(store.embedding_model.embed([
            f"themes setting premise of {title}"
        ]))[0]
        qvec = qemb.tolist() if hasattr(qemb, "tolist") else list(qemb)
        rows = (
            tbl.search(qvec)
            .where(f"metadata.book_id = '{book_id}'")
            .limit(n)
            .to_arrow()
            .to_pylist()
        )
        return [r.get("content", "") for r in rows if r.get("content")]
    except Exception as e:
        logger.debug("RAG passages unavailable for book %s: %s", book_id, e)
        return []


# ── Source routing table ──────────────────────────────────────────────────────

_SF_TAGS = {
    "science fiction", "sf", "fantasy", "space opera", "cyberpunk",
    "steampunk", "hard sf", "new weird", "speculative fiction",
    "alternate history", "horror", "dark fantasy",
}
_MANGA_TAGS = {
    "manga", "anime", "light novel", "manhwa", "manhua",
    "japanese", "japanese fiction",
}


def _select_sources(tags: list[str]) -> set[str]:
    """Return set of source keys to fetch based on book tags."""
    tag_set = {t.lower().strip() for t in tags}
    sources = {"wikipedia_book", "wikipedia_author"}
    if tag_set & _SF_TAGS:
        sources.add("sf_encyclopedia")
    if tag_set & _MANGA_TAGS:
        sources.add("anime_news_network")
    # TVTropes for any fiction — heuristic: not if purely non-fiction tags
    nonfiction_tags = {"non-fiction", "nonfiction", "history", "biography",
                       "science", "mathematics", "philosophy", "reference"}
    if not (tag_set <= nonfiction_tags):
        sources.add("tvtropes")
    return sources


# ── Sampling helper ───────────────────────────────────────────────────────────

async def _sample(ctx: Context, prompt: str,
                  system: str, max_tokens: int = 3000) -> str:
    """Call ctx.sample() with FastMCP 3.2 API, return text."""
    from mcp.types import (
        CreateMessageRequest,
        CreateMessageRequestParams,
        TextContent,
        UserMessage,
    )
    req = CreateMessageRequest(
        params=CreateMessageRequestParams(
            messages=[UserMessage(
                role="user",
                content=TextContent(type="text", text=prompt)
            )],
            maxTokens=max_tokens,
            systemPrompt=system,
        )
    )
    resp = await ctx.session.create_message(req)
    if resp and resp.content:
        if hasattr(resp.content, "text"):
            return resp.content.text
        if isinstance(resp.content, list) and resp.content:
            return getattr(resp.content[0], "text", "")
    return ""


# ── Main tool ─────────────────────────────────────────────────────────────────

@mcp.tool()
async def media_research_book(
    book_id: int,
    include_spoilers: bool = False,
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Deep external research on a single book from your Calibre library.

    Fetches Wikipedia (book + author), SF Encyclopedia (for genre fiction),
    TVTropes (for fiction), Anime News Network (for manga/light novels),
    and Open Library (if ISBN present). Combines with your local Calibre
    data — rating, tags, personal notes, and RAG passages from the book
    text if the content index has been built.

    Synthesises everything via LLM sampling into a structured markdown
    research report with sections: Overview, Context, Plot/Content,
    Critical Reception, Themes & Tropes, Adaptations, Related Works,
    Your Library.

    Requires a sampling-capable MCP client (Claude Desktop, Cursor).

    Args:
        book_id: Calibre book ID (visible in book URL).
        include_spoilers: Whether to include plot spoilers in synopsis sections.
        ctx: FastMCP context (injected).
    """
    if not ctx or not hasattr(ctx, "session") or \
            not hasattr(ctx.session, "create_message"):
        return {
            "success": False,
            "error": (
                "media_research_book requires a sampling-capable MCP client "
                "(Claude Desktop or Cursor). Raw HTTP calls are not supported."
            ),
        }

    # ── 1. Get book metadata from Calibre ────────────────────────────────────
    book = await _get_book_metadata(book_id)
    if not book:
        return {"success": False, "error": f"Book ID {book_id} not found."}

    title: str = book.get("title", "Unknown")
    authors: list[str] = book.get("authors", [])
    primary_author: str = authors[0] if authors else ""
    tags: list[str] = book.get("tags", [])
    rating: int | None = book.get("rating")
    series: str = book.get("series", "")
    series_index: float | None = book.get("series_index")
    identifiers: dict = book.get("identifiers", {})
    isbn: str = identifiers.get("isbn", "")
    library_path: str = book.get("library_path", "")
    calibre_comments: str = book.get("comments", "")

    logger.info("media_research_book: %s (id=%s, tags=%s)", title, book_id, tags)

    # ── 2. Select sources ─────────────────────────────────────────────────────
    sources_to_fetch = _select_sources(tags)
    if isbn:
        sources_to_fetch.add("open_library")

    # ── 3. Fetch all sources concurrently ─────────────────────────────────────
    fetched: dict[str, Any] = {}
    failed: list[str] = []

    async with httpx.AsyncClient() as client:
        tasks: dict[str, Any] = {}

        if "wikipedia_book" in sources_to_fetch:
            tasks["wikipedia_book"] = _fetch_wikipedia_book(title, authors, client)
        if "wikipedia_author" in sources_to_fetch and primary_author:
            tasks["wikipedia_author"] = _fetch_wikipedia_author(primary_author, client)
        if "sf_encyclopedia" in sources_to_fetch:
            tasks["sf_encyclopedia"] = _fetch_sf_encyclopedia(title, client)
        if "tvtropes" in sources_to_fetch:
            tasks["tvtropes"] = _fetch_tvtropes(title, client)
        if "anime_news_network" in sources_to_fetch:
            tasks["anime_news_network"] = _fetch_anime_news_network(title, client)
        if "open_library" in sources_to_fetch and isbn:
            tasks["open_library"] = _fetch_open_library(isbn, client)

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

    for key, result in zip(tasks.keys(), results):
        if isinstance(result, Exception):
            logger.warning("Source %s failed: %s", key, result)
            failed.append(key)
        elif result:
            fetched[key] = result
        else:
            failed.append(key)

    # ── 4. Get local data ─────────────────────────────────────────────────────
    personal_notes, rag_passages = await asyncio.gather(
        _get_personal_notes(book_id, library_path),
        _get_rag_passages(book_id, title),
    )

    # ── 5. Build synthesis prompt ─────────────────────────────────────────────
    sections: list[str] = []

    sections.append(f"BOOK: {title}")
    if primary_author:
        sections.append(f"AUTHOR: {primary_author}")
    if series:
        idx = f" #{series_index}" if series_index else ""
        sections.append(f"SERIES: {series}{idx}")
    sections.append(f"TAGS/GENRES: {', '.join(tags) if tags else 'unknown'}")
    if rating:
        sections.append(f"YOUR RATING: {rating}/5")

    if calibre_comments:
        sections.append(f"\n--- CALIBRE DESCRIPTION ---\n{calibre_comments[:1000]}")

    wiki_book = fetched.get("wikipedia_book", {})
    if wiki_book.get("summary"):
        sections.append(f"\n--- WIKIPEDIA SUMMARY ---\n{wiki_book['summary'][:1500]}")
    for sec_name in ("Plot", "Reception", "Critical reception",
                     "Adaptations", "Accolades", "Legacy", "Themes"):
        if wiki_book.get(sec_name):
            sections.append(
                f"\n--- WIKIPEDIA: {sec_name.upper()} ---\n{wiki_book[sec_name]}"
            )

    wiki_author = fetched.get("wikipedia_author", {})
    if wiki_author.get("author_summary"):
        sections.append(
            f"\n--- WIKIPEDIA AUTHOR ({primary_author}) ---\n"
            f"{wiki_author['author_summary'][:1000]}"
        )

    if fetched.get("sf_encyclopedia"):
        sections.append(
            f"\n--- SF ENCYCLOPEDIA ---\n{fetched['sf_encyclopedia']}"
        )

    if fetched.get("tvtropes"):
        sections.append(f"\n--- TVTROPES ---\n{fetched['tvtropes']}")

    if fetched.get("anime_news_network"):
        sections.append(
            f"\n--- ANIME NEWS NETWORK ---\n{fetched['anime_news_network']}"
        )

    if isinstance(fetched.get("open_library"), dict):
        ol = fetched["open_library"]
        sections.append(
            f"\n--- OPEN LIBRARY ---\n"
            f"First published: {ol.get('first_publish_date', 'unknown')}\n"
            f"Subjects: {', '.join(ol.get('subjects', [])[:10])}\n"
            f"{ol.get('description', '')}"
        )

    if rag_passages:
        joined = "\n\n---\n\n".join(rag_passages[:5])
        sections.append(
            f"\n--- PASSAGES FROM YOUR COPY ---\n"
            f"{'(spoilers included)' if include_spoilers else '(thematic excerpts)'}\n"
            f"{joined[:2000]}"
        )

    if personal_notes:
        sections.append(f"\n--- YOUR PERSONAL NOTES ---\n{personal_notes}")

    source_list = ", ".join(fetched.keys()) or "none"
    spoiler_instruction = (
        "You MAY include plot spoilers where relevant."
        if include_spoilers
        else "Do NOT reveal plot spoilers beyond what is common knowledge."
    )

    prompt = f"""You are an expert literary researcher and critic. Produce a comprehensive
research report on the book described below. Use ALL the source material provided.
{spoiler_instruction}

Format the report in clean Markdown with these sections (omit any section where
you have no meaningful content):

# [Book Title]

## Overview
Brief orientation: what the book is, when and where it fits in literary history,
why it matters.

## The Author
Relevant biography and bibliography context. Where does this book sit in their career?

## Plot & Content
What the book is about. (Respect the spoiler instruction above.)

## Critical Reception
How was it received? Reviews, awards, controversies, legacy. Be specific.

## Themes & Tropes
Major themes, recurring motifs, notable structural or stylistic choices.
If TVTropes data is available, mention notable tropes.

## Adaptations & Related Media
Films, TV, games, comics, sequels, prequels, shared universes.

## If You Liked This
Related works: same author, same subgenre, similar themes. Be concrete.

## Your Library
Your rating, read status, personal notes if provided. Make this section
feel personal and specific, not generic.

---

SOURCE MATERIAL:
{chr(10).join(sections)}

---

Sources consulted: {source_list}
Sources unavailable: {', '.join(failed) if failed else 'none'}

Write the report now. Be specific, be authoritative, be interesting.
Do not pad with vague generalities. If you have no data for a section, omit it.
"""

    # ── 6. Sample ─────────────────────────────────────────────────────────────
    logger.info("media_research_book: sampling LLM for %s", title)
    report = await _sample(
        ctx, prompt,
        system="You are an expert literary researcher, critic, and bibliographer.",
        max_tokens=4000,
    )

    if not report:
        return {
            "success": False,
            "error": "LLM sampling returned no content.",
            "sources_fetched": list(fetched.keys()),
        }

    return {
        "success": True,
        "book_id": book_id,
        "title": title,
        "authors": authors,
        "report": report,
        "sources_fetched": list(fetched.keys()),
        "sources_failed": failed,
        "local_data": {
            "rating": rating,
            "series": f"{series} #{series_index}" if series else None,
            "personal_notes": bool(personal_notes),
            "rag_passages": len(rag_passages),
        },
    }


# ── Existing tools below (unchanged) ─────────────────────────────────────────

@mcp.tool()
async def media_synopsis(
    book_id: str,
    title: str,
    chunks_to_analyze: int = 15,
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Generates a comprehensive, spoiler-aware synopsis using full-text semantic chunks and LLM sampling.
    """
    try:
        if not ctx or not hasattr(ctx, "session") or not hasattr(ctx.session, "sample"):
            return {
                "success": False,
                "error": "This tool requires a client that supports MCP sampling (e.g., Claude Desktop, Cursor).",
            }

        from calibre_mcp.tools.portmanteau.search import calibre_rag, _get_vector_store

        logger.info(f"Retrieving full-text chunks for '{title}' (ID: {book_id})")
        results = await calibre_rag(
            operation="search",
            query=f"Overview and plot summary of the book {title}",
            limit=chunks_to_analyze,
            search_type="fulltext",
        )

        if not results.get("success") or not results.get("results"):
            return {
                "success": False,
                "error": f"Failed to retrieve full-text chunks for '{title}'. Has it been deep-ingested?",
                "details": results.get("error", "No chunks found."),
            }

        store = _get_vector_store(table_name="calibre_fulltext")
        try:
            tbl = store.db.open_table(store.table_name)
            qemb = list(store.embedding_model.embed([f"Overview and plot summary of the book {title}"]))[0]
            qvec = qemb.tolist() if hasattr(qemb, "tolist") else list(qemb)
            raw_chunks = (
                tbl.search(qvec)
                .where(f"metadata.book_id = '{book_id}'")
                .limit(chunks_to_analyze)
                .to_arrow()
                .to_pylist()
            )
        except Exception as e:
            return {"success": False, "error": f"Failed to query LanceDB directly: {e}"}

        if not raw_chunks:
            return {"success": False, "error": f"No fulltext chunks found for book_id '{book_id}'."}

        compiled_text = "\n\n---\n\n".join([c.get("content", "") for c in raw_chunks])
        prompt = f"""Please act as an expert literary critic and archivist. Synthesize a comprehensive
synopsis for the book "{title}" from the excerpts below. Include: core premise, primary themes,
main narrative arc, brief style analysis. Return ONLY markdown-formatted synopsis.

<book_excerpts>
{compiled_text}
</book_excerpts>"""

        synopsis_text = await _sample(ctx, prompt,
                                       "You are an expert literary synthesizer and reviewer.",
                                       max_tokens=2000)

        return {
            "success": True,
            "operation": "media_synopsis",
            "title": title,
            "book_id": book_id,
            "synopsis": synopsis_text or "No response received from sampling.",
            "chunks_analyzed": len(raw_chunks),
        }

    except Exception as e:
        logger.error(f"Error in media_synopsis: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
async def media_critical_reception(
    author: str,
    title: str,
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Synthesizes external critical reviews and academic reception via web search and LLM sampling.
    """
    try:
        if not ctx or not hasattr(ctx, "session") or not hasattr(ctx.session, "sample"):
            return {"success": False, "error": "Requires sampling-capable MCP client."}

        query = f'"{title}" "{author}" book review AND (criticism OR reception OR analysis)'
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=_HEADERS, timeout=_FETCH_TIMEOUT)

        if resp.status_code != 200:
            return {"success": False, "error": f"Web search failed with status {resp.status_code}"}

        soup = BeautifulSoup(resp.text, "html.parser")
        snippets = [r.text.strip() for r in soup.find_all("div", class_="result__snippet")][:10]

        if not snippets:
            return {"success": False, "error": "No significant web reception found."}

        compiled = "\n".join(f"- {s}" for s in snippets)
        prompt = f"""Act as expert literary critic. Summarise critical reception of "{title}"
by {author} from these web snippets. Discuss positive and negative critiques.
Return ONLY markdown essay.

<web_context>
{compiled}
</web_context>"""

        essay = await _sample(ctx, prompt, "You are an expert literary critic.", max_tokens=2000)

        return {
            "success": True,
            "operation": "media_critical_reception",
            "title": title,
            "author": author,
            "reception_essay": essay or "No response received.",
            "sources_analyzed": len(snippets),
        }

    except Exception as e:
        logger.error(f"Error in media_critical_reception: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
async def media_deep_research(
    topic: str,
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Conducts multi-book comparative analysis on a thematic topic using full-text RAG and LLM sampling.
    """
    try:
        if not ctx or not hasattr(ctx, "session") or not hasattr(ctx.session, "sample"):
            return {"success": False, "error": "Requires sampling-capable MCP client."}

        from calibre_mcp.tools.portmanteau.search import _get_vector_store, calibre_rag

        meta_results = await calibre_rag(operation="search", query=topic, limit=3, search_type="metadata")

        if not meta_results.get("success") or not meta_results.get("results"):
            return {"success": False, "error": "Could not find any books matching the topic in metadata."}

        top_books = meta_results["results"]
        store = _get_vector_store(table_name="calibre_fulltext")

        compiled_research: list[str] = []
        books_analyzed: list[str] = []

        for book in top_books:
            b_id = book.get("book_id")
            b_title = book.get("title")
            try:
                tbl = store.db.open_table(store.table_name)
                qemb = list(store.embedding_model.embed([topic]))[0]
                qvec = qemb.tolist() if hasattr(qemb, "tolist") else list(qemb)
                rows = (
                    tbl.search(qvec)
                    .where(f"metadata.book_id = '{b_id}'")
                    .limit(5)
                    .to_arrow()
                    .to_pylist()
                )
                if rows:
                    books_analyzed.append(b_title)
                    compiled_research.append(f"### Source: {b_title}\n")
                    for c in rows:
                        compiled_research.append(f'- "{c.get("content", "")}"\n')
            except Exception as e:
                logger.warning(f"Failed chunks for '{b_title}': {e}")
                continue

        if not books_analyzed:
            return {"success": False, "error": "Found books but none have been deep-ingested yet."}

        research_context = "\n".join(compiled_research)
        prompt = f"""Act as academic researcher. Write comparative essay on topic: "{topic}".

<research_excerpts>
{research_context}
</research_excerpts>

Compare and contrast how these texts approach the topic. Return ONLY markdown essay."""

        essay = await _sample(ctx, prompt, "You are an academic media researcher.", max_tokens=3000)

        return {
            "success": True,
            "operation": "media_deep_research",
            "topic": topic,
            "research_essay": essay or "No response received.",
            "books_analyzed": books_analyzed,
        }

    except Exception as e:
        logger.error(f"Error in media_deep_research: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
