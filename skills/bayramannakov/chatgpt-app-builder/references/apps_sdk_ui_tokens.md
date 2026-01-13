# OpenAI Apps SDK UI Design Tokens

Complete reference for building widgets that match ChatGPT's native UI.

**Source**: https://openai.github.io/apps-sdk-ui/

---

## Gray Scale (0-1000)

| Token | Hex Value | Usage |
|-------|-----------|-------|
| gray-0 | #ffffff | Backgrounds (light mode) |
| gray-50 | #fafafa | Subtle backgrounds |
| gray-100 | #f5f5f5 | Card backgrounds, soft fills |
| gray-150 | #eeeeee | Hover states |
| gray-200 | #e5e5e5 | Borders (light mode) |
| gray-300 | #d4d4d4 | Disabled borders |
| gray-400 | #a3a3a3 | Tertiary text, placeholders |
| gray-500 | #737373 | Secondary text |
| gray-600 | #525252 | Icons |
| gray-700 | #404040 | Borders (dark mode) |
| gray-800 | #262626 | Card backgrounds (dark mode) |
| gray-900 | #171717 | Backgrounds (dark mode) |
| gray-1000 | #0a0a0a | Primary text (light mode) |

---

## Semantic Text Colors

| Token | Light Mode | Dark Mode |
|-------|------------|-----------|
| color-text | gray-1000 (#0a0a0a) | gray-0 (#ffffff) |
| color-text-secondary | gray-500 (#737373) | gray-400 (#a3a3a3) |
| color-text-tertiary | gray-400 (#a3a3a3) | gray-500 (#737373) |
| color-text-inverse | gray-0 (#ffffff) | gray-1000 (#0a0a0a) |

---

## Typography

### Font Family
```css
font-family: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
```

### Font Weights
| Token | Value | Usage |
|-------|-------|-------|
| font-weight-normal | 400 | Body text |
| font-weight-medium | 500 | Emphasis, labels |
| font-weight-semibold | 600 | Headings, buttons |
| font-weight-bold | 700 | Strong emphasis |

### Letter Spacing
| Token | Value | Usage |
|-------|-------|-------|
| font-tracking-normal | -0.01em | Body text |
| font-tracking-tight | -0.02em | Headings |

---

## Radius Scale

| Token | Value | Usage |
|-------|-------|-------|
| radius-2xs | 2px | Subtle rounding |
| radius-xs | 4px | Small elements, tags |
| radius-sm | 6px | Buttons, inputs |
| radius-md | 8px | Cards, modals |
| radius-lg | 10px | Large cards |
| radius-xl | 12px | Large containers |
| radius-2xl | 16px | Hero sections |
| radius-full | 9999px | Pills, avatars, circular elements |

---

## Spacing Scale

Uses 4px increments:

| Token | Value |
|-------|-------|
| space-1 | 4px |
| space-2 | 8px |
| space-3 | 12px |
| space-4 | 16px |
| space-5 | 20px |
| space-6 | 24px |
| space-8 | 32px |
| space-10 | 40px |
| space-12 | 48px |

---

## Transitions

| Token | Value | Usage |
|-------|-------|-------|
| transition-fast | 150ms ease | Hover states, toggles |
| transition-normal | 200ms ease | Page transitions, modals |

---

## Component Patterns

### Avatar
- **Colors**: primary, secondary, success, danger, info, discovery
- **Variants**:
  - `soft` - Light background, dark text (default for light mode)
  - `solid` - Dark background, light text
- **Default shape**: Fully rounded (radius-full)
- **Sizes**: sm (24px), md (32px), lg (40px), xl (48px)

### Badge
- **Colors**: secondary, success, warning, danger, info, discovery
- **Variants**: soft, solid, outline
- **Sizes**: sm, md, lg
- **Roundness**: Use `pill` prop for fully rounded badges

### LoadingDots
Three animated dots with staggered pulse animation:
- Dot size: 6px
- Gap: 4px
- Animation: 1.4s ease-in-out infinite
- Stagger delays: 0s, 0.2s, 0.4s

### Button
- **Variants**: primary, secondary, ghost, danger
- **Sizes**: sm, md, lg
- **Border radius**: radius-sm (6px)

---

## CSS Custom Properties Template

```css
:root {
  /* Gray Scale */
  --gray-0: #ffffff;
  --gray-50: #fafafa;
  --gray-100: #f5f5f5;
  --gray-150: #eeeeee;
  --gray-200: #e5e5e5;
  --gray-300: #d4d4d4;
  --gray-400: #a3a3a3;
  --gray-500: #737373;
  --gray-600: #525252;
  --gray-700: #404040;
  --gray-800: #262626;
  --gray-900: #171717;
  --gray-1000: #0a0a0a;

  /* Semantic Colors (Light Mode) */
  --color-text: var(--gray-1000);
  --color-text-secondary: var(--gray-500);
  --color-text-tertiary: var(--gray-400);
  --color-bg: var(--gray-0);
  --color-bg-soft: var(--gray-100);
  --color-border: var(--gray-200);

  /* Radius */
  --radius-2xs: 2px;
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 10px;
  --radius-xl: 12px;
  --radius-2xl: 16px;
  --radius-full: 9999px;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;

  /* Typography */
  --font-sans: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
}

/* Dark Mode Overrides */
.dark-mode {
  --color-text: var(--gray-0);
  --color-text-secondary: var(--gray-400);
  --color-text-tertiary: var(--gray-500);
  --color-bg: var(--gray-900);
  --color-bg-soft: var(--gray-800);
  --color-border: var(--gray-700);
}
```

---

## Dark Mode Detection

### In ChatGPT Widgets
```javascript
function updateTheme() {
  const theme = window.openai?.theme || 'light';
  document.body.classList.toggle('dark-mode', theme === 'dark');
}

// Initial setup
updateTheme();

// Listen for theme changes
window.addEventListener('openai:set_globals', updateTheme);
```

### Key Principle
Only override semantic color variables in dark mode, not component-specific colors. This ensures consistency and reduces maintenance.

---

## Related Resources

- [Apps SDK UI Storybook](https://openai.github.io/apps-sdk-ui/)
- [Widget Development Guide](./widget_development.md)
- [Widget CSS Template](./widget_css_template.md)
- [Widget UI Patterns](./widget_ui_patterns.md)
