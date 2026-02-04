"""Tool for managing CalibreMCP users and permissions."""

import secrets
import string
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

import jwt
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer, validator

try:
    from fastmcp import MCPTool
except ImportError:
    from ..compat import MCPTool


# Models
class UserRole(str, Enum):
    """User roles with permissions."""

    ADMIN = "admin"  # Full access, including user management
    LIBRARIAN = "librarian"  # Can manage books and metadata
    READER = "reader"  # Can only read books

    @classmethod
    def has_permission(cls, role: str, required: str) -> bool:
        """Check if a role has the required permission level."""
        hierarchy = {cls.ADMIN.value: 3, cls.LIBRARIAN.value: 2, cls.READER.value: 1}
        return hierarchy.get(role, 0) >= hierarchy.get(required, 99)


class UserCreate(BaseModel):
    """Model for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.READER
    full_name: str | None = None
    is_active: bool = True

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Model for updating an existing user."""

    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None
    full_name: str | None = None
    is_active: bool | None = None

    @validator("password")
    def validate_password(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserResponse(BaseModel):
    """Response model for user data (without sensitive info)."""

    model_config = ConfigDict()

    id: str
    username: str
    email: str
    role: UserRole
    full_name: str | None
    is_active: bool
    created_at: datetime
    last_login: datetime | None

    @field_serializer("created_at", "last_login")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        """Serialize datetime fields to ISO format strings."""
        return value.isoformat() if value else None


# Main tool
class UserManagerTool(MCPTool):
    """Manage users and authentication for CalibreMCP."""

    name = "user_manager"
    description = "Manage users and authentication"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._jwt_secret = self._load_or_create_secret()
        self._jwt_algorithm = "HS256"
        self._jwt_expire_minutes = 60 * 24 * 7  # 7 days

    def _load_or_create_secret(self) -> str:
        """Load or create a JWT secret key."""
        secret_path = Path("data/secrets/jwt_secret.txt")
        secret_path.parent.mkdir(parents=True, exist_ok=True)

        if secret_path.exists():
            return secret_path.read_text(encoding="utf-8").strip()

        # Generate a new secret
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        secret = "".join(secrets.choice(alphabet) for _ in range(64))
        secret_path.write_text(secret, encoding="utf-8")
        return secret

    async def _run(self, action: str, **kwargs) -> dict:
        """Route to the appropriate handler method."""
        handler = getattr(self, f"handle_{action}", None)
        if not handler:
            return {"error": f"Unknown action: {action}", "success": False}

        try:
            return await handler(**kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}

    # User Management
    async def handle_create_user(self, user_data: dict) -> dict:
        """Create a new user."""
        UserCreate(**user_data)

        # Hash password
        # hashed = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        # In a real implementation, save to database
        # user_id = await self._save_user_to_db({
        #     'username': user.username,
        #     'email': user.email,
        #     'password_hash': hashed.decode('utf-8'),
        #     'role': user.role,
        #     'full_name': user.full_name,
        #     'is_active': user.is_active,
        #     'created_at': datetime.utcnow(),
        #     'last_login': None
        # })

        # For now, just return a mock response
        return {"success": True, "user_id": "mock_user_id", "message": "User created successfully"}

    async def handle_update_user(self, user_id: str, update_data: dict) -> dict:
        """Update an existing user."""
        # update = UserUpdate(**update_data)

        # In a real implementation, update in database
        # if update.password:
        #     hashed = bcrypt.hashpw(update.password.encode('utf-8'), bcrypt.gensalt())
        #     update_data['password_hash'] = hashed.decode('utf-8')
        #     del update_data['password']
        #
        # await self._update_user_in_db(user_id, update_data)

        return {"success": True, "message": "User updated successfully"}

    async def handle_delete_user(self, user_id: str) -> dict:
        """Delete a user."""
        # In a real implementation, delete from database
        # await self._delete_user_from_db(user_id)

        return {"success": True, "message": "User deleted successfully"}

    # Authentication
    async def handle_login(self, username: str, password: str) -> dict:
        """Authenticate a user and return a JWT token."""
        # In a real implementation, get user from database
        # user = await self._get_user_by_username(username)
        # if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        #     return {"error": "Invalid username or password", "success": False}
        #
        # # Update last login
        # await self._update_user_in_db(user['id'], {'last_login': datetime.utcnow()})

        # For now, use a mock user
        if username != "admin" or password != "admin123":
            return {"error": "Invalid username or password", "success": False}

        user_data = {
            "id": "mock_admin_id",
            "username": "admin",
            "role": UserRole.ADMIN,
            "is_active": True,
        }

        # Generate JWT token
        token = self._generate_jwt(user_data)

        return {
            "success": True,
            "token": token,
            "user": {
                "id": user_data["id"],
                "username": user_data["username"],
                "role": user_data["role"],
                "token_expires": (
                    datetime.utcnow() + timedelta(minutes=self._jwt_expire_minutes)
                ).isoformat(),
            },
        }

    async def handle_verify_token(self, token: str) -> dict:
        """Verify a JWT token and return user data if valid."""
        try:
            payload = jwt.decode(token, self._jwt_secret, algorithms=[self._jwt_algorithm])
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
            return {"success": True, "valid": False, "error": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"success": True, "valid": False, "error": "Invalid token"}

    # Helper methods
    def _generate_jwt(self, user_data: dict) -> str:
        """Generate a JWT token for the user."""
        now = datetime.utcnow()
        expires = now + timedelta(minutes=self._jwt_expire_minutes)

        payload = {
            "sub": str(user_data["id"]),
            "username": user_data["username"],
            "role": user_data["role"],
            "iat": int(now.timestamp()),
            "exp": int(expires.timestamp()),
        }

        return jwt.encode(payload, self._jwt_secret, algorithm=self._jwt_algorithm)

    # User listing and details
    async def handle_list_users(self, page: int = 1, per_page: int = 20) -> dict:
        """List all users with pagination."""
        # In a real implementation, fetch from database with pagination
        # users = await self._get_users_from_db(page, per_page)
        # total = await self._count_users()

        # Mock response
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

    async def handle_get_user(self, user_id: str) -> dict:
        """Get details for a specific user."""
        # In a real implementation, fetch from database
        # user = await self._get_user_by_id(user_id)

        # Mock response
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

        return {"success": False, "error": "User not found"}
