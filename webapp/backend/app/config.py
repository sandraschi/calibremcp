"""Configuration for Calibre webapp backend."""

import os
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_TITLE: str = "Calibre Webapp API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "HTTP API wrapper for CalibreMCP server"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 13000
    RELOAD: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:13001",
        "http://127.0.0.1:13001",
    ]
    
    # MCP Server configuration
    # FastMCP HTTP endpoints are mounted at /mcp on the same backend server (port 13000)
    # No separate MCP server port - everything runs on backend port 13000!
    MCP_USE_HTTP: bool = os.getenv("MCP_USE_HTTP", "true").lower() == "true"
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://127.0.0.1:13000")
    
    # MCP Server Configuration
    MCP_SERVER_COMMAND: str = "python"
    MCP_SERVER_ARGS: List[str] = ["-m", "calibre_mcp.server"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
