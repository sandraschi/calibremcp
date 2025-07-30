# Pagination Plugin - Complete Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
  - [Minimal Setup](#minimal-setup)
  - [Basiconfiguration](#basic-configuration)
- [Advanced Configuration](#advanced-configuration)
  - [Customizing Navigation](#customizing-navigation)
  - [Filtering Pages](#filtering-pages)
  - [Custom Templates](#custom-templates)
  - [Cross-Chapter Navigation](#cross-chapter-navigation)
- [Theming and Styling](#theming-and-styling)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Browser Support](#browser-support)
- [Migration Guide](#migration-guide)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The Pagination plugin adds Previous/Next navigation links to your documentation, making it easier for users to navigate through your content in a linear fashion. This particularly useful for tutorials, guides, and any documentation that follows a sequential structure.

## Installation

### Using CDN (Recommended)

Add the following scripto your `index.html` file, after the main Docsify script:

```html
<!-- Pagination Plugin -->
<script src="https://cdn.jsdelivr.net/npm/docsify-pagination/dist/docsify-pagination.min.js"></script>
```

### Using npm

If you're using a build system:

```bash
npm install docsify-pagination --save
```

Then include it in your project:

```html
<script src="/path/to/docsify-pagination/dist/docsify-pagination.min.js"></script>
```

## Basic Usage

### Minimal Setup

Enable pagination with default settings:

```javascript
window.$docsify = {
  // Enable pagination with default options
  pagination: true
};
```

### Basiconfiguration

Customize the pagination behavior:

```javascript
window.$docsify = {
  pagination: {
    // Customize the previous button text
    previousText: 'Previous',
    
    // Customize the next button text
    nextText: 'Next',
    
    // Customize the cross-chapter text
    crossChapter: true,
    crossChapterText: true,
    
    // Customize the position ('top', 'bottom', or 'both')
    position: 'bottom',
    
    // Custom CSS class for the container
    className: 'pagination',
    
    // Custom CSS class for the navigationavClassName: 'pagination-nav',
    
    // Custom CSS class for the previous button
    previousClassName: 'pagination-nav__link--previous',
    
    // Custom CSS class for the next buttonextClassName: 'pagination-nav__link--next',
    
    // Custom CSS class for the linkClassName: 'pagination-nav__link',
    
    // Custom CSS class for the labelClassName: 'pagination-nav__label',
    
    // Custom CSS class for the titleClassName: 'pagination-nav__title',
    
    // Custom CSS class for the subtitleClassName: 'pagination-nav__subtitle',
    
    // Custom CSS class for the arrowClassName: 'pagination-nav__arrow',
    
    // Custom CSS class for the arrow icon
    arrowIconClassName: 'pagination-nav__arrow-icon',
    
    // Custom CSS class for the arrow icon previous
    arrowIconPreviousClassName: 'pagination-nav__arrow-icon--previous',
    
    // Custom CSS class for the arrow iconext
    arrowIconNextClassName: 'pagination-nav__arrow-icon--next',
    
    // Custom CSS class for the link text
    linkTextClassName: 'pagination-nav__link-text',
    
    // Custom CSS class for the link labelinkLabelClassName: 'pagination-nav__link-label',
    
    // Custom CSS class for the link title
    linkTitleClassName: 'pagination-nav__link-title',
    
    // Custom CSS class for the link subtitle
    linkSubtitleClassName: 'pagination-nav__link-subtitle',
    
    // Custom template for the navigation
    template: `
      <nav class="{{className}}">
        {{#previous}}
          <a class="{{previousClassName}}" href="{{route}}">
            <div class="{{arrowClassName}} {{arrowIconClassName}} {{arrowIconPreviousClassName}}"></div>
            <div class="{{linkTextClassName}}">
              <div class="{{linkLabelClassName}}">{{previousText}}</div>
              <div class="{{linkTitleClassName}}">{{title}}</div>
              {{#subtitle}}
                <div class="{{linkSubtitleClassName}}">{{subtitle}}</div>
              {{/subtitle}}
            </div>
          </a>
        {{/previous}}
        {{#next}}
          <a class="{{nextClassName}}" href="{{route}}">
            <div class="{{linkTextClassName}}">
              <div class="{{linkLabelClassName}}">{{nextText}}</div>
              <div class="{{linkTitleClassName}}">{{title}}</div>
              {{#subtitle}}
                <div class="{{linkSubtitleClassName}}">{{subtitle}}</div>
              {{/subtitle}}
            </div>
            <div class="{{arrowClassName}} {{arrowIconClassName}} {{arrowIconNextClassName}}"></div>
          </a>
        {{/next}}
      </nav>
    `
  }
};
```

## Advanced Configuration

### Filtering Pages

Control which pages appear in the pagination:

```javascript
window.$docsify = {
  pagination: {
    // Filter function to include/exclude pages
    filter: function(prevNext, currentPath) {
      // Skip certain paths
      const skipPaths = ['/changelog', '/license', '/404'];
      
      // Skip if current path is in the skip list
      if (skipPaths.includes(currentPath)) {
        return false;
      }
      
      // Skip if the page is in the skip list
      if (prevNext && prevNext.path && skipPaths.includes(prevNext.path)) {
        return false;
      }
      
      return true;
    },
    
    // Or use a regular expression to match paths
    matchPath: /^(?!\/(changelog|license|404)$).*$/
  }
};
```

### Custom Templates

Create a custom template for the pagination:

```javascript
window.$docsify = {
  pagination: {
    template: `
      <div class="custom-pagination">
        {{#previous}}
          <a href="{{route}}" class="custom-prev">
            ← {{title}}
          </a>
        {{/previous}}
        {{#next}}
          <a href="{{route}}" class="custom-next">
            {{title}} →
          </a>
        {{/next}}
      </div>
    `
  }
};
```

### Cross-Chapter Navigation

Enable navigation between different sections or chapters:

```javascript
window.$docsify = {
  pagination: {
    crossChapter: true,
    crossChapterText: true,
    crossChapterText: 'Continue to: {{title}}',
    crossChapterPreviousText: 'Go back to: {{title}}',
    
    // Custom filter for cross-chapter navigation
    crossChapterFilter: function(section) {
      // Only include sections that have a specific front-matter flag
      return section.meta && section.meta.pagination !== false;
    }
  }
};
```

## Theming and Styling

Customize the appearance of the pagination:

```css
/* Custom pagination styles */
.pagination {
  display: flex;
  justify-content: space-between;
  margin: 2rem 0;
  padding: 1rem 0;
  border-top: 1px solid #eaecef;
  border-bottom: 1px solid #eaecef;
}

.pagination-nav {
  display: flex;
  flex-direction: column;
  max-width: 45%;
}

.pagination-nav__link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border: 1px solid #eaecef;
  border-radius: 4px;
  color: #2c3e50;
  text-decoration: none;
  transition: all 0.2s ease;
}

.pagination-nav__link:hover {
  border-color: #42b983;
  color: #42b983;
}

.pagination-nav__link--previous {
  margin-right: auto;
  text-align: left;
}

.pagination-nav__link--next {
  margin-left: auto;
  text-align: right;
}

.pagination-nav__label {
  font-size: 0.8rem;
  color: #9e9e9e;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.pagination-nav__title {
  font-weight: 500;
  margin: 0.25rem 0;
}

.pagination-nav__subtitle {
  font-size: 0.9rem;
  color: #666;
  margin: 0.25rem 0;
}

/* Dark theme support */
[data-theme="dark"] .pagination-nav__link {
  border-color: #2d333b;
  color: #adbac7;
  background-color: #22272e;
}

[data-theme="dark"] .pagination-nav__link:hover {
  border-color: #539bf5;
  color: #539bf5;
  background-color: #2d333b;
}

[data-theme="dark"] .pagination-nav__label {
  color: #768390;
}

[data-theme="dark"] .pagination-nav__subtitle {
  color: #768390;
}
```

## API Reference

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `previousText` | string | `'Previous'` | Text for the previous button |
| `nextText` | string | `'Next'` | Text for the next button |
| `crossChapter` | boolean | `false` | Enable cross-chapter navigation |
| `crossChapterText` | boolean/string | `false` | Text for cross-chapter navigation |
| `position` | string | `'bottom'` | Position of the pagination (`'top'`, `'bottom'`, or `'both'`) |
| `className` | string | `'pagination'` | CSS class for the container |
| `previousClassName` | string | `'pagination-nav__link--previous'` | CSS class for the previous button |
| `nextClassName` | string | `'pagination-nav__link--next'` | CSS class for the next button |
| `template` | string | [See above](#basic-configuration) | Custom template for the pagination |
| `filter` | function | `null` | Filter function to include/exclude pages |
| `matchPath` | RegExp | `null` | Regular expression to match paths |

### Template Variables

| Variable | Type | Description |
|----------|------|-------------|
| `{{route}}` | string | URL of the previous/next page |
| `{{title}}` | string | Title of the previous/next page |
| `{{subtitle}}` | string | Subtitle of the page (if any) |
| `{{previousText}}` | string | Text for the previous button |
| `{{nextText}}` | string | Text for the next button |
| `{{className}}` | string | CSS class for the container |
| `{{previousClassName}}` | string | CSS class for the previous button |
| `{{nextClassName}}` | string | CSS class for the next button |

## Best Practices

1. **Logical Flow**
   - Ensure your documentation has a clear, logical flow
   - Use the `filter` option to exclude non-sequential pages
   - Test navigation all screen sizes

2. **Performance**
   - Keep the template simple for better performance
   - Avoid complex logic in the filter function
   - Consider lazy-loading the plugin for large documentation sites

3. **Accessibility**
   - Ensure proper contrast for text and background colors
   - Add ARIA labels for screen readers
   - Make sure the navigation is keyboard-accessible

4. **Internationalization**
   - Provide translations for the navigation text
   - Consideright-to-left (RTL) languages in your layout

## Troubleshooting

### Common Issues

1. **Paginationot Appearing**
   - Verify the plugin script is loaded after Docsify
   - Check the browser console for errors
   - Ensure your documentation has multiple pages

2. **Incorrect Navigation**
   - Check your `_sidebar.md` for correct order
   - Verify the `filter` function isn't excluding pages
   - Ensure all pages have proper front matter

3. **Styling Issues**
   - Check for CSS conflicts with your theme
   - Verify custom styles are properly scoped
   - Test in multiple browsers

### Debugging

Enable debug mode for more detailed error messages:

```javascript
window.$docsify = {
  pagination: {
    debug: true,
    // ... other options
  }
};
```

## Browser Supporthe plugin works in all modern browsers, including:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Opera (latest)

## Migration Guide

### From v1 to v2

1. Update the plugin scripto the latest version
2. Check for breaking changes in the configuration options
3. Update any custom templates to match the new structure
4. Testhe pagination all pages

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

For more information, visithe [docsify-pagination GitHub repository](https://github.com/imyelo/docsify-pagination).
