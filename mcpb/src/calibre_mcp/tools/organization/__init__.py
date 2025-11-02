"""
Library organization tools for Calibre MCP server.

This module provides tools for organizing the library,
including managing collections, tags, and series.
"""

from .. import tool  # noqa: F401

# Import the library organizer
from .library_organizer import LibraryOrganizer

# Initialize the organizer
library_organizer = LibraryOrganizer()


# Register the tools
@tool(
    name="organize_library",
    description="Organize the library according to a specified plan",
    parameters={
        "library_path": {"type": "string", "description": "Path to the Calibre library"},
        "plan": {
            "type": "object",
            "description": "Organization plan (or name of a saved plan)",
            "properties": {
                "name": {"type": "string", "description": "Name of the plan"},
                "description": {"type": "string", "description": "Description of the plan"},
                "rules": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of organization rules",
                },
                "dry_run": {"type": "boolean", "default": True},
                "backup_before": {"type": "boolean", "default": True},
            },
        },
        "book_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of book IDs to process (all books if None)",
        },
    },
)
async def organize_library(*args, **kwargs):
    """Organize the library according to a specified plan."""
    return await library_organizer.organize_library(*args, **kwargs)


@tool(
    name="organize_files",
    description="Organize files in the library based on a pattern",
    parameters={
        "library_path": {"type": "string", "description": "Path to the Calibre library"},
        "pattern": {
            "type": "string",
            "description": "Glob pattern to match files (e.g., '*.epub', '**/*.pdf')",
        },
        "target_dir": {"type": "string", "description": "Base directory to move files to"},
        "create_subdirs": {
            "type": "boolean",
            "default": True,
            "description": "Whether to create subdirectories based on metadata",
        },
        "dry_run": {
            "type": "boolean",
            "default": True,
            "description": "If True, only show what would be done",
        },
    },
)
async def organize_files(*args, **kwargs):
    """Organize files in the library based on a pattern."""
    return await library_organizer.organize_files(*args, **kwargs)


@tool(
    name="clean_tags",
    description="Clean and standardize tags across the library",
    parameters={
        "library_path": {"type": "string", "description": "Path to the Calibre library"},
        "book_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of book IDs to process (all books if None)",
        },
        "merge_similar": {
            "type": "boolean",
            "default": True,
            "description": "Whether to merge similar tags",
        },
        "min_length": {
            "type": "integer",
            "default": 2,
            "description": "Minimum tag length (shorter tags will be removed)",
        },
        "max_length": {
            "type": "integer",
            "default": 50,
            "description": "Maximum tag length (longer tags will be truncated)",
        },
        "remove_empty": {
            "type": "boolean",
            "default": True,
            "description": "Whether to remove empty tags",
        },
        "dry_run": {
            "type": "boolean",
            "default": True,
            "description": "If True, only show what would be changed",
        },
    },
)
async def clean_tags(*args, **kwargs):
    """Clean and standardize tags across the library."""
    return await library_organizer.clean_tags(*args, **kwargs)


@tool(
    name="save_organization_plan",
    description="Save an organization plan for future use",
    parameters={
        "plan": {
            "type": "object",
            "description": "Organization plan to save",
            "properties": {
                "name": {"type": "string", "description": "Name of the plan"},
                "description": {"type": "string", "description": "Description of the plan"},
                "rules": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of organization rules",
                },
                "dry_run": {"type": "boolean", "default": True},
                "backup_before": {"type": "boolean", "default": True},
            },
        }
    },
)
async def save_organization_plan(*args, **kwargs):
    """Save an organization plan for future use."""
    return await library_organizer.save_organization_plan(*args, **kwargs)


@tool(name="get_organization_plans", description="Get all saved organization plans", parameters={})
async def get_organization_plans():
    """Get all saved organization plans."""
    return await library_organizer.get_organization_plans()


@tool(
    name="get_organization_plan",
    description="Get a specific organization plan by name",
    parameters={"name": {"type": "string", "description": "Name of the plan to retrieve"}},
)
async def get_organization_plan(*args, **kwargs):
    """Get a specific organization plan by name."""
    return await library_organizer.get_organization_plan(*args, **kwargs)


@tool(
    name="delete_organization_plan",
    description="Delete a saved organization plan",
    parameters={"name": {"type": "string", "description": "Name of the plan to delete"}},
)
async def delete_organization_plan(*args, **kwargs):
    """Delete a saved organization plan."""
    return await library_organizer.delete_organization_plan(*args, **kwargs)
