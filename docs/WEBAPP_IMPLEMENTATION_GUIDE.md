# Calibre Webapp Implementation Guide

**Step-by-step guide for the Calibre webapp**

---

## Current Implementation (2025-01-30)

### Features

- **Retractable Sidebar** - Overview, Libraries, Books, Search, Authors, Series, Tags, Publishers, Import, Export, Chat, Logs, Settings, Help
- **Overview Dashboard** - Library stats, quick links
- **Authors / Series / Tags / Publishers** - List pages with search, drill to books
- **Book Modal** - Full metadata (rating, publisher, series, identifiers, comments), cover, Read button
- **Author Wikipedia Links** - Click author in book modal to open Wikipedia search
- **AI Chat** - Personality presets, Ollama/LM Studio/OpenAI; Settings for provider, model list
- **Logs** - Log file viewer (tail, filter, level, live tail with backoff); System status view
- **Import / Export** - Add books by path; export CSV/JSON with filters

### Tech Stack

- **Backend**: FastAPI, direct in-process MCP calls (no HTTP self-call)
- **Frontend**: Next.js 15 App Router, Tailwind CSS, server/client components
- **Proxies**: Next.js API routes proxy to backend (same-origin, CORS-free)

---

## Project Structure

```
calibre-mcp/webapp/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── cache.py
│   │   ├── api/
│   │   │   ├── books.py
│   │   │   ├── search.py
│   │   │   ├── library.py
│   │   │   ├── authors.py
│   │   │   ├── series.py
│   │   │   ├── tags.py
│   │   │   ├── export.py
│   │   │   ├── viewer.py
│   │   │   ├── llm.py         # Ollama/LM Studio/OpenAI
│   │   │   └── ...
│   │   └── mcp/
│   │       └── client.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx             # Overview
│   │   ├── books/, authors/, series/, tags/
│   │   ├── import/, export/, chat/, logs/, settings/, help/
│   │   ├── book/[id]/           # Book detail modal
│   │   └── api/                 # Next.js proxies
│   ├── components/
│   │   ├── layout/              # Sidebar, Topbar, AppLayout
│   │   ├── books/               # BookCard, BookGrid, BookModal
│   │   └── authors/             # AuthorLinks (Wikipedia)
│   └── lib/
│       ├── api.ts
│       └── proxy.ts
└── README.md
```

---

## 🔧 **Backend Implementation**

### **1. MCP Client Wrapper**

**`webapp/backend/app/mcp/client.py`:**

```python
"""MCP client wrapper for calling CalibreMCP tools."""

import asyncio
from typing import Any, Dict, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ..config import settings


class MCPClient:
    """Wrapper for MCP client to call CalibreMCP tools."""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self._lock = asyncio.Lock()
    
    async def connect(self):
        """Connect to CalibreMCP server."""
        if self.session is not None:
            return
        
        async with self._lock:
            if self.session is not None:
                return
            
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "calibre_mcp.server"],
                env=None
            )
            
            stdio_transport = await stdio_client(server_params)
            self.session = ClientSession(stdio_transport[0], stdio_transport[1])
            await self.session.initialize()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        if self.session is None:
            await self.connect()
        
        result = await self.session.call_tool(tool_name, arguments)
        return result.content[0].text if result.content else {}
    
    async def close(self):
        """Close MCP connection."""
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.session = None


# Global client instance
mcp_client = MCPClient()
```

### **2. FastAPI Application**

**`webapp/backend/app/main.py`:**

```python
"""FastAPI application for Calibre webapp."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import books, search, viewer, metadata, library
from .config import settings

app = FastAPI(
    title="Calibre Webapp API",
    description="HTTP API wrapper for CalibreMCP server",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(viewer.router, prefix="/api/viewer", tags=["viewer"])
app.include_router(metadata.router, prefix="/api/metadata", tags=["metadata"])
app.include_router(library.router, prefix="/api/libraries", tags=["libraries"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Calibre Webapp API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
```

### **3. Books API Endpoints**

**`webapp/backend/app/api/books.py`:**

