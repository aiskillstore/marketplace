# Responsive Grid

Auto-fit grid that adapts without media queries.

## Technique
`repeat(auto-fit, minmax(280px, 1fr))` — browser fits as many 280px+ columns as possible, remaining space distributed equally.

## When to use
- Card grids, photo galleries, product listings
- Any layout with repeated items of similar width
- When you want responsive behavior without writing media queries

## Key CSS
```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
```

## Variations
- Change `280px` to adjust minimum card width
- Use `auto-fill` instead of `auto-fit` to keep empty tracks
- Add `justify-items: center` to center cards within their cells
