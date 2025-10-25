"""
Simple syntax check for CalibreMCP server
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing imports...")
    
    # Test basic imports first
    from calibre_mcp.config import CalibreConfig
    print("Config import successful")
    
    from calibre_mcp.calibre_api import CalibreAPIClient, CalibreAPIError
    print("API client import successful")
    
    # Now test the main server
    from calibre_mcp.server import mcp
    print("Server import successful")
    
    print("All imports successful! CalibreMCP Phase 2 syntax is valid.")
    
    # Test FastMCP server creation
    print(f"Server name: {mcp.name}")
    print(f"Total tools registered: {len(mcp.tools)}")
    
    # List all tools
    print("\nAvailable tools:")
    for i, tool_name in enumerate(mcp.tools.keys(), 1):
        print(f"  {i:2d}. {tool_name}")
    
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except SyntaxError as e:
    print(f"Syntax error: {e}")
    print(f"   Line {e.lineno}: {e.text}")
    sys.exit(1)
except Exception as e:
    print(f"Other error: {e}")
    sys.exit(1)
