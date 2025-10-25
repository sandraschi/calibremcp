"""
CalibreMCP Launcher Script

Handles Python path setup and launches the FastMCP 2.0 server.
"""

import sys
from pathlib import Path

# Add src directory to Python path
repo_root = Path(__file__).parent
src_path = repo_root / "src"
sys.path.insert(0, str(src_path))

# Now import and run the server
from calibre_mcp.server import main

if __name__ == "__main__":
    print("Starting CalibreMCP Phase 2 - FastMCP 2.0 Server")
    print(f"Repository: {repo_root}")
    print(f"Python path: {src_path}")
    print("Austrian efficiency for Sandra's 1000+ book collection!")
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nCalibreMCP server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
