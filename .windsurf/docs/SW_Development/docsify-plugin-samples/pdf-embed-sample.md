# PDF Embed Plugin - Complete Guide

## Introduction

The PDF Embed plugin allows you to embed PDFiles directly in your documentation using the PDF.js library. It provides a cleand interactive way to display PDF content.

## Basic Usage

### Installation

```html
<!-- PDF.js library -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.min.js"></script>
<script>window.pdfjsLib = pdfjsLib;</script>

<!-- PDF Embed plugin -->
<script src="//cdn.jsdelivr.net/npm/docsify-pdf-embed@latest/dist/pdf-embed.min.js"></script>

<!-- Optional: Enable WebAssembly for better performance -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.worker.min.js"></script>
```

### Basiconfiguration

```javascript
window.$docsify = {
  // Enable with default options
  pdfEmbed: true
};
```

## Syntax

### Basic Embed

```markdown
[PDF Embed](/path/to/document.pdf)
```

### With Custom Height

```markdown
[PDF Embed](/path/to/document.pdf){height=600px}
```

### With Custom Title

```markdown
[PDF Documentitle](/path/to/document.pdf){title="My PDF Document"}
```

### With All Options

```markdown
[View PDF](/path/to/document.pdf){
  title="My Document",
  height="800px",
  download="custom-filename.pdf",
  fullscreen="true",
  print="true",
  open="true"
}
```

## Configuration Options

### Full Configuration

```javascript
window.$docsify = {
  pdfEmbed: {
    // PDF.js worker path (required for WebAssembly)
    pdfWorker: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.worker.min.js',
    
    // Default height for PDF viewer
    height: '500px',
    
    // Defaultitle for PDF viewer
    title: 'PDF Document',
    
    // Show download button
    showDownload: true,
    
    // Show print button
    showPrint: true,
    
    // Show open inew tabutton
    showOpen: true,
    
    // Show fullscreen button
    showFullscreen: true,
    
    // Show page controlshowPageControls: true,
    
    // Enable text selection
    enableTextSelection: true,
    
    // Default zoom level (1 = 100%)
    scale: 1,
    
    // Enable WebAssembly for better performance
    useWorker: true,
    
    // Custom CSS class for the container
    className: 'pdf-embed-container',
    
    // Custom CSS class for the toolbarClass: 'pdf-toolbar',
    
    // Custom CSS class for the iframeClass: 'pdf-iframe',
    
    // Callback when PDF is loaded
    onLoad: function(pdf) {
      console.log('PDF loaded:', pdf);
    },
    
    // Callback when there's an error
    onError: function(error) {
      console.error('PDF error:', error);
    }
  }
};
```

## Styling

### Basic Styling

```css
/* PDF container */
.pdf-embed-container {
  margin: 1.5rem 0;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Toolbar */
.pdf-toolbar {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #f6f8fa;
  border-bottom: 1px solid #e1e4e8;
}

/* Toolbar buttons */
.pdf-toolbar button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: none;
  border: 1px solid #d1d5da;
  border-radius: 3px;
  color: #24292e;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pdf-toolbar button:hover {
  background-color: #eaecef;
  border-color: #d1d5da;
}

/* Page controls */
.pdf-page-controls {
  display: flex;
  align-items: center;
  margin-left: auto;
  font-size: 0.85rem;
  color: #586069;
}

.pdf-page-controls input {
  width: 3em;
  margin: 0.5rem;
  padding: 0.25rem;
  text-align: center;
  border: 1px solid #d1d5da;
  border-radius: 3px;
}

/* Iframe */
.pdf-iframe {
  width: 100%;
  border: none;
  background: white;
}

/* Fullscreen mode */
.pdf-embed-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  margin: 0;
  border: none;
  border-radius: 0;
}

/* Dark theme support */
[data-theme="dark"] .pdf-toolbar {
  background-color: #2d333b;
  border-color: #444c56;
}

[data-theme="dark"] .pdf-toolbar button {
  background-color: #373e47;
  border-color: #444c56;
  color: #adbac7;
}

[data-theme="dark"] .pdf-toolbar button:hover {
  background-color: #444c56;
  border-color: #768390;
}

[data-theme="dark"] .pdf-iframe {
  background: #22272e;
}
```

## Advanced Usage

### Custom Button Icons

```javascript
window.$docsify = {
  pdfEmbed: {
    // Custom button HTML
    buttons: {
      download: '<i class="fas fa-download"></i> Download',
      print: '<i class="fas fa-print"></i> Print',
      open: '<i class="fas fa-external-link-alt"></i> Open',
      fullscreen: '<i class="fas fa-expand"></i> Fullscreen',
      fullscreenExit: '<i class="fas fa-compress"></i> Exit Fullscreen',
      prevPage: '<i class="fas fa-chevron-left"></i>',
      nextPage: '<i class="fas fa-chevron-right"></i>',
      zoomIn: '<i class="fas fa-search-plus"></i>',
      zoomOut: '<i class="fas fa-search-minus"></i>',
      zoomReset: '<i class="fas fa-search"></i> 100%'
    }
  }
};
```

