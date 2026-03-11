---
name: responsive-design
description: Create responsive web designs that work across all devices and screen sizes. Use when building mobile-first layouts, implementing breakpoints, or optimizing for different viewports. Handles CSS Grid, Flexbox, media queries, viewport units, and responsive images.
metadata:
  tags: responsive, mobile-first, CSS, Flexbox, Grid, media-query, viewport
  platforms: Claude, ChatGPT, Gemini
---


# Responsive Design


## When to use this skill

- **New website/app**: Layout design for combined mobile-desktop use
- **Legacy improvement**: Converting fixed layouts to responsive
- **Performance optimization**: Image optimization per device
- **Multiple screens**: Tablet, desktop, and large screen support

## Instructions

### Step 1: Mobile-First Approach

Design from small screens and progressively expand.

**Example**:
```css
/* Default: Mobile (320px~) */
.container {
  padding: 1rem;
  font-size: 14px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

/* Tablet (768px~) */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
    font-size: 16px;
  }

  .grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}

/* Desktop (1024px~) */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 3rem;
  }

  .grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }
}

/* Large screen (1440px~) */
@media (min-width: 1440px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

### Step 2: Flexbox/Grid Layout

Leverage modern CSS layout systems.

**Flexbox** (1-dimensional layout):
```css
/* Navigation bar */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

/* Card list */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .card-list {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .card {
    flex: 1 1 calc(50% - 0.5rem);  /* 2 columns */
  }
}

@media (min-width: 1024px) {
  .card {
    flex: 1 1 calc(33.333% - 0.667rem);  /* 3 columns */
  }
}
```

**CSS Grid** (2-dimensional layout):
```css
/* Dashboard layout */
.dashboard {
  display: grid;
  grid-template-areas:
    "header"
    "sidebar"
    "main"
    "footer";
  gap: 1rem;
}

@media (min-width: 768px) {
  .dashboard {
    grid-template-areas:
      "header header"
      "sidebar main"
      "footer footer";
    grid-template-columns: 250px 1fr;
  }
}

@media (min-width: 1024px) {
  .dashboard {
    grid-template-columns: 300px 1fr;
  }
}

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main { grid-area: main; }
.footer { grid-area: footer; }
```

### Step 3: Responsive Images

Provide images suited to the device.

**Using srcset**:
```html
<img
  src="image-800.jpg"
  srcset="
    image-400.jpg 400w,
    image-800.jpg 800w,
    image-1200.jpg 1200w,
    image-1600.jpg 1600w
  "
  sizes="
    (max-width: 600px) 100vw,
    (max-width: 900px) 50vw,
    33vw
  "
  alt="Responsive image"
/>
```

**picture element** (Art Direction):
```html
<picture>
  <!-- Mobile: portrait image -->
  <source media="(max-width: 767px)" srcset="portrait.jpg">

  <!-- Tablet: square image -->
  <source media="(max-width: 1023px)" srcset="square.jpg">

  <!-- Desktop: landscape image -->
  <img src="landscape.jpg" alt="Art direction example">
</picture>
```

**CSS background images**:
```css
.hero {
  background-image: url('hero-mobile.jpg');
}

@media (min-width: 768px) {
  .hero {
    background-image: url('hero-tablet.jpg');
  }
}

@media (min-width: 1024px) {
  .hero {
    background-image: url('hero-desktop.jpg');
  }
}

/* Or use image-set() */
.hero {
  background-image: image-set(
    url('hero-1x.jpg') 1x,
    url('hero-2x.jpg') 2x
  );
}
```

### Step 4: Responsive Typography

Adjust text size based on screen size.

**clamp() function** (fluid sizing):
```css
:root {
  /* min, preferred, max */
  --font-size-body: clamp(14px, 2.5vw, 18px);
  --font-size-h1: clamp(24px, 5vw, 48px);
  --font-size-h2: clamp(20px, 4vw, 36px);
}

body {
  font-size: var(--font-size-body);
}

h1 {
  font-size: var(--font-size-h1);
  line-height: 1.2;
}

h2 {
  font-size: var(--font-size-h2);
  line-height: 1.3;
}
```

**Media query approach**:
```css
body {
  font-size: 14px;
  line-height: 1.6;
}

@media (min-width: 768px) {
  body { font-size: 16px; }
}

