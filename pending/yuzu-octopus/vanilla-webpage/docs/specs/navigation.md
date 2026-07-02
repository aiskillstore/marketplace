# Navigation Spec

## Navbar

```css
nav {
  display: flex;
  align-items: center;
  height: var(--nav-height);
  background: var(--nav-bg);
  border-bottom: 1px solid var(--nav-border);
  padding: 0 var(--space-4);
}

nav ul { display: flex; gap: var(--space-2); list-style: none; margin-left: auto; }
```

**Pattern:** `margin-left: auto` on `<ul>` pushes nav items to the right. Logo stays left.

## Mobile Hamburger

```html
<button aria-expanded="false" aria-label="Toggle menu">☰</button>
<nav aria-label="Main navigation" aria-hidden="true">...</nav>
```

- ARIA attributes updated via JavaScript
- Close on outside click
- `aria-hidden` synced with visibility

## Sticky Header

```css
header { position: sticky; top: 0; z-index: 100; }
```

## Breadcrumbs

```html
<nav aria-label="breadcrumb">
  <ol>
    <li><a href="#">Home</a></li>
    <li><span aria-current="page">Current</span></li>
  </ol>
</nav>
```

## Rules

- Use `<nav>` with `aria-label` for all navigation
- Mobile: hide links behind hamburger at ≤768px
- Sticky headers: add `backdrop-filter: blur()` for frosted glass effect
- Breadcrumbs: separator via `::after` pseudo-element
