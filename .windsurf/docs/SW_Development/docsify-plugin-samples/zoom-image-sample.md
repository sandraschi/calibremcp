# Zoom Image Plugin - Complete Guide

## Introduction

The Zoom Image plugin adds a beautiful zoom effecto images in your documentation. When users click on an image, it expands to a larger size with a smooth animation, making it easier to view details.

## Basic Usage

### Installation

```html
<script src="//cdn.jsdelivr.net/npm/docsify-zoom-image/dist/zoom-image.min.js"></script>
```

### Basiconfiguration

```javascript
window.$docsify = {
  // Enable with default options
  zoomImage: true
};
```

## Configuration Options

### Full Configuration

```javascript
window.$docsify = {
  zoomImage: {
    // The background color of the overlay
    bgColor: 'rgba(0, 0, 0, 0.85)',
    
    // The z-index of the overlay
    zIndex: 1000,
    
    // The scale factor for the zoomed image (0 = fito screen, 1 = original size, >1 = zoom in)
    scale: 1,
    
    // The duration of the zoom animation in milliseconds
    duration: 300,
    
    // Theasing function for the zoom animation
    // See: https://developer.mozilla.org/en-US/docs/Web/CSS/transition-timing-function
    easing: 'cubic-bezier(0.4, 0, 0, 1)',
    
    // Whether to show the image title in the zoomed view
    showTitle: true,
    
    // Custom selector for images that should be zoomable
    // Default: 'img[data-zoomable]' (only images with data-zoomable attribute)
    // Seto 'img' to make all images zoomable
    selector: 'img[data-zoomable]',
    
    // Custom class for the zoomed image container
    zoomClass: 'zoom-image-container',
    
    // Custom class for the zoomed image
    zoomImageClass: 'zoomed-image',
    
    // Custom class for the overlayClass: 'zoom-overlay',
    
    // Callback when zooming starts
    onZoomIn: function(img) {
      console.log('Zooming in:', img.src);
    },
    
    // Callback when zooming out
    onZoomOut: function(img) {
      console.log('Zooming out:', img.src);
    }
  }
};
```

## Usagexamples

### Basic Usage

```markdown
<!-- Will be zoomable because of the data-zoomable attribute -->
![Sample Image](path/to/image.jpg){data-zoomable}

<!-- Will not be zoomable (unless you change the selector) -->
![Another Image](path/to/another-image.jpg)
```

### With Custom Options

```markdown
<!-- Custom zoom scale -->
![High Detail](path/to/detailed.jpg){data-zoom-scale="2" data-zoomable}

<!-- Custom background color -->
![Dark BG](path/to/light-image.jpg){data-zoom-bg="rgba(0, 0, 0, 0.95)" data-zoomable}
```

## Styling

### Basic Styling

```css
/* Zoom overlay */
.zoom-overlay {
  /* Overridefault styles here */
  background-color: rgba(0, 0, 0, 0.9) !important;
}

/* Zoomed image container */
.zoom-image-container {
  /* Add custom styles */
  max-width: 90%;
  max-height: 90%;
}

/* Zoomed image */
.zoomed-image {
  /* Add custom styles */
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  transition: transform 0.3s ease;
}

/* Image title */
.zoomed-image-title {
  color: white;
  text-align: center;
  margin-top: 1rem;
  font-size: 1.1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* Loading indicator */
.zoom-loading {
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: zoom-spin 1s ease-in-out infinite;
}

@keyframes zoom-spin {
  to { transform: rotate(360deg); }
}
```

### Dark Theme Support

```css
[data-theme="dark"] .zoom-overlay {
  background-color: rgba(0, 0, 0, 0.95) !important;
}

[data-theme="dark"] .zoomed-image {
  /* Addark theme specific styles */
  border: 1px solid #444;
}
```

## Advanced Usage

### Custom Selector

```javascript
window.$docsify = {
  zoomImage: {
    // Make all images zoomable
    selector: 'img',
    
    // Or be more specific
    // selector: '.markdown-section img:not(.no-zoom)'
  }
};
```

### Dynamic Image Loading

```javascript
// If you're loading images dynamically, you may need to reinitialize the plugin
document.addEventListener('content:updated', function() {
  if (window.DocsifyZoomImage && window.DocsifyZoomImage.init) {
    window.DocsifyZoomImage.init();
  }
});
```

### Custom Zoom Button

```html
<button id="custom-zoom-btn" class="zoom-button">
  <span class="zoom-icon">🔍</span> Click to Zoom
</button>

<script>
document.addEventListener('DOMContentLoaded', function() {
  const btn = document.getElementById('custom-zoom-btn');
  const img = document.getElementById('image-to-zoom');
  
  btn.addEventListener('click', function() {
    if (window.DocsifyZoomImage && window.DocsifyZoomImage.zoomImage) {
      window.DocsifyZoomImage.zoomImage(img);
    }
  });
});
</script>
```

## Best Practices

1. **Image Optimization**
   - Use appropriately sized images
   - Consider using responsive images with `srcset`
   - Compress images to reduce load times

2. **Performance**
   - Only enable zoom for images that benefit from it
   - Consider lazy loading images that are below the fold
   - Avoid zooming very large images

3. **User Experience**
   - Provide visual feedback when an image is zoomable
   - Ensure the zoom controls are intuitive
   - Make sure the zoomed image can be closed easily

4. **Accessibility**
   - Always includescriptive altext
   - Ensure keyboard navigation works
   - Provide sufficient color contrast

## Troubleshooting

- **Images not zooming?**
  - Make sure the plugin is loaded after Docsify
  - Check if the image has the correct selector (default: `data-zoomable`)
  - Look for JavaScript errors in the console

- **Zoomed image too small/large?**
  - Adjusthe `scale` option
  - Check if there are any CSS conflicts
  - Try setting explicit dimensions on the original image

- **Performance issues?**
  - Check image file sizes
  - Consider using WebP format for better compression
  - Make sure you're not zooming too many images at once

## Example Configurations

### Minimal Configuration

```javascript
window.$docsify = {
  zoomImage: true
};
```

### Custom Styling

```javascript
window.$docsify = {
  zoomImage: {
    bgColor: 'rgba(0, 0, 0, 0.9)',
    scale: 1.5,
    duration: 200,
    showTitle: true,
    selector: '.markdown-section img:not(.no-zoom)',
    onZoomIn: function(img) {
      console.log('Zooming in:', img.src);
    },
    onZoomOut: function(img) {
      console.log('Zooming out:', img.src);
    }
  }
};
```

### With Custom CSS

```javascript
window.$docsify = {
  zoomImage: {
    zoomClass: 'custom-zoom-container',
    zoomImageClass: 'custom-zoomed-image',
    overlayClass: 'custom-zoom-overlay'
  }
};
```

```css
.custom-zoom-overlay {
  background-color: rgba(0, 0, 0, 0.95) !important;
  backdrop-filter: blur(5px);
}

.custom-zoomed-image {
  max-width: 90%;
  max-height: 90%;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.custom-zoomed-image:hover {
  transform: scale(1.02);
}
```

---

For more information, visithe [docsify-zoom-image GitHub repository](https://github.com/francoischalifour/docsify-zoom-image).
