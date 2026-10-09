"""
Unit tests for manage_content_sync portmanteau tool.

Tests all 6 operations: register_device, update_device, get_device,
start, status, cancel
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.advanced_features.manage_content_sync import (
        manage_content_sync,
    )


@pytest.fixture
def mock_sync_helpers():
    """Mock the content sync helper functions."""
    with (
        patch("calibre_mcp.tools.advanced_features.manage_content_sync.register_device_helper") as register,
        patch("calibre_mcp.tools.advanced_features.manage_content_sync.update_device_helper") as update,
        patch("calibre_mcp.tools.advanced_features.manage_content_sync.get_device_helper") as get_device,
        patch("calibre_mcp.tools.advanced_features.manage_content_sync.start_sync_helper") as start,
        patch("calibre_mcp.tools.advanced_features.manage_content_sync.get_sync_status_helper") as status,
        patch("calibre_mcp.tools.advanced_features.manage_content_sync.cancel_sync_helper") as cancel,
    ):
        register.return_value = {"device_id": "device-123", "name": "Test Device"}

        update.return_value = {"success": True, "device_id": "device-123"}

        get_device.return_value = {"device_id": "device-123", "name": "Test Device", "type": "mobile"}

        start.return_value = {"job_id": "job-456", "status": "running"}

        status.return_value = {"job_id": "job-456", "status": "completed", "progress": 100}

        cancel.return_value = {"success": True, "job_id": "job-456"}

        yield {
            "register": register,
            "update": update,
            "get_device": get_device,
            "start": start,
            "status": status,
            "cancel": cancel,
        }


@pytest.mark.asyncio
async def test_manage_content_sync_register_device(mock_sync_helpers):
    """Test manage_content_sync register_device operation."""
    result = await manage_content_sync(operation="register_device", name="Test Device", device_type="mobile")

    assert result["device_id"] == "device-123"
    mock_sync_helpers["register"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_content_sync_update_device(mock_sync_helpers):
    """Test manage_content_sync update_device operation."""
    result = await manage_content_sync(
        operation="update_device", device_id="device-123", updates={"name": "Updated Device"}
    )

    assert result["success"] is True
    mock_sync_helpers["update"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_content_sync_get_device(mock_sync_helpers):
    """Test manage_content_sync get_device operation."""
    result = await manage_content_sync(operation="get_device", device_id="device-123")

    assert result["device_id"] == "device-123"
    mock_sync_helpers["get_device"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_content_sync_start(mock_sync_helpers):
    """Test manage_content_sync start operation."""
    result = await manage_content_sync(operation="start", device_id="device-123")

    assert result["job_id"] == "job-456"
    mock_sync_helpers["start"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_content_sync_status(mock_sync_helpers):
    """Test manage_content_sync status operation."""
    result = await manage_content_sync(operation="status", job_id="job-456")

    assert result["status"] == "completed"
    mock_sync_helpers["status"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_content_sync_cancel(mock_sync_helpers):
    """Test manage_content_sync cancel operation."""
    result = await manage_content_sync(operation="cancel", job_id="job-456")

    assert result["success"] is True
    mock_sync_helpers["cancel"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_content_sync_invalid_operation():
    """Test manage_content_sync with invalid operation."""
    result = await manage_content_sync(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_content_sync_missing_required_params():
    """Test manage_content_sync with missing required parameters."""
    # Register requires name and device_type
    result = await manage_content_sync(operation="register_device")

    assert "error" in result
    assert "name and device_type are required" in result["error"]
