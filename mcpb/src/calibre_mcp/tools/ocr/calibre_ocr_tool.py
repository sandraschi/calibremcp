"""OCR tool for CalibreMCP using FineReader CLI."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ..base_tool import BaseTool, mcp_tool

# Optional imports - handle gracefully if OCR dependencies are not available
try:
    from ...utils.finereader import FineReaderCLI, safe_ocr_process

    OCR_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    OCR_AVAILABLE = False
    FineReaderCLI = None
    safe_ocr_process = None

logger = logging.getLogger(__name__)


class OCRTool(BaseTool):
    """OCR tools for scanned document processing."""

    @mcp_tool(name="calibre_ocr", description="Process scanned documents with OCR using FineReader")
    async def process_ocr(
        self, source: str, language: Optional[str] = None, output_format: str = "pdf"
    ) -> Dict[str, Any]:
        """
        Process scanned documents with OCR using ABBYY FineReader CLI.

        Converts scanned images or PDFs into searchable text documents by extracting
        text through Optical Character Recognition. This tool requires FineReader CLI
        to be installed and accessible in the system PATH.

        The processed document will be saved in the same directory as the source file
        with "_ocr" appended to the filename and the specified output format extension.

        Args:
            source: Full path to the source document file (images: PNG, JPEG, TIFF; PDFs supported)
            language: OCR language code (default: "english"). Common options include:
                - "english", "german", "french", "spanish", "italian"
                - "japanese", "chinese", "korean" (if FineReader supports them)
                - Use language code matching FineReader CLI language identifiers
            output_format: Output file format (default: "pdf"). Options:
                - "pdf" - Searchable PDF with text layer
                - Other formats depend on FineReader CLI capabilities

        Returns:
            Dictionary containing processing results:
            {
                "success": bool - Whether OCR processing succeeded
                "output_path": str - Path to the processed output file (if successful)
                "error": str - Error message (if failed)
                "details": str - Additional error details (if failed)
            }

        Example:
            # Process a scanned PDF with English OCR
            result = process_ocr(
                source="/path/to/scanned_book.pdf",
                language="english",
                output_format="pdf"
            )

            # Process a Japanese document
            result = process_ocr(
                source="/path/to/japanese_doc.pdf",
                language="japanese",
                output_format="pdf"
            )

        Raises:
            FileNotFoundError: If source file doesn't exist or FineReader CLI not found
            Exception: For other OCR processing errors
        """
        # Check if OCR dependencies are available
        if not OCR_AVAILABLE:
            return {
                "success": False,
                "error": "OCR functionality not available",
                "details": "FineReader utilities could not be imported. OCR dependencies may not be installed.",
            }

        # Check if FineReader CLI is available (without instantiating)
        if not FineReaderCLI.is_available():
            return {
                "success": False,
                "error": "FineReader CLI not found",
                "details": (
                    "FineReader CLI executable not found. "
                    "Set FINEREADER_CLI_PATH environment variable, "
                    "add FineCmd.exe to PATH, or install FineReader 15+."
                ),
            }

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
