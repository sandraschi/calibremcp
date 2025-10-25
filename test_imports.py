"""
Quick import test for CalibreMCP
"""
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent
src_path = repo_root / "src"
sys.path.insert(0, str(src_path))

print("Testing CalibreMCP imports...")

try:
    print("1. Testing FastMCP import...")
    from fastmcp import FastMCP
    print("   fastmcp import successful")
    
    print("2. Testing config import...")
    from calibre_mcp.config import CalibreConfig
    print("   config import successful")
    
    print("3. Testing API client import...")
    from calibre_mcp.calibre_api import CalibreAPIClient, CalibreAPIError
    print("   API client import successful")
    
    print("4. Testing server import...")
    from calibre_mcp.server import mcp
    print("   server import successful")
    
    print("5. Checking server tools...")
    print(f"   Server name: {mcp.name}")
    print(f"   Total tools: {len(mcp.tools)}")
    
    print("\nALL IMPORTS SUCCESSFUL!")
    print("CalibreMCP Phase 2 is ready to run!")
    
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Other error: {e}")
    sys.exit(1)
