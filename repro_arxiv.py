import asyncio
import sys
from pathlib import Path

# Add src to sys.path
project_root = Path(r"D:\Dev\repos\calibre-mcp")
sys.path.insert(0, str(project_root / "src"))

from calibre_mcp.tools.import_export.arxiv_client import search_arxiv


async def main():
    result = await search_arxiv("diffusion", max_results=5)
    if result["success"]:
        for _res in result["results"]:
            pass
    else:
        pass

if __name__ == "__main__":
    asyncio.run(main())
