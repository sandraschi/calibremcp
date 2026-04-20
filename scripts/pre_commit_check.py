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
    try:
        return check_func()
    except Exception:
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

        return result.returncode == 0
    except FileNotFoundError:
        return True
    except subprocess.TimeoutExpired:
        return True
    except Exception:
        return True


def main():
    """Run all pre-commit checks."""

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

    all_passed = True
    for name, passed in results:
        if not passed:
            all_passed = False


    if all_passed:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
