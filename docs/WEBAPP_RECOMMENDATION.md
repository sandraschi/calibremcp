# SOTA Calibre Webapp Recommendation

**Modern web application frontend for CalibreMCP server**

---

## 🎯 **Architecture Overview**

```
┌─────────────────┐
│   Frontend      │  Next.js 15 + React Server Components
│   (Webapp)      │  TypeScript + shadcn/ui + Tailwind CSS
└────────┬────────┘
         │ HTTP/REST API
┌────────▼────────┐
│   FastAPI       │  HTTP wrapper around MCP server
│   Backend       │  Async Python, OpenAPI docs
└────────┬────────┘
         │ MCP Protocol
┌────────▼────────┐
│   CalibreMCP    │  Existing FastMCP server
│   Server        │  All portmanteau tools
└─────────────────┘
```

---

## 🏗️ **Recommended Stack (2025 SOTA)**

### **Backend: FastAPI HTTP Wrapper**

**Why FastAPI:**
- ✅ Python (matches existing codebase)
- ✅ Async/await (perfect for MCP calls)
- ✅ Automatic OpenAPI/Swagger docs
- ✅ Type hints + Pydantic models
- ✅ Fast performance
- ✅ Easy to wrap MCP tool calls

**Structure:**
```
webapp/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── api/
│   │   ├── books.py         # Book endpoints
│   │   ├── search.py        # Search endpoints
│   │   ├── viewer.py        # Reading/viewer endpoints
│   │   ├── metadata.py      # Metadata endpoints
│   │   └── library.py       # Library management
│   ├── mcp_client.py        # MCP client wrapper
│   └── models.py            # Pydantic response models
```

**Key Endpoints:**
- `GET /api/books` - List/search books
- `GET /api/books/{id}` - Get book details
- `GET /api/books/{id}/read` - Get reading content
- `POST /api/books/{id}/metadata` - Update metadata
- `GET /api/search` - Advanced search
- `GET /api/libraries` - Library management

---

### **Frontend: Next.js 15 (App Router)**

**Why Next.js 15:**
- ✅ React Server Components (optimal performance)
- ✅ Built-in routing & API routes
- ✅ TypeScript support
- ✅ Image optimization
- ✅ SEO-friendly
- ✅ Great DX (developer experience)

**Key Features:**
- **Server Components** for data fetching (no client JS needed)
- **Client Components** for interactivity (search, filters, reading)
- **Streaming SSR** for fast initial loads
- **Route handlers** for API proxying if needed

---

### **UI Framework: shadcn/ui + Tailwind CSS**

**Why shadcn/ui:**
- ✅ Copy-paste components (not a dependency)
- ✅ Built on Radix UI (accessible)
- ✅ Tailwind CSS (utility-first)
- ✅ Fully customizable
- ✅ Modern, beautiful defaults
- ✅ TypeScript-first

**Components Needed:**
- Book cards/grid
- Search bar with filters
- Metadata modal
- EPUB/PDF viewer
- Tag management UI
- Library switcher
- Reading progress

---

### **State Management**

**Server State: TanStack Query (React Query)**
- ✅ Automatic caching & refetching
- ✅ Optimistic updates
- ✅ Background sync
- ✅ Perfect for API calls

**Client State: Zustand**
- ✅ Lightweight (1KB)
- ✅ Simple API
- ✅ No boilerplate
- ✅ For UI state (modals, filters, etc.)

---

### **Reading/Viewing: EPUB.js**

**Why EPUB.js:**
- ✅ In-browser EPUB rendering
- ✅ No server-side conversion needed
- ✅ Responsive & mobile-friendly
- ✅ Supports annotations
- ✅ Open source & maintained

**Alternative: PDF.js** (for PDF files)

---

## 📋 **Core Features**

### **1. Book Browsing & Search**
- Grid/list view toggle
- Advanced filters (author, tag, rating, date, etc.)
- Full-text search
- Sort options (title, date, rating)
- Pagination/virtual scrolling

### **2. Book Details**
- Comprehensive metadata display
- Cover images
- Tags management
- Series information
- Reading progress
- Format availability

### **3. Reading Experience**
- In-browser EPUB viewer
- Reading progress tracking
- Bookmarks/annotations
- Font size/theme controls
- Mobile-responsive

### **4. Library Management**
- Multi-library support
- Library switching
- Statistics dashboard
- Health checks

