# Layout System Spec

## Responsive Grid (no media queries)

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-6);
}
```

## Dashboard (grid-template-areas)

```css
.dashboard {
  display: grid;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: 250px 1fr;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}
```

## Sidebar Layout (flexbox)

```css
.layout { display: flex; min-height: 100vh; }
.sidebar { width: 250px; flex-shrink: 0; }
.main { flex: 1; }
```

## Floating Footer Fix

```css
body {
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}
```

## Masonry (CSS columns)

```css
.masonry {
  columns: 3;
  column-gap: 1rem;
}
.masonry-item {
  break-inside: avoid;
  margin-bottom: 1rem;
}
```

## Rules

- Use `repeat(auto-fit, minmax())` for card grids — no media queries needed
- Use `grid-template-areas` for named regions in app layouts
- Use flexbox for one-dimensional layouts (navbars, sidebars)
- Use CSS columns for masonry (Pinterest-style)
- Container queries for component-level responsive
