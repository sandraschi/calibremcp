"""
CalibreMCP DXT Entry Point

Standard DXT-conformant entry point for CalibreMCP server.
Handles Python path setup and launches the FastMCP 2.1 server.
"""

import sys
import os
from pathlib import Path

# Add parent/src directory to Python path
repo_root = Path(__file__).parent.parent
src_path = repo_root / "src"
sys.path.insert(0, str(src_path))

# Now import and run the server
from calibre_mcp.server import main

if __name__ == "__main__":
    print("🚀 Starting CalibreMCP - DXT Packaged Version")
    print(f"📂 Repository: {repo_root}")
    print(f"🐍 Python path: {src_path}")
    print("📚 Austrian efficiency for Sandra's 1000+ book collection!")
    print("🎯 DXT-packaged MCP server ready!")
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 CalibreMCP server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
