"""
DEPRECATED: Individual system tools are deprecated in favor of the manage_system
portmanteau tool (see tools/system/manage_system.py). These functions are kept
as helpers but are no longer registered with FastMCP 2.13+.

Use manage_system(operation="...") instead:
- help() → manage_system(operation="help", level=..., topic=...)
- status() → manage_system(operation="status", status_level=..., focus=...)
- tool_help() → manage_system(operation="tool_help", tool_name=..., tool_help_level=...)
- list_tools() → manage_system(operation="list_tools", category=...)
- hello_world() → manage_system(operation="hello_world")
- health_check() → manage_system(operation="health_check")
"""

import os
import platform
import psutil
import sys
import inspect
from datetime import datetime
from typing import Dict, Optional, Any, List
from enum import Enum


# Import the MCP server instance and helper functions
from ...server import mcp, get_api_client, current_library
from ...logging_config import get_logger, log_operation, log_error
from ...config import CalibreConfig
from ...db.database import DatabaseService

logger = get_logger("calibremcp.tools.system")


class HelpLevel(str, Enum):
    """Help detail levels"""

    BASIC = "basic"  # Quick overview and essential commands
    INTERMEDIATE = "intermediate"  # Detailed tool descriptions and workflows
    ADVANCED = "advanced"  # Technical details and architecture
    EXPERT = "expert"  # Development and troubleshooting


class StatusLevel(str, Enum):
    """Status detail levels"""

    BASIC = "basic"  # Core system status
    INTERMEDIATE = "intermediate"  # Tool availability and configuration
    ADVANCED = "advanced"  # Performance metrics and system resources
    DIAGNOSTIC = "diagnostic"  # Detailed troubleshooting information


