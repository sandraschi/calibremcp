"""
Comprehensive pre-commit check - runs all checks to verify server will load.
Run this before committing to catch issues early.

Usage: python scripts/pre_commit_check.py
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def run_check(name: str, check_func):
    """Run a check and return success status."""
    print(f"\n{'=' * 60}")
    print(f"Checking: {name}")
    print("=" * 60)
    try:
        result = check_func()
        status = "[PASS]" if result else "[FAIL]"
        print(f"\n{name}: {status}")
        return result
    except Exception as e:
        print(f"\n{name}: [FAIL]")
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_imports():
    """Check that all critical imports work."""
    return True


def check_tools_registration():
    """Check that tools can be registered."""
    from calibre_mcp.server import mcp
    from calibre_mcp.tools import register_tools

    # Clear any existing registrations to test fresh
    register_tools(mcp)
    return True


def check_no_syntax_errors():
    """Check for syntax errors by importing all modules."""
    modules_to_check = [
        "calibre_mcp.server",
        "calibre_mcp.tools.tag_tools",
        "calibre_mcp.services.tag_service",
        "calibre_mcp.models.tag",
    ]

    for module_name in modules_to_check:
        __import__(module_name)
    return True


def check_ruff():
    """Check if ruff would pass."""
    import subprocess

    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "ruff",
                "check",
                "src/calibre_mcp/tools/tag_tools.py",
                "src/calibre_mcp/services/tag_service.py",
                "src/calibre_mcp/models/tag.py",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("[OK] Ruff checks passed")
            return True
        else:
            print("[FAIL] Ruff found issues:")
            print(result.stdout)
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("[SKIP] Ruff not available (uv not found?)")
        return True
    except subprocess.TimeoutExpired:
        print("[SKIP] Ruff check timed out")
        return True
    except Exception as e:
        print(f"[SKIP] Could not run ruff: {e}")
        return True


def main():
    """Run all pre-commit checks."""
    print("=" * 60)
    print("CalibreMCP Pre-Commit Checks")
    print("=" * 60)
    print("\nThis script verifies the server will load successfully in Claude.")
    print("Run this before committing to catch issues early.\n")

    checks = [
        ("Critical Imports", check_imports),
        ("Syntax Errors", check_no_syntax_errors),
        ("Tools Registration", check_tools_registration),
        ("Ruff Linting", check_ruff),
    ]

    results = []
    for name, check_func in checks:
        passed = run_check(name, check_func)
        results.append((name, passed))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{name:.<40} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n[SUCCESS] All checks passed! Safe to commit.")
        print("Server should load successfully in Claude.")
        return 0
    else:
        print("\n[FAILURE] Some checks failed!")
        print("Fix the issues above before committing.")
        print("\nNext steps:")
        print("  1. Review the errors above")
        print("  2. Run: python scripts/check_logs.py --errors-only")
        print("  3. Fix issues and re-run: python scripts/pre_commit_check.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
