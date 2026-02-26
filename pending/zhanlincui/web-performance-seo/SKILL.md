---
name: web-performance-seo
description: Fix PageSpeed Insights/Lighthouse accessibility "!" errors caused by contrast audit failures (CSS filters, OKLCH/OKLAB, low opacity, gradient text, image backgrounds). Use for accessibility-driven SEO/performance debugging and remediation.
---

# Web Performance SEO: Accessibility Contrast Error Fix

## When to use
- PSI/Lighthouse accessibility shows "!" or error instead of a numeric score
- color-contrast audit errors or getImageData failures
- Need to improve accessibility signals that impact SEO

## Workflow
1. Reproduce
   - Run Lighthouse or PSI; capture failing audit names.
2. Scan code for common triggers
   - CSS filters/backdrop blur, mix-blend-mode
   - OKLCH/OKLAB colors
   - Low opacity backgrounds (< 0.4)
   - Gradient text with color: transparent
   - Text over images without opaque overlays
3. Fix in priority order
   - Remove filters/blend modes
   - Convert OKLCH/OKLAB to HSL/RGB
   - Raise opacity thresholds
   - Add solid-color fallback for gradient text
   - Add overlay behind text on images
4. Verify locally with Lighthouse/axe
5. Verify in PSI after deployment

## Fast scan commands
```bash
rg -n "backdrop-blur|filter:|mix-blend-mode" .
rg -n "oklch|oklab" .
rg -n "/10|/20|/30|opacity-25|opacity-0" .
rg -n "background-clip.*text|color.*transparent" .
```

## Fix patterns
### Remove filters (critical)
```tsx
// Before
<div className="bg-card/50 backdrop-blur-sm">...</div>
// After
<div className="bg-card/80">...</div>
```

### Convert OKLCH/OKLAB to HSL/RGB
```css
/* Before */
:root { --primary: oklch(0.55 0.22 264); }
/* After */
:root { --primary: hsl(250, 60%, 50%); }
```

### Raise opacity thresholds
- Backgrounds >= 0.4 (prefer >= 0.6)
- Replace /10 -> /40, /20 -> /40, /30 -> /60

### Gradient text fallback
```css
.title { color: #111111; }
@media (prefers-contrast: no-preference) {
  .title.with-gradient {
    background: linear-gradient(90deg, #0ea5e9, #6366f1);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
}
@media (forced-colors: active) {
  .title.with-gradient { background: none; color: CanvasText; }
}
```

### Overlay for text on images
```tsx
<div className="relative">
  <img src="/hero.jpg" alt="Hero" />
  <div className="absolute inset-0 bg-black/60"></div>
  <h1 className="relative text-white">Title</h1>
</div>
```

## Acceptance criteria
- Accessibility score is numeric (not "!")
- color-contrast audit passes or lists actionable items
- Contrast ratios >= 4.5:1 for normal text, >= 3:1 for large text

## Notes
- "!" indicates audit failure, not a low score.
- Always test locally before waiting for PSI updates.
