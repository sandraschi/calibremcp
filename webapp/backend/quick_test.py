"""Quick test to verify MCP imports work."""
import sys
from pathlib import Path

# Add src to path (same logic as client.py)
project_root = Path(__file__).resolve().parent.parent.parent
src_path = project_root / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

print(f"Project root: {project_root}")
print(f"Source path: {src_path}")
print(f"Source exists: {src_path.exists()}")

# Test imports
print("\nTesting imports...")
try:
    import calibre_mcp.tools
    print("[PASS] calibre_mcp.tools imported")
except Exception as e:
    print(f"[FAIL] calibre_mcp.tools: {e}")
    sys.exit(1)

try:
    from calibre_mcp.tools.book_management.query_books import query_books
    print("[PASS] query_books imported")
except Exception as e:
    print(f"[FAIL] query_books: {e}")
    sys.exit(1)

try:
    from calibre_mcp.tools.library.manage_libraries import manage_libraries
    print("[PASS] manage_libraries imported")
except Exception as e:
    print(f"[FAIL] manage_libraries: {e}")
    sys.exit(1)

try:
    from calibre_mcp.tools.metadata.manage_metadata import manage_metadata
    print("[PASS] manage_metadata imported")
except Exception as e:
    print(f"[FAIL] manage_metadata: {e}")
    sys.exit(1)

try:
    from calibre_mcp.tools.viewer.manage_viewer import manage_viewer
    print("[PASS] manage_viewer imported")
except Exception as e:
    print(f"[FAIL] manage_viewer: {e}")
    sys.exit(1)

try:
    from calibre_mcp.tools.book_management.manage_books import manage_books
    print("[PASS] manage_books imported")
except Exception as e:
    print(f"[FAIL] manage_books: {e}")
    sys.exit(1)

print("\n[SUCCESS] All imports successful!")
