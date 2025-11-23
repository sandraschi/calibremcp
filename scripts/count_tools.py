"""Count registered MCP tools."""
import asyncio
from calibre_mcp.server import mcp


async def main():
    tools = await mcp.get_tools()
    print(f"Total tools: {len(tools)}")
    for i, name in enumerate(sorted(tools.keys()), 1):
        print(f"  {i}. {name}")


if __name__ == "__main__":
    asyncio.run(main())

