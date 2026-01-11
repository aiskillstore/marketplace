# Tailwind CSS V4: Performance Tuning

## Performance Baseline

### v3 vs v4 Metrics

| Metric | v3 | v4 | Improvement |
|--------|-----|-----|------------|
| Initial Build | 5-10s | 100-500ms | **10-100x** |
| HMR (Hot Reload) | ~3s | 50-200ms | **15-30x** |
| Memory Usage | ~200MB | ~30MB | **6-7x** |
| CSS Output Size | Baseline | -15-20% | **Leaner** |

The Oxide engine is a game-changer for build performance.

---

## Plugin Selection for Maximum Speed

### Best: Vite Plugin (@tailwindcss/vite)
```typescript
// vite.config.ts
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()]
});
```

**Performance:** Fastest possible. Native Vite integration.  
**Best For:** React, Vue, Svelte, any Vite-based project

**Metrics:**
- Build: ~200-300ms
- HMR: ~50-100ms

---

### Good: PostCSS Plugin (@tailwindcss/postcss)
```javascript
// postcss.config.js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  }
}
```

**Performance:** Fast, but slower than Vite plugin.  
**Best For:** Webpack, NextJS, CRA, traditional setups

**Metrics:**
- Build: ~300-500ms
- HMR: ~100-200ms

---

### Adequate: CLI (@tailwindcss/cli)
```bash
npx @tailwindcss/cli -i styles.css -o dist/styles.css --watch
```

**Performance:** Acceptable for simple projects.  
**Best For:** Static sites, server-rendered apps, non-bundled setups

**Metrics:**
- Build: ~100-200ms per run
- Watch mode: ~50-100ms per rebuild

---

## Configuration Optimization

### Pattern 1: Minimize @theme Block

```css
/* ❌ Inefficient: Many redundant variables */
@theme {
  --color-primary-50: ...;
  --color-primary-100: ...;
  /* ... 100 lines */
}

/* ✅ Efficient: Only override defaults when needed */
@theme {
  --color-primary-500: oklch(0.6 0.2 243);
  /* Oxide automatically generates shade variants */
}
```

**Why:** Oxide pre-generates standard scales. Only override what you change.

---

### Pattern 2: Use CSS Variable References

```css
/* ❌ Computed every time */
@theme {
  --color-primary-100: oklch(0.97 0.01 243);
  --color-primary-200: oklch(0.94 0.04 243);
  --color-primary-300: oklch(0.89 0.10 243);
  /* ... repetitive */
}

/* ✅ Computed once, reused */
:root {
  --primary-hue: 243;
  --primary-sat: 0.2;
}

@theme {
  --color-primary-500: oklch(0.7 var(--primary-sat) var(--primary-hue));
}
```

**Why:** Variables are resolved once, not recalculated per utility.

---

### Pattern 3: Limit Breakpoint Count

```css
/* ❌ Too many breakpoints */
@theme {
  --breakpoint-xs: 20rem;
  --breakpoint-sm: 30rem;
  --breakpoint-md: 40rem;
  --breakpoint-lg: 50rem;
  --breakpoint-xl: 60rem;
  --breakpoint-2xl: 70rem;
  --breakpoint-3xl: 80rem;
  /* Each generates 2-3x CSS output */
}

/* ✅ Tailored to your needs */
@theme {
  --breakpoint-sm: 36rem;
  --breakpoint-md: 48rem;
  --breakpoint-lg: 62rem;
  --breakpoint-xl: 80rem;
}
```

**Why:** Each breakpoint multiplies CSS output. Only define what you use.

---

## Oxide Engine Configuration

### Lightning CSS Integration (PostCSS)

```javascript
// postcss.config.js
export default {
  plugins: {
    "@tailwindcss/postcss": {
      lightningcss: true,  // Enable Lightning CSS
    },
  }
}
```

**Performance Gain:** 15-20% faster CSS output processing

---

### Vite Plugin Optimization

```typescript
// vite.config.ts
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    tailwindcss({
      // Automatic optimizations (enabled by default)
      // - Oxide engine
      // - Incremental builds
      // - Efficient HMR
    })
  ]
});
```

No additional configuration needed. Vite plugin auto-optimizes.

---

