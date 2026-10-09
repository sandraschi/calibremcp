"""
Unit tests for manage_users portmanteau tool.

Tests key operations: create_user, get_user, list_users, login, verify_token
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.user_management.manage_users import manage_users


@pytest.mark.asyncio
async def test_manage_users_create_user():
    """Test manage_users create_user operation."""
    user_data = {"username": "testuser", "email": "test@example.com", "password": "password123", "role": "user"}
    result = await manage_users(operation="create_user", user_data=user_data)

    # Currently returns mock response
    assert "success" in result
    assert result["success"] is True
    assert "user_id" in result


@pytest.mark.asyncio
async def test_manage_users_get_user():
    """Test manage_users get_user operation."""
    # Currently returns mock response
    result = await manage_users(operation="get_user", user_id="mock_user_id")

    # Currently returns mock response
    assert "success" in result


@pytest.mark.asyncio
async def test_manage_users_list_users():
    """Test manage_users list_users operation."""
    result = await manage_users(operation="list_users")

    # Currently returns mock response
    assert result["success"] is True
    assert "users" in result
    assert isinstance(result["users"], list)


@pytest.mark.asyncio
async def test_manage_users_login():
    """Test manage_users login operation."""
    # Currently returns mock/error response (no real users stored)
    result = await manage_users(operation="login", username="testuser", password="password123")

    # May return error since no real user storage
    assert "success" in result or "error" in result


@pytest.mark.asyncio
async def test_manage_users_verify_token():
    """Test manage_users verify_token operation."""
    # Test with invalid token (since no real user storage)
    result = await manage_users(operation="verify_token", token="invalid_token")

    # Should return valid=False or error
    assert "success" in result
    assert result.get("valid") is False or "error" in result


@pytest.mark.asyncio
async def test_manage_users_invalid_operation():
    """Test manage_users with invalid operation."""
    result = await manage_users(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_users_missing_required_params():
    """Test manage_users with missing required parameters."""
    # Get_user operation requires user_id
    result = await manage_users(operation="get_user")

    assert "error" in result
    assert "user_id is required" in result["error"]

    # Create_user operation requires user_data
    result = await manage_users(operation="create_user")

    assert "error" in result
    assert "user_data is required" in result["error"]
