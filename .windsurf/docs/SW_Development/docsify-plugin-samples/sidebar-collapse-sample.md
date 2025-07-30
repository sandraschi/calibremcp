# Sidebar Collapse Plugin - Complete Guide

## Introduction

The Sidebar Collapse plugin adds collapsible sections to your Docsify sidebar, making it easier to navigate large documentation sites. It automatically adds toggle buttons nexto folders and supports persistent state across page loads.

## Basic Usage

### Installation

```html
<script src="//cdn.jsdelivr.net/npm/docsify-sidebar-collapse/dist/docsify-sidebar-collapse.min.js"></script>
```

### Basiconfiguration

```javascript
window.$docsify = {
  loadSidebar: true, // Required for sidebar
  subMaxLevel: 3,    // Maximum header level to include in the sidebar
  
  // Sidebar Collapse plugin optionsidebarCollapse: {
    // Whether to show the collapse button
    collapseButton: true,
    
    // Whether to show the collapse button mobile
    collapseButtonMobile: true,
    
    // The texto showhen the sidebar is collapsed
    collapseLabel: '◄',
    
    // The texto showhen the sidebar is expanded
    expandLabel: '►',
    
    // Whether to persisthe sidebar state (collapsed/expanded)
    persist: true,
    
    // The key to use for localStorage
    persistKey: 'sidebar-collapse-state',
    
    // Whether to auto collapse other items when expanding one
    accordion: false,
    
    // The duration of the collapse/expand animation (ms)
    animationDuration: 250,
    
    // Callback when a section is toggled
    onToggle: function(isCollapsed) {
      console.log('Sidebar is now', isCollapsed ? 'collapsed' : 'expanded');
    }
  }
};
```

## Advanced Configuration

### Custom Icons

You can use custom icons or text for the collapse/expand buttons:

```javascript
window.$docsify = {
  sidebarCollapse: {
    collapseLabel: '<i class="fas fa-chevron-left"></i>',
    expandLabel: '<i class="fas fa-chevron-right"></i>',
    // Or use text
    // collapseLabel: '[-]',
    // expandLabel: '[+]',
  }
};
```

### Per-Section Configuration

You can control the initial state of specific sections using HTML comments in your `_sidebar.md`:

```markdown
- Section 1
  - [Page 1](page1.md)
  - [Page 2](page2.md)
  <!-- sidebar-collapse:collapsed -->
  
- Section 2
  - [Page 3](page3.md)
  - [Page 4](page4.md)
  <!-- sidebar-collapse:expanded -->
```

## Styling

### Basic Styling

```css
/* Sidebar container */
.sidebar {
  transition: all 0.3s ease;
}

/* Collapse button */
.sidebar-toggle-button {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 100;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.sidebar-toggle-button:hover {
  background: #388E3C;
  transform: scale(1.1);
}

/* Collapsible sections */
.sidebar-nav .collapse-btn {
  float: right;
  padding: 0 10px;
  cursor: pointer;
  user-select: none;
  opacity: 0.6;
  transition: all 0.2s ease;
}

.sidebar-nav .collapse-btn:hover {
  opacity: 1;
}

/* Indent child items when parent is collapsed */
.sidebar-nav .collapse-body {
  overflow: hidden;
  transition: height 0.3s ease;
}

/* Active link styling */
.sidebar-nav li.active > a {
  font-weight: bold;
  color: #4CAF50;
}
```

### Dark Theme Support

```css
[data-theme="dark"] .sidebar-toggle-button {
  background: #2E7D32;
  color: #fff;
}

[data-theme="dark"] .sidebar-nav .collapse-btn {
  color: #90A4AE;
}

[data-theme="dark"] .sidebar-nav li.active > a {
  color: #81C784;
}
```

## API

### Methods

You can control the sidebar programmatically:

