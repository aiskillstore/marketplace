# Spacing Spec

## Scale (4px base)

| Token | Value | Pixels |
|-------|-------|--------|
| `--space-1` | 0.25rem | 4px |
| `--space-2` | 0.5rem | 8px |
| `--space-3` | 0.75rem | 12px |
| `--space-4` | 1rem | 16px |
| `--space-5` | 1.25rem | 20px |
| `--space-6` | 1.5rem | 24px |
| `--space-8` | 2rem | 32px |
| `--space-10` | 2.5rem | 40px |
| `--space-12` | 3rem | 48px |
| `--space-16` | 4rem | 64px |
| `--space-20` | 5rem | 80px |
| `--space-24` | 6rem | 96px |

## Semantic Aliases

```css
:root {
  --space-xs: var(--space-1);
  --space-sm: var(--space-2);
  --space-md: var(--space-4);
  --space-lg: var(--space-8);
  --space-xl: var(--space-12);
  --space-2xl: var(--space-16);
}
```

## Rules

- Use only values from this scale — no ad-hoc values
- `gap` property for spacing between siblings (Flexbox/Grid)
- `margin` for spacing between distinct sections
- `padding` for internal spacing within components
- Consistent vertical rhythm: all margins are multiples of the base unit