## Build-Level Optimizations

### 1. Enable Source Maps Only in Dev

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    sourcemap: false, // Disable in production
  },
  define: {
    'process.env.NODE_ENV': '"production"',
  },
});
```

**Benefit:** Faster production builds, smaller artifacts.

---

### 2. CSS Minification (Automatic)

Oxide automatically minifies CSS output. No additional configuration needed.

```
Original: 15.2 KB
Minified: 12.4 KB (18% reduction)
```

---

### 3. Tree-Shaking Unused Utilities

Tailwind V4 automatically removes unused utilities via content analysis.

```css
/* @import "tailwindcss" scans your files for class usage */
@import "tailwindcss";

/* Classes like .shadow-2xl are only included if used */
```

**Configuration:** No setup needed. Works automatically.

---

### 4. CSS-in-JS Optimization (Framework-Specific)

#### Next.js

```javascript
// next.config.js
export default {
  experimental: {
    optimizePackageImports: ["@tailwindcss/vite"],
  },
};
```

#### Vite + React

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'tailwindcss': ['@tailwindcss/vite'],
        },
      },
    },
  },
});
```

---

## Measurement & Profiling

### Measure Build Time

```bash
# Before optimization
time npm run build
# real 2.345s

# After optimization
time npm run build
# real 0.456s
# Improvement: ~5x faster
```

---

### Profile Oxide Engine

```bash
# Enable debug output
DEBUG=tailwindcss:* npm run build

# Output shows:
# ✓ scanning files: 45ms
# ✓ generating styles: 120ms
# ✓ writing output: 35ms
# Total: 200ms
```

---

### Monitor File Size

```bash
# Check CSS size
du -h dist/styles.css

# Compare v3 vs v4
# v3: 18.2 KB
# v4: 14.8 KB
# Savings: 3.4 KB (-18.7%)
```

---

## Common Performance Pitfalls

### ❌ Pitfall 1: Defining Unused Theme Variables

```css
/* ❌ Slow: Defines 1000+ variables even if unused */
@theme {
  --color-red-50: ...;
  --color-red-100: ...;
  /* ... through red-900 */
  --color-blue-50: ...;
  /* ... repeat for all colors */
}

/* ✅ Fast: Only define what you need */
@theme {
  --color-primary-500: oklch(...);
  --color-secondary-500: oklch(...);
}
```

---

### ❌ Pitfall 2: Excessive Customization

```css
/* ❌ Slow: Overriding nearly everything */
@theme {
  --color-*: ...; /* 50+ lines */
  --spacing-*: ...; /* 30+ lines */
  --text-*: ...; /* 20+ lines */
  /* ... exhaustive config */
}

/* ✅ Fast: Override only what differs from defaults */
@theme {
  --color-primary: oklch(0.6 0.2 243);
  --font-display: "Custom", sans-serif;
}
```

---

### ❌ Pitfall 3: Multiple @theme Blocks

```css
/* ❌ Slower: Multiple parsing passes */
@theme {
  --color-primary: ...;
}

@layer base { ... }

@theme {
  --color-secondary: ...;
}

/* ✅ Faster: Single @theme block */
@theme {
  --color-primary: ...;
  --color-secondary: ...;
}
```

---

## Performance Checklist

- [ ] Using `@tailwindcss/vite` or `@tailwindcss/postcss`?
- [ ] @theme block contains only necessary overrides?
- [ ] No unused breakpoints defined?
- [ ] CSS minification enabled in production?
- [ ] Source maps disabled for production?
- [ ] Measured build time baseline?
- [ ] HMR time under 200ms?
- [ ] Final CSS size reasonable (<50 KB)?
- [ ] Oxide engine logs show good timing?

---

## Expected Performance After V4 Migration

| Metric | After Migration | Target |
|--------|-----|--------|
| Build Time | 100-500ms | 200-400ms |
| HMR | 50-200ms | 100-150ms |
| CSS Size | -15-20% reduction | -20% or better |
| Memory Usage | 30-50MB | <100MB |

If you're not seeing these improvements, check:
1. Using correct plugin for your build tool?
2. Production build vs dev build?
3. Baseline measurement accurate?
4. Oxide engine enabled?
5. Unnecessary content scans?