# Help documentation with multiple detail levels
HELP_DOCS = {
    "overview": {
        "title": "CalibreMCP Server Help",
        "description": {
            "basic": (
                "CalibreMCP is a FastMCP 2.14+ server that connects AI assistants to your Calibre "
                "ebook library. Search, browse, open books, and manage metadata via natural language."
            ),
            "intermediate": (
                "CalibreMCP uses portmanteau tools: single tools with an operation parameter "
                "for related actions. Direct database access (no Calibre app needed) or Calibre Content "
                "Server for remote. Auto-discovers libraries from Calibre config. Supports query_books, "
                "manage_books, manage_libraries, manage_viewer, and more."
            ),
            "advanced": (
                "Production MCP server with modular architecture, structured error handling, "
                "and 20+ portmanteau tools. Access: direct SQLite (metadata.db) or Calibre Content Server API. "
                "Library discovery: global.py, library_infos.json, CALIBRE_LIBRARY_PATH. "
                "Extended metadata (translator, first_published, user comments) in separate SQLite. "
                "Full search with author, tag, series, publisher, rating, date filters."
            ),
            "expert": (
                "FastMCP 2.14+ with cooperative/compositing patterns. Tools: query_books (search/list/by_author/by_series), "
                "manage_books (get/add/update/delete/details), manage_libraries (list/switch/stats), manage_authors, "
                "manage_series, manage_tags, manage_viewer (open_file/open_random), manage_metadata, manage_files, "
                "manage_comments, manage_descriptions, manage_publishers, manage_times, manage_user_comments, "
                "manage_extended_metadata, manage_specialized, manage_bulk_operations, manage_content_sync, "
                "manage_smart_collections, manage_users, manage_system. All return structured dicts."
            ),
        },
    },
    "tools": {
        "core": {
            "title": "Core Book Operations",
            "description": {
                "basic": "query_books and manage_books for searching and retrieving books.",
                "intermediate": "query_books(operation='search') with author, tag, text filters. manage_books for get/details.",
                "advanced": "Full query_books filters: author, tags, series, publisher, rating, pubdate, added_after, formats.",
                "expert": "Verb mapping: search/list/find all use operation='search'. by_author/by_series use IDs.",
            },
            "tools": ["query_books", "manage_books"],
        },
        "library": {
            "title": "Library Management",
            "description": {
                "basic": "manage_libraries: list libraries, switch active, get stats.",
                "intermediate": "Auto-discovery from Calibre config. CALIBRE_LIBRARY_PATH for direct access.",
                "advanced": "Multiple libraries supported. Switch changes active DB; stats per library.",
                "expert": "library_infos.json, global.py parsed. CALIBRE_SERVER_URL for remote.",
            },
            "tools": ["manage_libraries"],
        },
        "entities": {
            "title": "Authors, Series, Tags",
            "description": {
                "basic": "manage_authors, manage_series, manage_tags for list/get/get_books.",
                "intermediate": "Browse entities, then filter books. Pagination with limit/offset.",
                "advanced": "Series with index. Tags hierarchical. Author sort names.",
                "expert": "Linked to metadata.db. manage_series stats, manage_tags get_books.",
            },
            "tools": ["manage_authors", "manage_series", "manage_tags"],
        },
        "viewer": {
            "title": "Viewer",
            "description": {
                "basic": "manage_viewer(operation='open_file', book_id=N) opens in system default app.",
                "intermediate": "open_random by author/tag/series. Preferred format: EPUB, PDF, MOBI.",
                "advanced": "File path derived from library path + book path + format filename.",
                "expert": "Platform-specific open (subprocess). Fallback formats if primary missing.",
            },
            "tools": ["manage_viewer"],
        },
        "metadata": {
            "title": "Metadata and Content",
            "description": {
                "basic": "manage_metadata (show, update), manage_descriptions, manage_comments.",
                "intermediate": "manage_publishers, manage_times (added, published). manage_user_comments (CalibreMCP SQLite).",
                "advanced": "manage_extended_metadata: translator, first_published in external DB.",
                "expert": "metadata.db unchanged. calibre_mcp_data.db for user comments, extended fields.",
            },
            "tools": [
                "manage_metadata",
                "manage_descriptions",
                "manage_comments",
                "manage_publishers",
                "manage_times",
                "manage_user_comments",
                "manage_extended_metadata",
            ],
        },
        "files": {
            "title": "File Operations",
            "description": {
                "basic": "manage_files for format operations, add/remove formats.",
                "intermediate": "Convert, add format, remove format. Path resolution from library.",
                "advanced": "Bulk format operations via manage_bulk_operations.",
                "expert": "File naming, path sanitization. Preferred format order.",
            },
            "tools": ["manage_files", "manage_bulk_operations"],
        },
        "advanced": {
            "title": "Advanced Features",
            "description": {
                "basic": "manage_specialized, manage_content_sync, manage_smart_collections.",
                "intermediate": "Content sync, smart collections (saved searches), specialized curation.",
                "advanced": "manage_users for auth. Export via import_export tools.",
                "expert": "Full portmanteau set. Integration with Calibre plugin for extended metadata edit.",
            },
            "tools": [
                "manage_specialized",
                "manage_content_sync",
                "manage_smart_collections",
                "manage_users",
            ],
        },
        "system": {
            "title": "System",
            "description": {
                "basic": "manage_system: help, status, tool_help, list_tools, hello_world, health_check.",
                "intermediate": "status levels: basic, intermediate, advanced, diagnostic.",
                "advanced": "tool_help(tool_name) for per-tool docs. list_tools(category) for discovery.",
                "expert": "health_check machine-readable. Error handling via handle_tool_error.",
            },
            "tools": ["manage_system"],
        },
    },
    "examples": {
        "basic": [
            "# Search books by author",
            'query_books(operation="search", author="Conan Doyle")',
            "",
            "# List all books",
            'query_books(operation="list", limit=20)',
            "",
            "# Get book details",
            "manage_books(operation='get', book_id=123)",
            "",
            "# Open book in default viewer",
            "manage_viewer(operation='open_file', book_id=123)",
            "",
            "# List libraries",
            'manage_libraries(operation="list")',
        ],
        "intermediate": [
            "# Search with multiple filters",
            'query_books(operation="search", author="Agatha Christie", tags=["mystery"], min_rating=4)',
            "",
            "# Switch library",
            'manage_libraries(operation="switch", library_name="Calibre-Bibliothek IT")',
            "",
            "# Get library stats",
            'manage_libraries(operation="stats", library_name="Calibre-Bibliothek")',
            "",
            "# Open random book by tag",
            'manage_viewer(operation="open_random", tag="programming")',
            "",
            "# List authors",
            'manage_authors(operation="list", limit=50)',
        ],
        "advanced": [
            "# Search by date range",
            'query_books(operation="search", pubdate_start="2020-01-01", pubdate_end="2024-12-31")',
            "",
            "# Search recently added",
            'query_books(operation="search", added_after="2024-12-01", limit=10)',
            "",
            "# Get series books",
            'manage_series(operation="get_books", series_id=5, limit=20)',
            "",
            "# Update metadata",
            'manage_metadata(operation="update", book_id=123, title="New Title")',
            "",
            "# System status",
            'manage_system(operation="status", status_level="intermediate")',
        ],
        "expert": [
            "# Tool help",
            'manage_system(operation="tool_help", tool_name="query_books", tool_help_level="expert")',
            "",
            "# List tools by category",
            'manage_system(operation="list_tools", category="library")',
            "",
            "# Health check",
            'manage_system(operation="health_check")',
            "",
            "# User comments (CalibreMCP SQLite)",
            'manage_user_comments(operation="get", book_id=123)',
            "",
            "# Extended metadata",
            'manage_extended_metadata(operation="get", book_id=123)',
        ],
    },
}


