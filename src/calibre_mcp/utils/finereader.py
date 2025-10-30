"""
FineReader CLI integration for CalibreMCP.

This module provides OCR capabilities through ABBYY FineReader command-line interface.
"""
import os
import re
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class OCRProcessingError(Exception):
    """Raised when OCR processing fails."""
    pass


class OCRLanguage(str, Enum):
    """Supported OCR languages."""
    ENGLISH = "english"
    GERMAN = "german"
    FRENCH = "french"
    SPANISH = "spanish"
    ITALIAN = "italian"
    PORTUGUESE = "portuguese"
    DUTCH = "dutch"
    RUSSIAN = "russian"
    POLISH = "polish"
    CZECH = "czech"
    HUNGARIAN = "hungarian"
    CHINESE = "chinese"
    JAPANESE = "japanese"
    KOREAN = "korean"
    THAI = "thai"
    VIETNAMESE = "vietnamese"
    ARABIC = "arabic"
    HEBREW = "hebrew"
    TURKISH = "turkish"
    MULTILINGUAL = "multilingual"
    AUTO_DETECT = "AutoDetect"


class OCRFormat(str, Enum):
    """Supported OCR output formats."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    TXT = "txt"


class FineReaderCLI:
    """Wrapper for ABBYY FineCMD.exe CLI."""
    
    def __init__(self, cli_path: str = None):
        """Initialize FineReader CLI wrapper.
        
        Args:
            cli_path: Path to FineCMD.exe (auto-detected if None)
        """
        self.cli_path = Path(cli_path) if cli_path else self._find_cli_path()
        self.version = "15"  # Confirmed version
        logger.info(f"Initialized FineReader CLI wrapper with path: {self.cli_path}")
        
    def _find_cli_path(self) -> Path:
        """Auto-detect FineCMD.exe installation.
        
        Common locations:
        - C:\Program Files (x86)\ABBYY FineReader 15\FineCmd.exe
        - C:\Program Files\ABBYY FineReader 15\FineCmd.exe
        
        Returns:
            Path to FineCMD.exe
            
        Raises:
            FileNotFoundError: If FineReader CLI not found
        """
        possible_paths = [
            Path("C:/Program Files (x86)/ABBYY FineReader 15/FineCmd.exe"),
            Path("C:/Program Files/ABBYY FineReader 15/FineCmd.exe"),
        ]
        
        # Add dynamic paths based on environment variables
        programfiles_x86 = os.getenv("PROGRAMFILES(X86)", "")
        programfiles = os.getenv("PROGRAMFILES", "")
        
        if programfiles_x86:
            possible_paths.append(
                Path(programfiles_x86) / "ABBYY FineReader 15/FineCmd.exe"
            )
        if programfiles:
            possible_paths.append(
                Path(programfiles) / "ABBYY FineReader 15/FineCmd.exe"
            )
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found FineReader CLI at {path}")
                return path
                
        raise FileNotFoundError(
            "FineReader CLI not found. Please install FineReader 15+ or specify path."
        )
    
    def _validate_input_file(self, input_path: Path) -> None:
        """Validate input file before OCR processing.
        
        Args:
            input_path: Path to input file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is too large or unsupported format
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Check file size (100 MB limit)
        file_size = input_path.stat().st_size
        max_size = 100_000_000  # 100 MB
        if file_size > max_size:
            raise ValueError(
                f"File too large: {file_size / 1_000_000:.1f} MB "
                f"(max: {max_size / 1_000_000} MB)"
            )
        
        # Check if file is readable
        if not os.access(input_path, os.R_OK):
            raise PermissionError(f"Cannot read file: {input_path}")
    
    async def process_document(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        language: str = "english",
        output_format: str = "pdf",
        preserve_layout: bool = True
    ) -> Dict[str, Any]:
        """
        Process single document with OCR.
        
        Args:
            input_path: Input file (PDF, image, etc.)
            output_path: Output file path
            language: OCR language (e.g., "english", "german", "multilingual")
            output_format: Output format (pdf, docx, xlsx, txt)
            preserve_layout: Maintain original layout
            
        Returns:
            Processing results with confidence scores
            
        Raises:
            OCRProcessingError: If OCR processing fails
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        # Validate input file
        self._validate_input_file(input_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build command
        cmd = [
            str(self.cli_path),
            str(input_path),
            '/lang', language,
            '/out', str(output_path),
            '/quit'  # Close FineReader after processing
        ]
        
        if output_format.lower() not in ["pdf"]:
            cmd.extend(['/outputFormat', output_format.upper()])
            
        if preserve_layout:
            cmd.append('/preserveLayout')
        
        logger.info(f"Running OCR: {input_path.name} -> {output_path.name}")
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                raise OCRProcessingError(
                    f"FineReader failed with return code {process.returncode}: {error_msg}"
                )
            
            # Verify output file was created
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise OCRProcessingError("OCR output file not created or empty")
            
            # Parse confidence scores from stdout
            confidence = self._parse_confidence(stdout.decode('utf-8', errors='ignore'))
            
            logger.info(f"OCR completed successfully: {output_path.name}")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "confidence": confidence,
                "language": language,
                "format": output_format,
                "file_size": output_path.stat().st_size
            }
            
        except OCRProcessingError:
            raise
        except Exception as e:
            raise OCRProcessingError(f"Unexpected error during OCR: {str(e)}")
    
    def _parse_confidence(self, output: str) -> float:
        """Extract confidence score from FineReader output.
        
        Args:
            output: Stdout from FineReader
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # FineReader v15 outputs confidence as percentage
        # Look for patterns like "confidence: 85%" or "Confidence: 92.5%"
        patterns = [
            r'confidence[:\s]+(\d+\.?\d*)%',
            r'Confidence[:\s]+(\d+\.?\d*)%',
            r'confidence level[:\s]+(\d+\.?\d*)%',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output.lower())
            if match:
                return float(match.group(1)) / 100.0
        
        # Default confidence if not found in output
        logger.warning("Could not parse confidence score from FineReader output")
        return 0.85
    
    async def batch_process(
        self,
        input_files: List[Union[str, Path]],
        output_dir: Union[str, Path],
        language: str = "english",
        output_format: str = "pdf"
    ) -> Dict[str, Any]:
        """Process multiple files in batch.
        
        Args:
            input_files: List of input file paths
            output_dir: Directory for output files
            language: OCR language
            output_format: Output format
            
        Returns:
            Batch processing results with success/failure counts
        """
        input_files = [Path(f) for f in input_files]
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        logger.info(f"Starting batch OCR: {len(input_files)} files")
        
        for i, input_file in enumerate(input_files, 1):
            logger.info(f"Processing file {i}/{len(input_files)}: {input_file.name}")
            
            output_file = output_dir / f"{input_file.stem}_ocr.{output_format}"
            
            try:
                result = await self.process_document(
                    input_file,
                    output_file,
                    language=language,
                    output_format=output_format
                )
                results.append({
                    "file": str(input_file),
                    "success": True,
                    "output": result,
                    "error": None
                })
            except Exception as e:
                logger.error(f"Failed to process {input_file.name}: {e}")
                results.append({
                    "file": str(input_file),
                    "success": False,
                    "output": None,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        logger.info(f"Batch OCR complete: {successful} successful, {failed} failed")
        
        return {
            "total": len(input_files),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    async def detect_language(self, input_path: Union[str, Path]) -> str:
        """Auto-detect document language.
        
        Args:
            input_path: Path to document
            
        Returns:
            Detected language code
        """
        input_path = Path(input_path)
        self._validate_input_file(input_path)
        
        # FineReader v15 has auto-detect capabilities
        cmd = [
            str(self.cli_path),
            str(input_path),
            '/lang', OCRLanguage.AUTO_DETECT.value,
            '/out', 'NUL',  # No output needed for detection
            '/quit'
        ]
        
        logger.info(f"Detecting language for: {input_path.name}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning("Language detection failed, defaulting to english")
                return "english"
            
            # Parse detected language from output
            detected = self._parse_detected_language(stdout.decode('utf-8', errors='ignore'))
            return detected or "english"
            
        except Exception as e:
            logger.error(f"Error during language detection: {e}")
            return "english"
    
    def _parse_detected_language(self, output: str) -> Optional[str]:
        """Extract detected language from FineReader output.
        
        Args:
            output: Stdout from FineReader
            
        Returns:
            Detected language code or None
        """
        patterns = [
            r'detected language:\s*(\w+)',
            r'language detected:\s*(\w+)',
            r'language:\s*(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output.lower())
            if match:
                detected = match.group(1)
                logger.info(f"Detected language: {detected}")
                return detected
        
        logger.warning("Could not parse detected language from output")
        return None
    
    def is_ocr_supported(self, file_path: Union[str, Path]) -> bool:
        """Check if file format is supported for OCR.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if format is supported for OCR
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        supported_formats = [
            '.pdf', '.tif', '.tiff', '.jpg', '.jpeg', '.png', '.bmp',
            '.gif', '.djvu', '.doc', '.docx'
        ]
        
        return suffix in supported_formats


async def safe_ocr_process(
    file_path: Union[str, Path],
    output_path: Union[str, Path],
    language: str = "english",
    max_retries: int = 3
) -> Dict[str, Any]:
    """Wrap OCR processing with comprehensive error handling and retry logic.
    
    Args:
        file_path: Input file path
        output_path: Output file path
        language: OCR language
        max_retries: Maximum number of retry attempts
        
    Returns:
        OCR processing results with success status
    """
    finereader = FineReaderCLI()
    
    for attempt in range(max_retries):
        try:
            result = await finereader.process_document(
                file_path,
                output_path,
                language=language
            )
            return {
                "success": True,
                "result": result,
                "attempt": attempt + 1
            }
            
        except OCRProcessingError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(
                    f"OCR failed (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"OCR failed after {max_retries} attempts: {e}")
                return {
                    "success": False,
                    "error": "OCR processing failed after retries",
                    "details": str(e),
                    "attempt": max_retries
                }
        
        except Exception as e:
            logger.exception(f"Unexpected error during OCR: {e}")
            return {
                "success": False,
                "error": "Unexpected error",
                "details": str(e),
                "attempt": attempt + 1
            }
    
    return {
        "success": False,
        "error": "Unknown error",
        "attempt": max_retries
    }


# Import Union for type hints
from typing import Union

