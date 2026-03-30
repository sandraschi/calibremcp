"""
System management portmanteau tool for CalibreMCP.

Consolidates all system-related operations into a single unified interface.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error

# Import helper functions (NOT registered as MCP tools)
from . import system_tools

logger = get_logger("calibremcp.tools.system")


@mcp.tool()
async def manage_system(
    operation: str,
    # Help operation parameters
    level: str | None = "basic",
    topic: str | None = None,
    # Status operation parameters
    status_level: str | None = "basic",
    focus: str | None = None,
    # Tool help operation parameters
    tool_name: str | None = None,
    tool_help_level: str | None = "basic",
    # List tools operation parameters
    category: str | None = None,
) -> dict[str, Any]:
    """
    Administrative and diagnostic interface for the Calibre MCP server.

    Operations:
    - help: Comprehensive documentation for the server and its capabilities.
    - status: Real-time system health, database statistics, and connectivity diagnostics.
    - tool_help: Targeted usage instructions and examples for a specific tool.
    - list_tools: Catalog of all available operations organized by category.
    - hello_world: Simple reachability test and server identity confirmation.
    - health_check: Deep-dive diagnostic for database and service integrity.

    Example:
    - manage_system(operation="status", focus="library")
    - manage_system(operation="tool_help", tool_name="manage_books")
    """
    try:
        if operation == "help":
            from .system_tools import HelpLevel

            try:
                help_level = HelpLevel(level) if level else HelpLevel.BASIC
                result = await system_tools.help_helper(level=help_level, topic=topic)
                return {"content": result, "level": level, "topic": topic}
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"level": level, "topic": topic},
                    tool_name="manage_system",
                    context="Getting help documentation",
                )

        elif operation == "status":
            from .system_tools import StatusLevel

            try:
                status_lvl = StatusLevel(status_level) if status_level else StatusLevel.BASIC
                result = await system_tools.status_helper(level=status_lvl, focus=focus)
                return {"content": result, "level": status_level, "focus": focus}
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"status_level": status_level, "focus": focus},
                    tool_name="manage_system",
                    context="Getting system status",
                )

        elif operation == "tool_help":
            if not tool_name:
                return format_error_response(
                    error_msg=(
                        "tool_name is required for operation='tool_help'. "
                        "Provide the name of the tool to get help for."
                    ),
                    error_code="MISSING_TOOL_NAME",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide tool_name parameter (e.g., tool_name='search_books')",
                        "Use operation='list_tools' to see all available tools",
                    ],
                    related_tools=["manage_system"],
                )
            from .system_tools import HelpLevel

            try:
                tool_hlp_lvl = HelpLevel(tool_help_level) if tool_help_level else HelpLevel.BASIC
                result = await system_tools.tool_help_helper(
                    tool_name=tool_name, level=tool_hlp_lvl
                )
                return {
                    "content": result,
                    "tool_name": tool_name,
                    "level": tool_help_level,
                }
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={
                        "tool_name": tool_name,
                        "tool_help_level": tool_help_level,
                    },
                    tool_name="manage_system",
                    context=f"Getting help for tool '{tool_name}'",
                )

        elif operation == "list_tools":
            try:
                result = await system_tools.list_tools_helper(category=category)
                return result if isinstance(result, dict) else {"tools": result}
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"category": category},
                    tool_name="manage_system",
                    context="Listing available tools",
                )

        elif operation == "hello_world":
            try:
                result = await system_tools.hello_world_helper()
                return {"message": result}
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_system",
                    context="Hello world test",
                )

        elif operation == "health_check":
            try:
                result = await system_tools.health_check_helper()
                return (
                    result if isinstance(result, dict) else {"status": "unknown", "result": result}
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={},
                    tool_name="manage_system",
                    context="Health check",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'help', 'status', 'tool_help', 'list_tools', 'hello_world', 'health_check'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='help' for comprehensive help system",
                    "Use operation='status' for system status and diagnostics",
                    "Use operation='tool_help' to get help for a specific tool",
                    "Use operation='list_tools' to list all available tools",
                    "Use operation='hello_world' for a simple test",
                    "Use operation='health_check' for machine-readable health check",
                ],
                related_tools=["manage_system"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "level": level,
                "tool_name": tool_name,
                "category": category,
            },
            tool_name="manage_system",
            context="System management operation",
        )
