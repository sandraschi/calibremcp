"""
Minimal CalibreMCP Server for testing
"""

from fastmcp import FastMCP

# Create MCP instance
mcp = FastMCP("CalibreMCP Minimal")

async def test_tool() -> str:
    """A simple test tool"""
    return "Hello from Calibre MCP!"

# Register the tool
mcp.tool()(test_tool)

async def main():
    """Main server entry point"""
    await mcp.run_stdio_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())