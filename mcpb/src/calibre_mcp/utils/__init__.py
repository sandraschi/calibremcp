"""
Utilities package for CalibreMCP.

Contains OCR utilities (finereader) and library utilities.
File utilities are in the parent utils.py file.
"""

# Import from submodules
from .finereader import FineReaderCLI, safe_ocr_process

__all__ = [
    "FineReaderCLI",
    "safe_ocr_process",
]
