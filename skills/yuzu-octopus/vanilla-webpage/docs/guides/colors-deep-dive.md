# Colors Deep Dive

## OKLCH (recommended)

```css
:root {
  --blue: oklch(54% 0.23 255);
  --blue-light: oklch(95% 0.03 255);
  --blue-dark: oklch(80% 0.08 255);
}
```

L = lightness (0-100%), C = chroma (saturation), H = hue (angle). Perceptually uniform — equal changes look equal.

## Relative colors

```css
:root { --primary: oklch(54% 0.23 255); }
.btn-hover { background: oklch(from var(--primary) calc(l - 10%) c h); }
.btn-active { background: oklch(from var(--primary) calc(l - 20%) c h); }
```

Derive hover/active/disabled states from one base color.

## currentColor

```css
.icon { color: blue; }
.icon:hover { filter: drop-shadow(0 0 4px currentColor); }
.border { border: 2px solid currentColor; }
```

References the element's own `color` value. Great for icons and borders.

## color-mix()

```css
.btn-hover { background: color-mix(in oklch, var(--primary), black 15%); }
.subtle { background: color-mix(in oklch, var(--bg), var(--text) 5%); }
```

Mix two colors programmatically. No need to predefine every variant.

## Three-layer token system

1. **Base:** Raw values (`--lch-blue: 54% 0.23 255`)
2. **Semantic:** Meaningful names (`--color-primary: oklch(var(--lch-blue))`)
3. **Component:** Usage-specific (`--btn-bg: var(--color-primary)`)

Each layer references the one below via `var()`, never raw values directly.
