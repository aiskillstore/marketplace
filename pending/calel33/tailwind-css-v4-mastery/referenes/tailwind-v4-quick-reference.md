# Tailwind CSS v4: Quick Reference Card

## Installation (Pick One)
```bash
npm install -D tailwindcss @tailwindcss/cli          # CLI
npm install -D @tailwindcss/vite                     # Vite (fastest)
npm install -D tailwindcss @tailwindcss/postcss      # PostCSS
```

## CSS-First Configuration Template
```css
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.6 0.2 243);
  --color-secondary: oklch(0.7 0.15 28);
  --font-display: "Satoshi", "sans-serif";
  --breakpoint-3xl: 120rem;
  --spacing-xs: 0.5rem;
  --ease-fluid: cubic-bezier(0.3, 0, 0, 1);
}
```

## v3 → v4 Utility Renames
| v3 | v4 |
|----|-----|
| `.shadow` | `.shadow-sm` |
| `.shadow-sm` | `.shadow-xs` |
| `.rounded` | `.rounded-sm` |
| `.rounded-sm` | `.rounded-xs` |
| `.outline-none` | `.outline-hidden` |
| `.ring` | `.ring-1` (default) |
| `.bg-opacity-50` | `.bg-black/50` |
| `.overflow-ellipsis` | `.text-ellipsis` |

## Old vs New Syntax
```diff
/* v3 */
- @tailwind base;
- @tailwind components;
- @tailwind utilities;

/* v4 */
+ @import "tailwindcss";
+ @theme { --color-name: value; }
```

## Configuration Migration
```javascript
/* ❌ v3: JavaScript config (REMOVED) */
// module.exports = { theme: { colors: {...} } }

/* ✅ v4: CSS configuration (NEW) */
// @theme { --color-primary: #3b82f6; }
```

## Multi-Theme Setup
```css
@layer base {
  [data-theme="ocean"] {
    --color-primary: oklch(0.55 0.18 260);
  }
  
  [data-theme="sunset"] {
    --color-primary: oklch(0.60 0.22 25);
  }
}
```

## Component Extraction
```css
@layer components {
  .btn-primary {
    @apply px-4 py-2 rounded-sm bg-blue-600 text-white
           hover:bg-blue-700 transition-colors;
  }
}
```

## Browser Requirements
- ✅ Safari 16.4+
- ✅ Chrome 111+
- ✅ Firefox 128+
- ❌ IE11 (stick with v3.4 if needed)

## Breaking Changes Checklist
- [ ] Default border color: `currentColor` → `#e5e7eb`
- [ ] Default ring width: `3px` → `1px`
- [ ] `tailwind.config.js` no longer supported
- [ ] Opacity utilities removed (use slash syntax)
- [ ] PostCSS plugin moved to `@tailwindcss/postcss`
- [ ] Vite plugin now at `@tailwindcss/vite`

## Performance Gains
- **Build time:** 10-100x faster
- **Hot reload:** 15-30x faster
- **Memory:** Significantly lower
- **CSS size:** 15-20% leaner

## Common Gotchas
1. **No `tailwind.config.js`**: Must use `@theme {}` in CSS
2. **CSS variable naming**: Requires `--` prefix (`.--color-name: value`)
3. **Border defaults changed**: Use `.border-current` for old behavior
4. **Ring defaults changed**: Use `.ring-3` for old 3px behavior
5. **Modern CSS only**: Uses `@property`, `color-mix()`, nesting

## Vite Config Example
```typescript
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()]
});
```

## PostCSS Config Example
```javascript
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  }
}
```

## Dark Mode (Automatic)
```html
<!-- Works by default -->
<div class="bg-white dark:bg-gray-950">Content</div>

<!-- Or use data attribute -->
<html data-theme="dark">
```

## Key Mental Model Shift
```
v3: JavaScript Object → Tailwind Parser → CSS
v4: CSS @theme Block → Oxide Engine (Rust) → CSS ⚡
```

## Most Used @layer Directives
```css
@layer base { }      /* Global styles, resets */
@layer components { }  /* Custom component classes */
@layer utilities { }   /* Custom utility classes */
```

## Color Space (v4 Best Practice)
```css
@theme {
  /* Use modern OKLch color space */
  --color-primary-500: oklch(0.7 0.2 243);
  
  /* Or HSL with CSS variables */
  --color-primary-500: hsl(var(--primary-h) var(--primary-s) var(--primary-l));
}
```

## Quick Migration Path
1. Update import: `@import "tailwindcss"`
2. Convert config to `@theme { --var: value; }`
3. Rename utilities (shadow, rounded, outline, ring)
4. Replace opacity utils with slash syntax
5. Test responsive and dark modes
6. Done! 🚀

---

**Resources:**
- Docs: https://tailwindcss.com/docs
- GitHub: https://github.com/tailwindlabs/tailwindcss
- Playground: https://play.tailwindcss.com
