import fastmcp
print(f"FastMCP version: {getattr(fastmcp, '__version__', 'unknown')}")
mcp = fastmcp.FastMCP("Test")
print("FastMCP methods:", dir(mcp))
