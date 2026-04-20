"""Count registered MCP tools."""

import asyncio

from calibre_mcp.server import mcp
from calibre_mcp.tools import register_tools


async def main():
    # Register all tools with the MCP server
    register_tools(mcp)

    # Get tools
    tools = await mcp.get_tools()
    for _i, _name in enumerate(sorted(tools.keys()), 1):
        pass


if __name__ == "__main__":
    asyncio.run(main())
