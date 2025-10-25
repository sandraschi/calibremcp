"""
Test script to verify Calibre MCP integration with Claude Desktop.

This script tests the basic functionality of the Calibre MCP server
and verifies it can be properly called from Claude Desktop.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from calibre_mcp.server import mcp
from calibre_mcp.config import CalibreConfig

async def test_claude_integration():
    """Test the Calibre MCP server integration with Claude Desktop."""
    print("Testing Calibre MCP integration with Claude Desktop...")
    
    # Initialize with default config
    config = CalibreConfig(
        server_url="http://localhost:8080",
        username="admin",  # Update with your Calibre username
        password="admin123"  # Update with your Calibre password
    )
    
    try:
        # Get available tools
        tools = await mcp.get_tools()
        print(f"Found {len(tools)} tools in the MCP server")
        
        # Test list_books
        print("\nTesting list_books...")
        result = await mcp.call_tool("list_books", {"limit": 3})
        print(f"Found {len(result) if result else 0} books")
        
        # Test search_books
        print("\nTesting search_books...")
        result = await mcp.call_tool("search_books", {"text": "test", "limit": 2})
        print(f"Search results: {len(result) if result else 0} books found")
        
        # Test list_libraries
        print("\nTesting list_libraries...")
        libraries = await mcp.call_tool("list_libraries", {})
        print(f"Libraries: {libraries}")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_claude_integration())
