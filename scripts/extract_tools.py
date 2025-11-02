"""
Tool extraction script for FastMCP 2.12 migration.

This script extracts tool implementations from server.py and moves them
to the appropriate categorized tool files.
"""

import re
from pathlib import Path


def extract_tool_implementations():
    """Extract all tool implementations from server.py"""

    server_file = Path("src/calibre_mcp/server.py")
    content = server_file.read_text()

    # Find all tool definitions
    tool_pattern = r'@mcp\.tool\(\)\nasync def (\w+)\([^)]*\)[^:]*:\s*"""[^"]*"""\s*(.*?)(?=@mcp\.tool\(\)|if __name__)'

    tools = re.findall(tool_pattern, content, re.DOTALL)

    print(f"Found {len(tools)} tools:")
    for tool_name, implementation in tools:
        print(f"- {tool_name}")

    return tools


if __name__ == "__main__":
    extract_tool_implementations()
