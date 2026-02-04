"""
System management tools for CalibreMCP.

Core: manage_system portmanteau only. Granular tools deprecated (use manage_system(operation=...)).
"""

from .manage_system import manage_system

tools = [manage_system]
__all__ = ["manage_system"]
