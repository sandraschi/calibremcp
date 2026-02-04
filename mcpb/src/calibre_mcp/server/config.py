"""
Configuration settings for the Calibre MCP Server.
"""

import os
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    # Server configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Calibre MCP Server"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # CORS configuration
    CORS_ORIGINS: list[str] = ["*"]

    # Database configuration
    LIBRARY_PATH: str | None = None

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    class Config:
        case_sensitive = True
        env_file = ".env"


# Initialize settings
settings = Settings()

# Ensure library path exists if specified
if settings.LIBRARY_PATH:
    settings.LIBRARY_PATH = Path(settings.LIBRARY_PATH).absolute()
    if not settings.LIBRARY_PATH.exists():
        raise FileNotFoundError(f"Library path does not exist: {settings.LIBRARY_PATH}")

# Export settings
__all__ = ["settings"]
