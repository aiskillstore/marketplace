# Dark Mode Guide

## Two approaches

### 1. light-dark() (modern CSS)

```css
:root { color-scheme: light dark; }
body {
  background: light-dark(#ffffff, #121212);
  color: light-dark(#1a1a1a, #e0e0e0);
}
```

Single property, auto-switches with system preference. No JavaScript needed for the CSS side.

### 2. data-theme attribute (custom toggle)

```css
:root { --bg: #ffffff; --text: #1a1a1a; }
[data-theme="dark"] { --bg: #121212; --text: #e0e0e0; }
body { background: var(--bg); color: var(--text); }
```

```javascript
// Toggle
document.documentElement.toggleAttribute('data-theme', 'dark');

// Persist
localStorage.setItem('theme', isDark ? 'dark' : 'light');

// Load on startup
const saved = localStorage.getItem('theme');
if (saved) document.documentElement.setAttribute('data-theme', saved);
```

### 3. Respect system preference on first visit

```javascript
const preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
const saved = localStorage.getItem('theme') || preferred;
document.documentElement.setAttribute('data-theme', saved);
```

## Best practices

- Use CSS custom properties for all theme-dependent colors
- Never use pure black (#000) for dark mode backgrounds — use #121212 or similar
- Reduce color saturation in dark mode
- Test both themes before shipping
