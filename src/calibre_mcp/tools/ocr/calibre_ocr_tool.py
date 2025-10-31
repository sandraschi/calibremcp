"""OCR tool for CalibreMCP using FineReader CLI."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ..base_tool import BaseTool, mcp_tool
from ...utils.finereader import FineReaderCLI, safe_ocr_process

logger = logging.getLogger(__name__)


class OCRTool(BaseTool):
    """OCR tools for scanned document processing."""

    @mcp_tool(name="calibre_ocr", description="Process scanned documents with OCR using FineReader")
    async def process_ocr(
        self, source: str, language: Optional[str] = None, output_format: str = "pdf"
    ) -> Dict[str, Any]:
        """Process single document with OCR.

        Args:
            source: Source file path
            language: OCR language (default: english)
            output_format: Output format (default: pdf)

        Returns:
            OCR processing results
        """
        # Test if FineReader is available
        try:
            FineReaderCLI()
        except FileNotFoundError as e:
            return {"success": False, "error": "FineReader CLI not found", "details": str(e)}

        source_path = Path(source)
        if not source_path.exists():
            return {"success": False, "error": f"Source file not found: {source}"}

        output_path = source_path.parent / f"{source_path.stem}_ocr.{output_format}"
        language = language or "english"

        result = await safe_ocr_process(source_path, output_path, language=language)

        if result["success"]:
            return {"success": True, **result["result"]}
        else:
            return result
