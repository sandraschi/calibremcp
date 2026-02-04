"""
Configuration settings for the Calibre MCP Server.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# import sys # Removed unused
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

    # Server configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Calibre MCP Server"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # CORS configuration
    CORS_ORIGINS: list[str] = ["*"]

    # Database configuration (accepts CALIBRE_LIBRARY_PATH or LIBRARY_PATH)
    LIBRARY_PATH: str | None = Field(
        None,
        validation_alias=AliasChoices("CALIBRE_LIBRARY_PATH", "LIBRARY_PATH"),
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days


# Initialize settings
settings = Settings()

# Ensure library path exists if specified
if settings.LIBRARY_PATH:
    settings.LIBRARY_PATH = Path(settings.LIBRARY_PATH).absolute()
    if not settings.LIBRARY_PATH.exists():
        raise FileNotFoundError(f"Library path does not exist: {settings.LIBRARY_PATH}")

# Export settings
__all__ = ["settings"]
