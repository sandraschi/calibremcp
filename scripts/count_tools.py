"""Count registered MCP tools."""

import asyncio

from calibre_mcp.server import mcp
from calibre_mcp.tools import register_tools


async def main():
    # Register all tools with the MCP server
    register_tools(mcp)

    # Get tools
    tools = await mcp.get_tools()
    print(f"Total tools: {len(tools)}")
    for i, name in enumerate(sorted(tools.keys()), 1):
        print(f"  {i}. {name}")


if __name__ == "__main__":
    asyncio.run(main())
