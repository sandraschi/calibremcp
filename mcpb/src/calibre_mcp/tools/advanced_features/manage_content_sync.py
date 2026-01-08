"""
Content sync management portmanteau tool for CalibreMCP.

Consolidates all content synchronization operations into a single unified interface.
"""

from typing import Optional, Dict, Any

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response

# Import helper functions (NOT registered as MCP tools)
from .content_sync_helpers import (
    register_device_helper,
    update_device_helper,
    get_device_helper,
    start_sync_helper,
    get_sync_status_helper,
    cancel_sync_helper,
)

logger = get_logger("calibremcp.tools.content_sync")


@mcp.tool()
async def manage_content_sync(
    operation: str,
    # Device management parameters
    name: Optional[str] = None,
    device_type: Optional[str] = None,
    device_id: Optional[str] = None,
    sync_settings: Optional[Dict[str, Any]] = None,
    updates: Optional[Dict[str, Any]] = None,
    # Sync operation parameters
    sync_type: str = "full",
    library_path: Optional[str] = None,
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Comprehensive content synchronization tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating multiple separate tools, this tool consolidates related
    content synchronization operations into a single interface. This design:
    - Prevents tool explosion while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with sync tasks
    - Enables consistent sync interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - register_device: Register a new device for synchronization
    - update_device: Update device information and settings
    - get_device: Get device information
    - start: Start a synchronization job for a device
    - status: Get the status of a synchronization job
    - cancel: Cancel a running synchronization job

    OPERATIONS DETAIL:

    register_device: Register a new device
    - Creates a new device entry for synchronization
    - Parameters: name (required), device_type (required), device_id (optional), sync_settings (optional)

    update_device: Update device information
    - Updates device settings and information
    - Parameters: device_id (required), updates (required - dict of fields to update)

    get_device: Get device information
    - Retrieves device details by ID
    - Parameters: device_id (required)

    start: Start synchronization
    - Initiates a sync job for a device
    - Parameters: device_id (required), sync_type (default: "full"), library_path (optional)

    status: Get sync job status
    - Retrieves the current status of a sync job
    - Parameters: job_id (required)

    cancel: Cancel sync job
    - Cancels a running synchronization job
    - Parameters: job_id (required)

    Prerequisites:
        - Library must be configured (use manage_libraries(operation='switch'))

    Parameters:
        operation: The operation to perform. Must be one of:
            "register_device", "update_device", "get_device", "start", "status", "cancel"

        # Device management parameters
        name: Device name (required for 'register_device')
        device_type: Device type - 'web', 'mobile', 'desktop', 'ereader', 'other' (required for 'register_device')
        device_id: Device ID (required for 'update_device', 'get_device', 'start')
        sync_settings: Sync settings dictionary (optional for 'register_device')
        updates: Dictionary of fields to update (required for 'update_device')

        # Sync operation parameters
        sync_type: Sync type - 'full', 'incremental', 'metadata_only', 'content_only' (default: "full", for 'start')
        library_path: Path to library (optional, for 'start')
        job_id: Job ID (required for 'status', 'cancel')

    Returns:
        Dictionary containing operation-specific results

    Usage:
        # Register a device
        result = await manage_content_sync(
            operation="register_device",
            name="My E-reader",
            device_type="ereader"
        )

        # Start sync
        result = await manage_content_sync(
            operation="start",
            device_id="dev_123",
            sync_type="full"
        )

        # Check status
        result = await manage_content_sync(
            operation="status",
            job_id="job_1"
        )

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of the supported operations listed above
        - Missing required parameters: Provide all required parameters for the operation
        - Device not found: Verify device_id is correct
        - Job not found: Verify job_id is correct
    """
    try:
        if operation == "register_device":
            if not name:
                return format_error_response(
                    error_msg="name is required for operation='register_device'",
                    error_code="MISSING_NAME",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide name parameter (e.g., name='My Device')"],
                    related_tools=["manage_content_sync"],
                )
            if not device_type:
                return format_error_response(
                    error_msg="device_type is required for operation='register_device'",
                    error_code="MISSING_DEVICE_TYPE",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide device_type parameter (e.g., device_type='ereader')",
                        "Valid types: 'web', 'mobile', 'desktop', 'ereader', 'other'",
                    ],
                    related_tools=["manage_content_sync"],
                )
            try:
                return await register_device_helper(
                    name=name, device_type=device_type, device_id=device_id, sync_settings=sync_settings
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"name": name, "device_type": device_type},
                    tool_name="manage_content_sync",
                    context="Registering device for content sync",
                )

        elif operation == "update_device":
            if not device_id:
                return format_error_response(
                    error_msg="device_id is required for operation='update_device'",
                    error_code="MISSING_DEVICE_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide device_id parameter"],
                    related_tools=["manage_content_sync"],
                )
            if not updates:
                return format_error_response(
                    error_msg="updates is required for operation='update_device'",
                    error_code="MISSING_UPDATES",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide updates parameter (dict of fields to update)"],
                    related_tools=["manage_content_sync"],
                )
            try:
                return await update_device_helper(device_id=device_id, updates=updates)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"device_id": device_id, "updates": updates},
                    tool_name="manage_content_sync",
                    context=f"Updating device {device_id}",
                )

        elif operation == "get_device":
            if not device_id:
                return format_error_response(
                    error_msg="device_id is required for operation='get_device'",
                    error_code="MISSING_DEVICE_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide device_id parameter"],
                    related_tools=["manage_content_sync"],
                )
            try:
                return await get_device_helper(device_id=device_id)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"device_id": device_id},
                    tool_name="manage_content_sync",
                    context=f"Getting device information for {device_id}",
                )

        elif operation == "start":
            if not device_id:
                return format_error_response(
                    error_msg="device_id is required for operation='start'",
                    error_code="MISSING_DEVICE_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide device_id parameter"],
                    related_tools=["manage_content_sync"],
                )
            try:
                return await start_sync_helper(
                    device_id=device_id, sync_type=sync_type, library_path=library_path
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"device_id": device_id, "sync_type": sync_type},
                    tool_name="manage_content_sync",
                    context=f"Starting sync job for device {device_id}",
                )

        elif operation == "status":
            if not job_id:
                return format_error_response(
                    error_msg="job_id is required for operation='status'",
                    error_code="MISSING_JOB_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide job_id parameter"],
                    related_tools=["manage_content_sync"],
                )
            try:
                return await get_sync_status_helper(job_id=job_id)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"job_id": job_id},
                    tool_name="manage_content_sync",
                    context=f"Getting sync status for job {job_id}",
                )

        elif operation == "cancel":
            if not job_id:
                return format_error_response(
                    error_msg="job_id is required for operation='cancel'",
                    error_code="MISSING_JOB_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide job_id parameter"],
                    related_tools=["manage_content_sync"],
                )
            try:
                return await cancel_sync_helper(job_id=job_id)
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"job_id": job_id},
                    tool_name="manage_content_sync",
                    context=f"Cancelling sync job {job_id}",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'register_device', 'update_device', 'get_device', 'start', 'status', 'cancel'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='register_device' to register a device",
                    "Use operation='update_device' to update device settings",
                    "Use operation='get_device' to get device information",
                    "Use operation='start' to start a sync job",
                    "Use operation='status' to check sync status",
                    "Use operation='cancel' to cancel a sync job",
                ],
                related_tools=["manage_content_sync"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "device_id": device_id,
                "job_id": job_id,
            },
            tool_name="manage_content_sync",
            context="Content sync operation",
        )

