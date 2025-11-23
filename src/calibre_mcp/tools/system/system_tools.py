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
            "basic": "FastMCP 2.12 server for Calibre ebook library management with AI-powered features.",
            "intermediate": (
                "CalibreMCP is a comprehensive Model Context Protocol (MCP) server that seamlessly "
                "integrates Claude AI with your Calibre ebook library. It provides intelligent "
                "assistance for reading, research, and library organization with Austrian efficiency."
            ),
            "advanced": (
                "A high-performance, extensible MCP server built on FastMCP 2.12 framework. "
                "Features include automatic library discovery, multi-library support, advanced search, "
                "metadata management, format conversion, AI-powered recommendations, and comprehensive "
                "analytics. Designed for Austrian efficiency with weeb-friendly Japanese content support."
            ),
            "expert": (
                "Production-ready MCP server with modular architecture, structured logging, "
                "comprehensive error handling, and extensive tooling. Supports both local and remote "
                "Calibre libraries, automatic library discovery via Calibre configuration files, "
                "and advanced features like series analysis, duplicate detection, and reading analytics."
            ),
        },
    },
    "tools": {
        "core": {
            "title": "Core Library Operations",
            "description": {
                "basic": "Essential tools for basic library access",
                "intermediate": "Core functionality for listing, searching, and retrieving books",
                "advanced": "Comprehensive library operations with filtering and sorting",
                "expert": "Low-level library access with performance optimization",
            },
            "tools": ["query_books", "manage_books", "test_calibre_connection"],
        },
        "library": {
            "title": "Library Management",
            "description": {
                "basic": "Tools for managing multiple libraries",
                "intermediate": "Multi-library operations and switching",
                "advanced": "Cross-library search and statistics",
                "expert": "Library health monitoring and optimization",
            },
            "tools": [
                "list_libraries",
                "switch_library",
                "get_library_stats",
                "cross_library_search",
            ],
        },
        "analysis": {
            "title": "Library Analysis",
            "description": {
                "basic": "Basic statistics and health checks",
                "intermediate": "Comprehensive analytics and recommendations",
                "advanced": "Advanced metrics and trend analysis",
                "expert": "Deep analysis with performance profiling",
            },
            "tools": [
                "get_tag_statistics",
                "find_duplicate_books",
                "get_series_analysis",
                "analyze_library_health",
                "unread_priority_list",
                "reading_statistics",
            ],
        },
        "metadata": {
            "title": "Metadata Management",
            "description": {
                "basic": "Basic metadata updates",
                "intermediate": "Bulk metadata operations",
                "advanced": "AI-powered metadata enhancement",
                "expert": "Advanced metadata validation and repair",
            },
            "tools": ["update_book_metadata", "auto_organize_tags", "fix_metadata_issues"],
        },
        "files": {
            "title": "File Operations",
            "description": {
                "basic": "Basic file operations",
                "intermediate": "Format conversion and downloads",
                "advanced": "Bulk file operations",
                "expert": "Advanced file management with optimization",
            },
            "tools": ["convert_book_format", "download_book", "bulk_format_operations"],
        },
        "specialized": {
            "title": "Specialized Features",
            "description": {
                "basic": "Specialized content organization",
                "intermediate": "AI-powered recommendations",
                "advanced": "Advanced content curation",
                "expert": "Expert-level content analysis",
            },
            "tools": ["japanese_book_organizer", "it_book_curator", "reading_recommendations"],
        },
    },
    "examples": {
        "basic": [
            "# List books in your library",
            "list_books()",
            "",
            "# Search for a specific book",
            'query_books(operation="search", text="python programming")',
            "",
            "# Get details for a specific book",
            "manage_books(operation='get', book_id=123)",
            "",
            "# Get complete book details",
            "manage_books(operation='details', book_id=123)",
        ],
        "intermediate": [
            "# Advanced search with filters",
            'query_books(operation="search", text="machine learning", tags=["programming", "ai"])',
            "",
            "# Get library statistics",
            "get_library_stats()",
            "",
            "# Find duplicate books",
            "find_duplicate_books()",
            "",
            "# Analyze series completion",
            "get_series_analysis()",
        ],
        "advanced": [
            "# Cross-library search",
            'cross_library_search(query="python", libraries=["IT", "Programming"])',
            "",
            "# Bulk metadata update",
            'update_book_metadata([{"book_id": 123, "tags": ["programming", "python"]}])',
            "",
            "# Convert multiple books",
            'convert_book_format([{"book_id": 123, "target_format": "PDF"}])',
            "",
            "# Get reading recommendations",
            "reading_recommendations()",
        ],
        "expert": [
            "# Library health analysis",
            "analyze_library_health()",
            "",
            "# Japanese content organization",
            "japanese_book_organizer()",
            "",
            "# IT book curation",
            "it_book_curator()",
            "",
            "# Advanced reading analytics",
            "reading_statistics()",
        ],
    },
}


