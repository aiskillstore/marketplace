# Responsive Design Guide

## Fluid typography

```css
h1 { font-size: clamp(1.5rem, 4vw + 1rem, 3rem); }
```

Scales smoothly between min and max based on viewport width.

## Fluid spacing

```css
.container { padding: clamp(1rem, 3vw, 3rem); }
```

## Responsive grid (no media queries)

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
```

## Container queries (component-level responsive)

```css
.card-wrapper { container-type: inline-size; }
@container (min-width: 400px) {
  .card { display: grid; grid-template-columns: 1fr 2fr; }
}
```

## Media queries (when you need them)

```css
/* Mobile-first: base styles are for mobile */
.sidebar { display: none; }

/* Tablet and up */
@media (min-width: 768px) {
  .sidebar { display: block; }
}
```

## Responsive images

```html
<picture>
  <source media="(min-width: 800px)" srcset="large.jpg">
  <source media="(min-width: 400px)" srcset="medium.jpg">
  <img src="small.jpg" alt="Description">
</picture>
```

## Viewport meta tag (always include)

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```
