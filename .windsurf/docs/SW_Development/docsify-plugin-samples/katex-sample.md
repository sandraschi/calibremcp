# KaTeX Plugin - Complete Guide

## Introduction

The KaTeX plugin allows you to render beautiful mathematical formulas in your documentation using LaTeX syntax. It's fast and renders formulas on the client side.

## Basic Usage

### Installation

```html
<!-- KaTeX CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">

<!-- KaTeX JS -->
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>

<!-- Docsify KaTeX -->
<script src="https://cdn.jsdelivr.net/npm/docsify-katex@latest/dist/docsify-katex.js"></script>
```

### Basiconfiguration

```javascript
window.$docsify = {
  // Enable with default options
  katex: {
    // KaTeX options (optional)
    // See: https://katex.org/docs/options.html
    throwOnError: true,
    errorColor: '#cc0000',
    delimiters: [
      {left: '$$', right: '$$', display: true},
      {left: '$', right: '$', display: false},
      {left: '\\(', right: '\\)', display: false},
      {left: '\\[', right: '\\]', display: true}
    ]
  }
};
```

## Inline Math

Use single dollar signs for inline math:

```markdown
Euler's formula: $e^{i\pi} + 1 = 0$
```

Euler's formula: $e^{i\pi} + 1 = 0$

## Display Math

Use double dollar signs for display math:

```markdown
$$\frac{d}{dx}\left( \int_{0}^{x} f(u)\,du\right)=f(x)$$
```

$$\frac{d}{dx}\left( \int_{0}^{x} f(u)\,du\right)=f(x)$$

## Common Mathematical Expressions

### Fractions and Binomials

```markdown
Fractions: $\frac{a}{b}$ $\tfrac{a}{b}$ $\dfrac{a}{b}$

Binomial coefficients: $\binom{n}{k}$
```

Fractions: $\frac{a}{b}$ $\tfrac{a}{b}$ $\dfrac{a}{b}$

Binomial coefficients: $\binom{n}{k}$

### Square Roots and nth Roots

```markdown
Square root: $\sqrt{x}$
nth root: $\sqrt[n]{x}$
```

Square root: $\sqrt{x}$
nth root: $\sqrt[n]{x}$

### Sums, Products, and Integrals

```markdown
Sum: $\sum_{i=1}^{n} i^2 = \frac{n(n+1)(2n+1)}{6}$

Product: $\prod_{i=1}^{n} i = n!$

Integral: $\int_{a}^{b} x^2 \,dx = \left.\frac{x^3}{3}\right|_{a}^{b}$
```

Sum: $\sum_{i=1}^{n} i^2 = \frac{n(n+1)(2n+1)}{6}$

Product: $\prod_{i=1}^{n} i = n!$

Integral: $\int_{a}^{b} x^2 \,dx = \left.\frac{x^3}{3}\right|_{a}^{b}$

### Matrices and Arrays

```markdown
$\begin{matrix}
 a & b \\
 c & d
\end{matrix}$

$\begin{pmatrix}
 a & b \\
 c & d
\end{pmatrix}$

$\begin{bmatrix}
 a & b \\
 c & d
\end{bmatrix}$
```

$\begin{matrix}
 a & b \\
 c & d
\end{matrix}$

$\begin{pmatrix}
 a & b \\
 c & d
\end{pmatrix}$

$\begin{bmatrix}
 a & b \\
 c & d
\end{bmatrix}$

## Advanced Configuration

### Custom Delimiters

```javascript
window.$docsify = {
  katex: {
    delimiters: [
      // Default LaTeX delimiters
      {left: '$$', right: '$$', display: true},
      {left: '$', right: '$', display: false},
      {left: '\\(', right: '\\)', display: false},
      {left: '\\[', right: '\\]', display: true},
      
      // Additional custom delimiters
      {left: '\\begin{equation}', right: '\\end{equation}', display: true},
      {left: '\\begin{align}', right: '\\end{align}', display: true},
      {left: '\\[', right: '\\]', display: true}
    ]
  }
};
```

### Macros

Define customacros for frequently used expressions:

```javascript
window.$docsify = {
  katex: {
    macros: {
      "\\RR": "\\mathbb{R}",
      "\\CC": "\\mathbb{C}",
      "\\NN": "\\mathbb{N}",
      "\\ZZ": "\\mathbb{Z}",
      "\\QQ": "\\mathbb{Q}",
      "\\abs[1]": "\\left|#1\\right|",
      "\\norm[1]": "\\left\\|#1\\right\\|",
      "\\set[1]": "\\left\\{#1\\right\\}",
      "\\paren[1]": "\\left(#1\\right)",
      "\\bracket[1]": "\\left[#1\\right]"
    }
  }
};
```

Now you can use these macros in your formulas:

