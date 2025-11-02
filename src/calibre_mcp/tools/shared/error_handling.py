"""
Standardized error handling utilities for MCP tools.

All tools MUST use these functions to return AI-friendly error responses
that follow the .cursorrules Error Messages requirements.
"""

from typing import Dict, Any, Optional, List, Type
import logging
import traceback

logger = logging.getLogger(__name__)


def format_error_response(
    error_msg: str,
    error_code: str,
    error_type: str,
    operation: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    suggestions: Optional[List[str]] = None,
    related_tools: Optional[List[str]] = None,
    diagnostic_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Format a standardized error response for MCP tools.
    
    Follows .cursorrules Error Messages (AI-Friendly Requirements):
    - Actionable: Tells AI what to do
    - Contextual: Includes relevant information
    - Diagnostic: Helps identify root cause
    - Solution-oriented: Provides steps to fix
    
    Args:
        error_msg: Clear error message (actionable, contextual, diagnostic)
        error_code: Specific error code (e.g., "VALIDATION_ERROR", "BOOK_NOT_FOUND")
        error_type: Type of exception/error (e.g., "ValueError", "FileNotFoundError")
        operation: Operation that failed (for portmanteau tools)
        parameters: Parameters that were used (for diagnostic info)
        suggestions: List of actionable suggestions
        related_tools: List of related tools to try
        diagnostic_info: Additional diagnostic information
    
    Returns:
        Standardized error response dictionary:
        {
            "success": False,
            "error": "...",
            "error_code": "...",
            "error_type": "...",
            "operation": "...",
            "suggestions": [...],
            "related_tools": [...],
            "diagnostic": {...}
        }
    """
    response: Dict[str, Any] = {
        "success": False,
        "error": error_msg,
        "error_code": error_code,
        "error_type": error_type,
    }
    
    if operation:
        response["operation"] = operation
    
    if parameters:
        response["parameters"] = parameters
    
    if suggestions:
        response["suggestions"] = suggestions
    else:
        response["suggestions"] = []
    
    if related_tools:
        response["related_tools"] = related_tools
    else:
        response["related_tools"] = []
    
    if diagnostic_info:
        response["diagnostic"] = diagnostic_info
    
    return response


def handle_tool_error(
    exception: Exception,
    operation: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    tool_name: str = "tool",
    context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Handle exceptions in tools and return standardized error response.
    
    This is the main function tools should use in try/except blocks.
    
    Args:
        exception: The exception that was raised
        operation: Operation that failed (for portmanteau tools)
        parameters: Parameters that were used
        tool_name: Name of the tool (for logging)
        context: Additional context about what was happening
    
    Returns:
        Standardized error response dictionary
    """
    error_type = type(exception).__name__
    error_msg = str(exception)
    
    # Log the error with full traceback
    logger.error(
        f"Error in {tool_name}",
        extra={
            "tool": tool_name,
            "operation": operation,
            "error_type": error_type,
            "error": error_msg,
            "context": context,
            "parameters": parameters,
        },
        exc_info=True,
    )
    
    # Determine error code based on exception type
    if isinstance(exception, ValueError):
        error_code = "VALIDATION_ERROR"
        default_suggestions = [
            "Check the error message above for specific guidance",
            f"Verify all parameters are correctly formatted for {tool_name}",
            "Use query_books(operation='list', limit=5) to verify library access",
            "Use manage_libraries(operation='list') to check available libraries",
        ]
        default_tools = ["query_books", "manage_libraries"]
    elif isinstance(exception, FileNotFoundError):
        error_code = "FILE_NOT_FOUND"
        default_suggestions = [
            "Verify the file path exists and is accessible",
            "Check file permissions",
            "Ensure the library path is correct",
            "Use manage_libraries(operation='list') to see available libraries",
        ]
        default_tools = ["manage_libraries"]
    elif isinstance(exception, KeyError):
        error_code = "KEY_ERROR"
        default_suggestions = [
            "Check that all required parameters are provided",
            "Verify parameter names are correct",
            f"Review {tool_name} documentation for required parameters",
        ]
        default_tools = [tool_name]
    elif isinstance(exception, PermissionError):
        error_code = "PERMISSION_ERROR"
        default_suggestions = [
            "Check file system permissions",
            "Ensure user has read/write access to the library",
            "Try running with appropriate permissions",
        ]
        default_tools = []
    else:
        error_code = "OPERATION_ERROR"
        default_suggestions = [
            f"Check the error message above for details about the failure in {tool_name}",
            "Use manage_libraries(operation='list') to verify library is accessible",
            "Try a simpler operation to test basic functionality",
            "Check server logs for more detailed error information",
        ]
        default_tools = ["manage_libraries", "query_books"]
    
    # Build diagnostic information
    diagnostic: Dict[str, Any] = {
        "error_type": error_type,
        "error_message": error_msg,
    }
    if operation:
        diagnostic["operation"] = operation
    if parameters:
        diagnostic["parameters_used"] = parameters
    if context:
        diagnostic["context"] = context
    
    # Format comprehensive error message
    formatted_msg = (
        f"❌ {tool_name} failed with {error_type}: {error_msg}\n\n"
        f"**Diagnostic Information:**\n"
    )
    if operation:
        formatted_msg += f"- Operation: {operation}\n"
    if parameters:
        # Include key parameters for context
        key_params = {k: v for k, v in list(parameters.items())[:5]}  # First 5 params
        formatted_msg += f"- Parameters: {key_params}\n"
    formatted_msg += f"- Error Type: {error_type}\n\n"
    formatted_msg += "**Possible Solutions:**\n"
    for i, suggestion in enumerate(default_suggestions[:4], 1):
        formatted_msg += f"{i}. {suggestion}\n"
    
    if isinstance(exception, FileNotFoundError):
        formatted_msg += "\n**Important:** This is LOCAL library access using direct SQLite database.\n"
        formatted_msg += "Do NOT try to connect to a Calibre HTTP server or configure remote access."
    
    return format_error_response(
        error_msg=formatted_msg,
        error_code=error_code,
        error_type=error_type,
        operation=operation,
        parameters=parameters,
        suggestions=default_suggestions,
        related_tools=default_tools,
        diagnostic_info=diagnostic,
    )

