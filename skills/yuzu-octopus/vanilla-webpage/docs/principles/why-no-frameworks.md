# Why No Frameworks

## The Evidence

### 37signals (Campfire, Writebook, Fizzy)

37signals built three production products with vanilla CSS, no build step, no preprocessors:
- **Campfire** (2024): Vanilla CSS with modern features — nesting, `:has()`, `:is()`, `:where()`, oklch colors, View Transitions
- **Writebook** (2024): Same approach, added modern CSS capabilities
- **Fizzy** (2025): Full modern CSS — `@layer`, `color-mix()`, complex `:has()` chains

All three ship without a build step. They use CSS custom properties for theming, `@layer` for specificity, and native CSS nesting.

### Performance

- **No framework JS:** Average React page loads 400KB+ of JavaScript. A vanilla page loads 0KB.
- **No hydration delay:** Framework pages must hydrate before becoming interactive. Vanilla pages are interactive immediately.
- **Smaller payloads:** Pico CSS (14KB) vs Bootstrap (23KB gzipped) vs Tailwind (10-30KB purged)

### Maintenance

- **No dependency updates:** Frameworks release breaking changes. Vanilla CSS doesn't.
- **No version conflicts:** No "this package requires React 18 but you have 17."
- **No build failures:** No Webpack config, no Vite plugins, no PostCSS setup to break.

### When Frameworks Make Sense

- **Large teams (10+)** who need enforced conventions
- **Complex state management** across many interdependent components
- **Rich component libraries** with accessibility built in (e.g., Radix, React Aria)
- **SSR/SSG requirements** that need a framework's rendering pipeline

But start with vanilla. Add complexity only when the pain is real.
