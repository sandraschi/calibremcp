"""OCR tool for CalibreMCP using FineReader CLI and GOT-OCR2.0."""

import logging
from pathlib import Path
from typing import Any, Literal

from ..base_tool import BaseTool, mcp_tool
from ..ocr_output_schema import CALIBRE_OCR_OUTPUT_SCHEMA

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

    @staticmethod
    def _error(
        error: str,
        details: str | None = None,
        provider: str | None = None,
        recovery_options: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build a consistent OCR error response."""
        payload: dict[str, Any] = {"success": False, "error": error}
        if details:
            payload["details"] = details
        if provider:
            payload["provider"] = provider
        payload["recovery_options"] = recovery_options or []
        return payload

    @mcp_tool(
        name="calibre_ocr",
        description=(
            "Process scanned documents with OCR using FineReader or GOT-OCR2.0. "
            "Returns structured dicts with a success flag; see outputSchema for core fields. "
            "On failure, read error and details for recovery steps."
        ),
        output_schema=CALIBRE_OCR_OUTPUT_SCHEMA,
    )
    async def process_ocr(
        self,
        source: str,
        provider: Literal["auto", "finereader", "got-ocr"] = "auto",
        language: str | None = None,
        output_format: str = "pdf",
        ocr_mode: Literal["ocr", "format", "fine-grained"] = "ocr",
        region: tuple[int, int, int, int] | None = None,
        render_html: bool = False,
    ) -> dict[str, Any]:
        """
        Process scanned documents with OCR using FineReader or GOT-OCR2.0.

        Converts scanned images or PDFs into searchable text documents by extracting
        text through Optical Character Recognition. Supports multiple OCR backends
        with different capabilities.

        Args:
            source: Absolute path to the source file. Supported: common raster images
                (PNG, JPEG, TIFF, BMP, WebP) and PDF. Returns ``success: false`` if the
                path does not exist or is not readable.
            provider: OCR provider: ``auto`` | ``finereader`` | ``got-ocr``.
                ``auto`` prefers GOT-OCR when the model is loaded, else FineReader CLI.
            language: FineReader language preset name (e.g. ``english``, ``german``).
                For GOT-OCR, passed through when the backend supports it; not ISO-639
                codes. Default ``english`` for FineReader when omitted.
            output_format: FineReader export format (e.g. ``pdf``, ``txt``). Ignored for
                GOT-OCR text/HTML flows.
            ocr_mode: GOT-OCR mode: ``ocr`` | ``format`` | ``fine-grained``.
            region: Pixel bounding box ``[x1, y1, x2, y2]`` in **image coordinates**
                (origin top-left). Used when ``ocr_mode='fine-grained'`` with GOT-OCR;
                defines the crop prompt for the model.
            render_html: When using GOT-OCR ``format`` mode, embed formatted output as HTML.

        Returns:
            Dict with ``success`` and ``provider``; failures set ``error`` and ``details``.
            Additional keys (text, output paths, etc.) depend on the backend — see MCP
            ``outputSchema`` (additionalProperties allowed).

        Errors and recovery:
            - **Source file not found**: Verify path; use an absolute path on Windows.
            - **No OCR providers available**: Install/configure FineReader CLI
              (``FINEREADER_CLI_PATH``) or GOT-OCR dependencies/model.
            - **Provider unavailable**: Switch ``provider`` or install the missing engine.
            - **Unknown provider**: Use only ``auto``, ``finereader``, or ``got-ocr``.

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
                return self._error(
                    error="No OCR providers available",
                    details="Neither GOT-OCR2.0 nor FineReader CLI are available.",
                    provider="auto",
                    recovery_options=[
                        "Install GOT-OCR dependencies/model and verify load",
                        "Install FineReader CLI and set FINEREADER_CLI_PATH",
                        "Retry with provider='finereader' or provider='got-ocr' after setup",
                    ],
                )
        elif provider == "got-ocr":
            if not GOT_OCR_AVAILABLE or not GOTOCRProcessor.is_available():
                return self._error(
                    error="GOT-OCR2.0 not available",
                    details="GOT-OCR2.0 dependencies or model not loaded.",
                    provider="got-ocr",
                    recovery_options=[
                        "Install torch/transformers and GOT-OCR requirements",
                        "Download/load the GOT-OCR model",
                        "Fallback to provider='finereader'",
                    ],
                )
        elif provider == "finereader":
            if not FINEREADER_AVAILABLE or not FineReaderCLI.is_available():
                return self._error(
                    error="FineReader CLI not found",
                    details=(
                        "FineReader CLI executable not found. "
                        "Set FINEREADER_CLI_PATH environment variable, "
                        "add FineCmd.exe to PATH, or install FineReader 15+."
                    ),
                    provider="finereader",
                    recovery_options=[
                        "Set FINEREADER_CLI_PATH to FineCmd.exe",
                        "Add FineCmd.exe directory to PATH",
                        "Install FineReader 15+ or fallback to provider='got-ocr'",
                    ],
                )
        else:
            return self._error(
                error=f"Unknown OCR provider: {provider}",
                details="Supported providers: 'auto', 'finereader', 'got-ocr'",
                recovery_options=[
                    "Use provider='auto' for automatic selection",
                    "Use provider='finereader' for ABBYY OCR",
                    "Use provider='got-ocr' for layout-aware OCR",
                ],
            )

        source_path = Path(source)
        if not source_path.exists():
            return self._error(
                error=f"Source file not found: {source}",
                provider=provider,
                recovery_options=[
                    "Use an absolute Windows path (e.g. D:\\docs\\scan.pdf)",
                    "Verify file exists and process has read permission",
                    "Check escaping of backslashes in JSON/MCP arguments",
                ],
            )

        # Route to appropriate OCR backend
        if provider == "got-ocr":
            from ...utils.got_ocr import get_got_processor

            processor = get_got_processor()
            result = await processor.process_image(
                image_path=source_path,
                mode=ocr_mode,
                language=language,
                region=region,
                render_html=render_html,
            )
            result["provider"] = "got-ocr"
            return result

        if provider == "finereader":
            # Original FineReader logic
            output_path = source_path.parent / f"{source_path.stem}_ocr.{output_format}"
            language = language or "english"

            result = await safe_ocr_process(source_path, output_path, language=language)

            if result["success"]:
                final_result = {"success": True, "provider": "finereader", **result["result"]}
            else:
                final_result = {"provider": "finereader", **result}
            return final_result

        # Defensive fallback (should be unreachable due to Literal validation above)
        return self._error(error=f"Unsupported provider: {provider}")
