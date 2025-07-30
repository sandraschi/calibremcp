# Docsify Tabs - Complete Guide

## Introduction

The Tabs plugin allows you torganize content into tabbed sections, making your documentation more organized and easier to navigate. This guide covers everything from basic usage to advanced customization.

## Basic Usage

### Installation

```html
<!-- Add this to your index.html -->
<script src="//cdn.jsdelivr.net/npm/docsify-tabs@1"></script>
```

### Basic Tabs

```markdown
<!-- tabs:start -->

#### **English**
Hello! Thisome content in English.

#### **French**
Bonjour! Voici du contenu en français.

#### **Spanish**
¡Hola! Estes un contenido en español.

<!-- tabs:end -->
```

## Advanced Features

### Nested Tabs

```markdown
<!-- tabs:start -->

#### **Frontend**
Frontend technologies:

<!-- tabs:start -->

##### **React**
A JavaScript library for building user interfaces.

##### **Vue**
The Progressive JavaScript Framework.

##### **Angular**
One framework. Mobile & desktop.

<!-- tabs:end -->

#### **Backend**
Backend technologies:

<!-- tabs:start -->

##### **Node.js**
JavaScript runtime built on Chrome's V8 engine.

##### **Django**
A high-level Python Web framework.

##### **Spring**
Framework for building Javapplications.

<!-- tabs:end -->

<!-- tabs:end -->
```

## Configuration Options

### Global Configuration

```javascript
window.$docsify = {
  tabs: {
    // Basic Settings
    defaultTab: 0,           // Defaultab to display (0-based index or 'first'/'last')
    maxTabs: 5,              // Maximum number of tabs to display
    loadAllTabs: false,      // Load all tab content at once
    sync: true,              // Sync tabs withe same name across the page
    persist: false,          // Persisthe active tab across page loads
    
    // Styling
    theme: 'default',        // 'default' or 'material'
    tabHeadings: 'all',      // 'all' or 'active'
    
    // Animation: 200,          // Animation duration in milliseconds
    
    // Custom Classes
    tabContainerClass: 'docsify-tabs',
    tabNavigationClass: 'docsify-tabs__nav',
    tabItemClass: 'docsify-tabs__tab',
    tabActiveClass: 'docsify-tabs__tab--active',
    tabContentClass: 'docsify-tabs__content',
    
    // Callbacks
    onTabShow: function(tab) {
      // Called when a tab ishown
      console.log('Tab shown:', tab);
    },
    
    onTabHide: function(tab) {
      // Called when a tab is hidden
      console.log('Tab hidden:', tab);
    },
    
    // Advancedynamic: false,          // Enable dynamic tab loading
    updateHash: true,        // Update URL hash when switching tabs
    useStorage: true,        // Use localStorage to persistab state
    storageKey: 'docsify-tabs' // Key to use for localStorage
  }
};
```

### Per-Instance Configuration

```markdown
<!-- tabs:start { "maxTabs": 3, "theme": "material", "persist": true } -->

#### **Tab 1**
Content for Tab 1.

#### **Tab 2**
Content for Tab 2.

#### **Tab 3**
Content for Tab 3.

#### **Tab 4**
This tab won't be shown because maxTabs iseto 3.

<!-- tabs:end -->
```

## Styling

### Custom CSS

```css
/* Tab Container */
.docsify-tabs {
  margin: 1.5em 0;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  overflow: hidden;
}

/* Tab Navigation */
.docsify-tabs__nav {
  display: flex;
  flex-wrap: wrap;
  padding: 0;
  margin: 0;
  list-style: none;
  background: #f6f8fa;
  border-bottom: 1px solid #e1e4e8;
}

/* Tab Items */
.docsify-tabs__tab {
  padding: 0.5em 1em;
  margin: 0;
  border: none;
  border-right: 1px solid #e1e4e8;
  background: none;
  font: inherit;
  font-size: 0.9em;
  color: #24292e;
  cursor: pointer;
  transition: all 0.2s ease;
}

.docsify-tabs__tab:last-child {
  border-right: none;
}

.docsify-tabs__tab:hover {
  background: #eaecef;
}

.docsify-tabs__tab--active {
  background: white;
  color: #0366d6;
  font-weight: 600;
  border-bottom: 2px solid #0366d6;
  margin-bottom: -1px;
}

/* Tab Content */
.docsify-tabs__content {
  padding: 1.5em;
  background: white;
}

/* Dark Theme */
[data-theme="dark"] .docsify-tabs {
  border-color: #444c56;
}

[data-theme="dark"] .docsify-tabs__nav {
  background: #2d333b;
  border-color: #444c56;
}

[data-theme="dark"] .docsify-tabs__tab {
  color: #adbac7;
  border-color: #444c56;
}

[data-theme="dark"] .docsify-tabs__tab:hover {
  background: #373e47;
}

[data-theme="dark"] .docsify-tabs__tab--active {
  background: #1e2228;
  color: #539bf5;
  border-color: #539bf5;
}

[data-theme="dark"] .docsify-tabs__content {
  background: #22272e;
  color: #adbac7;
}
```

## Best Practices

1. **Performance**
   - Use lazy loading for content-heavy tabs with `<!-- tabs:lazy -->`
   - Limithe number of tabs to 3-5 for better usability
   - Avoid complex layouts inside tabs

2. **Accessibility**
   - Use descriptive tab labels
   - Ensure keyboard navigation works
   - Maintain sufficient color contrast

3. **Maintainability**
   - Keep tab content focused and concise
   - Use consistent styling
   - Group related contentogether

## Troubleshooting

- **Tabs not rendering?**
  - Make sure you've included the plugin script
  - Check for JavaScript errors in the console
  - Verify the HTML structure is correct

- **Content not showing?**
  - Check for syntax errors in your Markdown
  - Make sure all tabs are properly closed
  - Verify there are no JavaScript errors

- **Styling issues?**
  - Check for CSS conflicts with your theme
  - Make sure your custom styles have sufficient specificity
  - Test in multiple browsers

## Examples

### Code Comparison

````markdown
<!-- tabs:start -->

#### **JavaScript**
```javascript
function greet(name) {
  return `Hello, ${name}!`;
}
```

#### **TypeScript**
```typescript
function greet(name: string): string {
  return `Hello, ${name}!`;
}
```

#### **Python**
```python
def greet(name):
    return f"Hello, {name}!"
```

<!-- tabs:end -->
````

### API Documentation

```markdown
<!-- tabs:start -->

#### **GET /users**
Returns a list of users.

**Parameters:**
- `limit` (optional): Number of users to return
- `offset` (optional): Number of users to skip

#### **POST /users**
Creates a new user.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

#### **GET /users/:id**
Returns a single user by ID.

**Parameters:**
- `id` (required): The ID of the user to retrieve

<!-- tabs:end -->
```

## Browser Supporthe plugin works in all modern browsers, including:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- IE 11 (with polyfills)

## License

MIT

---

For more information, visithe [docsify-tabs GitHub repository](https://github.com/jhildenbiddle/docsify-tabs).
