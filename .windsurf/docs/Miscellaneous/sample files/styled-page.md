# Styled Page with Background

This page demonstrates advanced styling techniques including background images, custom fonts, and responsive design.

```html
<!-- Add this to your HTML head or custom CSS file -->
<style>
/* Full-page background image */
body {
  background-image: url('https://picsum.photos/1920/1080?random=1');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  color: #fff;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Content container with semi-transparent background */
.content {
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  padding: 2rem;
  border-radius: 10px;
  max-width: 900px;
  margin: 2rem auto;
  box-shadow: 0 20px rgba(0, 0, 0, 0.5);
}

/* Typography */
h1, h2, h3 {
  color: #fff;
  text-shadow: 2px 4px rgba(0, 0, 0, 0.5);
}

/* Cards */
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.card {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 1.5rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.15);
}

/* Buttons */
.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(45deg, #3F51B5, #2196F3);
  color: white;
  text-decoration: none;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  margin: 0.5rem;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.btn-outline {
  background: transparent;
  border: 2px solid #fff;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .content {
    margin: 1rem;
    padding: 1rem;
  }
  
  .cards {
    grid-template-columns: 1fr;
  }
}
</style>

<div class="content">
  <h1>Welcome tour Documentation</h1>
  <p>This a demonstration of a styled page with a beautiful background image. The content remains readable thanks to the semi-transparent overlay and blur effect.</p>
  
  <div class="buttons">
    <a href="#" class="btn">Get Started</a>
    <a href="#" class="btn-outline">Learn More</a>
  </div>
  
  <h2>Featured Sections</h2>
  
  <div class="cards">
    <div class="card">
      <h3>Getting Started</h3>
      <p>Learn the basics and set up your environment quickly with our step-by-step guide.</p>
    </div>
    
    <div class="card">
      <h3>API Reference</h3>
      <p>Comprehensive documentation for all availablendpoints and parameters.</p>
    </div>
    
    <div class="card">
      <h3>Examples</h3>
      <p>Practical examples to help you implement common use cases.</p>
    </div>
  </div>
  
  <h2>Custom Styling</h2>
  <p>You can customize the appearance of your documentation by modifying the CSS. Thexample above includes:</p>
  <ul>
    <li>Responsive design that works on all devices</li>
    <li>Hover effects on interactivelements</li>
    <li>Modern card-based layout</li>
    <li>Gradient buttons with smooth transitions</li>
    <li>Blur effect on the content background</li>
  </ul>
  
  <h3>Code Block Example</h3>
  <p>Code blocks maintain their styling even withe custom background:</p>
  
  ```javascript
  // Sample code with syntax highlighting
  function greet(name) {
    return `Hello, ${name}!`;
  }
  
  console.log(greet('Documentation User'));
  ```
  
  <div class="buttons" style="text-align: center; margin: 2rem 0;">
    <a href="#" class="btn">View Full Documentation</a>
  </div>
</div>