```javascript
// Toggle thentire sidebar
window.$docsify.sidebar.toggle();

// Collapse thentire sidebar
window.$docsify.sidebar.collapse();

// Expand thentire sidebar
window.$docsify.sidebar.expand();

// Toggle a specific section
const section = document.querySelector('.sidebar-nav li.has-child');
window.$docsify.sidebar.toggleSection(section);

// Collapse all sections
window.$docsify.sidebar.collapseAll();

// Expand all sections
window.$docsify.sidebar.expandAll();
```

### Events

```javascript
document.addEventListener('sidebar-collapse:toggle', function(e) {
  console.log('Sidebar toggled:', e.detail.isCollapsed);
});

document.addEventListener('sidebar-section:toggle', function(e) {
  console.log('Section toggled:', {
    section: e.detail.section,
    isCollapsed: e.detail.isCollapsed
  });
});
```

## Best Practices

1. **Consistent State**
   - Use `persist: true` to remember the user's preference
   - Set sensible defaults for first-time visitors

2. **Performance**
   - Avoideeply nested structures (more than 3 levels)
   - Use `subMaxLevel` to limithe depth of the sidebar

3. **Accessibility**
   - Ensure keyboard navigation works
   - Add proper ARIAttributes
   - Maintain sufficient color contrast

4. **Mobilexperience**
   - Testhe sidebar on different screen sizes
   - Consider a hamburger menu for very small screens

## Troubleshooting

- **Sidebar not collapsing?**
  - Make sure the plugin is loaded after Docsify
  - Check for JavaScript errors in the console
  - Verifyour `_sidebar.md` has a proper structure

- **State not persisting?**
  - Check if localStorage is available
  - Verify the `persistKey` is unique
  - Ensure `persist: true` iset

- **Styling issues?**
  - Check for CSS conflicts
  - Verifyour custom styles have sufficient specificity
  - Look for missing or overridden styles

## Example Configurations

### Minimal Configuration

```javascript
window.$docsify = {
  loadSidebar: true,
  subMaxLevel: 3,
  sidebarCollapse: true // Enable with default options
};
```

### Advanced Configuration

```javascript
window.$docsify = {
  loadSidebar: true,
  subMaxLevel: 4,
  
  sidebarCollapse: {
    collapseButton: true,
    collapseButtonMobile: true,
    collapseLabel: '◄',
    expandLabel: '►',
    persist: true,
    persistKey: 'my-docs-sidebar-state',
    accordion: true,
    animationDuration: 300,
    
    // Custom class for the sidebarClass: 'custom-sidebar',
    
    // Callback when sidebar state changes
    onToggle: function(isCollapsed) {
      const mainContent = document.querySelector('.content');
      if (mainContent) {
        mainContent.style.marginLeft = isCollapsed ? '40px' : '300px';
      }
    }
  }
};
```

### Custom Toggle Button

```html
<button id="custom-toggle" class="custom-toggle-btn">
  <span class="show-text">Show Sidebar</span>
  <span class="hide-text">Hide Sidebar</span>
</button>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    constoggleBtn = document.getElementById('custom-toggle');
    const showText = toggleBtn.querySelector('.show-text');
    const hideText = toggleBtn.querySelector('.hide-text');
    
    // Initial state
    updateButton();
    
    // Toggle on click
    toggleBtn.addEventListener('click', function() {
      window.$docsify.sidebar.toggle();
      updateButton();
    });
    
    // Update button text based on state
    function updateButton() {
      const isCollapsed = document.body.classList.contains('sidebar-collapsed');
      showText.style.display = isCollapsed ? 'inline' : 'none';
      hideText.style.display = isCollapsed ? 'none' : 'inline';
    }
    
    // Listen for sidebar togglevents
    document.addEventListener('sidebar-collapse:toggle', updateButton);
  });
</script>
```

---

For more information, visithe [docsify-sidebar-collapse GitHub repository](https://github.com/iPeng6/docsify-sidebar-collapse).