```markdown
$\RR, \CC, \NN, \ZZ, \QQ$

$\abs{x + y} \leq \abs{x} + \abs{y}$

$\norm{x + y} \leq \norm{x} + \norm{y}$

$\set{x \in \RR \mid x > 0}$

$\paren{\frac{a}{b}}^2 = \frac{a^2}{b^2}$

$\bracket{\frac{a}{b}}^2 = \frac{a^2}{b^2}$
```

$\RR, \CC, \NN, \ZZ, \QQ$

$\abs{x + y} \leq \abs{x} + \abs{y}$

$\norm{x + y} \leq \norm{x} + \norm{y}$

$\set{x \in \RR \mid x > 0}$

$\paren{\frac{a}{b}}^2 = \frac{a^2}{b^2}$

$\bracket{\frac{a}{b}}^2 = \frac{a^2}{b^2}$

## Common Pitfalls

1. **Escaping Special Characters**
   - Use double backslashes for LaTeX commands: `\\(` instead of `\(`
   - Escape special Markdown characters: `\{`, `\}`, `\[`, `\]`, `\|`

2. **Display Mode vs Inline Mode**
   - Use `$$...$$` or `\\[...\\]` for display mode (centered, on its own line)
   - Use `$...$` or `\\(...\\)` for inline mode

3. **Alignment**
   - Use `\begin{align}...\end{align}` for multi-linequations with alignment
   - Use `&` for alignment points
   - Use `\\` for line breaks

## Examples

### Aligned Equations

```markdown
$$\begin{align}
    (a + b)^2 &= a^2 + 2ab + b^2 \\
    (a - b)^2 &= a^2 - 2ab + b^2 \\
    a^2 - b^2 &= (a + b)(a - b)
\end{align}$$
```

$$\begin{align}
    (a + b)^2 &= a^2 + 2ab + b^2 \\
    (a - b)^2 &= a^2 - 2ab + b^2 \\
    a^2 - b^2 &= (a + b)(a - b)
\end{align}$$

### Piecewise Functions

```markdown
$$
f(x) =
  \begin{cases}
    x^2 & \text{if } x \geq 0 \\
    -x & \text{if } x < 0
  \end{cases}
$$
```

$$
f(x) =
  \begin{cases}
    x^2 & \text{if } x \geq 0 \\
    -x & \text{if } x < 0
  \end{cases}
$$

### Matrices with Different Brackets

```markdown
$$
\begin{matrix}
 a & b \\
 c & d
\end{matrix}
\quad
\begin{pmatrix}
 a & b \\
 c & d
\end{pmatrix}
\quad
\begin{bmatrix}
 a & b \\
 c & d
\end{bmatrix}
\quad
\begin{Bmatrix}
 a & b \\
 c & d
\end{Bmatrix}
\quad
\begin{vmatrix}
 a & b \\
 c & d
\end{vmatrix}
\quad
\begin{Vmatrix}
 a & b \\
 c & d
\end{Vmatrix}
$$
```

$$
\begin{matrix}
 a & b \\
 c & d
\end{matrix}
\quad
\begin{pmatrix}
 a & b \\
 c & d
\end{pmatrix}
\quad
\begin{bmatrix}
 a & b \\
 c & d
\end{bmatrix}
\quad
\begin{Bmatrix}
 a & b \\
 c & d
\end{Bmatrix}
\quad
\begin{vmatrix}
 a & b \\
 c & d
\end{vmatrix}
\quad
\begin{Vmatrix}
 a & b \\
 c & d
\end{Vmatrix}
$$

## Performance Considerations

1. **Server-Side Rendering**
   - KaTeX renders on the client side
   - For large documents, consider server-side rendering
   - Or use the `display: false` option for less critical formulas

2. **Font Loading**
   - KaTeX loads its own fonts
   - Consider preloading the KaTeX font files
   - Or use the `fontURL` option to specify a CDN

3. **Dynamicontent**
   - If you load content dynamically, you may need to re-render formulas
   - Use the `renderMathInElement` function from KaTeX

## Troubleshooting

- **Formulas not rendering?**
  - Check the browser console for errors
  - Make sure KaTeX is loaded before the plugin
  - Verifyour delimiters are correct

- **Syntax errors?**
  - Check for unescaped special characters
  - Make sure all `{` and `}` are properly escaped
  - Verify that all environments are properly closed

- **Alignment issues?**
  - Use `&` for alignment points
  - Make sure to use `\\` for line breaks
  - Check for missing `\end{...}`

## Additional Resources

- [KaTeX Documentation](https://katex.org/docs/supported.html)
- [LaTeX Mathematical Symbols](https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols)
- [Detexify - Find LaTeX symbols by drawing](http://detexify.kirelabs.org/classify.html)

---

For more information, visithe [docsify-katex GitHub repository](https://github.com/upupming/docsify-katex).