@media (min-width: 1024px) {
  body { font-size: 18px; }
}
```

### Step 5: Container Queries (New Feature)

Apply styles based on parent container size.

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

.card {
  padding: 1rem;
}

.card h2 {
  font-size: 1.2rem;
}

/* When container is 400px or wider */
@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
    padding: 1.5rem;
  }

  .card h2 {
    font-size: 1.5rem;
  }
}

/* When container is 600px or wider */
@container card (min-width: 600px) {
  .card {
    grid-template-columns: 300px 1fr;
    padding: 2rem;
  }
}
```

## Output format

### Standard Breakpoints

```css
/* Mobile (default): 320px ~ 767px */
/* Tablet: 768px ~ 1023px */
/* Desktop: 1024px ~ 1439px */
/* Large: 1440px+ */

:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}

/* Usage example */
@media (min-width: 768px) { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop */ }
```

## Constraints

### Mandatory Rules (MUST)

1. **Viewport meta tag**: Must be included in HTML
   ```html
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   ```

2. **Mobile-First**: Mobile default, use min-width media queries
   - ✅ `@media (min-width: 768px)`
   - ❌ `@media (max-width: 767px)` (Desktop-first)

3. **Relative units**: Use rem, em, %, vw/vh instead of px
   - font-size: rem
   - padding/margin: rem or em
   - width: % or vw

### Prohibited (MUST NOT)

1. **Fixed width prohibited**: Avoid `width: 1200px`
   - Use `max-width: 1200px`

2. **Duplicate code**: Avoid repeating same styles across all breakpoints
   - Common styles as default, only differences in media queries

## Examples

### Example 1: Responsive Navigation

```tsx
function ResponsiveNav() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="navbar">
      {/* Logo */}
      <a href="/" className="logo">MyApp</a>

      {/* Hamburger button (mobile) */}
      <button
        className="menu-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle menu"
        aria-expanded={isOpen}
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      {/* Navigation links */}
      <ul className={`nav-links ${isOpen ? 'active' : ''}`}>
        <li><a href="/about">About</a></li>
        <li><a href="/services">Services</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>
    </nav>
  );
}
```

```css
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
}

/* Hamburger button (mobile only) */
.menu-toggle {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-links {
  display: none;
  position: absolute;
  top: 60px;
  left: 0;
  right: 0;
  background: white;
  flex-direction: column;
}

.nav-links.active {
  display: flex;
}

/* Tablet and above: hide hamburger, always show */
@media (min-width: 768px) {
  .menu-toggle {
    display: none;
  }

  .nav-links {
    display: flex;
    position: static;
    flex-direction: row;
    gap: 2rem;
  }
}
```

### Example 2: Responsive Grid Card

```tsx
function ProductGrid({ products }) {
  return (
    <div className="product-grid">
      {products.map(product => (
        <div key={product.id} className="product-card">
          <img src={product.image} alt={product.name} />
          <h3>{product.name}</h3>
          <p className="price">${product.price}</p>
          <button>Add to Cart</button>
        </div>
      ))}
    </div>
  );
}
```

```css
.product-grid {
  display: grid;
  grid-template-columns: 1fr;  /* Mobile: 1 column */
  gap: 1rem;
  padding: 1rem;
}

@media (min-width: 640px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr);  /* 2 columns */
  }
}

@media (min-width: 1024px) {
  .product-grid {
    grid-template-columns: repeat(3, 1fr);  /* 3 columns */
    gap: 1.5rem;
  }
}

@media (min-width: 1440px) {
  .product-grid {
    grid-template-columns: repeat(4, 1fr);  /* 4 columns */
    gap: 2rem;
  }
}

.product-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
}

.product-card img {
  width: 100%;
  height: auto;
  aspect-ratio: 1 / 1;
  object-fit: cover;
}
```

## Best practices

1. **Container queries first**: Use container queries instead of media queries when possible
2. **Flexbox vs Grid**: Flexbox for 1-dimensional, Grid for 2-dimensional
3. **Performance**: Image lazy loading, use WebP format
4. **Testing**: Chrome DevTools Device Mode, BrowserStack

## References

- [MDN Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [CSS Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
- [Container Queries](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Container_Queries)

## Metadata

### Version
- **Current Version**: 1.0.0
- **Last Updated**: 2025-01-01
- **Compatible Platforms**: Claude, ChatGPT, Gemini

### Related Skills
- [ui-component-patterns](../ui-component-patterns/SKILL.md): Responsive components
- [web-accessibility](../web-accessibility/SKILL.md): Consider alongside accessibility

### Tags
`#responsive` `#mobile-first` `#CSS` `#Flexbox` `#Grid` `#media-query` `#frontend`
