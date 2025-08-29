"""
Comic viewer module for CalibreMCP - Handles CBZ and CBR formats.
"""
from typing import List, Dict, Any, Optional, Union, BinaryIO
from pathlib import Path
import zipfile
import rarfile
import io
import base64
from enum import Enum
import os

class ReadingDirection(str, Enum):
    """Reading direction for comics/manga."""
    LEFT_TO_RIGHT = "ltr"
    RIGHT_TO_LEFT = "rtl"

class PageLayout(str, Enum):
    """Page layout options."""
    SINGLE = "single"
    DOUBLE = "double"
    AUTO = "auto"

class ComicViewer:
    """Viewer for comic book formats (CBZ, CBR)."""
    
    SUPPORTED_FORMATS = ['cbz', 'cbr']
    
    def __init__(self):
        self._archive = None
        self._file_path = None
        self._file_list = []
        self._metadata = {}
        self._current_page = 0
        self._settings = {
            'reading_direction': ReadingDirection.LEFT_TO_RIGHT,
            'page_layout': PageLayout.SINGLE,
            'fit_to': 'width',  # 'width', 'height', 'both', 'original'
            'background_color': '#000000',
            'zoom_level': 1.0,
        }
    
    @classmethod
    def supports_format(cls, file_extension: str) -> bool:
        """Check if this viewer supports the given file format."""
        return file_extension.lower() in cls.SUPPORTED_FORMATS
    
    def load(self, file_path: str) -> None:
        """Load a comic book file (CBZ or CBR)."""
        self._file_path = Path(file_path)
        self._current_page = 0
        
        # Determine the archive type and open it
        ext = self._file_path.suffix.lower()[1:]
        
        try:
            if ext == 'cbz':
                self._archive = zipfile.ZipFile(file_path, 'r')
                self._file_list = [f for f in self._archive.namelist() 
                                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            elif ext == 'cbr':
                self._archive = rarfile.RarFile(file_path, 'r')
                self._file_list = [f for f in self._archive.namelist() 
                                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            
            # Sort files naturally (e.g., "page1.jpg", "page2.jpg")
            self._file_list.sort(key=lambda x: [int(t) if t.isdigit() else t.lower() 
                                             for t in re.split(r'(\d+)', x)])
            
            # Extract basic metadata
            self._metadata = {
                'title': self._file_path.stem,
                'page_count': len(self._file_list),
                'format': ext.upper(),
                'file_size': os.path.getsize(file_path)
            }
            
        except Exception as e:
            self.close()
            raise ValueError(f"Failed to load comic file: {str(e)}")
    
    def set_setting(self, key: str, value: Any) -> None:
        """Update a viewer setting."""
        if key in self._settings:
            if key == 'reading_direction':
                self._settings[key] = ReadingDirection(value)
            elif key == 'page_layout':
                self._settings[key] = PageLayout(value)
            else:
                self._settings[key] = value
    
    def render_page(self, page_number: int = 0) -> Dict[str, Any]:
        """Render a specific page of the comic."""
        if not self._archive or page_number < 0 or page_number >= len(self._file_list):
            return {
                'content': '<p>Page not found</p>',
                'total_pages': len(self._file_list) if self._archive else 0,
                'current_page': page_number,
                'metadata': self._metadata,
                'error': 'Page not found'
            }
        
        try:
            # Get the page file from the archive
            page_file = self._file_list[page_number]
            
            # Read the image data
            with self._archive.open(page_file) as f:
                img_data = f.read()
            
            # Convert to base64 for HTML display
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # Determine MIME type from file extension
            ext = os.path.splitext(page_file)[1].lower()
            mime_type = f'image/{ext[1:]}'  # Remove the dot
            if ext == '.jpg':
                mime_type = 'image/jpeg'
            
            # Apply viewer settings
            style = ""
            if self._settings['fit_to'] == 'width':
                style += "width: 100%; height: auto;"
            elif self._settings['fit_to'] == 'height':
                style += "width: auto; height: 100%;"
            elif self._settings['fit_to'] == 'both':
                style += "max-width: 100%; max-height: 100%;"
            
            # Apply zoom
            if self._settings['zoom_level'] != 1.0:
                style += f"transform: scale({self._settings['zoom_level']});"
            
            return {
                'content': f'<div style="background-color: {self._settings["background_color"]}; ' \
                         f'text-align: center; overflow: auto; height: 100%;">' \
                         f'<img src="data:{mime_type};base64,{img_base64}" ' \
                         f'style="{style}" /></div>',
                'total_pages': len(self._file_list),
                'current_page': page_number,
                'metadata': self._metadata,
                'settings': {k: str(v) for k, v in self._settings.items()},
                'navigation': {
                    'has_prev': page_number > 0,
                    'has_next': page_number < len(self._file_list) - 1,
                    'reading_direction': self._settings['reading_direction'].value,
                    'page_layout': self._settings['page_layout'].value
                }
            }
            
        except Exception as e:
            return {
                'content': f'<p>Error rendering page: {str(e)}</p>',
                'total_pages': len(self._file_list) if self._archive else 0,
                'current_page': page_number,
                'metadata': self._metadata,
                'error': str(e)
            }
    
    def next_page(self) -> Dict[str, Any]:
        """Go to the next page."""
        if self._current_page < len(self._file_list) - 1:
            self._current_page += 1
        return self.render_page(self._current_page)
    
    def previous_page(self) -> Dict[str, Any]:
        """Go to the previous page."""
        if self._current_page > 0:
            self._current_page -= 1
        return self.render_page(self._current_page)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the comic."""
        return self._metadata
    
    def close(self) -> None:
        """Clean up resources."""
        if self._archive:
            try:
                self._archive.close()
            except:
                pass
            self._archive = None
        self._file_list = []
        self._metadata = {}
        self._current_page = 0
        self._file_path = None
