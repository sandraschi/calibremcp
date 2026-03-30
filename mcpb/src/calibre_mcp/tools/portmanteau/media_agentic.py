import logging
from typing import Any

from mcp.server.fastmcp import Context

from calibre_mcp.server import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def media_synopsis(
    book_id: str,
    title: str,
    chunks_to_analyze: int = 15,
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Agentic Workflow: Generates a comprehensive, spoiler-aware synopsis of a specific book.

    This tool uses the DeepIngestor's 'fulltext' semantic search to retrieve the most
    representative chunks of a book's text, and then uses FastMCP 2.14.3+ sampling to
    request the host LLM to synthesize a high-quality summary without needing internal API keys.

    Args:
        book_id: The Calibre ID of the book.
        title: The title of the book.
        chunks_to_analyze: Number of full-text chunks to sample (default: 15).
        ctx: FastMCP Context (injected automatically).

    Returns:
        A dictionary containing the synthesized synopsis and metadata.
    """
    try:
        if not ctx or not hasattr(ctx, "session") or not hasattr(ctx.session, "sample"):
            return {
                "success": False,
                "error": "This tool requires a client that supports MCP sampling (e.g., Claude Desktop, Cursor).",
            }

        # 1. Retrieve the text chunks using the calibre_rag tool programmatically
        from calibre_mcp.tools.portmanteau.search import calibre_rag

        logger.info(f"Retrieving full-text chunks for '{title}' (ID: {book_id})")
        # We search specifically filtered by book_id to only get this book's text.
        # Note: We pass the query as the title to get a broad contextual spread.
        results = await calibre_rag(
            operation="search",
            query=f"Overview and plot summary of the book {title}",
            limit=chunks_to_analyze,
            search_type="fulltext",
        )

        if not results.get("success") or not results.get("results"):
            return {
                "success": False,
                "error": f"Failed to retrieve full-text chunks for '{title}'. Has it been deep-ingested? Run 'calibre_rag(operation=\"ingest_fulltext\", ...)' first.",
                "details": results.get("error", "No chunks found."),
            }

        # 2. Extract the text content from the results
        # Note: We added 'content_preview' to the search results previously, but for sampling we need the full content
        # Actually, let's just use the `content_preview` or we can directly query LanceDB here if we need raw text.
        # Let's import LanceDB to get the raw text since `content_preview` is truncated.
        from calibre_mcp.tools.portmanteau.search import _get_vector_store

        store = _get_vector_store(table_name="calibre_fulltext")
        # Direct LanceDB query with prefilter on book_id
        try:
            tbl = store.db.open_table(store.table_name)
            qemb = list(
                store.embedding_model.embed([f"Overview and plot summary of the book {title}"])
            )[0]
            qvec = qemb.tolist() if hasattr(qemb, "tolist") else list(qemb)
            search_req = (
                tbl.search(qvec).where(f"metadata.book_id = '{book_id}'").limit(chunks_to_analyze)
            )
            raw_chunks = search_req.to_arrow().to_pylist()
        except Exception as e:
            return {"success": False, "error": f"Failed to query LanceDB directly: {e}"}

        if not raw_chunks:
            return {
                "success": False,
                "error": f"No fulltext chunks found for book_id '{book_id}' in LanceDB.",
            }

        compiled_text = "\n\n---\n\n".join([c.get("content", "") for c in raw_chunks])

        # 3. Create the sampling prompt for the host LLM
        prompt = f"""
        Please act as an expert literary critic and archivist. I need you to synthesize a comprehensive synopsis for the book "{title}".

        Below are several excerpts pulled directly from the book's full text. These are not necessarily in order.

        <book_excerpts>
        {compiled_text}
        </book_excerpts>

        Based on these excerpts, please write a detailed, spoiler-aware synopsis of the book.
        Include:
        - The core premise or setting.
        - Primary themes explored in the text.
        - The main narrative arc (if fiction) or core arguments (if non-fiction).
        - A brief analysis of the writing style.

        Return ONLY the markdown-formatted synopsis.
        """

        # 4. Request sampling from the client
        from mcp.types import (
            CreateMessageRequest,
            CreateMessageRequestParams,
            TextContent,
            UserMessage,
        )

        msg_request = CreateMessageRequest(
            params=CreateMessageRequestParams(
                messages=[UserMessage(role="user", content=TextContent(type="text", text=prompt))],
                maxTokens=2000,
                systemPrompt="You are an expert literary synthesizer and reviewer.",
                # includeNoneToIncludeAllTools=False
            )
        )

        logger.info(f"Requesting LLM sampling for synopsis of '{title}'...")
        # Note: FastMCP 2.14.3 uses create_message on the session object
        response = await ctx.session.create_message(msg_request)

        # 5. Return the result
        synopsis_text = "No response received from sampling."
        if response and response.content and getattr(response.content, "text", None):
            synopsis_text = response.content.text

        # Fallback if content is a list
        elif (
            response
            and response.content
            and isinstance(response.content, list)
            and len(response.content) > 0
        ):
            if hasattr(response.content[0], "text"):
                synopsis_text = response.content[0].text

        return {
            "success": True,
            "operation": "media_synopsis",
            "title": title,
            "book_id": book_id,
            "synopsis": synopsis_text,
            "chunks_analyzed": len(raw_chunks),
        }

    except Exception as e:
        logger.error(f"Error in media_synopsis tool: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
async def media_critical_reception(
    author: str,
    title: str,
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Agentic Workflow: Synthesizes external critical reception and reviews for a book.

    This tool searches the web for academic, critical, and popular reception of the book,
    and then heavily synthesizes this context via FastMCP sampling.

    Args:
        author: The author of the book.
        title: The title of the book.
        ctx: FastMCP Context (injected automatically).

    Returns:
        A dictionary containing the critical reception essay and web links used.
    """
    try:
        if not ctx or not hasattr(ctx, "session") or not hasattr(ctx.session, "sample"):
            return {
                "success": False,
                "error": "This tool requires a client that supports MCP sampling (e.g., Claude Desktop, Cursor).",
            }

        # 1. Fetch search results (We use DuckDuckGo lite via HTTPX for zero-dep fast search)
        from urllib.parse import quote_plus

        import httpx
        from bs4 import BeautifulSoup

        query = f'"{title}" "{author}" book review AND (criticism OR reception OR analysis)'
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        logger.info(f"Searching web for critical reception of '{title}' by {author}...")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)

        if resp.status_code != 200:
            return {"success": False, "error": f"Web search failed with status {resp.status_code}"}

        soup = BeautifulSoup(resp.text, "html.parser")
        results = soup.find_all("div", class_="result__snippet")

        snippets = []
        for res in results[:10]:  # take top 10
            snippets.append(res.text.strip())

        if not snippets:
            return {"success": False, "error": "No significant web reception found for this book."}

        compiled_snippets = "\n".join([f"- {s}" for s in snippets])

        # 2. Create the sampling prompt
        prompt = f"""
        Please act as an expert literary critic. I need a summary of the critical reception for the book "{title}" by {author}.

        I have pulled the following snippets from a web search regarding its reviews, reception, and critical analysis:

        <web_context>
        {compiled_snippets}
        </web_context>

        Based on these snippets and your own internal knowledge of the text, write a coherent, multi-paragraph essay
        summarizing how the book was received by critics and the public. Discuss both positive and negative critiques if present.

        Return ONLY the markdown-formatted critical reception essay.
        """

        # 3. Request sampling from the client
        from mcp.types import (
            CreateMessageRequest,
            CreateMessageRequestParams,
            TextContent,
            UserMessage,
        )

        msg_request = CreateMessageRequest(
            params=CreateMessageRequestParams(
                messages=[UserMessage(role="user", content=TextContent(type="text", text=prompt))],
                maxTokens=2000,
                systemPrompt="You are an expert literary critic.",
            )
        )

        response = await ctx.session.create_message(msg_request)

        # 4. Return the result
        essay_text = "No response received from sampling."
        if response and response.content and getattr(response.content, "text", None):
            essay_text = response.content.text
        elif (
            response
            and response.content
            and isinstance(response.content, list)
            and len(response.content) > 0
        ):
            if hasattr(response.content[0], "text"):
                essay_text = response.content[0].text

        return {
            "success": True,
            "operation": "media_critical_reception",
            "title": title,
            "author": author,
            "reception_essay": essay_text,
            "sources_analyzed": len(snippets),
        }

    except Exception as e:
        logger.error(f"Error in media_critical_reception tool: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@mcp.tool()
async def media_deep_research(
    topic: str,
    ctx: Context = None,
) -> dict[str, Any]:
    """
    Agentic Workflow: Conducts a deep, multi-book comparative analysis on a specific topic.

    This workflow queries the calibre metadata to find 3 books related to the topic,
    pulls excerpts from their deep fulltext indexes, and then samples the LLM to write a
    comparative essay on how the different texts approach the topic.

    Args:
        topic: The thematic topic to research (e.g., "Cyberpunk societal collapse").
        ctx: FastMCP Context (injected automatically).

    Returns:
        A dictionary containing the comparative research essay and metadata.
    """
    try:
        if not ctx or not hasattr(ctx, "session") or not hasattr(ctx.session, "sample"):
            return {
                "success": False,
                "error": "This tool requires a client that supports MCP sampling.",
            }

        # 1. Broad Metadata Search
        from calibre_mcp.tools.portmanteau.search import _get_vector_store, calibre_rag

        logger.info(f"Researching topic: '{topic}' across metadata.")
        meta_results = await calibre_rag(
            operation="search",
            query=topic,
            limit=3,
            search_type="metadata",
        )

        if not meta_results.get("success") or not meta_results.get("results"):
            return {
                "success": False,
                "error": "Could not find any books matching the topic in metadata.",
            }

        top_books = meta_results["results"]

        # 2. Extract Fulltext Chunks
        store = _get_vector_store(table_name="calibre_fulltext")

        compiled_research = []
        books_analyzed = []

        for book in top_books:
            b_id = book.get("book_id")
            b_title = book.get("title")

            try:
                tbl = store.db.open_table(store.table_name)
                qemb = list(store.embedding_model.embed([topic]))[0]
                qvec = qemb.tolist() if hasattr(qemb, "tolist") else list(qemb)
                search_req = tbl.search(qvec).where(f"metadata.book_id = '{b_id}'").limit(5)
                raw_chunks = search_req.to_arrow().to_pylist()

                if raw_chunks:
                    books_analyzed.append(b_title)
                    compiled_research.append(f"### Source: {b_title}\n")
                    for c in raw_chunks:
                        compiled_research.append(f'- "{c.get("content", "")}"\n')
            except Exception as e:
                logger.warning(f"Failed to extract deep chunks for '{b_title}': {e}. Skipping.")
                continue

        if not books_analyzed:
            return {
                "success": False,
                "error": "Found books in metadata, but none of them have been deep-ingested yet. Please run 'ingest_fulltext' on them first.",
            }

        # 3. Create the sampling prompt
        research_context = "\n".join(compiled_research)
        prompt = f"""
        Please act as an academic researcher. You are writing a comparative essay on the topic: "{topic}".

        I have pulled relevant excerpts from {len(books_analyzed)} books in my library:

        <research_excerpts>
        {research_context}
        </research_excerpts>

        Based on these excerpts, write a comprehensive, multi-paragraph comparative essay analyzing how these
        different texts approach the core topic. Compare and contrast their perspectives, themes, and explicit statements.

        Return ONLY the markdown-formatted comparative essay.
        """

        # 4. Request sampling from the client
        from mcp.types import (
            CreateMessageRequest,
            CreateMessageRequestParams,
            TextContent,
            UserMessage,
        )

        msg_request = CreateMessageRequest(
            params=CreateMessageRequestParams(
                messages=[UserMessage(role="user", content=TextContent(type="text", text=prompt))],
                maxTokens=3000,
                systemPrompt="You are an academic media researcher.",
            )
        )

        response = await ctx.session.create_message(msg_request)

        # 5. Return the result
        essay_text = "No response received from sampling."
        if response and response.content and getattr(response.content, "text", None):
            essay_text = response.content.text
        elif (
            response
            and response.content
            and isinstance(response.content, list)
            and len(response.content) > 0
        ):
            if hasattr(response.content[0], "text"):
                essay_text = response.content[0].text

        return {
            "success": True,
            "operation": "media_deep_research",
            "topic": topic,
            "research_essay": essay_text,
            "books_analyzed": books_analyzed,
        }

    except Exception as e:
        logger.error(f"Error in media_deep_research tool: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
