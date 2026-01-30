"""
Library organization portmanteau tool for Calibre MCP server.

Consolidates all library organization operations into a single unified interface:
- Library organization and file management
- Tag cleaning and standardization
- Organization plan management
"""

from typing import Optional, Dict, Any, List

from ...server import mcp
from ...logging_config import get_logger

# Import organization tool implementations
from .library_organizer import LibraryOrganizer

logger = get_logger("calibremcp.tools.organization")


@mcp.tool()
async def manage_organization(
    operation: str,
    # Common parameters
    library_path: Optional[str] = None,
    book_ids: Optional[List[str]] = None,
    dry_run: bool = True,
    # Organization plan parameters
    plan: Optional[Dict[str, Any]] = None,
    plan_name: Optional[str] = None,
    # File organization parameters
    pattern: Optional[str] = None,
    target_dir: Optional[str] = None,
    create_subdirs: bool = True,
    # Tag cleaning parameters
    merge_similar: bool = True,
    min_length: int = 2,
    max_length: int = 50,
    remove_empty: bool = True,
) -> Dict[str, Any]:
    """
    Comprehensive library organization portmanteau tool for Calibre MCP server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 7 related organization operations into single interface. Prevents tool explosion while maintaining
    full functionality. Enables unified library organization workflow management.

    SUPPORTED OPERATIONS:
    - organize_library: Apply organization plan to library structure
    - organize_files: Move files based on patterns and metadata
    - clean_tags: Clean and standardize tag data
    - save_plan: Save organization plan for reuse
    - get_plans: List all saved organization plans
    - get_plan: Retrieve specific organization plan
    - delete_plan: Remove saved organization plan

    OPERATIONS DETAIL:

    organize_library:
    - Apply comprehensive organization rules to library
    - Supports custom plans with backup and dry-run modes
    - Parameters: plan (required), library_path, book_ids, dry_run

    organize_files:
    - Move and organize files based on glob patterns
    - Create subdirectory structure from metadata
    - Parameters: pattern, target_dir (required), create_subdirs, dry_run

    clean_tags:
    - Standardize and clean tag data across library
    - Merge similar tags, remove invalid entries
    - Parameters: merge_similar, min_length, max_length, remove_empty, dry_run

    save_plan:
    - Save organization configuration for future use
    - Parameters: plan (required)

    get_plans:
    - List all saved organization plans
    - No additional parameters required

    get_plan:
    - Retrieve specific organization plan by name
    - Parameters: plan_name (required)

    delete_plan:
    - Remove saved organization plan
    - Parameters: plan_name (required)

    Prerequisites:
        - Valid library path configured
        - For file operations: Appropriate permissions on target directories
        - For plan operations: Plan data must be properly formatted

    Returns:
        Dict with operation results, success status, and conversational messaging

    Examples:
        # Organize library with specific plan
        {"operation": "organize_library", "plan": {...}, "dry_run": true}

        # Clean tags with custom settings
        {"operation": "clean_tags", "min_length": 3, "merge_similar": true}

        # Save organization plan
        {"operation": "save_plan", "plan": {...}}
    """

    try:
        # Initialize organizer
        library_organizer = LibraryOrganizer()

        if operation == "organize_library":
            if not plan:
                return {
                    "success": False,
                    "error": "plan parameter required for library organization",
                    "message": "Please provide an organization plan to apply to the library."
                }
            return await library_organizer.organize_library(
                library_path=library_path, plan=plan, book_ids=book_ids
            )

        elif operation == "organize_files":
            if not pattern or not target_dir:
                return {
                    "success": False,
                    "error": "pattern and target_dir parameters required for file organization",
                    "message": "Please specify a file pattern and target directory for organization."
                }
            return await library_organizer.organize_files(
                library_path=library_path, pattern=pattern, target_dir=target_dir,
                create_subdirs=create_subdirs, dry_run=dry_run
            )

        elif operation == "clean_tags":
            return await library_organizer.clean_tags(
                library_path=library_path, book_ids=book_ids, merge_similar=merge_similar,
                min_length=min_length, max_length=max_length, remove_empty=remove_empty,
                dry_run=dry_run
            )

        elif operation == "save_plan":
            if not plan:
                return {
                    "success": False,
                    "error": "plan parameter required for saving organization plan",
                    "message": "Please provide an organization plan to save."
                }
            return await library_organizer.save_organization_plan(plan=plan)

        elif operation == "get_plans":
            return await library_organizer.get_organization_plans()

        elif operation == "get_plan":
            if not plan_name:
                return {
                    "success": False,
                    "error": "plan_name parameter required for retrieving organization plan",
                    "message": "Please specify the name of the organization plan to retrieve."
                }
            return await library_organizer.get_organization_plan(name=plan_name)

        elif operation == "delete_plan":
            if not plan_name:
                return {
                    "success": False,
                    "error": "plan_name parameter required for deleting organization plan",
                    "message": "Please specify the name of the organization plan to delete."
                }
            return await library_organizer.delete_organization_plan(name=plan_name)

        else:
            available_ops = ["organize_library", "organize_files", "clean_tags", "save_plan",
                           "get_plans", "get_plan", "delete_plan"]
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "message": f"Available operations: {', '.join(available_ops)}",
                "available_operations": available_ops
            }

    except Exception as e:
        logger.error(f"Organization operation '{operation}' failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Organization operation failed: {str(e)}",
            "operation": operation,
            "message": f"Sorry, the {operation.replace('_', ' ')} operation encountered an error. Please check the logs for details."
        }
