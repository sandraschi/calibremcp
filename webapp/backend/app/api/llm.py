"""LLM API endpoints for chat (Ollama, LM Studio, OpenAI-compatible)."""

import json
import logging

import httpx
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

OLLAMA_DEFAULT = "http://127.0.0.1:11434"
LMSTUDIO_DEFAULT = "http://127.0.0.1:1234/v1"
OPENAI_DEFAULT = "https://api.openai.com/v1"

# ── Tool definitions (OpenAI-compatible function schema) ─────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": "Search books by title, author, tags, or full-text. Use for any question about specific books or authors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search text — title, author name, or keywords. Can be left empty to browse recent books.",
                    },
                    "author": {"type": "string", "description": "Author name filter (optional)."},
                    "limit": {"type": "integer", "description": "Max results (1-50).", "default": 15},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_libraries",
            "description": "List all Calibre libraries with book counts and active library.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_library_stats",
            "description": "Get statistics (total books, authors, series, tags) for a library.",
            "parameters": {
                "type": "object",
                "properties": {
                    "library": {
                        "type": "string",
                        "description": "Library name (optional — uses active library if omitted).",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_book",
            "description": "Get full details including description for a specific book by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "book_id": {
                        "type": "string",
                        "description": "Numeric book ID from search results.",
                    }
                },
                "required": ["book_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tags",
            "description": "List all tags/genres in the library.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_authors",
            "description": "List all authors (paginated).",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max results.", "default": 30},
                    "offset": {"type": "integer", "description": "Pagination offset.", "default": 0},
                },
                "required": [],
            },
        },
    },
]


def _get_base_url(provider: str | None = None, base_url: str | None = None) -> str:
    if base_url and base_url.strip():
        return base_url.rstrip("/")
    p = (provider or settings.LLM_PROVIDER).lower()
    if p in ("ollama",):
        return settings.LLM_BASE_URL or OLLAMA_DEFAULT
    if p in ("lmstudio", "lm_studio"):
        return settings.LLM_BASE_URL or LMSTUDIO_DEFAULT
    return settings.LLM_BASE_URL or OPENAI_DEFAULT