### Custom Toolbar Layout

```javascript
window.$docsify = {
  pdfEmbed: {
    // Custom toolbar HTML
    toolbarTemplate: `
      <div class="pdf-toolbar">
        <div class="pdf-toolbar-group">
          <button class="pdf-btn pdf-btn-prev" title="Previous page">
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="pdf-page-info">
            Page <inputype="number" class="pdf-page-input" min="1"> of <span class="pdf-page-count"></span>
          </span>
          <button class="pdf-btn pdf-btn-next" title="Next page">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
        <div class="pdf-toolbar-group">
          <button class="pdf-btn pdf-btn-zoom-out" title="Zoom out">
            <i class="fas fa-search-minus"></i>
          </button>
          <span class="pdf-zoom-level">100%</span>
          <button class="pdf-btn pdf-btn-zoom-in" title="Zoom in">
            <i class="fas fa-search-plus"></i>
          </button>
          <button class="pdf-btn pdf-btn-zoom-reset" title="Reset zoom">
            <i class="fas fa-search"></i> 100%
          </button>
        </div>
        <div class="pdf-toolbar-group">
          <button class="pdf-btn pdf-btn-download" title="Download">
            <i class="fas fa-download"></i>
          </button>
          <button class="pdf-btn pdf-btn-print" title="Print">
            <i class="fas fa-print"></i>
          </button>
          <button class="pdf-btn pdf-btn-open" title="Open inew tab">
            <i class="fas fa-external-link-alt"></i>
          </button>
          <button class="pdf-btn pdf-btn-fullscreen" title="Fullscreen">
            <i class="fas fa-expand"></i>
          </button>
        </div>
      </div>
    `
  }
};
```

### Custom PDF Rendering

```javascript
// Access the PDF.js API directly
const loadingTask = pdfjsLib.getDocument('/path/to/document.pdf');
loadingTask.promise.then(function(pdf) {
  // Gethe first page
  return pdf.getPage(1);
}).then(function(page) {
  const viewport = page.getViewport({ scale: 1.5 });
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  
  // Set canvas dimensions
  canvas.height = viewport.height;
  canvas.width = viewport.width;
  
  // Render PDF page
  const renderContext = {
    canvasContext: context,
    viewport: viewport
  };
  
  return page.render(renderContext).promise.then(function() {
    // Add canvas to the document.body.appendChild(canvas);
  });
}).catch(function(error) {
  console.error('Error loading PDF:', error);
});
```

## Best Practices

1. **File Size**
   - Optimize PDFiles for web viewing
   - Consider splitting large documents into multiple smaller files
   - Use appropriate compression settings

2. **Performance**
   - Enable WebAssembly for better performance
   - Use the worker thread for large documents
   - Consider lazy loading PDFs that are below the fold

3. **Accessibility**
   - Provide alternative text or HTML versions of PDF content
   - Ensure sufficient color contrast
   - Make sure controls are keyboard-navigable

4. **Mobilexperience**
   - Test on variouscreen sizes
   - Consideresponsive sizing
   - Ensure touch controls work properly

## Troubleshooting

- **PDF not loading?**
  - Check the browser console for errors
  - Verify the PDFile path is correct
  - Make sure CORS is properly configured if loading from a different domain

- **Performance issues?**
  - Try enabling WebAssembly
  - Use the worker thread for large documents
  - Considereducing the PDFile size

- **Missing features?**
  - Check the PDF.js version
  - Verify that all required scripts are loaded
  - Check for browser compatibility issues

## Example Configurations

### Minimal Configuration

```javascript
window.$docsify = {
  pdfEmbed: true
};
```

### Custom Styling

```javascript
window.$docsify = {
  pdfEmbed: {
    height: '600px',
    showDownload: true,
    showPrint: true,
    showOpen: false,
    showFullscreen: true,
    showPageControls: true,
    className: 'custom-pdf-viewer',
    toolbarClass: 'custom-pdf-toolbar',
    iframeClass: 'custom-pdf-iframe'
  }
};
```

### Advanced Configuration

```javascript
window.$docsify = {
  pdfEmbed: {
    pdfWorker: '/path/to/pdf.worker.js',
    height: '800px',
    scale: 1.2,
    useWorker: true,
    showDownload: true,
    showPrint: true,
    showOpen: true,
    showFullscreen: true,
    showPageControls: true,
    enableTextSelection: true,
    onLoad: function(pdf) {
      console.log('PDF loaded successfully');
      console.log('Number of pages:', pdf.numPages);
    },
    onError: function(error) {
      console.error('Failed to load PDF:', error);
    }
  }
};
```

---

For more information, visithe [docsify-pdf-embed GitHub repository](https://github.com/lazypanda10117/docsify-pdf-embed).
