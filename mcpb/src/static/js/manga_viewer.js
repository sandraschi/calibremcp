/**
 * Manga/Comic Viewer for CalibreMCP
 * Core functionality for the manga/comic viewer
 */

class MangaViewer {
    constructor() {
        // DOM Elements
        this.dom = {
            app: document.getElementById('app'),
            viewerContainer: document.getElementById('viewer-container'),
            pageContainer: document.getElementById('page-container'),
            loadingIndicator: document.getElementById('loading-indicator'),
            currentPageEl: document.getElementById('current-page'),
            totalPagesEl: document.getElementById('total-pages'),
            documentTitle: document.getElementById('document-title'),
            thumbnailStrip: document.getElementById('thumbnail-strip'),
            sidebar: document.getElementById('sidebar'),
            contextMenu: document.getElementById('context-menu')
        };

        // State
        this.state = {
            currentPage: 0,
            totalPages: 0,
            pages: [],
            zoomMode: 'fit-width',
            zoomLevel: 1.0,
            readingDirection: 'rtl',
            pageLayout: 'single',
            showThumbnails: true,
            isFullscreen: false,
            metadata: {},
            bookmarks: [],
            isLoading: false
        };

        // Initialize
        this.initializeEventListeners();
        this.loadFromURL();
        this.updateUI();
    }

