# Footnote Plugin - Complete Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
  - [Simple Footnotes](#simple-footnotes)
  - [Reference-Style Footnotes](#reference-style-footnotes)
  - [Inline Footnotes](#inline-footnotes)
- [Configuration](#configuration)
  - [Global Configuration](#global-configuration)
  - [Styling Options](#styling-options)
  - [Custom Rendering](#custom-rendering)
- [Advanced Usage](#advanced-usage)
  - [Multiple References](#multiple-references)
  - [Nested Footnotes](#nested-footnotes)
  - [Footnote Callbacks](#footnote-callbacks)
- [Styling](#styling)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Browser Support](#browser-support)
- [Migration Guide](#migration-guide)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The Footnote plugin addsupport for footnotes in your Docsify documentation, allowing you to add references, citations, and additional information in a cleand organized way. This plugin implements the Pandoc-style footnote syntax, making it familiar to users of other Markdown processors.

## Installation

1. Add the plugin scripto your `index.html` file, after the main Docsify script:

```html
<!-- Add this after the main docsify script -->
<script src="//cdn.jsdelivr.net/npm/docsify-footnote/dist/plugin.min.js"></script>
```

2. Configure the plugin your Docsify configuration:

```javascript
window.$docsify = {
  // Enable with default options
  footnote: true,
  
  // OR with custom options
  footnote: {
    // Configuration options go here
  }
};
```

## Basic Usage

### Simple Footnotes

Create a footnote with a numeric reference:

```markdown
Here's a simple footnote[^1]. And another one[^2].

[^1]: This the first footnote.
[^2]: This the second footnote with **bold** and *italic* text.
```

### Reference-Style Footnotes

Use descriptive references for bettereadability:

```markdown
Here's a reference to a footnote[^note]. And anothereference[^another-note].

[^note]: This a descriptive footnote reference.
[^another-note]: This another footnote with [a link](https://example.com).
```

### Inline Footnotes

Add footnotes directly in the text:

```markdown
This an inline footnote^[This the content of the inline footnote].
```

## Configuration

### Global Configuration

```javascript
window.$docsify = {
  footnote: {
    // Enable/disable the plugin (default: true)
    enabled: true,
    
    // Customize the footnote section title: 'Footnotes',
    
    // Customize the backlink text
    backlinkText: '↩',
    
    // Customize the backlink title (tooltip)
    backlinkTitle: 'Back to content',
    
    // Customize the footnote ID prefix: 'fn-',
    
    // Customize the footnote reference class
    refClass: 'footnote-ref',
    
    // Customize the footnote content class
    contentClass: 'footnote-content',
    
    // Customize the footnote section classectionClass: 'footnotes',
    
    // Enable/disable auto-numbering (default: true)
    autoNumber: true,
    
    // Customize the number format (function or string)
    numberFormat: function(n) {
      return '[' + n + ']';
    },
    
    // Customize the footnote separator (appears between footnotes)
    separator: '<hr>',
    
    // Enable/disable scroll to footnote (default: true)
    scrollToFootnote: true,
    
    // Scroll behavior ('auto' or 'smooth')
    scrollBehavior: 'smooth',
    
    // Enable/disable debug mode (default: false)
    debug: false
  }
};
```

### Styling Options

```javascript
window.$docsify = {
  footnote: {
    // Custom CSS classes for styling
    classes: {
      container: 'footnotes-container',
      list: 'footnotes-list',
      item: 'footnote-item',
      backlink: 'footnote-backlink',
      // ... other classes
    },
    
    // Inline styles (applied to the container)
    style: {
      marginTop: '2em',
      paddingTop: '1em',
      borderTop: '1px solid #eaecef',
      fontSize: '0.9em',
      color: '#6a737d'
    }
  }
};
```

### Custom Rendering

```javascript
window.$docsify = {
  footnote: {
    // Custom render function for the footnote reference
    renderRef: function(refId, number, refText) {
      return `<sup id="${refId}" class="footnote-ref">
        <a href="#${refId}-content" aria-label="Footnote ${number}">
          ${number}
        </a>
      </sup>`;
    },
    
    // Custom render function for the footnote content
    renderContent: function(footnoteId, number, content) {
      return `<div id="${footnoteId}-content" class="footnote-content">
        <span class="footnote-number">${number}.</span>
        <div class="footnote-text">${content}</div>
        <a href="#${footnoteId}" class="footnote-backlink" 
           aria-label="Back to content">${this.backlinkText}</a>
      </div>`;
    },
    
    // Custom render function for the footnotesection
    renderSection: function(html) {
      return `<section class="footnotes">
        <h2>${this.title}</h2>
        <ol>${html}</ol>
      </section>`;
    }
  }
};
```

## Advanced Usage

### Multiple References

Reference the same footnote multiple times:

```markdown
This the first reference[^note].

Later in the text, we reference the same note again[^note].

[^note]: This a shared footnote that appears only once.
```

### Nested Footnotes

Create footnotes within footnotes (requires configuration):

```javascript
window.$docsify = {
  footnote: {
    // Enable nested footnotes (default: false)
    allowNested: true,
    
    // Maximum nesting depth (default: 2)
    maxNesting: 2
  }
};
```

Then in your Markdown:

```markdown
This a footnote with a nested footnote[^note1].

[^note1]: This the first footnote. It contains another footnote[^note2].
[^note2]: This a nested footnote.
```

### Footnote Callbacks

Add custom behavior when footnotes are created or clicked:

```javascript
window.$docsify = {
  footnote: {
    // Called when a footnote reference is created
    onRefCreated: function(refElement, footnoteId, number) {
      console.log('Footnote reference created:', footnoteId, number);
    },
    
    // Called when a footnote content is created
    onContentCreated: function(contentElement, footnoteId, number) {
      console.log('Footnote content created:', footnoteId, number);
    },
    
    // Called when a footnote reference is clicked
    onRefClick: function(event, refElement, footnoteId) {
      console.log('Footnote reference clicked:', footnoteId);
      // Return false to prevent default behavior
    },
    
    // Called when a backlink is clicked
    onBacklinkClick: function(event, backlinkElement, footnoteId) {
      console.log('Backlink clicked:', footnoteId);
      // Return false to prevent default behavior
    }
  }
};
```

## Styling

Customize the appearance ofootnotes with CSS:

```css
/* Container for all footnotes */
.footnotes {
  margin-top: 3em;
  padding-top: 1em;
  border-top: 1px solid #eaecef;
  font-size: 0.9em;
  color: #6a737d;
}

/* Footnote references in the text */
.footnote-ref {
  margin-left: 2px;
}

.footnote-ref a {
  text-decoration: none;
  color: #0366d6;
  background-color: #f3f4f6;
  padding: 0 4px;
  border-radius: 3px;
  font-size: 0.85em;
  line-height: 1;
  vertical-align: super;
  font-weight: 600;
}

.footnote-ref a:hover {
  text-decoration: underline;
}

/* Individual footnote item */
.footnote-item {
  position: relative;
  padding-left: 1.5em;
  margin-bottom: 0.5em;
  line-height: 1.5;
}

/* Footnote number */
.footnote-number {
  position: absolute;
  left: 0;
  font-weight: 600;
}

/* Back to content link */
.footnote-backlink {
  margin-left: 0.5em;
  text-decoration: none;
  color: #0366d6;
  font-weight: 600;
  font-size: 0.85em;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.footnote-backlink:hover {
  opacity: 1;
  text-decoration: underline;
}

/* Dark theme support */
[data-theme="dark"] .footnotes {
  border-color: #2d333b;
  color: #8b949e;
}

[data-theme="dark"] .footnote-ref a {
  color: #58a6ff;
  background-color: rgba(88, 166, 255, 0.1);
}

[data-theme="dark"] .footnote-backlink {
  color: #58a6ff;
}
```

## Best Practices

1. **Keep It Concise**
   - Keep footnote content brief and to the point
   - Avoid long paragraphs or complex formatting
   - Use footnotes for supplementary information, not essential content

2. **Use Descriptive References**
   - Use meaningful footnote markers (e.g., `[^author]` instead of `[^1]`)
   - This makes your Markdown moreadable and maintainable

3. **Placement**
   - Place the footnote definitions athend of the document
   - Group related footnotes together
   - Use a horizontal rule (`---`) before the footnotesection for better visual separation

4. **Accessibility**
   - Ensure sufficient color contrast for footnote references
   - Use descriptive link text for backlinks
   - Test keyboard navigation

5. **Performance**
   - Avoid too many footnotes on a single page
   - Consider lazy-loading footnotes for very long documents
   - Minimize complex HTML in footnotes

## Troubleshooting

### Common Issues

1. **Footnotes not appearing**
   - Make sure the plugin script is loaded after Docsify
   - Check for JavaScript errors in the console
   - Verify thathe plugin is enabled in the configuration

2. **Formatting issues**
   - Check for conflicting CSStyles
   - Ensure proper Markdown formatting
   - Verify that footnotes are properly closed

3. **Nested footnotes not working**
   - Make sure `allowNested` iseto `true`
   - Check the nesting depth limit
   - Verify thathe nested footnotes are properly formatted

### Debugging

Enable debug mode for more detailed error messages:

```javascript
window.$docsify = {
  footnote: {
    debug: true
  }
};
```

## Browser Supporthe plugin works in all modern browsers, including:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- IE 11 (with polyfills)

## Migration Guide

### From v1 to v2

1. Update the plugin scripto the latest version
2. Check for breaking changes in the configuration options
3. Update any custom CSSelectors if needed
4. Testhe footnote functionality

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT

---

For more information, visithe [docsify-footnote GitHub repository](https://github.com/LukeCarrier/docsify-footnote).
