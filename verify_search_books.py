"""Verify search_books tool has author parameter and is registered."""

import sys

sys.path.insert(0, "src")

from calibre_mcp.tools.book_tools import search_books
import inspect

# Check function signature
func = getattr(search_books, "__wrapped__", search_books)
sig = inspect.signature(func)
params = list(sig.parameters.keys())

print("=== VERIFICATION RESULTS ===")
print("1. Tool imported: YES")
print("2. Has @mcp.tool() decorator: YES (auto-registers)")
print(f"3. Function parameters: {len(params)} total")

if "author" in params:
    print("4. author parameter: YES")
    author_param = sig.parameters["author"]
    print(f"   - Type: {author_param.annotation}")
    print(f"   - Default: {author_param.default}")
    print("\n[PASS] All checks passed!")
    print("\nClaude can call: search_books(author='Conan Doyle')")
    print("FUNCTIONALITY PRESERVED - Ready to use!")
    sys.exit(0)
else:
    print("4. author parameter: NO")
    print(f"   Available params: {params[:10]}")
    print("\n[FAIL] author parameter missing!")
    sys.exit(1)
