#!/usr/bin/env python3
"""
Scan repository for incorrect description= pattern.

Checks repo for @mcp.tool(description=...) and reports findings.
"""

import re
from pathlib import Path


def scan_repo(repo_path: Path) -> dict:
    """Scan a repository for description= usage.

    Args:
        repo_path: Path to repository

    Returns:
        Dict with repo name, files with issues, and count
    """
    result = {
        "name": repo_path.name,
        "path": str(repo_path),
        "files_with_description": [],
        "total_count": 0,
    }

    # Find all Python files
    for py_file in repo_path.rglob("*.py"):
        if ".git" in str(py_file) or "__pycache__" in str(py_file):
            continue

        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")

            # Look for @mcp.tool( followed by description=
            pattern = r"@mcp\.tool\([^)]*description="
            matches = re.findall(pattern, content, re.DOTALL)

            if matches:
                result["files_with_description"].append(str(py_file.relative_to(repo_path)))
                result["total_count"] += len(matches)

        except Exception:
            pass  # Skip files that can't be read

    return result


def main():
    import sys

    if len(sys.argv) > 1:
        repo_path = Path(sys.argv[1])
    else:
        repo_path = Path(".")

    print("Scanning repository for description= parameter...")
    print("=" * 60)

    result = scan_repo(repo_path)

    if result["total_count"] > 0:
        print(
            f"Found {result['total_count']} issues in {len(result['files_with_description'])} files:"
        )
        for file_path in result["files_with_description"]:
            print(f"  - {file_path}")
    else:
        print("Clean! No description= parameters found.")

    print("=" * 60)


if __name__ == "__main__":
    main()
