"""
Remote storage backend for Calibre MCP.

Provides access to Calibre content server via HTTP API.
"""
import aiohttp
import logging
from typing import List, Optional, Dict, Any, Union

from ..models.book import Book
from ..models.library import LibraryInfo
from ..auth import AuthManager
from . import StorageBackend

logger = logging.getLogger(__name__)

class RemoteStorage(StorageBackend):
    """Remote storage backend using Calibre Content Server API"""
    
    def __init__(self, server_name: str, base_url: str, auth: Optional[AuthManager] = None):
        """
        Initialize remote storage backend.
        
        Args:
            server_name: Unique name of the remote server
            base_url: Base URL of the Calibre content server
            auth: Optional AuthManager instance
        """
        self.server_name = server_name
        self.base_url = base_url.rstrip('/')
        self.auth = auth or AuthManager()
        self.session = None
    
    async def _ensure_session(self):
        """Ensure we have an active aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        creds = self.auth.get_credentials(self.server_name)
        if not creds:
            raise ValueError(f"No credentials found for server: {self.server_name}")
        return {
            "X-Username": creds[0],
            "X-Password": creds[1]
        }
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make an authenticated request to the Calibre server"""
        await self._ensure_session()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Add auth headers if not already provided
        if 'headers' not in kwargs:
            kwargs['headers'] = await self._get_auth_headers()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                if response.content_type == 'application/json':
                    return await response.json()
                return await response.text()
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise
    
    async def list_books(self, **filters) -> List[Book]:
        """List books with optional filtering"""
        params = {}
        
        # Map filters to API parameters
        if 'author' in filters:
            params['author'] = filters['author']
        if 'title' in filters:
            params['query'] = f'title:"{filters["title"]}"'
        if 'limit' in filters:
            params['num'] = filters['limit']
        
        try:
            data = await self._make_request('GET', '/ajax/books', params=params)
            return [
                Book(
                    id=book['id'],
                    title=book['title'],
                    authors=book['authors'],
                    timestamp=book['timestamp'],
                    pubdate=book['pubdate'],
                    series_index=book.get('series_index', 0),
                    path=book.get('path', ''),
                    has_cover=book.get('has_cover', False),
                    last_modified=book.get('last_modified', ''),
                    uuid=book.get('uuid', '')
                )
                for book in data
            ]
        except Exception as e:
            logger.error(f"Failed to list books: {e}")
            raise
    
    async def get_book(self, book_id: Union[int, str]) -> Optional[Book]:
        """Get a book by ID"""
        try:
            data = await self._make_request('GET', f'/ajax/book/{book_id}')
            if not data:
                return None
                
            return Book(
                id=data['id'],
                title=data['title'],
                authors=data.get('authors', []),
                timestamp=data.get('timestamp', ''),
                pubdate=data.get('pubdate', ''),
                series_index=data.get('series_index', 0),
                path=data.get('path', ''),
                has_cover=data.get('has_cover', False),
                last_modified=data.get('last_modified', ''),
                uuid=data.get('uuid', '')
            )
        except Exception as e:
            logger.error(f"Failed to get book {book_id}: {e}")
            raise
    
    async def get_library_info(self) -> LibraryInfo:
        """Get library metadata"""
        try:
            # Get library name from server info
            server_info = await self._make_request('GET', '/ajax/site')
            
            # Get book count
            books = await self._make_request('GET', '/ajax/books', params={'num': 1})
            
            return LibraryInfo(
                name=server_info.get('library_name', 'Remote Library'),
                path=self.base_url,
                book_count=len(books) if books else 0,
                total_size=0,  # Not available via standard API
                is_local=False
            )
        except Exception as e:
            logger.error(f"Failed to get library info: {e}")
            raise
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Ensure session is closed on garbage collection"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            import asyncio
            if asyncio.iscoroutinefunction(self.session.close):
                asyncio.create_task(self.session.close())
            else:
                asyncio.get_event_loop().run_until_complete(self.session.close())
