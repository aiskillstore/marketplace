# Dashboard Layout

Named layout regions with `grid-template-areas`.

## Technique
`grid-template-areas` assigns semantic names to grid cells, making layout readable and maintainable.

## When to use
- Admin dashboards, app layouts
- Any page with distinct header/sidebar/main/footer regions
- When you want layout to be readable in CSS

## Key CSS
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
