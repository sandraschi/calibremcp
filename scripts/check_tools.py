"""Check what tools are registered."""

import asyncio
import sys

sys.path.insert(0, "src")

# Import tools to trigger registration
from calibre_mcp import tools  # noqa: F401
from calibre_mcp.server import mcp
from calibre_mcp.tools import book_tools  # noqa: F401


async def check_tools():
    tools_dict = await mcp.get_tools()
    search_tools = [k for k in tools_dict.keys() if "search" in k.lower() or "book" in k.lower()]
    print(f"Total tools: {len(tools_dict)}")
    print(f"Search/book tools: {search_tools[:10]}")
    print(f"All tools: {list(tools_dict.keys())[:20]}")


if __name__ == "__main__":
    asyncio.run(check_tools())
