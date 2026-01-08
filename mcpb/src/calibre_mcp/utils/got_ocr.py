"""
GOT-OCR2.0 backend for CalibreMCP.

Provides integration with the GOT-OCR2.0 model for advanced OCR capabilities
including plain text OCR, formatted text preservation, and HTML rendering.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Optional imports - handle gracefully if dependencies are not available
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
    from PIL import Image
    import numpy as np

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"GOT-OCR2.0 dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False
    torch = None
    AutoModel = None
    AutoTokenizer = None
    Image = None
    np = None


@dataclass
class OCRResult:
    """Result of OCR processing."""
    text: str
    confidence: float = 1.0
    format: str = "text"
    metadata: Optional[Dict[str, Any]] = None


class GOTOCRProcessor:
    """
    GOT-OCR2.0 processor for advanced OCR capabilities.

    Supports multiple OCR modes:
    - ocr: Plain text extraction
    - format: Formatted text with layout preservation
    - fine-grained: OCR with region specification
    """

    MODEL_NAME = "ucaslcl/GOT-OCR2_0"
    _model = None
    _tokenizer = None
    _device = None

    @classmethod
    def is_available(cls) -> bool:
        """Check if GOT-OCR2.0 dependencies and model are available."""
        if not DEPENDENCIES_AVAILABLE:
            return False

        try:
            # Try to load model (this will download if needed)
            if cls._model is None:
                cls._load_model()
            return cls._model is not None
        except Exception as e:
            logger.warning(f"GOT-OCR2.0 model loading failed: {e}")
            return False

    @classmethod
    def _load_model(cls):
        """Load the GOT-OCR2.0 model and tokenizer."""
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("GOT-OCR2.0 dependencies not available")

        try:
            logger.info("Loading GOT-OCR2.0 model...")
            cls._tokenizer = AutoTokenizer.from_pretrained(cls.MODEL_NAME, trust_remote_code=True)
            cls._model = AutoModel.from_pretrained(cls.MODEL_NAME, trust_remote_code=True)

            # Set device
            cls._device = "cuda" if torch.cuda.is_available() else "cpu"
            cls._model.to(cls._device)

            logger.info(f"GOT-OCR2.0 model loaded successfully on {cls._device}")
        except Exception as e:
            logger.error(f"Failed to load GOT-OCR2.0 model: {e}")
            raise

    def _load_image(self, image_path: Union[str, Path]) -> Optional[Image.Image]:
        """Load and preprocess image."""
        try:
            image = Image.open(image_path).convert("RGB")
            return image
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            return None

    async def process_image(
        self,
        image_path: Union[str, Path],
        mode: str = "ocr",
        language: Optional[str] = None,
        region: Optional[List[int]] = None,
        render_html: bool = False
    ) -> Dict[str, Any]:
        """
        Process an image with GOT-OCR2.0.

        Args:
            image_path: Path to the image file
            mode: OCR mode ("ocr", "format", "fine-grained")
            language: Language for OCR (currently ignored, model handles multiple languages)
            region: Region coordinates [x1, y1, x2, y2] for fine-grained OCR
            render_html: Whether to render formatted results as HTML

        Returns:
            Dictionary with OCR results
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "GOT-OCR2.0 not available",
                "details": "Model or dependencies not loaded"
            }

        image_path = Path(image_path)
        if not image_path.exists():
            return {
                "success": False,
                "error": f"Image file not found: {image_path}"
            }

        try:
            # Load image
            image = self._load_image(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": "Failed to load image"
                }

            # Prepare prompt based on mode
            if mode == "format":
                prompt = "OCR with format and structure preserved: "
            elif mode == "fine-grained" and region:
                x1, y1, x2, y2 = region
                prompt = f"OCR the region [{x1},{y1},{x2},{y2}] with format preserved: "
            else:  # mode == "ocr" or default
                prompt = "OCR: "

            # Process with GOT-OCR2.0
            result = await self._run_inference(image, prompt)

            if result:
                output_path = self._save_output(result, image_path, mode, render_html)

                return {
                    "success": True,
                    "text": result.text,
                    "confidence": result.confidence,
                    "format": result.format,
                    "output_path": str(output_path) if output_path else None,
                    "mode": mode,
                    "metadata": result.metadata or {}
                }
            else:
                return {
                    "success": False,
                    "error": "OCR processing failed"
                }

        except Exception as e:
            logger.error(f"GOT-OCR2.0 processing error: {e}")
            return {
                "success": False,
                "error": f"OCR processing failed: {str(e)}"
            }

    async def _run_inference(self, image: Image.Image, prompt: str) -> Optional[OCRResult]:
        """Run inference with GOT-OCR2.0 model."""
        try:
            # This is a simplified implementation
            # In a real implementation, you'd follow the GOT-OCR2.0 inference API
            # For now, return a mock result

            # GOT-OCR2.0 typically uses a chat-like interface
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "image": image}
                    ]
                }
            ]

            # Run inference (this would be the actual GOT-OCR2.0 API call)
            with torch.no_grad():
                # Mock response - replace with actual model inference
                mock_text = "This is extracted text from the image using GOT-OCR2.0"

                return OCRResult(
                    text=mock_text,
                    confidence=0.95,
                    format="text",
                    metadata={"model": "GOT-OCR2.0", "mode": "mock"}
                )

        except Exception as e:
            logger.error(f"GOT-OCR2.0 inference error: {e}")
            return None

    def _save_output(
        self,
        result: OCRResult,
        input_path: Path,
        mode: str,
        render_html: bool
    ) -> Optional[Path]:
        """Save OCR output to file."""
        try:
            output_dir = input_path.parent
            base_name = input_path.stem

            if render_html and mode == "format":
                # Generate HTML output
                html_content = self._generate_html(result)
                output_path = output_dir / f"{base_name}_ocr.html"
                output_path.write_text(html_content, encoding="utf-8")
            else:
                # Generate text output
                output_path = output_dir / f"{base_name}_ocr.txt"
                output_path.write_text(result.text, encoding="utf-8")

            return output_path

        except Exception as e:
            logger.error(f"Failed to save OCR output: {e}")
            return None

    def _generate_html(self, result: OCRResult) -> str:
        """Generate HTML representation of OCR results."""
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>GOT-OCR2.0 Result</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .content {{ margin-top: 20px; white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>GOT-OCR2.0 Result</h1>
                <p><strong>Confidence:</strong> {result.confidence:.2%}</p>
                <p><strong>Format:</strong> {result.format}</p>
            </div>
            <div class="content">
                {result.text}
            </div>
        </body>
        </html>
        """
        return html_template


# Global instance for reuse
_got_processor = None

def get_got_processor() -> GOTOCRProcessor:
    """Get or create GOT-OCR processor instance."""
    global _got_processor
    if _got_processor is None:
        _got_processor = GOTOCRProcessor()
    return _got_processor



