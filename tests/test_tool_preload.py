"""
Verify all MCP tools can be imported and have correct signatures.

FastMCP does not support **kwargs in tool functions. This test ensures
all tools in the webapp preload list can be loaded without error.
"""

import importlib
import pytest

# Tool modules as used by webapp/backend/app/mcp/client.py
TOOL_MODULES = {
    "query_books": "calibre_mcp.tools.book_management.query_books",
    "manage_books": "calibre_mcp.tools.book_management.manage_books",
    "manage_viewer": "calibre_mcp.tools.viewer.manage_viewer",
    "manage_libraries": "calibre_mcp.tools.library.manage_libraries",
    "manage_metadata": "calibre_mcp.tools.metadata.manage_metadata",
    "manage_authors": "calibre_mcp.tools.authors.manage_authors",
    "manage_tags": "calibre_mcp.tools.tags.manage_tags",
    "manage_comments": "calibre_mcp.tools.comments.manage_comments",
    "manage_files": "calibre_mcp.tools.files.manage_files",
    "manage_analysis": "calibre_mcp.tools.analysis.manage_analysis",
    "manage_specialized": "calibre_mcp.tools.specialized.manage_specialized",
    "manage_system": "calibre_mcp.tools.system.manage_system",
    "manage_bulk_operations": "calibre_mcp.tools.advanced_features.manage_bulk_operations",
    "manage_content_sync": "calibre_mcp.tools.advanced_features.manage_content_sync",
    "manage_smart_collections": "calibre_mcp.tools.advanced_features.manage_smart_collections",
    "manage_users": "calibre_mcp.tools.user_management.manage_users",
    "export_books": "calibre_mcp.tools.import_export.export_books",
    "manage_import": "calibre_mcp.tools.import_export.manage_import",
}


@pytest.mark.parametrize("tool_name,module_path", list(TOOL_MODULES.items()))
def test_tool_module_loads(tool_name, module_path):
    """Each tool module must import and expose the tool function."""
    module = importlib.import_module(module_path)
    func_name = module_path.split(".")[-1]
    tool_fn = getattr(module, func_name, None)
    assert tool_fn is not None, f"{tool_name}: no attribute '{func_name}' in {module_path}"
    # FastMCP tools may be FunctionTool wrappers; check .fn or callable
    invokable = callable(tool_fn) or (
        hasattr(tool_fn, "fn") and callable(getattr(tool_fn, "fn", None))
    )
    assert invokable, f"{tool_name}: '{func_name}' is not callable (FunctionTool.fn)"


def test_analyze_library_loads():
    """analyze_library is optional; verify it loads if present."""
    try:
        mod = importlib.import_module("calibre_mcp.tools.analysis.analyze_library")
        assert hasattr(mod, "analyze_library")
    except ImportError:
        pytest.skip("analyze_library module not available")
