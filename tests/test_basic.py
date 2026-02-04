import asyncio

from src.calibre_mcp.tools.system import manage_system


async def test():
    try:
        result = await manage_system("list_tools")
        print("Available tools:")
        for tool in result["tools"]:
            print(f"  - {tool['name']}: {tool['description']}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test())
