# Typography Spec

## Type Scale

Fluid scale using `clamp()`:

| Token | Value | Use |
|-------|-------|-----|
| `--text-h1` | `clamp(1.875rem, 4vw + 1rem, 3rem)` | Page titles |
| `--text-h2` | `clamp(1.5rem, 3vw + 0.75rem, 2.25rem)` | Section headings |
| `--text-h3` | `clamp(1.25rem, 2vw + 0.5rem, 1.875rem)` | Subsection headings |
| `--text-h4` | `clamp(1.125rem, 1vw + 0.5rem, 1.5rem)` | Card headings |
| `--text-base` | `1rem` | Body text |
| `--text-sm` | `0.875rem` | Captions, labels |

## Rules

- **Max 4 font sizes** per page (prevents typography bloat)
- **Line height:** 1.5 for body, 1.25 for headings
- **`text-wrap: balance`** on headings (6 lines or fewer)
- **Font stack:** `system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`
- **Max content width:** 65ch for body text (optimal readability)

## Code

```css
:root {
  --text-h1: clamp(1.875rem, 4vw + 1rem, 3rem);
  --text-h2: clamp(1.5rem, 3vw + 0.75rem, 2.25rem);
  --text-h3: clamp(1.25rem, 2vw + 0.5rem, 1.875rem);
  --text-base: 1rem;
  --text-sm: 0.875rem;
  --leading-tight: 1.25;
  --leading-normal: 1.5;
}

h1, h2, h3 { text-wrap: balance; }
body { font-size: var(--text-base); line-height: var(--leading-normal); }
```