# NOTE: @mcp.tool() decorator removed - use manage_system portmanteau tool instead
async def help_helper(level: HelpLevel = HelpLevel.BASIC, topic: Optional[str] = None) -> str:
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
    try:
        log_operation(logger, "help_requested", level=level.value, topic=topic)

        # Build help content
        content = []

        # Overview section
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

        # Examples section
        if level in [HelpLevel.BASIC, HelpLevel.INTERMEDIATE]:
            content.append("## Quick Examples")
            content.append("")
            for example in HELP_DOCS["examples"][level.value]:
                content.append(example)
            content.append("")

        # Advanced examples
        if level in [HelpLevel.ADVANCED, HelpLevel.EXPERT]:
            content.append("## Advanced Examples")
            content.append("")
            for example in HELP_DOCS["examples"][level.value]:
                content.append(example)
            content.append("")

        # Configuration section
        if level in [HelpLevel.INTERMEDIATE, HelpLevel.ADVANCED, HelpLevel.EXPERT]:
            content.append("## Configuration")
            content.append("")
            content.append("CalibreMCP automatically discovers Calibre libraries:")
            content.append("")
            content.append("```python")
            content.append("from calibre_mcp.config import CalibreConfig")
            content.append("config = CalibreConfig()")
            content.append("libraries = config.list_libraries()")
            content.append("```")
            content.append("")

        # Troubleshooting section
        if level in [HelpLevel.ADVANCED, HelpLevel.EXPERT]:
            content.append("## Troubleshooting")
            content.append("")
            content.append("### Common Issues")
            content.append("")
            content.append(
                "1. **Library not found**: Use `list_libraries()` to see discovered libraries"
            )
            content.append(
                "2. **Connection failed**: Check Calibre server with `test_calibre_connection()`"
            )
            content.append(
                "3. **Performance issues**: Use `analyze_library_health()` for diagnostics"
            )
            content.append("")

        return "\n".join(content)

    except Exception as e:
        log_error(logger, "help_error", e)
        return f"Error generating help: {str(e)}"


# NOTE: @mcp.tool() decorator removed - use manage_system portmanteau tool instead
async def status_helper(level: StatusLevel = StatusLevel.BASIC, focus: Optional[str] = None) -> str:
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
        if level in [StatusLevel.INTERMEDIATE, StatusLevel.ADVANCED, StatusLevel.DIAGNOSTIC]:
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
                    if any(x in name_lower for x in ["list_books", "search_books", "get_book"]):
                        tool_categories["Core Operations"].append(tool)
                    elif any(x in name_lower for x in ["library", "switch"]):
                        tool_categories["Library Management"].append(tool)
                    elif any(x in name_lower for x in ["statistics", "analysis", "series", "tag"]):
                        tool_categories["Analysis"].append(tool)
                    elif "metadata" in name_lower or "update" in name_lower:
                        tool_categories["Metadata"].append(tool)
                    elif "download" in name_lower or "format" in name_lower:
                        tool_categories["Files"].append(tool)
                    elif any(x in name_lower for x in ["help", "status", "health", "tool"]):
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
                content.append(f"**Server URL:** {calibre_info.get('server_url', 'Unknown')}")
                content.append(f"**Server Version:** {calibre_info.get('version', 'Unknown')}")
                content.append(f"**Total Books:** {calibre_info.get('total_books', 'Unknown')}")
                content.append("")
            else:
                content.append("### Calibre Connection Issues")
                content.append(f"**Error:** {calibre_info.get('error', 'Unknown error')}")
                content.append("")

            # Configuration details
            content.append("### Configuration")
            content.append(f"**Auto-discover Libraries:** {config.auto_discover_libraries}")
            content.append(f"**Server URL:** {config.server_url}")
            content.append(f"**Timeout:** {config.timeout}s")
            content.append(f"**Max Retries:** {config.max_retries}")
            content.append("")

            # Environment variables
            content.append("### Environment Variables")
            env_vars = ["CALIBRE_SERVER_URL", "CALIBRE_LIBRARY_PATH", "CALIBRE_LIBRARIES"]
            for var in env_vars:
                value = "Set" if var in os.environ else "Not set"
                content.append(f"**{var}:** {value}")
            content.append("")

        return "\n".join(content)

    except Exception as e:
        log_error(logger, "status_error", e)
        return f"Error generating status: {str(e)}"


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


