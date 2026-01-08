"""
User management portmanteau tool for CalibreMCP.

Migrated from UserManagerTool (MCPTool) to FastMCP 2.13+ @mcp.tool() pattern.
Consolidates all user management and authentication operations into a single portmanteau tool.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
import string
import secrets

import jwt

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response
from .user_manager import (
    UserCreate,
    UserUpdate,
    UserRole,
)

logger = get_logger("calibremcp.tools.user_management")


def _load_or_create_secret() -> str:
    """Load or create a JWT secret key."""
    secret_path = Path("data/secrets/jwt_secret.txt")
    secret_path.parent.mkdir(parents=True, exist_ok=True)

    if secret_path.exists():
        return secret_path.read_text(encoding="utf-8").strip()

    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    secret = "".join(secrets.choice(alphabet) for _ in range(64))
    secret_path.write_text(secret, encoding="utf-8")
    return secret


_jwt_secret = _load_or_create_secret()
_jwt_algorithm = "HS256"
_jwt_expire_minutes = 60 * 24 * 7  # 7 days


def _generate_jwt(user_data: Dict[str, Any]) -> str:
    """Generate a JWT token for the user."""
    now = datetime.utcnow()
    expires = now + timedelta(minutes=_jwt_expire_minutes)

    payload = {
        "sub": str(user_data["id"]),
        "username": user_data["username"],
        "role": user_data["role"],
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }

    return jwt.encode(payload, _jwt_secret, algorithm=_jwt_algorithm)


@mcp.tool()
async def manage_users(
    operation: str,
    user_id: Optional[str] = None,
    user_data: Optional[Dict[str, Any]] = None,
    update_data: Optional[Dict[str, Any]] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> Dict[str, Any]:
    """
    Manage users and authentication with multiple operations in a single unified interface.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 7 separate tools (one per operation), this tool consolidates related
    user management operations into a single interface. This design:
    - Prevents tool explosion (7 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with user management tasks
    - Enables consistent user interface across all operations
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - create_user: Create a new user account
    - update_user: Update an existing user's information
    - delete_user: Delete a user account
    - list_users: List all users with pagination
    - get_user: Get details for a specific user
    - login: Authenticate a user and get a JWT token
    - verify_token: Verify a JWT token's validity

    OPERATIONS DETAIL:

    create_user: Create a new user account
    - Creates a user with username, email, password, and role
    - Parameters: user_data (required) with username, email, password, role
    - Returns: Created user ID and status

    update_user: Update user information
    - Updates user fields such as email, role, password, etc.
    - Parameters: user_id (required), update_data (required)
    - Returns: Update confirmation

    delete_user: Delete a user account
    - Removes user from system
    - Parameters: user_id (required)
    - Returns: Deletion confirmation

    list_users: List all users
    - Returns paginated list of all users
    - Parameters: page (optional, default: 1), per_page (optional, default: 20)
    - Returns: List of users with pagination info

    get_user: Get user details
    - Retrieves complete user information by ID
    - Parameters: user_id (required)
    - Returns: User data

    login: Authenticate user
    - Validates credentials and returns JWT token
    - Parameters: username (required), password (required)
    - Returns: JWT token and user information

    verify_token: Verify JWT token
    - Validates JWT token and returns user information
    - Parameters: token (required)
    - Returns: Token validity and user information

    Prerequisites:
        - For 'create_user': Provide user_data with username, email, password, role
        - For 'update_user', 'delete_user', 'get_user': User must exist (user_id required)
        - For 'login': Valid username and password required
        - For 'verify_token': Valid JWT token required

    Parameters:
        operation: The operation to perform. Must be one of: "create_user", "update_user", "delete_user", "list_users", "get_user", "login", "verify_token"
            - "create_user": Create a new user. Requires `user_data` parameter.
            - "update_user": Update user information. Requires `user_id` and `update_data` parameters.
            - "delete_user": Delete a user. Requires `user_id` parameter.
            - "list_users": List all users. Optional `page` and `per_page` parameters.
            - "get_user": Get user details. Requires `user_id` parameter.
            - "login": Authenticate user. Requires `username` and `password` parameters.
            - "verify_token": Verify JWT token. Requires `token` parameter.

        user_id: ID of the user (required for 'update_user', 'delete_user', 'get_user')
            - Use operation="list_users" to see all user IDs
            - Example: "user_123" or "mock_admin_id"

        user_data: User data for creation (required for 'create_user')
            - Must include: username, email, password, role
            - Optional: full_name, is_active
            - Example: {"username": "john_doe", "email": "john@example.com", "password": "secure123", "role": "user"}

        update_data: Updates to apply (required for 'update_user')
            - Can update: username, email, password, role, full_name, is_active
            - Example: {"email": "newemail@example.com", "role": "admin"}

        username: Username for login (required for 'login')
            - Must match an existing user account

        password: Password for login (required for 'login')
            - Must match the user's password

        token: JWT token to verify (required for 'verify_token')
            - Token obtained from operation="login"

        page: Page number for listing (for 'list_users', default: 1)

        per_page: Items per page (for 'list_users', default: 20)

    Returns:
        Dictionary containing operation-specific results:

        For operation="create_user":
            {
                "success": bool - Whether creation succeeded
                "user_id": str - Created user ID
                "message": str - Status message
            }

        For operation="update_user":
            {
                "success": bool - Whether update succeeded
                "message": str - Status message
            }

        For operation="delete_user":
            {
                "success": bool - Whether deletion succeeded
                "message": str - Status message
            }

        For operation="list_users":
            {
                "success": bool - Always True
                "users": List[Dict] - List of users
                "pagination": Dict - Pagination information
            }

        For operation="get_user":
            {
                "success": bool - Whether user was found
                "user": Dict - User data
            }

        For operation="login":
            {
                "success": bool - Whether authentication succeeded
                "token": str - JWT token (if successful)
                "user": Dict - User data with token expiration
                "error": str - Error message (if failed)
            }

        For operation="verify_token":
            {
                "success": bool - Always True
                "valid": bool - Whether token is valid
                "user": Optional[Dict] - User data if valid
                "error": Optional[str] - Error message if invalid
            }

    Usage:
        # Create a new user
        result = await manage_users(
            operation="create_user",
            user_data={
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure123",
                "role": "user"
            }
        )

        # Login
        result = await manage_users(
            operation="login",
            username="john_doe",
            password="secure123"
        )
        token = result["token"]

        # Verify token
        result = await manage_users(
            operation="verify_token",
            token=token
        )

        # List users
        result = await manage_users(
            operation="list_users",
            page=1,
            per_page=20
        )

    Examples:
        # Create admin user
        result = await manage_users(
            operation="create_user",
            user_data={
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
                "role": "admin",
                "full_name": "Administrator",
                "is_active": True
            }
        )

        # Login and get token
        login_result = await manage_users(
            operation="login",
            username="admin",
            password="admin123"
        )
        if login_result["success"]:
            token = login_result["token"]
            print(f"Token expires: {login_result['user']['token_expires']}")

        # Verify token before making authenticated requests
        verify_result = await manage_users(
            operation="verify_token",
            token=token
        )
        if verify_result["valid"]:
            print(f"Authenticated as: {verify_result['user']['username']}")

        # Update user role
        update_result = await manage_users(
            operation="update_user",
            user_id="user_123",
            update_data={"role": "admin"}
        )

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of the supported operations
        - Missing user_id: Provide user_id for update/delete/get operations
        - Missing user_data: Provide user_data for create_user operation
        - Missing username/password: Provide both for login operation
        - Missing token: Provide token for verify_token operation
        - Invalid credentials: Check username and password for login
        - User not found: Verify user_id is correct

    See Also:
        - UserManagerTool: Legacy tool (deprecated in favor of this portmanteau tool)
    """
    try:
        if operation == "create_user":
            if not user_data:
                return format_error_response(
                    error_msg="user_data is required for operation='create_user'.",
                    error_code="MISSING_USER_DATA",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=[
                        "Provide user_data with username, email, password, and role",
                        "Example: user_data={'username': 'john', 'email': 'john@example.com', 'password': 'pass123', 'role': 'user'}",
                    ],
                    related_tools=["manage_users"],
                )
            return await _handle_create_user(user_data)

        elif operation == "update_user":
            if not user_id:
                return format_error_response(
                    error_msg="user_id is required for operation='update_user'.",
                    error_code="MISSING_USER_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Use operation='list_users' to see all available user IDs"],
                    related_tools=["manage_users"],
                )
            if not update_data:
                return format_error_response(
                    error_msg="update_data is required for operation='update_user'.",
                    error_code="MISSING_UPDATE_DATA",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide update_data dictionary with fields to update"],
                    related_tools=["manage_users"],
                )
            return await _handle_update_user(user_id, update_data)

        elif operation == "delete_user":
            if not user_id:
                return format_error_response(
                    error_msg="user_id is required for operation='delete_user'.",
                    error_code="MISSING_USER_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Use operation='list_users' to see all available user IDs"],
                    related_tools=["manage_users"],
                )
            return await _handle_delete_user(user_id)

        elif operation == "list_users":
            return await _handle_list_users(page, per_page)

        elif operation == "get_user":
            if not user_id:
                return format_error_response(
                    error_msg="user_id is required for operation='get_user'.",
                    error_code="MISSING_USER_ID",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Use operation='list_users' to see all available user IDs"],
                    related_tools=["manage_users"],
                )
            return await _handle_get_user(user_id)

        elif operation == "login":
            if not username:
                return format_error_response(
                    error_msg="username is required for operation='login'.",
                    error_code="MISSING_USERNAME",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide username parameter"],
                    related_tools=["manage_users"],
                )
            if not password:
                return format_error_response(
                    error_msg="password is required for operation='login'.",
                    error_code="MISSING_PASSWORD",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide password parameter"],
                    related_tools=["manage_users"],
                )
            return await _handle_login(username, password)

        elif operation == "verify_token":
            if not token:
                return format_error_response(
                    error_msg="token is required for operation='verify_token'.",
                    error_code="MISSING_TOKEN",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=["Provide token parameter from operation='login'"],
                    related_tools=["manage_users"],
                )
            return await _handle_verify_token(token)

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'create_user', 'update_user', 'delete_user', 'list_users', "
                    "'get_user', 'login', 'verify_token'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='create_user' to create a new user",
                    "Use operation='update_user' to update user information",
                    "Use operation='delete_user' to delete a user",
                    "Use operation='list_users' to list all users",
                    "Use operation='get_user' to get user details",
                    "Use operation='login' to authenticate and get a token",
                    "Use operation='verify_token' to verify a JWT token",
                ],
                related_tools=["manage_users"],
            )
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "user_id": user_id,
                "username": username,
            },
            tool_name="manage_users",
            context="User management operation",
        )


async def _handle_create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle create user operation."""
    try:
        UserCreate(**user_data)

        # In a real implementation, save to database
        # hashed = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
        # user_id = await save_user_to_db({...})

        return {"success": True, "user_id": "mock_user_id", "message": "User created successfully"}
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="create_user",
            parameters={"user_data": user_data},
            tool_name="manage_users",
            context="Creating new user",
        )


