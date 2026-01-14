"""
Minimal CalibreMCP Server for testing
"""

print("MINIMAL SERVER: Starting...", file=__import__('sys').stderr)

from fastmcp import FastMCP
print("MINIMAL SERVER: FastMCP imported", file=__import__('sys').stderr)

# Create MCP instance
mcp = FastMCP("CalibreMCP Minimal")
print("MINIMAL SERVER: MCP instance created", file=__import__('sys').stderr)

@mcp.tool()
async def test_tool() -> str:
    """A simple test tool"""
    return "Hello from Calibre MCP!"

print("MINIMAL SERVER: Tool registered", file=__import__('sys').stderr)

async def main():
    """Main server entry point"""
    print("MINIMAL SERVER: Main function called", file=__import__('sys').stderr)
    await mcp.run_stdio_async()

if __name__ == "__main__":
    import asyncio
    print("MINIMAL SERVER: Running main", file=__import__('sys').stderr)
    asyncio.run(main())