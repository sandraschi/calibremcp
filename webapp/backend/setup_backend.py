"""Setup script to verify backend can import calibre_mcp."""
import sys
import subprocess
from pathlib import Path

def main():
    """Install calibre_mcp and verify imports."""
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent.parent
    
    print("="*60)
    print("Backend Setup - CalibreMCP Import Verification")
    print("="*60)
    print(f"Backend dir: {backend_dir}")
    print(f"Project root: {project_root}")
    print(f"Project root exists: {project_root.exists()}")
    
    # Check if calibre_mcp is already importable
    print("\n[1] Checking if calibre_mcp is already importable...")
    try:
        import calibre_mcp
        print("[PASS] calibre_mcp is already importable")
        print(f"      Location: {calibre_mcp.__file__}")
        return 0
    except ImportError:
        print("[FAIL] calibre_mcp is not importable")
    
    # Try installing in editable mode
    print("\n[2] Installing calibre_mcp in editable mode...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(project_root)],
            cwd=str(backend_dir),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[PASS] Installation successful")
        else:
            print(f"[FAIL] Installation failed: {result.stderr}")
            return 1
    except Exception as e:
        print(f"[FAIL] Installation error: {e}")
        return 1
    
    # Verify import works now
    print("\n[3] Verifying import after installation...")
    try:
        import calibre_mcp
        import calibre_mcp.tools
        print("[PASS] calibre_mcp.tools imported successfully")
        print(f"      Location: {calibre_mcp.__file__}")
        return 0
    except ImportError as e:
        print(f"[FAIL] Import still fails: {e}")
        print("\nTroubleshooting:")
        print(f"  1. Check that {project_root / 'src' / 'calibre_mcp'} exists")
        print(f"  2. Try: cd {backend_dir} && pip install -e ../../")
        print(f"  3. Check Python path: {sys.path[:3]}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
