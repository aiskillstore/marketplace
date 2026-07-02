# Tutorial 2: Layout Masterclass

Master CSS Grid, Flexbox, and Container Queries.

## Part 1: Responsive Grid (no media queries)

```html
<div class="grid">
  <div class="card">1</div>
  <div class="card">2</div>
  <div class="card">3</div>
  <div class="card">4</div>
</div>
```

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
```

**Key concept:** `auto-fit` fits as many 250px+ columns as possible. Remaining space is distributed equally via `1fr`.

## Part 2: Dashboard with grid-template-areas

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

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main { grid-area: main; }
.footer { grid-area: footer; }
```

**Key concept:** Named areas make layout readable. Responsive by redefining areas in media queries.

## Part 3: Flexbox Patterns

### Navbar with margin:auto isolation
```css
nav ul { display: flex; gap: 1rem; }
nav ul li:first-child { margin-right: auto; } /* Logo stays left */
```

### 3-card layout with aligned buttons
```css
.card { display: flex; flex-direction: column; }
.card-content { flex: 1; } /* Takes remaining space */
.card button { margin-top: auto; } /* Pushes to bottom */
```

### Floating footer fix
```css
body { display: grid; grid-template-rows: auto 1fr auto; min-height: 100vh; }
```

## Part 4: Container Queries

```css
.card-wrapper { container-type: inline-size; }

@container (min-width: 400px) {
  .card { display: grid; grid-template-columns: 1fr 2fr; }
}
```

**Key concept:** Components respond to their own container size, not the viewport. Useful for cards in a grid that may be different widths.

## Part 5: Holy Grail Layout

```css
body { display: grid; grid-template-rows: auto 1fr auto; min-height: 100vh; }
.content { display: flex; }
.sidebar { width: 200px; flex-shrink: 0; }
.main { flex: 1; }

@media (max-width: 768px) {
  .content { flex-direction: column; }
  .sidebar { width: 100%; }
}
```