# NOTE: @mcp.tool() decorator removed - use manage_system portmanteau tool instead
async def tool_help_helper(tool_name: str, level: HelpLevel = HelpLevel.BASIC) -> str:
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
        log_operation(logger, "tool_help_requested", tool_name=tool_name, level=level.value)

        # Get tool information
        tool_info = _get_tool_by_name(tool_name)

        if not tool_info:
            # Try to find similar tool names
            all_tools = _get_registered_tools()
            similar = [t["name"] for t in all_tools if tool_name.lower() in t["name"].lower()]

            if similar:
                return f"Tool '{tool_name}' not found. Did you mean: {', '.join(similar[:5])}?"
            else:
                return (
                    f"Tool '{tool_name}' not found. Use `list_tools()` to see all available tools."
                )

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
                    content.append(f"- **Required:** {'Yes' if param['required'] else 'No'}")
                    if param["default"] is not None:
                        content.append(f"- **Default:** `{repr(param['default'])}`")
                    content.append("")

            content.append("")

        # Signature
        if level in [HelpLevel.ADVANCED, HelpLevel.EXPERT] and tool_info.get("signature"):
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


def _get_tool_examples(tool_name: str, level: HelpLevel) -> List[str]:
    """Get example usage for a tool."""
    examples = []

    # Tool-specific examples
    tool_examples = {
        "query_books": [
            "# Search for books",
            "result = query_books(operation='search', text='python programming')",
            "",
            "# Get recently added books",
            "result = query_books(operation='recent', limit=10)",
            "",
            "# List all books",
            "result = query_books(operation='list', limit=50)",
        ],
        "manage_books": [
            "# Get book by ID",
            "book = manage_books(operation='get', book_id=123)",
            "# Get complete book details",
            "book = manage_books(operation='details', book_id=123)",
        ],
        "list_libraries": ["# List all libraries", "libraries = list_libraries()"],
        "switch_library": [
            "# Switch to a different library",
            "result = switch_library(library_name='Programming')",
        ],
        "update_book_metadata": [
            "# Update single book",
            "result = update_book_metadata([{'book_id': 123, 'rating': 5}])",
        ],
        "download_book": [
            "# Download in preferred format",
            "result = download_book(book_id=123, format_preference='EPUB')",
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
        "search_books": [
            "Use field-specific searches for better performance",
            "Combine multiple search criteria for precise results",
            "Large result sets are automatically paginated",
        ],
        "list_books": [
            "Use limit and offset for pagination",
            "Filtering reduces database load",
            "Sorting can impact performance on large libraries",
        ],
        "update_book_metadata": [
            "Batch updates are more efficient than single updates",
            "Validate metadata before bulk operations",
            "Use transaction-aware updates for consistency",
        ],
    }

    return tips_map.get(tool_name, [])


# NOTE: @mcp.tool() decorator removed - use manage_system portmanteau tool instead
async def list_tools_helper(category: Optional[str] = None) -> Dict[str, Any]:
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
            elif any(x in name_lower for x in ["statistics", "analysis", "series", "tag"]):
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
                k: [{"name": t["name"], "description": t["description"][:100]} for t in v]
                for k, v in categories.items()
                if v
            },
        }

    except Exception as e:
        log_error(logger, "list_tools_error", e)
        return {"total": 0, "tools": [], "categories": {}, "error": str(e)}


# NOTE: @mcp.tool() decorator removed - use manage_system portmanteau tool instead
async def hello_world_helper() -> str:
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


# NOTE: @mcp.tool() decorator removed - use manage_system portmanteau tool instead
async def health_check_helper() -> Dict[str, Any]:
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
                "status": "healthy" if memory.percent < 90 and cpu_percent < 90 else "warning",
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
            check for check in health_status["checks"].values() if check["status"] == "unhealthy"
        ]
        if unhealthy_checks:
            health_status["status"] = "unhealthy"

        return health_status

    except Exception as e:
        log_error(logger, "health_check_error", e)
        return {"status": "unhealthy", "timestamp": datetime.now().isoformat(), "error": str(e)}