    // Initialize event listeners
    initializeEventListeners() {
        // Navigation
        document.getElementById('first-page').addEventListener('click', () => this.goToPage(0));
        document.getElementById('prev-page').addEventListener('click', () => this.navigate(-1));
        document.getElementById('next-page').addEventListener('click', () => this.navigate(1));
        document.getElementById('last-page').addEventListener('click', () => this.goToPage(this.state.totalPages - 1));
        
        // Zoom controls
        document.getElementById('zoom-in').addEventListener('click', () => this.zoomIn());
        document.getElementById('zoom-out').addEventListener('click', () => this.zoomOut());
        document.getElementById('fit-width').addEventListener('click', () => this.setZoomMode('fit-width'));
        
        // UI toggles
        document.getElementById('sidebar-toggle').addEventListener('click', () => this.toggleSidebar());
        document.getElementById('toggle-thumbnails').addEventListener('click', () => this.toggleThumbnails());
        document.getElementById('fullscreen').addEventListener('click', () => this.toggleFullscreen());
        
        // Reading direction
        document.querySelectorAll('.direction-option').forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                this.setReadingDirection(option.dataset.direction);
            });
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            switch (e.key) {
                case 'ArrowLeft':
                    this.navigate(this.state.readingDirection === 'rtl' ? 1 : -1);
                    break;
                case 'ArrowRight':
                    this.navigate(this.state.readingDirection === 'rtl' ? -1 : 1);
                    break;
                case 'f':
                case 'F11':
                    this.toggleFullscreen();
                    break;
                case 'Escape':
                    if (this.state.isFullscreen) this.toggleFullscreen(false);
                    break;
            }
        });
    }
    
    // Load data from URL parameters
    loadFromURL() {
        const params = new URLSearchParams(window.location.search);
        const page = parseInt(params.get('page')) || 0;
        const zoom = parseFloat(params.get('zoom')) || 1.0;
        const mode = params.get('mode') || 'fit-width';
        const direction = params.get('dir') || 'rtl';
        
        this.state.zoomLevel = Math.max(0.1, Math.min(zoom, 5.0));
        this.state.zoomMode = ['fit-width', 'fit-height', 'fit-both', 'original'].includes(mode) ? mode : 'fit-width';
        this.state.readingDirection = ['ltr', 'rtl', 'vertical'].includes(direction) ? direction : 'rtl';
        
        // Load the specified page after a short delay to allow the UI to initialize
        setTimeout(() => this.goToPage(page), 100);
    }
    
    // Update the URL to reflect current state
    updateURL() {
        const params = new URLSearchParams({
            page: this.state.currentPage,
            zoom: this.state.zoomLevel.toFixed(2),
            mode: this.state.zoomMode,
            dir: this.state.readingDirection
        });
        
        window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`);
    }
    
    // Navigation methods
    navigate(delta) {
        const newPage = this.state.currentPage + delta;
        if (newPage >= 0 && newPage < this.state.totalPages) {
            this.goToPage(newPage);
        }
    }
    
    async goToPage(pageIndex) {
        if (pageIndex < 0 || pageIndex >= this.state.totalPages) return;
        
        this.state.currentPage = pageIndex;
        this.updateURL();
        this.updateUI();
        
        // Load the page if not already loaded
        if (!this.state.pages[pageIndex]?.loaded) {
            await this.loadPage(pageIndex);
        } else {
            this.showPage(pageIndex);
        }
    }
    
    // Zoom methods
    zoomIn() {
        if (this.state.zoomMode === 'original') return;
        
        const newZoom = Math.min(5.0, this.state.zoomLevel + 0.25);
        this.setZoom('custom', newZoom);
    }
    
    zoomOut() {
        if (this.state.zoomMode === 'original') return;
        
        const newZoom = Math.max(0.1, this.state.zoomLevel - 0.25);
        this.setZoom('custom', newZoom);
    }
    
    setZoom(mode, level = 1.0) {
        this.state.zoomMode = mode;
        this.state.zoomLevel = level;
        this.updateURL();
        this.updatePageLayout();
    }
    
    setZoomMode(mode) {
        this.setZoom(mode);
    }
    
    // UI update methods
    updateUI() {
        // Update page info
        this.dom.currentPageEl.textContent = this.state.currentPage + 1;
        this.dom.totalPagesEl.textContent = this.state.totalPages;
        
        // Update zoom level display
        document.getElementById('zoom-level').textContent = `${Math.round(this.state.zoomLevel * 100)}%`;
        
        // Update active page in thumbnails
        document.querySelectorAll('.thumbnail').forEach(thumb => {
            const pageIndex = parseInt(thumb.dataset.page, 10);
            thumb.classList.toggle('active', pageIndex === this.state.currentPage);
        });
        
        // Update reading direction icon
        const directionIcon = document.querySelector('#reading-direction i');
        if (directionIcon) {
            directionIcon.className = this.state.readingDirection === 'rtl' ? 'bi bi-text-right' : 'bi bi-text-left';
        }
    }
    
    // Page loading and display
    async loadPage(pageIndex) {
        if (this.state.isLoading) return;
        
        this.state.isLoading = true;
        this.showLoading(true);
        
        try {
            // Simulate page loading (replace with actual API call)
            await new Promise(resolve => setTimeout(resolve, 300));
            
            // Create page data if it doesn't exist
            if (!this.state.pages[pageIndex]) {
                this.state.pages[pageIndex] = {
                    index: pageIndex,
                    loaded: true,
                    element: null
                };
            }
            
            // Show the page
            this.showPage(pageIndex);
            
        } catch (error) {
            console.error(`Error loading page ${pageIndex + 1}:`, error);
        } finally {
            this.state.isLoading = false;
            this.showLoading(false);
        }
    }
    
    showPage(pageIndex) {
        const page = this.state.pages[pageIndex];
        if (!page || !page.loaded) return;
        
        // Create page element if it doesn't exist
        if (!page.element) {
            const pageEl = document.createElement('div');
            pageEl.className = 'page';
            pageEl.dataset.page = pageIndex;
            
            const img = document.createElement('img');
            img.src = `/api/manga/page/${pageIndex}`;
            img.alt = `Page ${pageIndex + 1}`;
            img.loading = 'eager';
            
            // Handle image load/error
            img.onload = () => {
                pageEl.classList.remove('loading');
                this.updatePageLayout();
            };
            
            pageEl.appendChild(img);
            page.element = pageEl;
            this.dom.pageContainer.appendChild(pageEl);
        }
        
        // Show only the current page
        this.updatePageVisibility();
    }
    
    updatePageVisibility() {
        const pages = Array.from(this.dom.pageContainer.querySelectorAll('.page'));
        pages.forEach(pageEl => {
            const pageIndex = parseInt(pageEl.dataset.page, 10);
            pageEl.classList.toggle('hidden', pageIndex !== this.state.currentPage);
        });
    }
    
    updatePageLayout() {
        const container = this.dom.pageContainer;
        const pages = Array.from(container.querySelectorAll('.page'));
        
        pages.forEach(pageEl => {
            const img = pageEl.querySelector('img');
            if (!img) return;
            
            // Apply zoom and layout based on current settings
            // This is a simplified version - implement your own layout logic
            switch (this.state.zoomMode) {
                case 'fit-width':
                    img.style.width = '100%';
                    img.style.height = 'auto';
                    break;
                case 'fit-height':
                    img.style.width = 'auto';
                    img.style.height = '100%';
                    break;
                case 'fit-both':
                    img.style.maxWidth = '100%';
                    img.style.maxHeight = '100%';
                    img.style.width = 'auto';
                    img.style.height = 'auto';
                    break;
                case 'original':
                case 'custom':
                    img.style.width = `${img.naturalWidth * this.state.zoomLevel}px`;
                    img.style.height = 'auto';
                    break;
            }
        });
    }
    
    // UI helpers
    showLoading(show) {
        this.dom.loadingIndicator.style.display = show ? 'flex' : 'none';
    }
    
    toggleSidebar(show) {
        if (typeof show === 'undefined') {
            show = !this.dom.sidebar.classList.contains('show');
        }
        
        this.dom.sidebar.classList.toggle('show', show);
        document.body.classList.toggle('sidebar-visible', show);
    }
    
    toggleThumbnails() {
        this.state.showThumbnails = !this.state.showThumbnails;
        this.dom.thumbnailStrip.classList.toggle('hidden', !this.state.showThumbnails);
        this.updateUI();
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.dom.app.requestFullscreen().catch(console.error);
        } else {
            document.exitFullscreen().catch(console.error);
        }
    }
    
    setReadingDirection(direction) {
        this.state.readingDirection = direction;
        this.updateURL();
        this.updateUI();
    }
    
    // Initialize the viewer with data
    initialize(data) {
        this.state.metadata = data.metadata || {};
        this.state.totalPages = data.pageCount || 0;
        this.state.pages = Array(this.state.totalPages).fill().map((_, i) => ({
            index: i,
            loaded: false,
            element: null
        }));
        
        // Update UI
        this.updateUI();
        
        // Load the first page
        if (this.state.totalPages > 0) {
            this.loadPage(0);
        }
    }
}

// Initialize the viewer when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mangaViewer = new MangaViewer();
    
    // Example initialization (replace with actual data loading)
    mangaViewer.initialize({
        metadata: {
            title: 'Sample Manga',
            author: 'Author Name',
            pageCount: 10
        },
        pageCount: 10
    });
});
