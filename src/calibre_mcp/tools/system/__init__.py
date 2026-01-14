"""
System management tools for CalibreMCP.

This module provides the manage_system portmanteau tool for comprehensive system management.
"""

# Import portmanteau and granular tools
from .manage_system import manage_system
from .system_tools import (
    help,
    status,
    tool_help,
    list_tools,
    hello_world,
    health_check,
    ping,
    version,
    maintenance,
    config_view,
)

# List of tools to register
tools = [
    manage_system,
    help,
    status,
    tool_help,
    list_tools,
    hello_world,
    health_check,
    ping,
    version,
    maintenance,
    config_view,
]

__all__ = ["manage_system", "help", "status", "ping", "version"]
