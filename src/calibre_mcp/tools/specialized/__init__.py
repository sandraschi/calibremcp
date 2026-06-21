"""
Specialized tools for CalibreMCP.

NOTE: Only portmanteau tools are registered with @mcp.tool() and visible to Claude.
The individual specialized helpers were never implemented (empty stubs) and have been
removed; reintroduce them alongside a real manage_specialized portmanteau when needed.
"""

# Portmanteau tool: optional until manage_specialized.py exists
try:
    from .manage_specialized import manage_specialized

    tools = [manage_specialized]
    __all__ = ["manage_specialized"]
except ModuleNotFoundError:
    manage_specialized = None  # type: ignore[misc, assignment]
    tools = []
    __all__ = []
