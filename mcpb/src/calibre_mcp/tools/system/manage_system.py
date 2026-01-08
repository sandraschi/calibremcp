"""
System management portmanteau tool for CalibreMCP.

Consolidates all system-related operations into a single unified interface.
"""

from typing import Optional, Dict, Any

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response

# Import helper functions (NOT registered as MCP tools)
from . import system_tools

logger = get_logger("calibremcp.tools.system")


@mcp.tool()
async def manage_system(
    operation: str,
    # Help operation parameters
    level: Optional[str] = "basic",
    topic: Optional[str] = None,
    # Status operation parameters
    status_level: Optional[str] = "basic",
    focus: Optional[str] = None,
    # Tool help operation parameters
    tool_name: Optional[str] = None,
    tool_help_level: Optional[str] = "basic",
    # List tools operation parameters
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Comprehensive system management tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 6 separate tools (one per operation), this tool consolidates related
    system operations into a single interface. This design:
    - Prevents tool explosion (6 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with system management tasks
    - Enables consistent system interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - help: Comprehensive help system with multiple detail levels
    - status: System status and diagnostic information
    - tool_help: Get detailed help for a specific tool
    - list_tools: List all available tools with descriptions
    - hello_world: Simple test/demonstration tool
    - health_check: Machine-readable health check for monitoring

    OPERATIONS DETAIL:

    help: Comprehensive help system
    - Provides contextual assistance and documentation for CalibreMCP features
    - Organized by knowledge levels: basic, intermediate, advanced, expert
    - Can focus on specific topics
    - Parameters: level (optional, default: "basic"), topic (optional)

    status: System status and diagnostics
    - Provides different levels of diagnostic information about CalibreMCP
    - Levels: basic, intermediate, advanced, diagnostic
    - Can focus on specific areas (library, tools, performance, etc.)
    - Parameters: status_level (optional, default: "basic"), focus (optional)

    tool_help: Get detailed help for a specific tool
    - Provides comprehensive documentation for a single tool
    - Includes parameters, return values, examples, and usage patterns
    - Parameters: tool_name (required), tool_help_level (optional, default: "basic")

    list_tools: List all available tools
    - Provides comprehensive list of all registered tools
    - Can filter by category
    - Useful for discovering available functionality
    - Parameters: category (optional)

    hello_world: Simple test tool
    - Returns a friendly greeting message
    - Useful for testing tool registration and basic server functionality
    - No parameters required

    health_check: Machine-readable health check
    - Returns structured health information suitable for monitoring systems
    - Checks Calibre connection, library discovery, system resources
    - Returns health status and metrics
    - No parameters required

    Prerequisites:
        - Server must be running
        - For 'status' and 'health_check': Library should be configured

    Parameters:
        operation: The operation to perform. Must be one of:
            "help", "status", "tool_help", "list_tools", "hello_world", "health_check"

        # Help operation parameters
        level: Help detail level (optional, default: "basic")
               Valid: "basic", "intermediate", "advanced", "expert"
        topic: Specific topic to focus on (optional)

        # Status operation parameters
        status_level: Status detail level (optional, default: "basic")
                     Valid: "basic", "intermediate", "advanced", "diagnostic"
        focus: Specific area to focus on (optional, e.g., "library", "tools", "performance")

        # Tool help operation parameters
        tool_name: Name of the tool to get help for (required for operation="tool_help")
        tool_help_level: Detail level for tool help (optional, default: "basic")
                        Valid: "basic", "intermediate", "advanced", "expert"

        # List tools operation parameters
        category: Optional category filter (optional, e.g., "library", "metadata", "analysis")

    Returns:
        Operation-specific results:

        For operation="help":
            str: Formatted help content with examples and guidance

        For operation="status":
            str: Formatted status report with system information

        For operation="tool_help":
            str: Formatted help content for the specified tool

        For operation="list_tools":
            {
                "total": int - Total number of tools
                "tools": List[Dict] - List of tool information dictionaries
                "categories": Dict[str, int] - Available tool categories with counts
            }

        For operation="hello_world":
            str: Greeting message

        For operation="health_check":
            {
                "status": str - Overall health status (healthy/degraded/unhealthy)
                "timestamp": str - ISO timestamp
                "version": str - Server version
                "checks": Dict - Individual health check results
            }

    Usage:
        # Get basic help
        result = await manage_system(operation="help")

        # Get advanced help on a specific topic
        result = await manage_system(operation="help", level="advanced", topic="tools")

        # Get system status
        result = await manage_system(operation="status")

        # Get detailed status focusing on library
        result = await manage_system(operation="status", status_level="advanced", focus="library")

        # Get help for a specific tool
        result = await manage_system(operation="tool_help", tool_name="search_books")

        # List all tools
        result = await manage_system(operation="list_tools")

        # List tools in a category
        result = await manage_system(operation="list_tools", category="library")

        # Test server
        result = await manage_system(operation="hello_world")

        # Check system health
        result = await manage_system(operation="health_check")

    Examples:
        # Get intermediate help
        help_text = await manage_system(operation="help", level="intermediate")

        # Get expert-level status
        status_text = await manage_system(operation="status", status_level="diagnostic")

        # Get expert help for a tool
        tool_help_text = await manage_system(
            operation="tool_help",
            tool_name="manage_books",
            tool_help_level="expert"
        )

        # List metadata tools
        tools = await manage_system(operation="list_tools", category="metadata")

        # Simple health check
        health = await manage_system(operation="health_check")

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of the supported operations listed above
        - Missing tool_name (tool_help): Provide tool_name parameter for tool_help operation
        - Invalid level: Use one of "basic", "intermediate", "advanced", "expert"
        - Invalid status_level: Use one of "basic", "intermediate", "advanced", "diagnostic"
        - Tool not found (tool_help): Verify tool name using operation="list_tools"

    See Also:
        - manage_libraries(): For library management
        - manage_books(): For book management operations
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
                result = await system_tools.tool_help_helper(tool_name=tool_name, level=tool_hlp_lvl)
                return {"content": result, "tool_name": tool_name, "level": tool_help_level}
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"tool_name": tool_name, "tool_help_level": tool_help_level},
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
                return result if isinstance(result, dict) else {"status": "unknown", "result": result}
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

