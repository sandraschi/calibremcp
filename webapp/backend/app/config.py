"""Configuration for Calibre webapp backend."""

from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # API Configuration
    API_TITLE: str = "Calibre Webapp API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "HTTP API wrapper for CalibreMCP server"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 13000
    RELOAD: bool = True

    # CORS Configuration (comma-separated string in .env)
    CORS_ORIGINS: str = "http://localhost:13001,http://127.0.0.1:13001"

    @property
    def cors_origins_list(self) -> List[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]
    
    # MCP Server configuration
    # false = direct in-process calls (faster, recommended for webapp)
    # true = HTTP to /mcp (adds latency, can deadlock; use only for stdio MCP clients)
    MCP_USE_HTTP: bool = False
    BACKEND_URL: str = "http://127.0.0.1:13000"

    @field_validator("MCP_USE_HTTP", mode="before")
    @classmethod
    def parse_mcp_use_http(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.strip().lower() == "true"
        return False
    
    # MCP Server Configuration
    MCP_SERVER_COMMAND: str = "python"
    MCP_SERVER_ARGS: List[str] = ["-m", "calibre_mcp.server"]

    # LLM/AI Configuration (Ollama, LM Studio, OpenAI-compatible)
    LLM_PROVIDER: str = "ollama"
    LLM_BASE_URL: str = "http://127.0.0.1:11434"
    LLM_API_KEY: str = ""


settings = Settings()
