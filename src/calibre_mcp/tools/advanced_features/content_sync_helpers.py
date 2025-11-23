"""
Helper functions for content sync operations.

These functions are NOT registered as MCP tools - they are called by
the manage_content_sync portmanteau tool.
"""

from typing import Dict, Any, Optional
from ...logging_config import get_logger
from ..shared.error_handling import format_error_response

# Import the deprecated ContentSyncTool as a helper
from .content_sync import ContentSyncTool

logger = get_logger("calibremcp.tools.content_sync")

# Create a singleton instance for helper functions
_sync_tool_instance = None


def _get_sync_tool() -> ContentSyncTool:
    """Get or create the ContentSyncTool instance."""
    global _sync_tool_instance
    if _sync_tool_instance is None:
        _sync_tool_instance = ContentSyncTool()
    return _sync_tool_instance


async def register_device_helper(
    name: str,
    device_type: str,
    device_id: Optional[str] = None,
    sync_settings: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Helper to register a device."""
    try:
        tool = _get_sync_tool()
        return await tool.sync_register_device(
            name=name, device_type=device_type, device_id=device_id, sync_settings=sync_settings
        )
    except Exception as e:
        logger.error(f"Error registering device: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to register device: {str(e)}",
            error_code="REGISTER_DEVICE_ERROR",
            error_type=type(e).__name__,
            operation="register_device",
        )


async def update_device_helper(device_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to update device information."""
    try:
        tool = _get_sync_tool()
        return await tool.sync_update_device(device_id=device_id, updates=updates)
    except Exception as e:
        logger.error(f"Error updating device: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to update device: {str(e)}",
            error_code="UPDATE_DEVICE_ERROR",
            error_type=type(e).__name__,
            operation="update_device",
        )


async def get_device_helper(device_id: str) -> Dict[str, Any]:
    """Helper to get device information."""
    try:
        tool = _get_sync_tool()
        return await tool.sync_get_device(device_id=device_id)
    except Exception as e:
        logger.error(f"Error getting device: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get device: {str(e)}",
            error_code="GET_DEVICE_ERROR",
            error_type=type(e).__name__,
            operation="get_device",
        )


async def start_sync_helper(
    device_id: str,
    sync_type: str = "full",
    library_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper to start a sync job."""
    try:
        tool = _get_sync_tool()
        return await tool.sync_start(
            device_id=device_id, sync_type=sync_type, library_path=library_path
        )
    except Exception as e:
        logger.error(f"Error starting sync: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to start sync: {str(e)}",
            error_code="START_SYNC_ERROR",
            error_type=type(e).__name__,
            operation="start",
        )


async def get_sync_status_helper(job_id: str) -> Dict[str, Any]:
    """Helper to get sync job status."""
    try:
        tool = _get_sync_tool()
        return await tool.sync_status(job_id=job_id)
    except Exception as e:
        logger.error(f"Error getting sync status: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to get sync status: {str(e)}",
            error_code="GET_SYNC_STATUS_ERROR",
            error_type=type(e).__name__,
            operation="status",
        )


async def cancel_sync_helper(job_id: str) -> Dict[str, Any]:
    """Helper to cancel a sync job."""
    try:
        tool = _get_sync_tool()
        return await tool.sync_cancel(job_id=job_id)
    except Exception as e:
        logger.error(f"Error canceling sync: {e}", exc_info=True)
        return format_error_response(
            error_msg=f"Failed to cancel sync: {str(e)}",
            error_code="CANCEL_SYNC_ERROR",
            error_type=type(e).__name__,
            operation="cancel",
        )