```python
"""Book API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from ..mcp.client import mcp_client
from ..models.book import BookResponse, BookListResponse

router = APIRouter()


@router.get("/", response_model=BookListResponse)
async def list_books(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    author: Optional[str] = None,
    tag: Optional[str] = None,
):
    """List books with optional filters."""
    try:
        result = await mcp_client.call_tool(
            "query_books",
            {
                "operation": "search",
                "limit": limit,
                "offset": offset,
                "author": author,
                "tag": tag,
            }
        )
        return BookListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    """Get book details by ID."""
    try:
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "get",
                "book_id": str(book_id),
                "include_metadata": True,
                "include_formats": True,
            }
        )
        return BookResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
```

---

## 🎨 **Frontend Implementation**

### **1. API Client**

**`webapp/frontend/lib/api.ts`:**

```typescript
/** API client for Calibre webapp. */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:13000';

export interface Book {
  id: number;
  title: string;
  authors: string[];
  rating?: number;
  tags: string[];
  formats: string[];
  cover_url?: string;
}

export interface BookListResponse {
  items: Book[];
  total: number;
  page: number;
  per_page: number;
}

export async function getBooks(params?: {
  limit?: number;
  offset?: number;
  author?: string;
  tag?: string;
}): Promise<BookListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());
  if (params?.author) searchParams.set('author', params.author);
  if (params?.tag) searchParams.set('tag', params.tag);

  const response = await fetch(`${API_BASE_URL}/api/books?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch books');
  return response.json();
}

export async function getBook(id: number): Promise<Book> {
  const response = await fetch(`${API_BASE_URL}/api/books/${id}`);
  if (!response.ok) throw new Error('Failed to fetch book');
  return response.json();
}
```

### **2. Books Page (Server Component)**

**`webapp/frontend/app/books/page.tsx`:**

```typescript
/** Books browse page. */

import { getBooks } from '@/lib/api';
import { BookGrid } from '@/components/books/book-grid';
import { SearchBar } from '@/components/search/search-bar';

export default async function BooksPage({
  searchParams,
}: {
  searchParams: { author?: string; tag?: string; page?: string };
}) {
  const page = parseInt(searchParams.page || '1');
  const limit = 50;
  const offset = (page - 1) * limit;

  const data = await getBooks({
    limit,
    offset,
    author: searchParams.author,
    tag: searchParams.tag,
  });

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Browse Books</h1>
      <SearchBar />
      <BookGrid books={data.items} />
      {/* Pagination */}
    </div>
  );
}
```

### **3. Book Card Component**

**`webapp/frontend/components/books/book-card.tsx`:**

```typescript
/** Book card component. */

'use client';

import Image from 'next/image';
import Link from 'next/link';
import { Book } from '@/lib/api';

interface BookCardProps {
  book: Book;
}

export function BookCard({ book }: BookCardProps) {
  return (
    <Link href={`/books/${book.id}`}>
      <div className="border rounded-lg p-4 hover:shadow-lg transition-shadow">
        {book.cover_url && (
          <Image
            src={book.cover_url}
            alt={book.title}
            width={200}
            height={300}
            className="w-full h-auto mb-2"
          />
        )}
        <h3 className="font-semibold text-lg">{book.title}</h3>
        <p className="text-sm text-gray-600">{book.authors.join(', ')}</p>
        {book.rating && (
          <div className="flex items-center mt-2">
            {'⭐'.repeat(book.rating)}
          </div>
        )}
      </div>
    </Link>
  );
}
```

---

## 🚀 **Quick Start**

### **Backend Setup**

```bash
cd webapp/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install fastapi uvicorn httpx mcp
uvicorn app.main:app --reload --port 13000
```

### **Frontend Setup**

```bash
cd webapp/frontend
npm install
npm run dev
```

---

## 📝 **Next Steps**

1. **Implement MCP client wrapper** (handle stdio communication)
2. **Create FastAPI endpoints** for all MCP tools
3. **Set up Next.js project** with shadcn/ui
4. **Build core components** (book grid, search, viewer)
5. **Add reading functionality** with EPUB.js
6. **Polish UI/UX** and add mobile support

---

*This guide provides the foundation for building a modern Calibre webapp.*