async def help_helper(
    level: HelpLevel, topic: Optional[str] = None
) -> str:
    """
    Helper for manage_system(operation='help'). Generates multi-level help content.
    Used by manage_system; not registered as a standalone MCP tool.
    """
    try:
        log_operation(logger, "help_requested", level=level.value, topic=topic)

        content = []

        # Overview
        overview = HELP_DOCS["overview"]
        content.append(f"# {overview['title']}")
        content.append("")
        content.append(overview["description"][level.value])
        content.append("")

        # Tools section
        if not topic or topic == "tools":
            content.append("## Available Tools")
            content.append("")

            for category, info in HELP_DOCS["tools"].items():
                content.append(f"### {info['title']}")
                content.append("")
                content.append(info["description"][level.value])
                content.append("")
                if level in [HelpLevel.ADVANCED, HelpLevel.EXPERT]:
                    content.append("**Tools:**")
                    for tool_name in info["tools"]:
                        content.append(f"- `{tool_name}()`")
                    content.append("")

        # Examples
        content.append("## Examples")
        content.append("")
        for example in HELP_DOCS["examples"][level.value]:
            content.append(example)
        content.append("")

        # Configuration (intermediate+)
        if level in [HelpLevel.INTERMEDIATE, HelpLevel.ADVANCED, HelpLevel.EXPERT]:
            content.append("## Configuration")
            content.append("")
            content.append("- CALIBRE_LIBRARY_PATH: Library directory (direct DB access)")
            content.append("- CALIBRE_SERVER_URL: Calibre Content Server (optional, remote)")
            content.append("- Auto-discovery: global.py, library_infos.json")
            content.append("")

        # Troubleshooting (advanced+)
        if level in [HelpLevel.ADVANCED, HelpLevel.EXPERT]:
            content.append("## Troubleshooting")
            content.append("")
            content.append("1. **Library not found**: manage_libraries(operation='list') to see discovered libraries")
            content.append("2. **DB offline**: Ensure library path exists; check CALIBRE_LIBRARY_PATH")
            content.append("3. **Open file fails**: Verify book has EPUB/PDF; check library path resolution")
            content.append("")

        return "\n".join(content)

    except Exception as e:
        log_error(logger, "help_error", e)
        return f"Error generating help: {str(e)}"


# Deprecated: use manage_system(operation="help") - kept as helper only, not registered
async def help(level: HelpLevel = HelpLevel.BASIC, topic: Optional[str] = None) -> str:
    """
    Comprehensive help system with multiple detail levels.

    Provides contextual assistance and documentation for CalibreMCP features,
    organized by knowledge levels from basic usage to advanced technical details.

    Args:
        level: Help detail level (basic/intermediate/advanced/expert)
        topic: Specific topic to focus on (optional)

    Returns:
        Formatted help content with examples and guidance
    """
    return await help_helper(level=level, topic=topic)


