# Pagination Plugin - Complete Guide

## Introduction

The Pagination plugin adds Previous/Next navigation links to your documentation, making it easier for users to navigate through your content in a linear fashion.

## Basic Usage

### Installation

```html
<script src="//cdn.jsdelivr.net/npm/docsify-pagination/dist/docsify-pagination.min.js"></script>
```

### Basiconfiguration

```javascript
window.$docsify = {
  // Enable pagination with default options
  pagination: true
};
```

## Configuration Options

### Full Configuration

```javascript
window.$docsify = {
  pagination: {
    // Customize the previous button text
    previousText: 'Previous',
    
    // Customize the next button text
    nextText: 'Next',
    
    // Whether to show the page title in the button
    // Can be true, false, or a function that returns a string
    crossChapter: true,
    
    // Customize the separator between chapter and title
    crossChapterText: ' - ',
    
    // Custom CSS class for the pagination container
    className: 'pagination',
    
    // Custom CSS class for the previous button
    previousClassName: 'pagination-prev',
    
    // Custom CSS class for the next buttonextClassName: 'pagination-next',
    
    // Custom CSS class for the page titleClassName: 'pagination-title',
    
    // Custom template for the pagination
    // Available variables: previousText, previousLink, previousTitle, nextText, nextLink, nextTitle
    template: `
      <nav class="pagination-nav">
        <div class="pagination-item pagination-item--previous">
          {{#previousLink}}
            <a href="{{previousLink}}" class="pagination-link pagination-link--previous">
              <span class="pagination-label">{{previousText}}</span>
              <span class="pagination-title">{{previousTitle}}</span>
            </a>
          {{/previousLink}}
        </div>
        <div class="pagination-item pagination-item--next">
          {{#nextLink}}
            <a href="{{nextLink}}" class="pagination-link pagination-link--next">
              <span class="pagination-label">{{nextText}}</span>
              <span class="pagination-title">{{nextTitle}}</span>
            </a>
          {{/nextLink}}
        </div>
      </nav>
    `,
    
    // Custom filter function to determine the previous/next page
    filter: function(prevNext, currentPath) {
      // prevNext is an object with `prev` and `next` properties
      // currentPath is the path of the current page
      // You can modify the prev/next values hereturn prevNext;
    },
    
    // Custom sort function to determine the order of pagesort: function(pages) {
      // pages is an array of all pages
      // You can sorthem hereturn pages.sort();
    },
    
    // Customize the position where the pagination is inserted
    // Can be 'top', 'bottom', or a CSSelector
    position: 'bottom',
    
    // Whether to hide the pagination when there's no previous/next page
    hideOnSinglePage: true
  }
};
```

## Styling

### Basic Styling

```css
/* Pagination container */
.pagination-nav {
  display: flex;
  justify-content: space-between;
  margin: 2rem 0;
  padding: 1rem 0;
  border-top: 1px solid #eaecef;
  border-bottom: 1px solid #eaecef;
}

/* Pagination item */
.pagination-item {
  display: flex;
  flex: 1;
}

/* Pagination links */
.pagination-link {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: #2c3e50;
  transition: color 0.2s ease;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.pagination-link:hover {
  color: #4CAF50;
  text-decoration: none;
  background-color: #f5f5f5;
}

/* Next link */
.pagination-item--next {
  text-align: right;
  justify-content: flex-end;
}

/* Labels */
.pagination-label {
  font-size: 0.8rem;
  color: #7f8c8d;
  margin-bottom: 0.25rem;
}

/* Titles */
.pagination-title {
  font-weight: 500;
  position: relative;
}

/* Add arrow icons */
.pagination-item--previous .pagination-title::before {
  content: '← ';
}

.pagination-item--next .pagination-title::after {
  content: ' →';
}
```

### Dark Theme Support

```css
[data-theme="dark"] .pagination-link {
  color: #e0e0e0;
}

[data-theme="dark"] .pagination-link:hover {
  color: #81C784;
  background-color: #333;
}

[data-theme="dark"] .pagination-label {
  color: #b0bec5;
}

[data-theme="dark"] .pagination-nav {
  border-color: #424242;
}
```

## Advanced Usage

### Custom Page Order

You can define a custom order for your pages by creating a `_order.md` file in your docs directory:

```markdown
# _order.md

- getting-started.md
- installation.md
- configuration/
  - basic.md
  - advanced.md
- guides/
  - theming.md
  - plugins.md
- api/
  - reference.md
```

### Dynamic Filtering

You can filter or modify the previous/next pages dynamically:

```javascript
window.$docsify = {
  pagination: {
    filter: function(prevNext, currentPath) {
      // Example: Skip certain paths
      const skipPaths = ['/changelog', '/license'];
      
      if (prevNext.prev && skipPaths.includes(prevNext.prev.path)) {
        prevNext.prev = null;
      }
      
      if (prevNext.next && skipPaths.includes(prevNext.next.path)) {
        prevNext.next = null;
      }
      
      return prevNext;
    }
  }
};
```

### Custom Template with Icons

```javascript
window.$docsify = {
  pagination: {
    template: `
      <nav class="pagination-nav">
        <div class="pagination-item pagination-item--previous">
          {{#previousLink}}
            <a href="{{previousLink}}" class="pagination-link pagination-link--previous">
              <span class="pagination-label">
                <svg width="12" height="12" viewBox="0 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M19 12H5M12 19l-7-7-7"/>
                </svg>
                {{previousText}}
              </span>
              <span class="pagination-title">{{previousTitle}}</span>
            </a>
          {{/previousLink}}
        </div>
        <div class="pagination-item pagination-item--next">
          {{#nextLink}}
            <a href="{{nextLink}}" class="pagination-link pagination-link--next">
              <span class="pagination-label">
                {{nextText}}
                <svg width="12" height="12" viewBox="0 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M5 12h14M12 5l7-7"/>
                </svg>
              </span>
              <span class="pagination-title">{{nextTitle}}</span>
            </a>
          {{/nextLink}}
        </div>
      </nav>
    `
  }
};
```

## Best Practices

1. **Clear Navigation**
   - Use descriptive titles for your pages
   - Keep the navigation consistent across your documentation

2. **Visual Hierarchy**
   - Make the next/previous buttons easily distinguishable
   - Use icons to improve visual cues

3. **Mobilexperience**
   - Ensure the pagination is usable on small screens
   - Consider stacking the buttons on mobile

4. **Accessibility**
   - Add appropriate ARIA labels
   - Ensure keyboard navigation works
   - Maintain sufficient color contrast

## Troubleshooting

- **Paginationot appearing?**
  - Make sure the plugin is loaded after Docsify
  - Check for JavaScript errors in the console
  - Verifyour `_sidebar.md` is properly structured

- **Incorrect page order?**
  - Check your `_order.md` file
  - Verify the file names match exactly
  - Ensure the paths are correct

- **Styling issues?**
  - Check for CSS conflicts
  - Verifyour custom styles have sufficient specificity
  - Look for missing or overridden styles

## Example Configurations

### Minimal Configuration

```javascript
window.$docsify = {
  pagination: true
};
```

### Custom Text and Styling

```javascript
window.$docsify = {
  pagination: {
    previousText: '← Previous',
    nextText: 'Next →',
    crossChapter: true,
    crossChapterText: ':',
    className: 'docs-pagination',
    position: 'bottom'
  }
};
```

### Advanced Customization

```javascript
window.$docsify = {
  pagination: {
    template: `
      <div class="custom-pagination">
        {{#previousLink}}
          <a href="{{previousLink}}" class="btn-outline">
            <span class="icon">←</span>
            <span class="text">{{previousTitle || previousText}}</span>
          </a>
        {{/previousLink}}
        {{#nextLink}}
          <a href="{{nextLink}}" class="btn-primary">
            <span class="text">{{nextTitle || nextText}}</span>
            <span class="icon">→</span>
          </a>
        {{/nextLink}}
      </div>
    `,
    filter: function(prevNext, currentPath) {
      // Custom filtering logic
      return prevNext;
    },
    position: 'bottom',
    hideOnSinglePage: true
  }
};
```

---

For more information, visithe [docsify-pagination GitHub repository](https://github.com/imyelo/docsify-pagination).
