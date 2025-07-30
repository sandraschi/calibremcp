# KaTeX Plugin - Complete Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
  - [Inline Math](#inline-math)
  - [Display Math](#display-math)
- [Configuration](#configuration)
  - [Global Configuration](#global-configuration)
  - [KaTeX Options](#katex-options)
  - [Macros](#macros)
- [Advanced Usage](#advanced-usage)
  - [Chemical Equations](#chemical-equations)
  - [Physics and Units](#physics-and-units)
  - [Theorems and Proofs](#theorems-and-proofs)
  - [Matrices and Arrays](#matrices-and-arrays)
- [Common Formulas](#common-formulas)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Browser Support](#browser-support)
- [Performance Considerations](#performance-considerations)
- [Migration Guide](#migration-guide)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The KaTeX plugin allows you to render beautiful mathematical formulas in your documentation using LaTeX syntax. It's fast, renders formulas on the client side, and is designed to beasy to use while supporting a wide range of mathematical notation.

## Installation

### Using CDN (Recommended)

Add these scripts to your `index.html` file, after the main Docsify script:

```html
<!-- KaTeX CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css" 
      integrity="sha384-GvrOXuhz4Q9Y6m4Y6sVhQl8Y4Xb3p3Ze8zF5fD8F5z0F8L8vIY5Zf5F5F5F5F5F5" 
      crossorigin="anonymous">

<!-- KaTeX JS -->
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js" 
        integrity="sha384-GvrOXuhz4Q9Y6m4Y6sVhQl8Y4Xb3p3Ze8zF5fD8F5z0F8L8vIY5Zf5F5F5F5F5F5" 
        crossorigin="anonymous"></script>

<!-- Auto-render extension for automatic rendering -->
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
        integrity="sha384-GvrOXuhz4Q9Y6m4Y6sVhQl8Y4Xb3p3Ze8zF5fD8F5z0F8L8vIY5Zf5F5F5F5F5F5"
        crossorigin="anonymous"
        onload="renderMathInElement(document.body);"></script>

<!-- Docsify KaTeX -->
<script src="https://cdn.jsdelivr.net/npm/docsify-katex@latest/dist/docsify-katex.js"></script>
```

### Using npm

If you're using a build system:

```bash
npm install katex @docsify/plugin-katex --save
```

Then in your `index.html`:

```html
<!-- In your head -->
<link rel="stylesheet" href="/path/to/katex.min.css">

<!-- After docsify -->
<script src="/path/to/katex.min.js"></script>
<script src="/path/to/auto-render.min.js"></script>
<script src="/path/to/docsify-katex.js"></script>
```

## Basic Usage

### Inline Math

Use single dollar signs `$...$` for inline math:

```markdown
The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$.
```

Renders as:

The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$.

### Display Math

Use double dollar signs `$$...$$` for displayed equations:

````markdown
$$\int_{-\infty}^\infty e^{-x^2} dx = \sqrt{\pi}$$
````

Renders as:

$$\int_{-\infty}^\infty e^{-x^2} dx = \sqrt{\pi}$$

## Configuration

### Global Configuration

Configure the plugin your Docsify configuration:

```javascript
window.$docsify = {
  // Enable KaTeX with default options
  katex: {
    // KaTeX options (see below)
    throwOnError: false,  // Don'throw on renderrorColor: "#cc0000",
    delimiters: [
      {left: "$$", right: "$$", display: true},
      {left: "$", right: "$", display: false},
      {left: "\\(", right: "\\)", display: false},
      {left: "\\[", right: "\\]", display: true}
    ],
    // Macros (see below)
    macros: {
      "\\R": "\\mathbb{R}",
      "\\C": "\\mathbb{C}",
      "\\Z": "\\mathbb{Z}",
      "\\N": "\\mathbb{N}",
      "\\Q": "\\mathbb{Q}",
      "\\abs": ["\\left|#1\\right|", 1],
      "\\norm": ["\\left\\|#1\\right\\|_", 1]
    },
    // Trust settings (for security)
    trust: false,
    // Strict mode (throw on unsupported commands)
    strict: false,
    // Output mode ('mathml', 'html', or 'htmlAndMathml')
    output: 'mathml',
    // Display mode for errors
    displayMode: true,
    // Add CSS classes to rendered math
    fleqn: false,  // Flush left equations
    leqno: false,  // Putags on the left side
    throwOnError: true,  // Throw error on parserrorColor: "#cc0000",  // Color for error messages
    // Min rule thickness
    minRuleThickness: 0.04,  // em
    // Max size for non-math text
    maxSize: Infinity,
    // Max expansion for stretchy commands
    maxExpand: 1000,
    // Allowed protocols for URLs
    allowedProtocols: ["http", "https", "mailto", "_relative"]
  }
};
```

### KaTeX Options

#### Common Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `displayMode` | boolean | `false` | Render in display mode (centered, on own line) |
| `throwOnError` | boolean | `true` | Throw error on parserror |
| `errorColor` | string | `#cc0000` | Color for error messages |
| `fleqn` | boolean | `false` | Flush left equations |
| `leqno` | boolean | `false` | Putags on the left side |
| `macros` | object | `{}` | Customacros (see below) |

#### Advanced Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `maxSize` | number | `Infinity` | Max size for non-math text |
| `maxExpand` | number | `1000` | Max expansion for stretchy commands |
| `strict` | boolean/string/function | `false` | Strict mode |
| `trust` | boolean/function | `false` | Trust input |
| `output` | string | `'mathml'` | Output format |
| `minRuleThickness` | number | `0.04` | Min rule thickness (em) |

### Macros

Define customacros for commonly used expressions:

```javascript
window.$docsify = {
  katex: {
    macros: {
      // Simple macro
      "\\R": "\\mathbb{R}",
      
      // Macro with parameters
      "\\abs": ["\\left|#1\\right|", 1],
      
      // Macro with optional parameter
      "\\pd": ["\\frac{\\partial#1}{\\partial#2}", 2],
      
      // Complex macro with multiple cases
      "\\evalat": ["\\left.#1\\right|_{#2}", 2]
    }
  }
};
```

Usage in Markdown:

```markdown
Let $x \in \R$ and $\abs{x} \ge 0$.

Partial derivative: $\pd{f}{x}$

Evaluation: $\evalat{\frac{df}{x}}{x=0}$
```

## Advanced Usage

### Chemical Equations

Use the `mhchem` extension for chemical equations:

```markdown
$$\ce{2H2 + O2 -> 2H2O}$$

$$\ce{SO4^2- + Ba^2+ -> BaSO4 v}$$

$$\ce{CH3-CHO}$$
```

### Physics and Units

```markdown
$$F = ma = m\frac{dv}{dt}$$

$$E = mc^2$$

$$\hbar = \frac{h}{2\pi} = 1.0545718 \times 10^{-34}\ \text{J}\cdot\text{s}$$
```

### Theorems and Proofs

```markdown
**Theorem 1** (Pythagorean Theorem). For a rightriangle with legs $a$ and $b$ and hypotenuse $c$,

$$a^2 + b^2 = c^2$$

*Proof.* Consider a rightriangle with sides $a$, $b$, and $c$...
```

### Matrices and Arrays

```markdown
$$\begin{pmatrix}
  a & b \\
  c & d 
\end{pmatrix}
\begin{pmatrix}
  x \\
  y
\end{pmatrix} =
\begin{pmatrix}
  ax + by \\
  cx + dy
\end{pmatrix}$$

$$\begin{bmatrix}
  a_{11} & a_{12} & \cdots & a_{1n} \\
  a_{21} & a_{22} & \cdots & a_{2n} \\
  \vdots & \vdots & \ddots & \vdots \\
  a_{m1} & a_{m2} & \cdots & a_{mn}
\end{bmatrix}$$
```

## Common Formulas

### Algebra

```markdown
Quadratic formula: $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$

Binomial theorem: $(a + b)^n = \sum_{k=0}^n \binom{n}{k} a^{n-k}b^k$
```

### Calculus

```markdown
Derivative: $\frac{d}{dx} x^n = nx^{n-1}$

Integral: $\int x^n dx = \frac{x^{n+1}}{n+1} + C$

Taylor series: $f(x) = \sum_{n=0}^\infty \frac{f^{(n)}(a)}{n!}(x-a)^n$
```

### Statistics

```markdownormal distribution: $\frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$

Correlation: $\rho_{X,Y} = \frac{\text{cov}(X,Y)}{\sigma_X \sigma_Y}$
```

## Best Practices

1. **Use Display Mode for Important Equations**
   - Use `$$...$$` for important equations that should be centered
   - Use `$...$` for inline mathematical expressions

2. **Group Related Equations**
   ```markdown
   $$
   \begin{align}
     (a + b)^2 &= a^2 + 2ab + b^2 \\
     (a - b)^2 &= a^2 - 2ab + b^2 \\
     a^2 - b^2 &= (a + b)(a - b)
   \end{align}
   $$
   ```

3. **Use Macros forepetitivexpressions**
   - Define macros for commonly used expressions
   - Makes your source moreadable and maintainable

4. **Add Labels and References**
   ```markdown
   $$
   \begin{equation}
     E = mc^2
     \label{eq:emc2}
   \end{equation}
   
   Ashown in equation \eqref{eq:emc2}, energy equals mass times the speed of light squared.
   ```

5. **Considereadability**
   - Break long equations into multiple lines
   - Add comments in your LaTeX source for complexpressions
   - Use proper spacing and alignment

## Troubleshooting

### Common Issues

1. **Formulas Not Rendering**
   - Check browser console for errors
   - Ensure KaTeX is properly loaded
   - Verify delimiters are correctly configured

2. **Parserrors**
   - Check for unescaped special characters
   - Ensure all braces `{}` are balanced
   - Verify command spelling

3. **Performance Issues**
   - Limithe number of complex formulas per page
   - Consider using `renderMathInElement` for dynamicontent
   - Use `displayMode: false` for inline math

### Debugging

Enable debug mode for more detailed error messages:

```javascript
window.$docsify = {
  katex: {
    throwOnError: true,
    errorColor: '#ff0000',
    strict: true
  }
};
```

## Browser Support

KaTeX supports all modern browsers, including:

- Chrome
- Firefox
- Safari
- Edge
- Opera

For Internet Explorer 11, you'll need to include polyfills for `Promise` and `Object.assign`.

## Performance Considerations

1. **Minimize DOM Elements**
   - Each formula creates DOM elements
   - Avoid excessive use of inline math in large documents

2. **Use Display Mode Wisely**
   - Display mode formulas are morexpensive to render
   - Use inline mode when possible

3. **Lazy Loading**
   - Consider loading KaTeX only on pages that need it
   - Use the `renderMathInElement` function for dynamicontent

## Migration Guide

### FromathJax to KaTeX

1. **Syntax Differences**
   - KaTeX is more strict about syntax
   - Some MathJax commands may not be supported
   - Check the KaTeX supportable for compatibility

2. **Configuration Changes**
   - Update configuration options
   - Replace MathJax delimiters if needed

3. **Macro Migration**
   - Convert MathJax macros to KaTeX format
   - Test all macros for compatibility

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

For more information, visithe [KaTeX documentation](https://katex.org/docs/supported.html) and the [docsify-katex GitHub repository](https://github.com/upupming/docsify-katex).