# Deprecated: use manage_system(operation="status") - kept as helper only, not registered
async def status(
    level: StatusLevel = StatusLevel.BASIC, focus: Optional[str] = None
) -> str:
    """
    Comprehensive system status and diagnostic information.

    Provides different levels of diagnostic information about the CalibreMCP
    server, library connections, and system health.

    Args:
        level: Status detail level (basic/intermediate/advanced/diagnostic)
        focus: Optional focus area for detailed information

    Returns:
        Formatted status report with system information
    """
    try:
        log_operation(logger, "status_requested", level=level.value, focus=focus)

        # Get system information
        system_info = {
            "platform": platform.system(),
            "python_version": sys.version,
            "calibremcp_version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
        }

        # Get library information
        config = CalibreConfig()
        libraries = config.list_libraries()

        # Get Calibre connection status
        try:
            client = await get_api_client()
            connection_test = await client.test_connection()
            calibre_status = "connected"
            calibre_info = connection_test
        except Exception as e:
            calibre_status = "disconnected"
            calibre_info = {"error": str(e)}

        # Build status report
        content = []

        # Header
        content.append("# CalibreMCP System Status")
        content.append("")
        content.append(f"**Timestamp:** {system_info['timestamp']}")
        content.append(f"**Version:** {system_info['calibremcp_version']}")
        content.append(f"**Platform:** {system_info['platform']}")
        content.append("")

        # Basic status
        content.append("## Core Status")
        content.append("")
        content.append(f"**Calibre Connection:** {calibre_status.upper()}")
        content.append(f"**Libraries Discovered:** {len(libraries)}")
        content.append(f"**Current Library:** {current_library}")
        content.append("")

        # Library information
        if libraries:
            content.append("## Discovered Libraries")
            content.append("")
            for lib in libraries:
                status_icon = "🟢" if lib["is_active"] else "⚪"
                content.append(f"{status_icon} **{lib['name']}**: {lib['path']}")
            content.append("")

        # Intermediate level - Tool information
        if level in [
            StatusLevel.INTERMEDIATE,
            StatusLevel.ADVANCED,
            StatusLevel.DIAGNOSTIC,
        ]:
            content.append("## Tool Status")
            content.append("")

            # Get actual registered tools dynamically
            try:
                registered_tools = _get_registered_tools()
                content.append(f"**Total Tools Registered:** {len(registered_tools)}")
                content.append("")

                # Group tools by category
                tool_categories = {
                    "Core Operations": [],
                    "Library Management": [],
                    "Analysis": [],
                    "Metadata": [],
                    "Files": [],
                    "System": [],
                    "Other": [],
                }

                for tool in registered_tools:
                    name_lower = tool["name"].lower()
                    if any(
                        x in name_lower
                        for x in ["list_books", "search_books", "get_book"]
                    ):
                        tool_categories["Core Operations"].append(tool)
                    elif any(x in name_lower for x in ["library", "switch"]):
                        tool_categories["Library Management"].append(tool)
                    elif any(
                        x in name_lower
                        for x in ["statistics", "analysis", "series", "tag"]
                    ):
                        tool_categories["Analysis"].append(tool)
                    elif "metadata" in name_lower or "update" in name_lower:
                        tool_categories["Metadata"].append(tool)
                    elif "download" in name_lower or "format" in name_lower:
                        tool_categories["Files"].append(tool)
                    elif any(
                        x in name_lower for x in ["help", "status", "health", "tool"]
                    ):
                        tool_categories["System"].append(tool)
                    else:
                        tool_categories["Other"].append(tool)

                for category, tools in tool_categories.items():
                    if not tools:
                        continue
                    content.append(f"### {category}")
                    content.append(f"**Count:** {len(tools)}")
                    if level == StatusLevel.DIAGNOSTIC:
                        for tool in tools:
                            desc = (
                                tool["description"][:60] + "..."
                                if len(tool.get("description", "")) > 60
                                else tool.get("description", "")
                            )
                            content.append(f"- `{tool['name']}()` - {desc}")
                    else:
                        tool_names = [t["name"] for t in tools[:5]]
                        if len(tools) > 5:
                            tool_names.append(f"... and {len(tools) - 5} more")
                        content.append(f"**Tools:** {', '.join(tool_names)}")
                    content.append("")
            except Exception as e:
                content.append(f"**Error retrieving tool information:** {str(e)}")
                content.append("")

        # Advanced level - Performance metrics
        if level in [StatusLevel.ADVANCED, StatusLevel.DIAGNOSTIC]:
            content.append("## Performance Metrics")
            content.append("")

            try:
                # System resources
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=1)

                content.append(
                    f"**Memory Usage:** {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)"
                )
                content.append(f"**CPU Usage:** {cpu_percent}%")
                content.append("")

                # Python process info
                process = psutil.Process()
                content.append(
                    f"**Python Process Memory:** {process.memory_info().rss // (1024**2)}MB"
                )
                content.append(f"**Python Process CPU:** {process.cpu_percent()}%")
                content.append("")

            except Exception as e:
                content.append(f"**Performance Metrics:** Error retrieving - {str(e)}")
                content.append("")

        # Diagnostic level - Detailed troubleshooting
        if level == StatusLevel.DIAGNOSTIC:
            content.append("## Diagnostic Information")
            content.append("")

            # Calibre connection details
            if calibre_status == "connected":
                content.append("### Calibre Server Details")
                content.append(
                    f"**Server URL:** {calibre_info.get('server_url', 'Unknown')}"
                )
                content.append(
                    f"**Server Version:** {calibre_info.get('version', 'Unknown')}"
                )
                content.append(
                    f"**Total Books:** {calibre_info.get('total_books', 'Unknown')}"
                )
                content.append("")
            else:
                content.append("### Calibre Connection Issues")
                content.append(
                    f"**Error:** {calibre_info.get('error', 'Unknown error')}"
                )
                content.append("")

            # Configuration details
            content.append("### Configuration")
            content.append(
                f"**Auto-discover Libraries:** {config.auto_discover_libraries}"
            )
            content.append(f"**Server URL:** {config.server_url}")
            content.append(f"**Timeout:** {config.timeout}s")
            content.append(f"**Max Retries:** {config.max_retries}")
            content.append("")

            # Environment variables
            content.append("### Environment Variables")
            env_vars = [
                "CALIBRE_SERVER_URL",
                "CALIBRE_LIBRARY_PATH",
                "CALIBRE_LIBRARIES",
            ]
            for var in env_vars:
                value = "Set" if var in os.environ else "Not set"
                content.append(f"**{var}:** {value}")
            content.append("")

        return "\n".join(content)

    except Exception as e:
        log_error(logger, "status_error", e)
        return f"Error generating status: {str(e)}"


