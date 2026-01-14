import sys
import os

# Add src to path
cwd = os.getcwd()
src_path = os.path.join(cwd, "src")
sys.path.insert(0, src_path)

print(f"CWD: {cwd}")
print(f"Added to path: {src_path}")

print("Attempting to import calibre_mcp...")
try:
    # First, force stdio detection to False so we DONT redirect in __init__
    # This allows us to see output if possible, OR we confirm if the crash is IN the redirection logic
    # But __init__.py checks sys.stdin.isatty().
    # Let's mock it to be True (interactive) so redirection is skipped.

    # Actually, let's keep it as is. If I run this from terminal, isatty will be True.
    # So __init__.py WILL NOT redirect.
    # This is perfect. If I see the crash here, then we know the crash happens regardless of redirection.
    # If I DO NOT see the crash here, then the crash is CAUSED by redirection loop or file access.

    # Mock isatty to force _is_stdio = True
    sys.stdin.isatty = lambda: False

    import calibre_mcp

    print("Import success!")
except Exception as e:
    print(f"Import FAILED: {e}")
    import traceback

    traceback.print_exc()

print("Script finished.")
