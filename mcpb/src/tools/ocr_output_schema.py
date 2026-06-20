"""MCP output schema for calibre_ocr (FineReader / GOT-OCR2.0).

Kept at ``tools/ocr_output_schema.py`` (not under ``ocr/``) so importing the schema
does not run ``ocr/__init__.py`` (which eagerly imports GOT-OCR / PIL).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CalibreOCROutput(BaseModel):
    """
    OCR tool result: always an object; ``success`` discriminates happy path vs failure.

    Provider-specific fields (GOT-OCR text, FineReader output paths, etc.) are allowed
    via ``additionalProperties`` for forward compatibility.
    """

    model_config = ConfigDict(extra="allow")

    success: bool = Field(
        description="True when OCR completed; False on missing file, CLI, or model"
    )
    error: str | None = Field(
        default=None, description="Human-readable failure summary when success is false"
    )
    details: str | None = Field(
        default=None,
        description="Recovery hints: FINEREADER_CLI_PATH, install GOT-OCR deps, etc.",
    )
    recovery_options: list[str] | None = Field(
        default=None,
        description="Actionable next steps to recover from errors.",
    )
    provider: str | None = Field(
        default=None,
        description="Backend used or attempted: auto | finereader | got-ocr",
    )


CALIBRE_OCR_OUTPUT_SCHEMA: dict[str, Any] = CalibreOCROutput.model_json_schema()