async def status_helper(
    level: StatusLevel, focus: Optional[str] = None
) -> str:
    """Helper for manage_system(operation='status')."""
    return await status(level=level, focus=focus)


def _get_registered_tools() -> List[Dict[str, Any]]:
    """
    Get all registered tools from the MCP server.

    Returns:
        List of tool metadata dictionaries
    """
    tools = []
    try:
        # FastMCP stores tools in _tools dict
        if hasattr(mcp, "_tools"):
            for tool_name, tool_obj in mcp._tools.items():
                tool_info = {
                    "name": tool_name,
                    "description": getattr(tool_obj, "__doc__", "") or "",
                    "signature": str(inspect.signature(tool_obj.func))
                    if hasattr(tool_obj, "func")
                    else "",
                }

                # Try to get parameter info
                if hasattr(tool_obj, "func"):
                    sig = inspect.signature(tool_obj.func)
                    params = []
                    for param_name, param in sig.parameters.items():
                        param_info = {
                            "name": param_name,
                            "type": str(param.annotation)
                            if param.annotation != inspect.Parameter.empty
                            else "Any",
                            "default": param.default
                            if param.default != inspect.Parameter.empty
                            else None,
                            "required": param.default == inspect.Parameter.empty,
                        }
                        params.append(param_info)
                    tool_info["parameters"] = params

                tools.append(tool_info)
    except Exception as e:
        logger.warning(f"Error getting registered tools: {e}")

    return tools


