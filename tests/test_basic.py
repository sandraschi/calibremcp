import asyncio

from src.calibre_mcp.tools.system import manage_system


async def test():
    try:
        result = await manage_system("list_tools")
        for _tool in result["tools"]:
            pass
    except Exception:
        pass


if __name__ == "__main__":
    asyncio.run(test())
