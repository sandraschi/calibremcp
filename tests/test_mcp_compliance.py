"""
Calibre MCP Server — FastMCP 3.x Compliance Tests.

Verifies that the server is properly packaged, has required metadata,
and conforms to FastMCP / MCPB conventions.
"""

import json
import sys
from pathlib import Path

import pytest

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from calibre_mcp.server import mcp

_REPO_ROOT = Path(__file__).parent.parent


class TestFastMCPCompliance:
    """Test suite for FastMCP 3.x compliance."""

    @pytest.fixture
    def server(self):
        """Get the MCP server instance."""
        return mcp

    def test_has_required_metadata(self):
        """Server must have a name attribute."""
        assert hasattr(mcp, "name")
        assert mcp.name == "CalibreMCP"

    def test_has_tool_decorator(self, server):
        """Server must expose the @tool decorator used by portmanteau tools."""
        assert hasattr(server, "tool")
        assert callable(server.tool)

    def test_mcpb_manifest_exists(self):
        """MCPB manifest.json must exist and be valid JSON with required fields."""
        manifest_path = _REPO_ROOT / "manifest.json"
        assert manifest_path.exists(), "manifest.json not found in repo root"

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in manifest.json: {e}")

        for field in ("manifest_version", "name", "version", "server"):
            assert field in manifest, f"Missing required field in manifest.json: {field}"

        assert "type" in manifest["server"], "Missing server.type in manifest.json"
        assert "entry_point" in manifest["server"], "Missing server.entry_point in manifest.json"
        assert "mcp_config" in manifest["server"], "Missing server.mcp_config in manifest.json"
        assert "command" in manifest["server"]["mcp_config"], (
            "Missing server.mcp_config.command in manifest.json"
        )
        assert "user_config" in manifest, "Missing user_config in manifest.json"
        assert isinstance(manifest["user_config"], dict), "user_config must be a dict"
        assert "tools" in manifest, "Missing tools in manifest.json"
        assert isinstance(manifest["tools"], list), "tools must be a list"
        assert len(manifest["tools"]) > 0, "No tools defined in manifest.json"

    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Server instance must exist and have the tool decorator."""
        assert mcp is not None
        assert hasattr(mcp, "tool")

    def test_pyproject_toml_exists_and_is_valid(self):
        """pyproject.toml must exist and contain the required TOML sections."""
        pyproject_path = _REPO_ROOT / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml not found"

        content = pyproject_path.read_text(encoding="utf-8")
        for section in ("[build-system]", "[project]", "name = ", "version = "):
            assert section in content, f"pyproject.toml missing: {section}"

    def test_pyproject_lists_fastmcp_dependency(self):
        """pyproject.toml must declare fastmcp as a dependency."""
        pyproject_path = _REPO_ROOT / "pyproject.toml"
        content = pyproject_path.read_text(encoding="utf-8")
        assert "fastmcp" in content, "fastmcp not listed in pyproject.toml dependencies"

    def test_entry_point_exists(self):
        """The declared console-script entry point module must be importable."""
        # pyproject.toml declares: schip-mcp-calibre = "calibre_mcp.__main__:run"
        from calibre_mcp.__main__ import run  # noqa: F401

    # ------------------------------------------------------------------
    # Tests that require a live Calibre library are skipped in CI
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_list_books_tool_skip(self, server):
        """Tool execution tests require a real library — skipped in non-integration runs."""
        assert server is not None
        pytest.skip("Tool execution tests require real library — use integration suite")

    @pytest.mark.asyncio
    async def test_search_books_tool_skip(self, server):
        """Tool execution tests require a real library — skipped in non-integration runs."""
        assert server is not None
        pytest.skip("Tool execution tests require real library — use integration suite")
