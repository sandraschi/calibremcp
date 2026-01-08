"""OCR tool for CalibreMCP using FineReader CLI and GOT-OCR2.0."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, List

from ..base_tool import BaseTool, mcp_tool

# Optional imports - handle gracefully if OCR dependencies are not available
try:
    from ...utils.finereader import FineReaderCLI, safe_ocr_process

    FINEREADER_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    FINEREADER_AVAILABLE = False
    FineReaderCLI = None
    safe_ocr_process = None

# GOT-OCR2.0 imports
try:
    from ...utils.got_ocr import GOTOCRProcessor

    GOT_OCR_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    GOT_OCR_AVAILABLE = False
    GOTOCRProcessor = None

logger = logging.getLogger(__name__)


class OCRTool(BaseTool):
    """OCR tools for scanned document processing."""

    @mcp_tool(name="calibre_ocr", description="Process scanned documents with OCR using FineReader or GOT-OCR2.0")
    async def process_ocr(
        self,
        source: str,
        provider: str = "auto",
        language: Optional[str] = None,
        output_format: str = "pdf",
        ocr_mode: str = "ocr",
        region: Optional[List[int]] = None,
        render_html: bool = False
    ) -> Dict[str, Any]:
        """
        Process scanned documents with OCR using FineReader or GOT-OCR2.0.

        Converts scanned images or PDFs into searchable text documents by extracting
        text through Optical Character Recognition. Supports multiple OCR backends
        with different capabilities.

        Args:
            source: Full path to the source document file (images: PNG, JPEG, TIFF; PDFs supported)
            provider: OCR provider to use ("auto", "finereader", "got-ocr"). Default: "auto"
                     - "auto": Choose best available provider
                     - "finereader": Use ABBY FineReader CLI
                     - "got-ocr": Use GOT-OCR2.0 (supports formatted text, HTML rendering)
            language: OCR language code (default: "english"). Used by FineReader.
                Common options include: "english", "german", "french", "spanish", "italian"
            output_format: Output file format for FineReader (default: "pdf").
                Options: "pdf", "txt", etc. (GOT-OCR returns text/HTML)
            ocr_mode: OCR mode for GOT-OCR2.0 ("ocr", "format", "fine-grained"). Default: "ocr"
            region: Region coordinates [x1,y1,x2,y2] for fine-grained GOT-OCR. Default: None
            render_html: Render GOT-OCR formatted results as HTML. Default: False

        Returns:
            Dictionary containing processing results with provider-specific fields

        Examples:
            # Auto-select best OCR provider
            result = process_ocr(source="/path/to/scanned_book.pdf")

            # Use FineReader for traditional OCR
            result = process_ocr(
                source="/path/to/scanned_book.pdf",
                provider="finereader",
                language="english",
                output_format="pdf"
            )

            # Use GOT-OCR2.0 for formatted text preservation
            result = process_ocr(
                source="/path/to/book_page.png",
                provider="got-ocr",
                ocr_mode="format",
                render_html=True
            )

            # Fine-grained OCR on specific region
            result = process_ocr(
                source="/path/to/document.png",
                provider="got-ocr",
                ocr_mode="fine-grained",
                region=[100, 200, 400, 500]
            )

        Raises:
            FileNotFoundError: If source file doesn't exist or FineReader CLI not found
            Exception: For other OCR processing errors
        """
        # Determine which OCR provider to use
        if provider == "auto":
            # Auto-select: prefer GOT-OCR if available, fallback to FineReader
            if GOT_OCR_AVAILABLE and GOTOCRProcessor.is_available():
                provider = "got-ocr"
            elif FINEREADER_AVAILABLE and FineReaderCLI.is_available():
                provider = "finereader"
            else:
                return {
                    "success": False,
                    "error": "No OCR providers available",
                    "details": "Neither GOT-OCR2.0 nor FineReader CLI are available."
                }
        elif provider == "got-ocr":
            if not GOT_OCR_AVAILABLE or not GOTOCRProcessor.is_available():
                return {
                    "success": False,
                    "error": "GOT-OCR2.0 not available",
                    "details": "GOT-OCR2.0 dependencies or model not loaded."
                }
        elif provider == "finereader":
            if not FINEREADER_AVAILABLE or not FineReaderCLI.is_available():
                return {
                    "success": False,
                    "error": "FineReader CLI not found",
                    "details": (
                        "FineReader CLI executable not found. "
                        "Set FINEREADER_CLI_PATH environment variable, "
                        "add FineCmd.exe to PATH, or install FineReader 15+."
                    ),
                }
        else:
            return {
                "success": False,
                "error": f"Unknown OCR provider: {provider}",
                "details": "Supported providers: 'auto', 'finereader', 'got-ocr'"
            }

        source_path = Path(source)
        if not source_path.exists():
            return {"success": False, "error": f"Source file not found: {source}"}

        # Route to appropriate OCR backend
        if provider == "got-ocr":
            from ...utils.got_ocr import get_got_processor
            processor = get_got_processor()
            result = await processor.process_image(
                image_path=source_path,
                mode=ocr_mode,
                language=language,
                region=region,
                render_html=render_html
            )
            result["provider"] = "got-ocr"
            return result

        elif provider == "finereader":
            # Original FineReader logic
            output_path = source_path.parent / f"{source_path.stem}_ocr.{output_format}"
            language = language or "english"

            result = await safe_ocr_process(source_path, output_path, language=language)

            if result["success"]:
                final_result = {"success": True, "provider": "finereader", **result["result"]}
            else:
                final_result = {"provider": "finereader", **result}
            return final_result

        else:
            # This should never happen due to validation above
            return {
                "success": False,
                "error": f"Unsupported provider: {provider}"
            }
