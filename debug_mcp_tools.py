import sys

sys.path.append(r"d:\Dev\repos\calibre-mcp\src")
import asyncio

from calibre_mcp.server import mcp


async def test_tools():
    from calibre_mcp.tools import get_available_tools, register_tools

    register_tools(mcp)

    get_available_tools()


if __name__ == "__main__":
    asyncio.run(test_tools())
