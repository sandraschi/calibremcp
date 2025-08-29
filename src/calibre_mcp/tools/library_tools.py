"""
Library management tools for CalibreMCP.

Provides functionality to list, switch, and manage Calibre libraries.
"""
from typing import List, Dict, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table

from ..utils.library_utils import (
    discover_calibre_libraries,
    get_library_metadata,
    get_current_library
)
from ..models.library import LibraryInfo

console = Console()

class LibraryListResponse(BaseModel):
    """Response model for list_libraries tool"""
    libraries: List[LibraryInfo] = Field(..., description="List of available libraries")
    current_library: Optional[str] = Field(None, description="Currently active library name")

def list_libraries() -> LibraryListResponse:
    """
    List all available Calibre libraries with their details.
    
    Scans the configured base directory for Calibre libraries and returns
    information about each one, including the currently active library.
    
    Returns:
        LibraryListResponse with list of libraries and current selection
    """
    libraries = discover_calibre_libraries()
    current_lib = get_current_library()
    
    library_list = []
    for name, path in libraries.items():
        metadata = get_library_metadata(path)
        library_list.append(
            LibraryInfo(
                name=name,
                display_name=name.replace('_', ' ').title(),
                path=str(path),
                total_books=metadata.get('book_count', 0),
                size_mb=metadata.get('size_mb', 0),
                is_current=current_lib and str(path) == str(current_lib)
            )
        )
    
    # Sort by name
    library_list.sort(key=lambda x: x.name)
    
    return LibraryListResponse(
        libraries=library_list,
        current_library=current_lib.name if current_lib else None
    )

def switch_library(library_name: str) -> LibraryListResponse:
    """
    Switch to a different Calibre library.
    
    Changes the active library that will be used for subsequent operations.
    
    Args:
        library_name: Name of the library to switch to (must exist)
        
    Returns:
        Updated library list with new active library
        
    Raises:
        ValueError: If the specified library is not found
    """
    libraries = discover_calibre_libraries()
    
    if library_name not in libraries:
        available = ", ".join(f'"{name}"' for name in libraries.keys())
        raise ValueError(f"Library '{library_name}' not found. Available libraries: {available}")
    
    # Update configuration
    from ...config import update_config
    update_config({"local_library_path": str(libraries[library_name])})
    
    # Return updated library list
    return list_libraries()

def print_library_list(libraries: List[LibraryInfo], current_library: Optional[str] = None):
    """
    Print a formatted table of available libraries.
    
    Args:
        libraries: List of LibraryInfo objects
        current_library: Name of the currently active library
    """
    table = Table(title="Available Calibre Libraries")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Path", style="magenta")
    table.add_column("Books", justify="right")
    table.add_column("Size (MB)", justify="right")
    table.add_column("Status", style="green")
    
    for lib in libraries:
        table.add_row(
            lib.display_name,
            lib.path,
            str(lib.total_books),
            f"{lib.size_mb:,.1f}",
            "✓ Current" if lib.is_current else ""
        )
    
    console.print(table)
    
    if current_library:
        console.print(f"\nCurrent library: [bold green]{current_library}[/bold green]")
    else:
        console.print("\n[bold yellow]No active library selected.[/bold yellow]")

# Register tools for MCP
tools = [list_libraries, switch_library]
