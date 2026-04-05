"""Settings and configuration API."""

from fastapi import APIRouter
from pydantic import BaseModel

from calibre_mcp.config import CalibreConfig
from ..config import settings

router = APIRouter()


class SettingsUpdate(BaseModel):
    """Request body for updating settings."""

    annas_mirrors: list[str] | None = None
    gutenberg_mirror: str | None = None


@router.get("/")
async def get_settings():
    """Get current mirror settings."""
    config = CalibreConfig.load_config(settings.CALIBRE_CONFIG_PATH)
    return {
        "annas_mirrors": config.annas_mirrors,
        "gutenberg_mirror": config.gutenberg_mirror,
    }


@router.patch("/")
async def update_settings(body: SettingsUpdate):
    """Update mirror settings."""
    config = CalibreConfig.load_config(settings.CALIBRE_CONFIG_PATH)

    if body.annas_mirrors is not None:
        config.annas_mirrors = body.annas_mirrors
    if body.gutenberg_mirror is not None:
        config.gutenberg_mirror = body.gutenberg_mirror

    # Try to persist using common config path
    if config.save_config(settings.CALIBRE_CONFIG_PATH):
        return {"success": True, "message": "Settings updated and saved."}
    else:
        # Fallback: updated in memory only if save fails
        return {"success": True, "message": "Settings updated in memory (save failed)."}
