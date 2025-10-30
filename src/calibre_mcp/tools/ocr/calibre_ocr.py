"""
CalibreMCP OCR tool using FineReader CLI.

Provides comprehensive OCR operations for scanned documents with multi-language support.
"""
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base_tool import BaseTool, mcp_tool

from ...utils.finereader import (
    FineReaderCLI,
    OCRProcessingError,
    OCRLanguage,
    OCRFormat,
    safe_ocr_process
)

logger = logging.getLogger(__name__)


class OCRTool(BaseTool):
    """OCR tools for scanned document processing."""
    
    @mcp_tool(
        name="calibre_ocr",
        description="Comprehensive OCR operations for scanned documents"
    )
    async def calibre_ocr(
        self,
        operation: str,
        source: str,
        language: Optional[str] = None,
        output_format: str = "pdf",
        preserve_layout: bool = True,
        book_id: Optional[int] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive OCR operations for scanned documents.
        
        This tool integrates ABBYY FineReader for optical character recognition,
        enabling searchable text extraction from scanned PDFs and images.
        
        Args:
            operation: Operation to perform. Options:
                - "process": Single file OCR with searchable PDF output
                - "batch_process": Process multiple files
                - "detect_language": Auto-detect document language
                - "get_status": Check OCR processing status
            source: Source file path or comma-separated list for batch processing
            language: OCR language (e.g., "english", "german", "multilingual")
                     Defaults to "english". Use "multilingual" for multi-language documents.
            output_format: Output format - "pdf", "docx", "xlsx", or "txt"
                          Defaults to "pdf".
            preserve_layout: Whether to preserve original document layout.
                            Defaults to True.
            book_id: Optional Calibre book ID to associate OCR results with
            output_path: Optional custom output path. Defaults to source_dir with _ocr suffix.
        
        Returns:
            Dictionary with operation results:
            - For "process": OCR results with confidence scores
            - For "batch_process": Batch processing summary with success/failure counts
            - For "detect_language": Detected language code
            - For "get_status": Processing status information
        
        Examples:
            >>> # Process single scanned PDF
            >>> result = await calibre_ocr(
            ...     operation="process",
            ...     source="scanned_book.pdf",
            ...     language="english"
            ... )
            
            >>> # Batch process multiple files
            >>> result = await calibre_ocr(
            ...     operation="batch_process",
            ...     source="file1.pdf,file2.pdf,file3.pdf",
            ...     language="multilingual",
            ...     output_format="pdf"
            ... )
            
            >>> # Auto-detect language
            >>> result = await calibre_ocr(
            ...     operation="detect_language",
            ...     source="unknown_document.pdf"
            ... )
        """
    
    try:
        finereader = FineReaderCLI()
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": "FineReader CLI not found",
            "details": str(e),
            "suggestion": "Please install ABBYY FineReader 15+ or verify installation"
        }
    
    # Default language if not specified
    language = language or "english"
    
    # Validate operation
    valid_operations = ["process", "batch_process", "detect_language", "get_status"]
    if operation not in valid_operations:
        return {
            "success": False,
            "error": f"Invalid operation: {operation}",
            "valid_operations": valid_operations
        }
    
    try:
        if operation == "process":
            return await _process_single_document(
                finereader, source, language, output_format,
                preserve_layout, output_path
            )
        
        elif operation == "batch_process":
            return await _process_batch(
                finereader, source, language, output_format
            )
        
        elif operation == "detect_language":
            return await _detect_language(finereader, source)
        
        elif operation == "get_status":
            return {
                "success": True,
                "status": "ready",
                "clipper": finereader.is_ocr_supported,
                "language": language,
                "format": output_format
            }
        
    except Exception as e:
        logger.exception(f"Error in calibre_ocr operation {operation}")
        return {
            "success": False,
            "error": str(e),
            "operation": operation
        }


async def _process_single_document(
    finereader: FineReaderCLI,
    source: str,
    language: str,
    output_format: str,
    preserve_layout: bool,
    output_path: Optional[str]
) -> Dict[str, Any]:
    """Process single document with OCR."""
    source_path = Path(source)
    
    if not source_path.exists():
        return {
            "success": False,
            "error": f"Source file not found: {source}"
        }
    
    # Determine output path
    if output_path is None:
        output_path = str(source_path.parent / f"{source_path.stem}_ocr.{output_format}")
    
    output_path_obj = Path(output_path)
    
    logger.info(f"Processing document: {source} -> {output_path}")
    
    # Use safe wrapper with retry logic
    result = await safe_ocr_process(
        source_path,
        output_path_obj,
        language=language
    )
    
    if result["success"]:
        return {
            "success": True,
            "operation": "process",
            "input_file": source,
            "output_file": output_path,
            **result["result"],
            "attempts": result["attempt"]
        }
    else:
        return {
            "success": False,
            "operation": "process",
            "error": result.get("error", "Unknown error"),
            "details": result.get("details", ""),
            "attempts": result.get("attempt", 0)
        }


async def _process_batch(
    finereader: FineReaderCLI,
    source: str,
    language: str,
    output_format: str
) -> Dict[str, Any]:
    """Process multiple files in batch."""
    # Parse comma-separated file list
    source_files = [Path(f.strip()) for f in source.split(',')]
    
    # Validate all files exist
    missing_files = [str(f) for f in source_files if not f.exists()]
    if missing_files:
        return {
            "success": False,
            "error": "One or more files not found",
            "missing_files": missing_files
        }
    
    # Create output directory
    output_dir = Path.cwd() / "ocr_output"
    output_dir.mkdir(exist_ok=True)
    
    logger.info(f"Batch processing {len(source_files)} files")
    
    # Process batch
    result = await finereader.batch_process(
        source_files,
        output_dir,
        language=language,
        output_format=output_format
    )
    
    return {
        "success": True,
        "operation": "batch_process",
        **result
    }


async def _detect_language(
    finereader: FineReaderCLI,
    source: str
) -> Dict[str, Any]:
    """Auto-detect document language."""
    source_path = Path(source)
    
    if not source_path.exists():
        return {
            "success": False,
            "error": f"Source file not found: {source}"
        }
    
    logger.info(f"Detecting language for: {source}")
    
    try:
        detected = await finereader.detect_language(source_path)
        
        return {
            "success": True,
            "operation": "detect_language",
            "detected_language": detected,
            "confidence": "high"  # FineReader doesn't provide confidence for detection
        }
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        return {
            "success": False,
            "error": "Language detection failed",
            "details": str(e)
        }


# Export for tool discovery
__all__ = ['calibre_ocr']