### **5. Metadata Management**
- Edit book metadata
- Tag organization
- Bulk operations
- Import/export

### **6. Smart Collections**
- Create/edit collections
- Dynamic filtering
- Reading recommendations

---

## 🚀 **Implementation Plan**

### **Phase 1: Backend API (Week 1)**
1. Set up FastAPI project structure
2. Create MCP client wrapper
3. Implement core endpoints:
   - Books CRUD
   - Search
   - Library management
4. Add OpenAPI documentation
5. Error handling & validation

### **Phase 2: Frontend Foundation (Week 2)**
1. Initialize Next.js 15 project
2. Set up shadcn/ui + Tailwind
3. Create layout & navigation
4. Implement book grid/list views
5. Basic search functionality

### **Phase 3: Core Features (Week 3-4)**
1. Book detail pages
2. Metadata editing
3. Tag management
4. Library switching
5. Reading viewer (EPUB.js integration)

### **Phase 4: Advanced Features (Week 5-6)**
1. Advanced search filters
2. Smart collections
3. Reading progress tracking
4. Bulk operations
5. Export functionality

### **Phase 5: Polish & Optimization (Week 7)**
1. Performance optimization
2. Mobile responsiveness
3. Error handling
4. Loading states
5. Documentation

---

## 📦 **Dependencies**

### **Backend (`requirements-webapp.txt`)**
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
httpx>=0.25.0  # For MCP client
python-multipart>=0.0.6  # For file uploads
```

### **Frontend (`package.json`)**
```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.4.0",
    "epubjs": "^0.3.0",
    "lucide-react": "^0.300.0",
    "tailwindcss": "^3.4.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

---

## 🎨 **UI/UX Recommendations**

### **Design Principles**
- **Clean & Minimal**: Focus on content (books)
- **Fast**: Optimize for speed (RSC, streaming)
- **Accessible**: WCAG 2.1 AA compliance
- **Mobile-First**: Responsive design
- **Dark Mode**: System preference + toggle

### **Key Pages**
1. **Home/Dashboard**: Library stats, recent books, recommendations
2. **Browse**: Grid/list of books with filters
3. **Book Detail**: Full metadata, reading options
4. **Reader**: Full-screen reading experience
5. **Search**: Advanced search with filters
6. **Library Settings**: Multi-library management

---

## 🔧 **Technical Considerations**

### **MCP Client Integration**
- Use `mcp` Python client library
- Wrap tool calls in FastAPI endpoints
- Handle async MCP responses
- Error translation (MCP → HTTP)

### **File Serving**
- Serve book files via FastAPI static files
- Support range requests for streaming
- CORS configuration for cross-origin

### **Performance**
- Server Components for initial load
- Client-side caching (TanStack Query)
- Image optimization (Next.js Image)
- Virtual scrolling for large lists

### **Security**
- Authentication (if needed)
- Rate limiting
- Input validation (Pydantic)
- CORS configuration

---

## 📚 **Reference Implementations**

### **Similar Projects**
- **Calibre Content Server**: Official Calibre web interface
- **Calibre-Web**: Popular Calibre webapp (Flask-based)
- **Readarr**: Media management webapp (React)

### **Inspiration**
- **Goodreads**: Book discovery & reviews
- **LibraryThing**: Library management
- **Readwise Reader**: Reading experience

---

## ✅ **Advantages of This Stack**

1. **Modern & Maintainable**: Latest best practices
2. **Type-Safe**: TypeScript + Pydantic
3. **Performant**: Server Components + caching
4. **Developer-Friendly**: Great DX, good docs
5. **Scalable**: Can handle large libraries
6. **Accessible**: Built-in accessibility features
7. **Mobile-Ready**: Responsive by default

---

## 🚦 **Getting Started**

### **Quick Start Commands**

```bash
# Backend
cd webapp/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements-webapp.txt
uvicorn main:app --reload

# Frontend
cd webapp/frontend
npm install
npm run dev
```

---

## 📝 **Next Steps**

1. **Create project structure** (`webapp/` directory)
2. **Set up FastAPI backend** with MCP client wrapper
3. **Initialize Next.js frontend** with shadcn/ui
4. **Implement core book browsing** feature
5. **Add reading viewer** with EPUB.js
6. **Iterate based on feedback**

---

*This recommendation follows 2025 SOTA practices for web applications, prioritizing performance, developer experience, and user experience.*