def _get_tool_by_name(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific tool.

    Args:
        tool_name: Name of the tool to look up

    Returns:
        Tool metadata dictionary or None if not found
    """
    tools = _get_registered_tools()
    for tool in tools:
        if tool["name"] == tool_name:
            return tool
    return None


# Deprecated: use manage_system(operation="tool_help") - kept as helper only, not registered
async def tool_help(tool_name: str, level: HelpLevel = HelpLevel.BASIC) -> str:
    """
    Get detailed help for a specific tool.

    Provides comprehensive documentation for a single tool, including
    parameters, return values, examples, and usage patterns at different
    detail levels.

    Args:
        tool_name: Name of the tool to get help for
        level: Detail level for the help content (basic/intermediate/advanced/expert)

    Returns:
        Formatted help content for the specified tool

    Examples:
        # Get basic help for search_books
        tool_help("search_books", level="basic")

        # Get expert-level help with all details
        tool_help("list_libraries", level="expert")
    """
    try:
        log_operation(
            logger, "tool_help_requested", tool_name=tool_name, level=level.value
        )

        # Get tool information
        tool_info = _get_tool_by_name(tool_name)

        if not tool_info:
            # Try to find similar tool names
            all_tools = _get_registered_tools()
            similar = [
                t["name"] for t in all_tools if tool_name.lower() in t["name"].lower()
            ]

            if similar:
                return f"Tool '{tool_name}' not found. Did you mean: {', '.join(similar[:5])}?"
            else:
                return f"Tool '{tool_name}' not found. Use `list_tools()` to see all available tools."

        # Build help content
        content = []
        content.append(f"# {tool_info['name']}")
        content.append("")

        # Description
        if tool_info["description"]:
            content.append(tool_info["description"])
        else:
            content.append(f"Documentation for the `{tool_info['name']}` tool.")
        content.append("")

        # Parameters section
        if "parameters" in tool_info and tool_info["parameters"]:
            content.append("## Parameters")
            content.append("")

            if level in [HelpLevel.BASIC, HelpLevel.INTERMEDIATE]:
                # Basic parameter list
                for param in tool_info["parameters"]:
                    if param["name"] == "self":
                        continue
                    param_str = f"**{param['name']}**"
                    if param["type"] != "Any":
                        param_str += f": {param['type']}"
                    if not param["required"]:
                        param_str += " (optional)"
                    if param["default"] is not None:
                        param_str += f" = {repr(param['default'])}"
                    content.append(f"- {param_str}")
            else:
                # Advanced parameter details
                for param in tool_info["parameters"]:
                    if param["name"] == "self":
                        continue
                    content.append(f"### `{param['name']}`")
                    content.append("")
                    content.append(f"- **Type:** `{param['type']}`")
                    content.append(
                        f"- **Required:** {'Yes' if param['required'] else 'No'}"
                    )
                    if param["default"] is not None:
                        content.append(f"- **Default:** `{repr(param['default'])}`")
                    content.append("")

            content.append("")

        # Signature
        if level in [HelpLevel.ADVANCED, HelpLevel.EXPERT] and tool_info.get(
            "signature"
        ):
            content.append("## Function Signature")
            content.append("")
            content.append("```python")
            content.append(f"async def {tool_info['name']}{tool_info['signature']}")
            content.append("```")
            content.append("")

        # Examples based on tool category
        examples_section = _get_tool_examples(tool_name, level)
        if examples_section:
            content.append("## Examples")
            content.append("")
            content.extend(examples_section)
            content.append("")

        # Related tools
        if level in [HelpLevel.INTERMEDIATE, HelpLevel.ADVANCED, HelpLevel.EXPERT]:
            related = _get_related_tools(tool_name)
            if related:
                content.append("## Related Tools")
                content.append("")
                for related_tool in related:
                    content.append(f"- `{related_tool}`")
                content.append("")

        # Expert-level tips
        if level == HelpLevel.EXPERT:
            content.append("## Expert Tips")
            content.append("")
            tips = _get_tool_tips(tool_name)
            if tips:
                for tip in tips:
                    content.append(f"- {tip}")
            else:
                content.append("- This tool follows FastMCP 2.12 conventions")
                content.append("- All parameters are type-checked automatically")
                content.append("- Async operations are non-blocking")
            content.append("")

        return "\n".join(content)

    except Exception as e:
        log_error(logger, "tool_help_error", e, tool_name=tool_name)
        return f"Error generating tool help: {str(e)}"


async def tool_help_helper(
    tool_name: str, level: HelpLevel = HelpLevel.BASIC
) -> str:
    """Helper for manage_system(operation='tool_help')."""
    return await tool_help(tool_name=tool_name, level=level)


def _get_tool_examples(tool_name: str, level: HelpLevel) -> List[str]:
    """Get example usage for a tool."""
    examples = []

    # Tool-specific examples
    tool_examples = {
        "query_books": [
            "# Search for books",
            "result = query_books(operation='search', text='python programming')",
            "",
            "# List all books",
            "result = query_books(operation='list', limit=50)",
            "",
            "# Search by author",
            "result = query_books(operation='search', author='Conan Doyle')",
        ],
        "manage_books": [
            "# Get book by ID",
            "book = manage_books(operation='get', book_id=123)",
            "# Get complete book details",
            "book = manage_books(operation='details', book_id=123)",
        ],
        "manage_libraries": [
            "# List all libraries",
            "result = manage_libraries(operation='list')",
            "",
            "# Switch library",
            "result = manage_libraries(operation='switch', library_name='Calibre-Bibliothek IT')",
        ],
        "manage_viewer": [
            "# Open book in default app",
            "manage_viewer(operation='open_file', book_id=123)",
            "",
            "# Open random book by tag",
            "manage_viewer(operation='open_random', tag='programming')",
        ],
        "manage_metadata": [
            "# Update book metadata",
            "manage_metadata(operation='update', book_id=123, title='New Title')",
        ],
    }

    if tool_name in tool_examples:
        examples.extend(tool_examples[tool_name])
    elif level in [HelpLevel.ADVANCED, HelpLevel.EXPERT]:
        examples.append("# Usage example")
        examples.append(f"result = {tool_name}()")

    return examples


def _get_related_tools(tool_name: str) -> List[str]:
    """Get related tools based on functionality."""
    related_map = {
        "query_books": ["manage_books", "manage_metadata"],
        "manage_books": ["query_books", "manage_metadata", "manage_files"],
        "manage_metadata": ["manage_books", "query_books"],
        "manage_files": ["manage_books", "query_books"],
        "list_libraries": ["switch_library", "get_library_stats"],
        "switch_library": ["list_libraries", "get_library_stats"],
    }

    return related_map.get(tool_name, [])


def _get_tool_tips(tool_name: str) -> List[str]:
    """Get expert tips for a tool."""
    tips_map = {
        "query_books": [
            "Use operation='search' for any verb: search, list, find, get, show me",
            "Combine author, tag, series, publisher for precise results",
            "Use limit and offset for pagination on large result sets",
        ],
        "manage_books": [
            "operation='details' returns full metadata including formats",
            "Use get before update to verify book exists",
        ],
        "manage_libraries": [
            "Switch changes active DB; all subsequent queries use that library",
            "Stats are per-library; list shows all discovered libraries",
        ],
        "manage_viewer": [
            "open_file derives path from library + book path + format",
            "Preferred format order: EPUB, PDF, MOBI, AZW3",
        ],
    }

    return tips_map.get(tool_name, [])


# Deprecated: use manage_system(operation="list_tools") - kept as helper only, not registered
async def list_tools(category: Optional[str] = None) -> Dict[str, Any]:
    """
    List all available tools with their descriptions.

    Provides a comprehensive list of all registered tools, optionally
    filtered by category. Useful for discovering available functionality.

    Args:
        category: Optional category filter (e.g., "library", "metadata", "analysis")

    Returns:
        Dictionary containing:
        - total: Total number of tools
        - tools: List of tool information dictionaries
        - categories: Available tool categories

    Examples:
        # List all tools
        result = list_tools()

        # List tools in a specific category
        result = list_tools(category="library")
    """
    try:
        log_operation(logger, "list_tools_requested", category=category)

        all_tools = _get_registered_tools()

        # Filter by category if specified
        if category:
            # Simple category matching
            filtered = [
                t
                for t in all_tools
                if category.lower() in t["name"].lower()
                or category.lower() in (t.get("description", "").lower())
            ]
        else:
            filtered = all_tools

        # Group by inferred categories
        categories = {
            "core": [],
            "library": [],
            "analysis": [],
            "metadata": [],
            "files": [],
            "system": [],
            "other": [],
        }

        for tool in filtered:
            name_lower = tool["name"].lower()
            if any(x in name_lower for x in ["list_books", "search_books", "get_book"]):
                categories["core"].append(tool)
            elif any(x in name_lower for x in ["library", "switch"]):
                categories["library"].append(tool)
            elif any(
                x in name_lower for x in ["statistics", "analysis", "series", "tag"]
            ):
                categories["analysis"].append(tool)
            elif "metadata" in name_lower or "update" in name_lower:
                categories["metadata"].append(tool)
            elif "download" in name_lower or "format" in name_lower:
                categories["files"].append(tool)
            elif any(x in name_lower for x in ["help", "status", "health"]):
                categories["system"].append(tool)
            else:
                categories["other"].append(tool)

        return {
            "total": len(filtered),
            "tools": filtered,
            "categories": {k: len(v) for k, v in categories.items() if v},
            "categorized_tools": {
                k: [
                    {"name": t["name"], "description": t["description"][:100]}
                    for t in v
                ]
                for k, v in categories.items()
                if v
            },
        }

    except Exception as e:
        log_error(logger, "list_tools_error", e)
        return {"total": 0, "tools": [], "categories": {}, "error": str(e)}


async def list_tools_helper(category: Optional[str] = None) -> Dict[str, Any]:
    """Helper for manage_system(operation='list_tools')."""
    return await list_tools(category=category)


# Deprecated: use manage_system(operation="hello_world") - kept as helper only, not registered
async def hello_world() -> str:
    """
    A simple hello world tool for testing and demonstration purposes.

    Returns a friendly greeting message to verify the MCP server is working correctly.
    This tool is useful for testing tool registration and basic server functionality.

    Returns:
        A greeting message string

    Examples:
        # Get a simple greeting
        message = hello_world()
        # Returns: "Hello, World! The CalibreMCP server is working correctly."
    """
    try:
        log_operation(logger, "hello_world_called")
        return "Hello, World! The CalibreMCP server is working correctly."
    except Exception as e:
        log_error(logger, "hello_world_error", e)
        return f"Error in hello_world: {str(e)}"


async def hello_world_helper() -> str:
    """Helper for manage_system(operation='hello_world')."""
    return await hello_world()


# Deprecated: use manage_system(operation="health_check") - kept as helper only, not registered
async def health_check() -> Dict[str, Any]:
    """
    Machine-readable health check for monitoring systems.

    Returns structured health information suitable for monitoring
    systems, CI/CD pipelines, and automated health checks.

    Returns:
        Dictionary with health status and metrics
    """
    try:
        log_operation(logger, "health_check_requested")

        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "checks": {},
        }

        # Check Calibre connection
        try:
            client = await get_api_client()
            await client.test_connection()
            health_status["checks"]["calibre_connection"] = {
                "status": "healthy",
                "message": "Calibre server accessible",
            }
        except Exception as e:
            health_status["checks"]["calibre_connection"] = {
                "status": "unhealthy",
                "message": f"Calibre connection failed: {str(e)}",
            }
            health_status["status"] = "degraded"

        # Check library discovery
        try:
            config = CalibreConfig()
            libraries = config.list_libraries()
            health_status["checks"]["library_discovery"] = {
                "status": "healthy",
                "message": f"Found {len(libraries)} libraries",
                "libraries_count": len(libraries),
            }
        except Exception as e:
            health_status["checks"]["library_discovery"] = {
                "status": "unhealthy",
                "message": f"Library discovery failed: {str(e)}",
            }
            health_status["status"] = "degraded"

        # Check system resources
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)

            health_status["checks"]["system_resources"] = {
                "status": "healthy"
                if memory.percent < 90 and cpu_percent < 90
                else "warning",
                "memory_percent": memory.percent,
                "cpu_percent": cpu_percent,
            }

            if memory.percent >= 90 or cpu_percent >= 90:
                health_status["status"] = "degraded"

        except Exception as e:
            health_status["checks"]["system_resources"] = {
                "status": "unknown",
                "message": f"Could not check system resources: {str(e)}",
            }

        # Overall status determination
        unhealthy_checks = [
            check
            for check in health_status["checks"].values()
            if check["status"] == "unhealthy"
        ]
        if unhealthy_checks:
            health_status["status"] = "unhealthy"

        return health_status

    except Exception as e:
        log_error(logger, "health_check_error", e)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


async def health_check_helper() -> Dict[str, Any]:
    """Helper for manage_system(operation='health_check')."""
    return await health_check()


# Deprecated: use manage_system - kept as helper only, not registered
async def ping() -> str:
    """
    Verify connectivity to the Calibre database and API.

    Returns:
        "pong" if successful, or an error message.
    """
    try:
        client = await get_api_client()
        await client.test_connection()
        return "pong"
    except Exception as e:
        return f"Ping failed: {str(e)}"


# Deprecated: use manage_system - kept as helper only, not registered
async def version() -> str:
    """
    Get the current version of the CalibreMCP server.
    """
    return "12.1.0-SOTA"


# Deprecated: use manage_system - kept as helper only, not registered
async def maintenance(operation: str = "vacuum") -> str:
    """
    Perform database maintenance operations.

    Args:
        operation: The maintenance operation to perform (vacuum, integrity_check).
    """
    db = DatabaseService()
    try:
        if operation == "vacuum":
            db.execute_raw("VACUUM")
            return "Database vacuumed successfully."
        elif operation == "integrity_check":
            result = db.execute_raw("PRAGMA integrity_check")
            return f"Integrity check result: {result}"
        else:
            return f"Unknown maintenance operation: {operation}"
    except Exception as e:
        return f"Maintenance failed: {str(e)}"


# Deprecated: use manage_system - kept as helper only, not registered
async def config_view() -> Dict[str, Any]:
    """
    View non-sensitive server configuration.
    """
    config = CalibreConfig()
    return {
        "server_url": config.server_url,
        "timeout": config.timeout,
        "max_retries": config.max_retries,
        "auto_discover": config.auto_discover_libraries,
    }
