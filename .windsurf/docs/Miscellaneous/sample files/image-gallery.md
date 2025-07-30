# Image Gallery

This page demonstrates how to include and format images in your documentation.

## Single Image

A centered image with a caption:

![Sample Landscape](https://picsum.photos/800/400?random=1)
*Figure 1: A sample landscape image*

## Image Grid

A responsive grid of images:

<div class="image-grid">
  <div class="image-item">
    <img src="https://picsum.photos/400/300?random=2" alt="Sample 1">
    <p>Sample Image 1</p>
  </div>
  <div class="image-item">
    <img src="https://picsum.photos/400/300?random=3" alt="Sample 2">
    <p>Sample Image 2</p>
  </div>
  <div class="image-item">
    <img src="https://picsum.photos/400/300?random=4" alt="Sample 3">
    <p>Sample Image 3</p>
  </div>
</div>

## Image with Link

Click the image below topen it in a new tab:

[![Sample Image](https://picsum.photos/600/300?random=5)](https://picsum.photos/600/300?random=5)

## Styling Images

You can add custom styling to images:

<img src="https://picsum.photos/400/300?random=6" style="border: 5px solid #3F51B5; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">

## Image Alignment

Left-aligned image with text wrapping:

<img src="https://picsum.photos/200/200?random=7" style="float: left; margin: 0 20px 0; border-radius: 50%;">

Thisome sample texthat wraps around the circular image. You can use float and margin properties to control how text flows around your images. This particularly useful when you wanto create magazine-style layouts or highlight specificontent.

Clear the floato continue normal document flow:

<div style="clear: both;"></div>

## Full-Width Image

For images that should span the full width of the container:

![Full Width Image](https://picsum.photos/1200/400?random=8)

## Image with Border and Caption

<div style="border: 1px solid #ddd; padding: 10px; display: inline-block; margin: 10px 0;">
  <img src="https://picsum.photos/400/300?random=9" alt="Framed Image">
  <p style="text-align: center; margin: 10px 0; font-style: italic;">A nicely framed image with a caption</p>
</div>

## Image Gallery with Lightbox

Click on any image below to view it in a lightbox:

<div class="gallery">
  <a href="https://picsum.photos/1200/800?random=10" data-fancybox="gallery" data-caption="Sample Image 1">
    <img src="https://picsum.photos/200/150?random=10" alt="Thumbnail 1">
  </a>
  <a href="https://picsum.photos/1200/800?random=11" data-fancybox="gallery" data-caption="Sample Image 2">
    <img src="https://picsum.photos/200/150?random=11" alt="Thumbnail 2">
  </a>
  <a href="https://picsum.photos/1200/800?random=12" data-fancybox="gallery" data-caption="Sample Image 3">
    <img src="https://picsum.photos/200/150?random=12" alt="Thumbnail 3">
  </a>
</div>

## CSS for the Gallery

Add this to your custom CSS file to style the image grid:

```css
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.image-item {
  border: 1px solid #eee;
  padding: 10px;
  border-radius: 8px;
  text-align: center;
}

.image-item img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 20px 0;
}

.gallery a {
  flex: 1 200px;
}

.gallery img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
  transition: transform 0.3s ease;
}

.gallery img:hover {
  transform: scale(1.05);
}
```

## Notes

- Always includescriptive altext for accessibility
- Optimize images for web to ensure fast loading times
- Consider using responsive images with `srcset` for different screen sizes
- Be mindful of copyright when using images from the web
