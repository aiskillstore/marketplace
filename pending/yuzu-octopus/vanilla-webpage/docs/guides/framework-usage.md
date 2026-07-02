# Framework Usage Guide

## When to use a classless CSS framework

Use when you want a polished look without writing CSS, and the project is:
- A prototype, demo, or internal tool
- Content-heavy (docs, blog, landing page)
- Time-constrained

## How to add one

```html
<!-- In <head> -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.classless.min.css">
```

That's it. Write semantic HTML and the framework styles it automatically.

## Choosing a framework

| Need | Best choice |
|------|-------------|
| Most complete | Pico CSS (~14KB) |
| Smallest | EdibleCSS (~3.8KB) or Acorn (~3.8KB) |
| Fastest loading | The New CSS (~5KB) |
| shadcn aesthetics | slick-css (~5.7KB) |
| 20+ themes | µCSS (~19KB) |

## Customizing

All frameworks use CSS custom properties. Override in your own CSS:

```css
:root {
  --pico-primary: #667eea;
  --pico-font-family: system-ui, sans-serif;
}
```

## When NOT to use a framework

- When you need full control over every pixel
- When the design is highly custom (not standard page layout)
- When you're building a complex app with many component states
- When the framework's aesthetic doesn't match your brand

## Adding HTMX for interactivity

```html
<script src="https://unpkg.com/htmx.org@2.0.4"></script>

<!-- Example: load content without page reload -->
<button hx-get="/api/data" hx-target="#result">Load Data</button>
<div id="result"></div>
```

HTMX (~14KB) adds AJAX, CSS transitions, and SSE support to HTML. Use it when vanilla JS event handling becomes tedious for server-driven UIs.
