# Colors Spec

## Three-Layer Token System

### Layer 1: Base (raw values)

```css
:root {
  --lch-blue: 54% 0.23 255;
  --lch-blue-light: 95% 0.03 255;
  --lch-blue-dark: 80% 0.08 255;
  --lch-gray: 96% 0.005 96;
  --lch-green: 62% 0.19 145;
  --lch-red: 62% 0.22 25;
}
```

### Layer 2: Semantic (meaningful names)

```css
:root {
  --color-primary: oklch(var(--lch-blue));
  --color-bg: #ffffff;
  --color-text: #1a1a1a;
  --color-border: oklch(var(--lch-gray));
  --color-success: oklch(var(--lch-green));
  --color-error: oklch(var(--lch-red));
}

[data-theme="dark"] {
  --color-bg: #121212;
  --color-text: #e0e0e0;
}
```

### Layer 3: Component (usage-specific)

```css
:root {
  --btn-bg: var(--color-primary);
  --card-bg: var(--color-bg);
  --input-border: var(--color-border);
}
```

## Rules

- Each layer references the one below via `var()`, never raw values
- Dark mode overrides only Layer 2 (semantic)
- Use OKLCH for colors that need variants (hover, active, disabled)
- Never use pure black (#000) or pure white (#fff) for large surfaces

## Contrast Requirements (WCAG AA)

- Normal text: 4.5:1
- Large text (18px+): 3:1
- UI components: 3:1
