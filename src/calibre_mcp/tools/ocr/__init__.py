"""
OCR tools for Calibre MCP server.

This package contains tools for optical character recognition and document processing.
"""
from typing import List

from .calibre_ocr_tool import OCRTool

# List of all available tools
__all__ = [
    'OCRTool',
]

# Tools list for automatic registration
tools = [
    OCRTool
]

