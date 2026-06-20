"""
Analysis tools initialization.

Core: manage_analysis portmanteau only. Granular tools deprecated.
"""

from .manage_analysis import manage_analysis  # noqa: F401

tools = [manage_analysis]
__all__ = ["manage_analysis"]