async def _llm_call(
    messages: list[dict],
    model: str,
    url: str,
    tools: list | None = None,
) -> dict | None:
    """Call LLM. Returns the full response dict for tool-calling, or None on failure."""
    if "ollama" in url or ":11434" in url:
        payload = {"model": model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                r = await client.post(f"{url}/api/chat", json=payload)
                if r.status_code != 200:
                    return None
                return r.json()
            except httpx.ConnectError:
                return None
    headers = {"Content-Type": "application/json"}
    if settings.LLM_API_KEY:
        headers["Authorization"] = f"Bearer {settings.LLM_API_KEY}"
    payload = {"model": model, "messages": messages, "stream": False}
    if tools:
        payload["tools"] = tools
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            r = await client.post(f"{url}/chat/completions", json=payload, headers=headers)
            if r.status_code != 200:
                return None
            return r.json()
        except httpx.ConnectError:
            return None


def _extract_message(data: dict | None) -> dict | None:
    """Extract the assistant message dict from Ollama or OpenAI response."""
    if not data:
        return None
    if "message" in data:
        return data["message"]
    choices = data.get("choices", [])
    return choices[0].get("message") if choices else None


def _extract_content(msg: dict | None) -> str:
    return (msg or {}).get("content") or ""


def _extract_tool_calls(msg: dict | None) -> list[dict]:
    tc = (msg or {}).get("tool_calls") or []
    # Normalise Ollama format to OpenAI format
    return [{"id": t.get("id", ""), "function": t.get("function", t)} for t in tc]


async def _dispatch(mcp_tool: str, mcp_args: dict) -> dict:
    """Call an MCP tool via the local mcp_client."""
    from ..mcp.client import mcp_client as _mc

    try:
        result = await _mc.call_tool(mcp_tool, mcp_args)
        return result if isinstance(result, dict) else {"result": str(result)}
    except Exception as e:
        logger.warning("Tool call %s failed: %s", mcp_tool, e)
        return {"error": str(e)}


TOOL_ROUTES = {
    "search_books": ("query_books", ["query", "author", "limit"]),
    "list_libraries": ("manage_libraries", []),
    "get_library_stats": ("manage_libraries", ["library"]),
    "get_book": ("query_books", ["book_id"]),
    "list_tags": ("manage_tags", []),
    "list_authors": ("manage_authors", ["limit", "offset"]),
}

TOOL_ARG_MAP = {
    "search_books": lambda a: {
        "operation": "search",
        "text": a.get("query", ""),
        "author": a.get("author", ""),
        "limit": min(a.get("limit", 15), 50),
    },
    "list_libraries": lambda a: {"operation": "list"},
    "get_library_stats": lambda a: {"operation": "stats", "library_name": a.get("library")},
    "get_book": lambda a: {"operation": "get", "book_id": a.get("book_id")},
    "list_tags": lambda a: {"operation": "list"},
    "list_authors": lambda a: {
        "operation": "list",
        "limit": min(a.get("limit", 30), 100),
        "offset": a.get("offset", 0),
    },
}


@router.get("/models")
async def list_models(
    provider: str | None = None,
    base_url: str | None = None,
):
    """List available models (Ollama/LM Studio/OpenAI-compatible)."""
    url = _get_base_url(provider, base_url)
    if "ollama" in url or ":11434" in url:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{url}/api/tags")
                if r.status_code != 200:
                    return {"models": [], "error": r.text}
                data = r.json()
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                return {"models": models, "provider": "ollama"}
        except Exception as e:
            logger.warning("Ollama models fetch failed: %s", e)
            return {"models": [], "error": str(e)}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {}
            key = settings.LLM_API_KEY
            if key:
                headers["Authorization"] = f"Bearer {key}"
            ep = f"{url.rstrip('/')}/models"
            r = await client.get(ep, headers=headers or None)
            if r.status_code != 200:
                return {"models": [], "error": r.text}
            data = r.json()
            items = data.get("data", data.get("models", []))
            if isinstance(items, list):
                names = [m.get("id") or m.get("name") or m for m in items if isinstance(m, dict)]
            else:
                names = []
            return {"models": names, "provider": "openai-compatible"}
    except Exception as e:
        logger.warning("Models fetch failed: %s", e)
        return {"models": [], "error": str(e)}


@router.post("/chat")
async def chat(
    messages: list[dict[str, str]] = Body(...),
    model: str = Body("llama3.2", description="Model name"),
    stream: bool = Body(False),
    provider: str | None = Body(None),
    base_url: str | None = Body(None),
):
    """Chat completion. Supports streaming."""
    url = _get_base_url(provider, base_url)
    if "ollama" in url or ":11434" in url:
        req_url = f"{url}/api/chat"
        payload = {"model": model, "messages": messages, "stream": stream}
        if stream:

            async def _stream():
                async with httpx.AsyncClient(timeout=60.0) as client:
                    async with client.stream("POST", req_url, json=payload) as r:
                        async for chunk in r.aiter_text():
                            yield chunk

            return StreamingResponse(_stream(), media_type="text/event-stream")
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                r = await client.post(req_url, json=payload)
                if r.status_code != 200:
                    return {"error": r.text, "status": r.status_code}
                return r.json()
            except httpx.ConnectError:
                return {"error": f"Cannot connect to {url}. Is Ollama/LM Studio running?", "status": 503}
    req_url = f"{url}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if settings.LLM_API_KEY:
        headers["Authorization"] = f"Bearer {settings.LLM_API_KEY}"
    payload = {"model": model, "messages": messages, "stream": stream}
    if stream:

        async def _stream_openai():
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", req_url, json=payload, headers=headers) as r:
                    async for chunk in r.aiter_text():
                        yield chunk

        return StreamingResponse(_stream_openai(), media_type="text/event-stream")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            r = await client.post(req_url, json=payload, headers=headers)
            if r.status_code != 200:
                return {"error": r.text, "status": r.status_code}
            return r.json()
        except httpx.ConnectError:
            return {"error": f"Cannot connect to {url}. Is Ollama/LM Studio running?", "status": 503}


@router.post("/agentic")
async def agentic_chat(
    messages: list[dict[str, str]] = Body(...),
    model: str = Body("llama3.2"),
    provider: str | None = Body(None),
    base_url: str | None = Body(None),
):
    """Agentic chat with proper OpenAI-compatible tool calling."""
    try:
        return await _agentic_impl(messages, model, provider, base_url)
    except Exception as e:
        logger.error("Agentic chat error: %s", e, exc_info=True)
        return {"message": {"role": "assistant", "content": f"Sorry, something went wrong: {e}"}}


async def _agentic_impl(
    messages: list[dict[str, str]],
    model: str,
    provider: str | None,
    base_url: str | None,
) -> dict:
    url = _get_base_url(provider, base_url)
    # Include system messages from frontend (skill content, context, personality)
    system_msgs = [m for m in messages if m["role"] == "system"]
    history = [m for m in messages if m["role"] in ("user", "assistant")]
    if not history:
        return {"message": {"role": "assistant", "content": "Send a message to start."}}

    ctx = [*system_msgs, *history]
    max_turns = 5
    for _turn in range(max_turns):
        data = await _llm_call(ctx, model, url, tools=TOOLS)
        msg = _extract_message(data)
        if not msg:
            return {"message": {"role": "assistant", "content": "LLM not reachable"}}

        content = _extract_content(msg)
        tool_calls = _extract_tool_calls(msg)

        if not tool_calls:
            # LLM is done — return final answer
            return {"message": {"role": "assistant", "content": content or "Done."}}

        # Execute tool calls
        ctx.append({"role": "assistant", "content": content or "", "tool_calls": tool_calls})
        for tc in tool_calls:
            fn = tc.get("function", {})
            name = fn.get("name", "") if isinstance(fn, dict) else ""
            raw_args = fn.get("arguments", "{}") if isinstance(fn, dict) else "{}"
            if isinstance(raw_args, str):
                try:
                    parsed_args = json.loads(raw_args)
                except json.JSONDecodeError:
                    parsed_args = {}
            else:
                parsed_args = raw_args

            # Build MCP args
            builder = TOOL_ARG_MAP.get(name)
            if builder:
                mcp_args = builder(parsed_args)
                result = await _dispatch(TOOL_ROUTES[name][0], mcp_args)
            else:
                result = {"error": f"Unknown tool: {name}"}

            result_str = json.dumps(result, default=str, ensure_ascii=False)
            if len(result_str) > 4000:
                result_str = result_str[:4000] + "\n... (truncated)"

            ctx.append(
                {
                    "role": "tool",
                    "content": result_str,
                    "tool_call_id": tc.get("id", ""),
                    "name": name,
                }
            )

    # Max turns exhausted — return whatever we have
    last_msg = _extract_message(await _llm_call(ctx, model, url))
    return {
        "message": {
            "role": "assistant",
            "content": _extract_content(last_msg) or "I've looked into it but need more specific information.",
        }
    }
