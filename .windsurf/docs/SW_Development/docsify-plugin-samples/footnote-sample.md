# Footnote Plugin - Complete Guide

## Introduction

The Footnote plugin addsupport for footnotes in your documentation, allowing you to add references and citations in a cleand organized way.

## Basic Usage

### Installation

```html
<script src="//cdn.jsdelivr.net/npm/docsify-footnote/dist/plugin.min.js"></script>
```

### Basiconfiguration

```javascript
window.$docsify = {
  // Enable with default options
  footnote: true
};
```

## Syntax

### Inline Footnotes

```markdown
This a sentence with a footnote[^note].

[^note]: This the footnote content.
```

This a sentence with a footnote[^note].

[^note]: This the footnote content.

### Multiple Footnotes

```markdown
You can have multiple footnotes[^first] in your document[^second].

[^first]: This the first footnote.
[^second]: This the second footnote.
```

You can have multiple footnotes[^first] in your document[^second].

[^first]: This the first footnote.
[^second]: This the second footnote.

### Inline Footnote Content

```markdown
You can also write footnotes inline^[This an inline footnote.].
```

You can also write footnotes inline^[This an inline footnote.].

## Configuration Options

### Full Configuration

```javascript
window.$docsify = {
  footnote: {
    // The class name for the footnote container
    className: 'footnotes',
    
    // The title of the footnotesection
    title: 'Footnotes',
    
    // The title tag to use (h1-h6)
    titleTag: 'h2',
    
    // The class name for the footnote backref link
    backrefClassName: 'footnote-backref',
    
    // The text for the backref link
    backrefLabel: '↩',
    
    // The title attribute for the backref link
    backrefTitle: 'Back to reference',
    
    // The class name for the footnote reference
    refClassName: 'footnote-ref',
    
    // The class name for the footnote itemClassName: 'footnote-item',
    
    // Whether to add a link to the footnote section
    link: true,
    
    // The text for the link to the footnote section
    linkText: 'Jump to footnotes',
    
    // The class name for the link to the footnote section
    linkClassName: 'footnote-link',
    
    // The position of the footnote section
    // Can be 'bottom' (default) or 'aside'
    position: 'bottom',
    
    // Callback when a footnote is rendered
    onRender: function(footnote) {
      console.log('Footnote rendered:', footnote);
    }
  }
};
```

## Styling

### Basic Styling

```css
/* Footnote container */
.footnotes {
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid #eaecef;
  font-size: 0.9em;
  color: #6a737d;
}

/* Footnote title */
.footnotes h2 {
  font-size: 1.2em;
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* Footnote list */
.footnotes ol {
  padding-left: 1.5em;
  margin: 0;
}

/* Footnote item */
.footnotes li {
  margin-bottom: 0.5rem;
  position: relative;
  padding-left: 1em;
  line-height: 1.6;
}

/* Footnote reference in text */
.footnote-ref {
  font-size: 0.8em;
  vertical-align: super;
  margin-left: 0.2em;
  text-decoration: none;
  color: #0366d6;
}

.footnote-ref:hover {
  text-decoration: underline;
}

/* Back to reference link */
.footnote-backref {
  margin-left: 0.3em;
  text-decoration: none;
  color: #0366d6;
  font-weight: bold;
}

.footnote-backref:hover {
  text-decoration: underline;
}

/* Link to footnotesection */
.footnote-link {
  display: inline-block;
  margin-top: 1rem;
  font-size: 0.9em;
  color: #0366d6;
  text-decoration: none;
}

.footnote-link:hover {
  text-decoration: underline;
}
```

### Dark Theme Support

```css
[data-theme="dark"] .footnotes {
  border-color: #444;
  color: #b0bec5;
}

[data-theme="dark"] .footnotes h2 {
  color: #e0e0e0;
}

[data-theme="dark"] .footnote-ref,
[data-theme="dark"] .footnote-backref,
[data-theme="dark"] .footnote-link {
  color: #64b5f6;
}
```

## Advanced Usage

### Custom Footnote Markers

You can use customarkers for footnotes:

```markdown
This a sentence with a customarker[^custom].

[^custom]: This footnote uses a customarker.
```

### Reference the Same Footnote Multiple Times

```markdown
You can reference the same footnote multiple times[^same][^same].

[^same]: This a reusable footnote.
```

### Nested Footnotes

```markdown
This a sentence with a nested footnote[^nested].

[^nested]: This the outer footnote[^inner].
[^inner]: This the inner footnote.
```

### Inline HTML in Footnotes

```markdown
This a sentence with a formatted footnote[^html].

[^html]: This footnote contains <strong>HTML</strong> and a [link](https://example.com).
```

## Best Practices

1. **Keep Footnotes Concise**
   - Use footnotes for supplementary information
   - Keep them brief and to the point
   - Avoid long paragraphs or complex formatting

2. **Use Descriptive Markers**
   - Use meaningful footnote markers (e.g., `[^author]` instead of `[^1]`)
   - This makes your Markdown moreadable and maintainable

3. **Placement**
   - Place footnotes near the contenthey reference
   - Group related footnotes together
   - Consider using inline footnotes for very short notes

4. **Accessibility**
   - Ensure sufficient color contrast
   - Make sure the back-to-reference links are keyboard-navigable
   - Use descriptive link text

## Troubleshooting

- **Footnotes not appearing?**
  - Make sure the plugin is loaded after Docsify
  - Check for JavaScript errors in the console
  - Verifyour Markdown syntax is correct

- **Formatting issues?**
  - Check for CSS conflicts
  - Make sure your custom styles have sufficient specificity
  - Look for missing or overridden styles

- **Links not working?**
  - Check for duplicate footnote markers
  - Make sure all footnotes are properly defined
  - Verify thathe plugin is properly initialized

## Example Configurations

### Minimal Configuration

```javascript
window.$docsify = {
  footnote: true
};
```

### Custom Styling

```javascript
window.$docsify = {
  footnote: {
    className: 'custom-footnotes',
    title: 'References',
    titleTag: 'h3',
    backrefLabel: '↵',
    backrefTitle: 'Back to content',
    position: 'bottom',
    link: true,
    linkText: 'View all references',
    linkClassName: 'ref-link'
  }
};
```

### Advanced Configuration with Callbacks

```javascript
window.$docsify = {
  footnote: {
    onRender: function(footnote) {
      // Add a custom class to specific footnotes
      if (footnote.content.includes('important')) {
        footnote.element.classList.add('important-note');
      }
      
      // Log when footnotes arendered
      console.log(`Footnote ${footnote.id} rendered`);
    }
  }
};
```

## Additional Features

### Custom Footnote Formatting

You can customize how footnotes are displayed using CSS:

```css
/* Custom styling for specific footnotes */
.footnote-item.important-note {
  background-color: #fff3cd;
  padding: 0.5rem;
  border-left: 3px solid #ffc107;
  margin: 0.5rem 0;
}

/* Style the footnote numbers */
.footnote-ref::before {
  content: '[';
}

.footnote-ref::after {
  content: ']';
}

/* Style the backref link */
.footnote-backref {
  font-family: monospace;
  font-size: 1.2em;
  text-decoration: none;
}
```

### Dynamicontent

If you're loading content dynamically, you may need to reinitialize the footnotes:

```javascript
document.addEventListener('content:updated', function() {
  if (window.DocsifyFootnotes && window.DocsifyFootnotes.init) {
    window.DocsifyFootnotes.init();
  }
});
```

---

For more information, visithe [docsify-footnote GitHub repository](https://github.com/LincZero/docsify-footnote).