async def _handle_update_user(user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle update user operation."""
    try:
        UserUpdate(**update_data)

        # In a real implementation, update in database
        return {"success": True, "message": "User updated successfully"}
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="update_user",
            parameters={"user_id": user_id, "update_data": update_data},
            tool_name="manage_users",
            context=f"Updating user {user_id}",
        )


async def _handle_delete_user(user_id: str) -> Dict[str, Any]:
    """Handle delete user operation."""
    try:
        # In a real implementation, delete from database
        return {"success": True, "message": "User deleted successfully"}
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="delete_user",
            parameters={"user_id": user_id},
            tool_name="manage_users",
            context=f"Deleting user {user_id}",
        )


async def _handle_list_users(page: int, per_page: int) -> Dict[str, Any]:
    """Handle list users operation."""
    try:
        # Mock response - in real implementation, fetch from database
        users = [
            {
                "id": "mock_admin_id",
                "username": "admin",
                "email": "admin@example.com",
                "role": UserRole.ADMIN,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat(),
            }
        ]

        return {
            "success": True,
            "users": users,
            "pagination": {"page": page, "per_page": per_page, "total": 1, "total_pages": 1},
        }
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="list_users",
            parameters={"page": page, "per_page": per_page},
            tool_name="manage_users",
            context="Listing users",
        )


async def _handle_get_user(user_id: str) -> Dict[str, Any]:
    """Handle get user operation."""
    try:
        # Mock response - in real implementation, fetch from database
        if user_id == "mock_admin_id":
            user = {
                "id": "mock_admin_id",
                "username": "admin",
                "email": "admin@example.com",
                "role": UserRole.ADMIN,
                "full_name": "Administrator",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat(),
            }
            return {"success": True, "user": user}

        return format_error_response(
            error_msg=f"User {user_id} not found",
            error_code="USER_NOT_FOUND",
            error_type="KeyError",
            operation="get_user",
            suggestions=["Use operation='list_users' to see all available users"],
            related_tools=["manage_users"],
        )
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="get_user",
            parameters={"user_id": user_id},
            tool_name="manage_users",
            context=f"Getting user {user_id}",
        )


async def _handle_login(username: str, password: str) -> Dict[str, Any]:
    """Handle login operation."""
    try:
        # Mock authentication - in real implementation, verify against database
        if username != "admin" or password != "admin123":
            return format_error_response(
                error_msg="Invalid username or password",
                error_code="INVALID_CREDENTIALS",
                error_type="ValueError",
                operation="login",
                suggestions=[
                    "Check your username and password",
                    "Contact administrator if you forgot your credentials",
                ],
                related_tools=["manage_users"],
            )

        user_data = {
            "id": "mock_admin_id",
            "username": "admin",
            "role": UserRole.ADMIN,
            "is_active": True,
        }

        token = _generate_jwt(user_data)

        return {
            "success": True,
            "token": token,
            "user": {
                "id": user_data["id"],
                "username": user_data["username"],
                "role": user_data["role"],
                "token_expires": (
                    datetime.utcnow() + timedelta(minutes=_jwt_expire_minutes)
                ).isoformat(),
            },
        }
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation="login",
            parameters={"username": username},
            tool_name="manage_users",
            context=f"Logging in user '{username}'",
        )


async def _handle_verify_token(token: str) -> Dict[str, Any]:
    """Handle verify token operation."""
    try:
        payload = jwt.decode(token, _jwt_secret, algorithms=[_jwt_algorithm])
        return {
            "success": True,
            "valid": True,
            "user": {
                "id": payload["sub"],
                "username": payload["username"],
                "role": payload["role"],
                "expires": payload["exp"],
            },
        }
    except jwt.ExpiredSignatureError:
        return {
            "success": True,
            "valid": False,
            "error": "Token has expired",
            "suggestions": ["Login again to get a new token"],
        }
    except jwt.InvalidTokenError:
        return {
            "success": True,
            "valid": False,
            "error": "Invalid token",
            "suggestions": ["Verify the token is correct", "Login again to get a new token"],
        }
    except Exception as e:
        logger.error(f"Error verifying token: {e}", exc_info=True)
        return {"success": True, "valid": False, "error": f"Token verification failed: {str(e)}"}
