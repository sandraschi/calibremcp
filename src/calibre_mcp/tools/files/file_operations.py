"""
File operations tools for CalibreMCP.

These tools handle book format conversion, downloading,
and bulk file operations for library management.
"""

from typing import Optional, List, Dict, Any
from pydantic import Field

# Import the MCP server instance
from ...server import mcp

# Import response models
from ...server import ConversionRequest, ConversionResponse


@mcp.tool()
async def convert_book_format(
    conversion_requests: List[ConversionRequest]
) -> List[ConversionResponse]:
    """
    Convert books between different formats (EPUB, PDF, MOBI, etc.).
    
    Handles format conversion requests for single or multiple books,
    supporting various input and output formats with quality options.
    
    Args:
        conversion_requests: List of conversion requests with source and target formats
        
    Returns:
        List[ConversionResponse]: Results of conversion operations
    """
    # Implementation will be moved from server.py
    pass


@mcp.tool()
async def download_book(
    book_id: int,
    format_preference: str = Field("EPUB", description="Preferred format (EPUB, PDF, MOBI)")
) -> Dict[str, Any]:
    """
    Download a book file in the specified format.
    
    Retrieves and downloads a book file from the Calibre library
    in the preferred format, handling format availability and conversion.
    
    Args:
        book_id: Unique identifier of the book to download
        format_preference: Preferred file format for download
        
    Returns:
        Dict[str, Any]: Download information including file path and metadata
    """
    # Implementation will be moved from server.py
    pass


@mcp.tool()
async def bulk_format_operations(
    operation_type: str = Field(description="Operation: convert, validate, or cleanup"),
    target_format: Optional[str] = None,
    book_ids: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Perform bulk operations on book formats across multiple books.
    
    Supports bulk conversion, format validation, and cleanup operations
    for efficient management of large book collections.
    
    Args:
        operation_type: Type of operation (convert, validate, cleanup)
        target_format: Target format for conversion operations
        book_ids: List of book IDs to process (processes all if None)
        
    Returns:
        Dict[str, Any]: Results of bulk operations with statistics
    """
    # Implementation will be moved from server.py
    pass
