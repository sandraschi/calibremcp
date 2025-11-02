"""
Utilities package for CalibreMCP.

Contains OCR utilities (finereader) and library utilities.
File utilities are in the parent utils.py file.
"""

# Import from submodules
from .finereader import FineReaderCLI, safe_ocr_process

# Re-export functions from parent utils.py module (file utilities)
# This allows importing from calibre_mcp.utils package
import sys
from pathlib import Path

# Import from the parent utils.py file (not the package)
_parent_dir = Path(__file__).parent.parent
_utils_module_path = _parent_dir / "utils.py"

if _utils_module_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("calibre_mcp._utils_module", _utils_module_path)
    if spec and spec.loader:
        _utils_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_utils_module)
        
        # Re-export needed functions
        get_book_format_from_extension = _utils_module.get_book_format_from_extension
        extract_metadata = _utils_module.extract_metadata
        convert_book = _utils_module.convert_book
        generate_thumbnail = _utils_module.generate_thumbnail
        calculate_file_hash = _utils_module.calculate_file_hash
        FileTypeNotSupportedError = _utils_module.FileTypeNotSupportedError

__all__ = [
    "FineReaderCLI",
    "safe_ocr_process",
    # Re-exported from utils.py
    "get_book_format_from_extension",
    "extract_metadata",
    "convert_book",
    "generate_thumbnail",
    "calculate_file_hash",
    "FileTypeNotSupportedError",
]
