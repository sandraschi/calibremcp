"""
Viewer API endpoints for CalibreMCP.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import os
from typing import Optional, Dict, Any

from ...viewers import get_viewer, ViewerType
from ...storage import get_storage_backend
from ...models.book import Book

router = APIRouter(tags=["viewer"])

# In-memory storage for active viewers (in a real app, use Redis or similar)
_active_viewers: Dict[str, Any] = {}

@router.get("/view/book/{book_id}", response_class=HTMLResponse)
async def view_book(
    book_id: str,
    page: int = 0,
    library_id: Optional[str] = None
):
    """
    View a book in the web reader.
    """
    try:
        # In a real implementation, get book info from database
        storage = get_storage_backend()
        book = storage.get_book(book_id)
        
        if not book or not book.file_path or not os.path.exists(book.file_path):
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Get or create viewer instance
        viewer_key = f"{book_id}:{library_id or 'default'}"
        if viewer_key not in _active_viewers:
            viewer = get_viewer(book.file_path)
            if not viewer:
                raise HTTPException(status_code=400, detail="Unsupported file format")
            viewer.load(book.file_path)
            _active_viewers[viewer_key] = viewer
        else:
            viewer = _active_viewers[viewer_key]
        
        # Render the viewer page with the book content
        return get_viewer_html(book, page, viewer)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/viewer/page")
async def get_page(
    book_id: str,
    page: int = Query(0, ge=0),
    library_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a specific page from a book.
    """
    try:
        viewer_key = f"{book_id}:{library_id or 'default'}"
        if viewer_key not in _active_viewers:
            raise HTTPException(status_code=404, detail="Viewer not found")
        
        viewer = _active_viewers[viewer_key]
        return viewer.render_page(page)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/viewer/settings")
async def update_viewer_settings(
    book_id: str,
    settings: Dict[str, Any],
    library_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update viewer settings (for comics/manga).
    """
    try:
        viewer_key = f"{book_id}:{library_id or 'default'}"
        if viewer_key not in _active_viewers:
            raise HTTPException(status_code=404, detail="Viewer not found")
        
        viewer = _active_viewers[viewer_key]
        
        # Update settings if the viewer supports them
        if hasattr(viewer, 'set_setting'):
            for key, value in settings.items():
                viewer.set_setting(key, value)
        
        return {"status": "success", "settings": settings}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_viewer_html(book: Book, current_page: int, viewer: Any) -> str:
    """Generate HTML for the book viewer."""
    # This would be a more sophisticated template in a real app
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{book.title} - CalibreMCP Viewer</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ 
                margin: 0; 
                padding: 0; 
                overflow: hidden;
                font-family: Arial, sans-serif;
            }}
            #viewer-container {{
                display: flex;
                flex-direction: column;
                height: 100vh;
            }}
            #toolbar {{
                padding: 10px;
                background: #f0f0f0;
                border-bottom: 1px solid #ccc;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            #content {{
                flex: 1;
                overflow: auto;
                display: flex;
                justify-content: center;
                align-items: center;
                background: #333;
            }}
            #page-content {{
                max-width: 100%;
                max-height: 100%;
                text-align: center;
            }}
            #page-content img {{
                max-width: 100%;
                max-height: 90vh;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
            }}
            .nav-button {{
                padding: 8px 16px;
                margin: 0 5px;
                cursor: pointer;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }}
            .nav-button:disabled {{
                background: #cccccc;
                cursor: not-allowed;
            }}
            #page-info {{
                margin: 0 15px;
            }}
        </style>
    </head>
    <body>
        <div id="viewer-container">
            <div id="toolbar">
                <div>
                    <button id="prev-page" class="nav-button">Previous</button>
                    <span id="page-info">Page <span id="current-page">{current_page + 1}</span> of <span id="total-pages">?</span></span>
                    <button id="next-page" class="nav-button">Next</button>
                </div>
                <div>
                    <span id="book-title">{book.title}</span>
                </div>
                <div>
                    <button id="settings-btn" class="nav-button">Settings</button>
                </div>
            </div>
            <div id="content">
                <div id="page-content">
                    Loading...
                </div>
            </div>
        </div>

        <script>
            let currentPage = {current_page};
            let totalPages = 0;
            const bookId = "{book.id}";
            
            // Load the first page
            loadPage(currentPage);
            
            // Navigation buttons
            document.getElementById('prev-page').addEventListener('click', () => {{
                if (currentPage > 0) {{
                    loadPage(currentPage - 1);
                }}
            }});
            
            document.getElementById('next-page').addEventListener('click', () => {{
                if (currentPage < totalPages - 1) {{
                    loadPage(currentPage + 1);
                }}
            }});
            
            // Keyboard navigation
            document.addEventListener('keydown', (e) => {{
                if (e.key === 'ArrowLeft') {{
                    if (currentPage > 0) loadPage(currentPage - 1);
                }} else if (e.key === 'ArrowRight') {{
                    if (currentPage < totalPages - 1) loadPage(currentPage + 1);
                }}
            }});
            
            async function loadPage(page) {{
                try {{
                    const response = await fetch(`/api/viewer/page?book_id=${{bookId}}&page=${{page}}`);
                    if (!response.ok) throw new Error('Failed to load page');
                    
                    const data = await response.json();
                    
                    // Update page content
                    document.getElementById('page-content').innerHTML = data.content;
                    
                    // Update page info
                    currentPage = page;
                    totalPages = data.total_pages;
                    document.getElementById('current-page').textContent = currentPage + 1;
                    document.getElementById('total-pages').textContent = totalPages;
                    
                    // Update navigation buttons
                    document.getElementById('prev-page').disabled = currentPage <= 0;
                    document.getElementById('next-page').disabled = currentPage >= totalPages - 1;
                    
                }} catch (error) {{
                    console.error('Error loading page:', error);
                    document.getElementById('page-content').innerHTML = 
                        `<p style="color: red;">Error loading page: ${{error.message}}</p>`;
                }}
            }}
            
            // Settings button
            document.getElementById('settings-btn').addEventListener('click', () => {{
                alert('Settings dialog would appear here');
                // In a real implementation, show a modal with viewer settings
            }});
        </script>
    </body>
    </html>
    """
