# Cards Spec

## Tokens

```css
:root {
  --card-bg: var(--color-bg);
  --card-border: var(--color-border);
  --card-radius: var(--radius-lg);
  --card-shadow: var(--shadow-md);
  --card-padding: var(--space-6);
}
```

## Code

```css
.card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  padding: var(--card-padding);
  overflow: hidden;
}

/* 3-card layout: align buttons at bottom */
.card { display: flex; flex-direction: column; }
.card-content { flex: 1; }
.card button { margin-top: auto; }
```

## Variants

| Variant | Use |
|---------|-----|
| Profile card | User/team pages |
| Product card | E-commerce, catalogs |
| Article card | Blog feeds, news |
| Pricing card | Pricing pages |

## Container queries (component-level responsive)

```css
.card-wrapper { container-type: inline-size; }
@container (min-width: 400px) {
  .card { display: grid; grid-template-columns: 1fr 2fr; }
}
```

## Rules

- Max width: 350-400px for single-column cards
- Use `margin-top: auto` on buttons to align at bottom when content varies
- Box shadow on rest, enhanced on hover
- Border radius consistent with design tokens
