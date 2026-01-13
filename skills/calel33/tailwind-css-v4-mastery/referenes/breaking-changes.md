# Tailwind CSS V4: Breaking Changes Reference

## Utility Renames

### Shadows
| v3 | v4 | Notes |
|-----|-----|-------|
| `.shadow` | `.shadow-sm` | Default shadow reduced |
| `.shadow-sm` | `.shadow-xs` | Small shadow now extra-small |
| `.shadow-md` | `.shadow` | Medium is now default |
| `.shadow-lg` | `.shadow-lg` | Large shadow unchanged |
| `.shadow-xl` | `.shadow-xl` | XL shadow unchanged |
| `.shadow-2xl` | `.shadow-2xl` | 2XL shadow unchanged |

### Rounded Corners
| v3 | v4 | Notes |
|-----|-----|-------|
| `.rounded` | `.rounded-sm` | Default reduced to small |
| `.rounded-sm` | `.rounded-xs` | Small reduced to extra-small |
| `.rounded-md` | `.rounded` | Medium is now default |
| `.rounded-lg` | `.rounded-lg` | Large unchanged |
| `.rounded-full` | `.rounded-full` | Full unchanged |

### Outlines
| v3 | v4 | Notes |
|-----|-----|-------|
| `.outline-none` | `.outline-hidden` | Different semantics |
| `.outline` | `.outline-1` | Explicitly specify width |
| `.outline-0` | `.outline-hidden` | None becomes hidden |

### Rings
| v3 | v4 | Notes |
|-----|-----|-------|
| `.ring` | `.ring-1` | Default width changed 3px → 1px |
| `.ring-inset` | `.ring-inset` | Unchanged |

### Typography
| v3 | v4 | Notes |
|-----|-----|-------|
| `.overflow-ellipsis` | `.text-ellipsis` | More semantic |
| `.overflow-clip` | (unchanged) | Still `.overflow-clip` |

### Flexbox
| v3 | v4 | Notes |
|-----|-----|-------|
| `.flex-grow-*` | `.grow-*` | Shorter alias |
| `.flex-shrink-*` | `.shrink-*` | Shorter alias |
| `.flex-grow` | `.grow` | Same as grow-1 |
| `.flex-shrink` | `.shrink` | Same as shrink-1 |

---

## Removed Utilities

### Opacity Utilities (Complete Removal)
```javascript
/* REMOVED — Use CSS color modifiers instead */
.bg-opacity-*
.text-opacity-*
.border-opacity-*
.divide-opacity-*
.placeholder-opacity-*
.ring-opacity-*
.shadow-opacity-*

/* NEW SYNTAX — CSS color modifiers */
.bg-black/50        /* 50% opacity */
.text-white/75      /* 75% opacity */
.border-gray-400/30 /* 30% opacity */
```

### Removed Classes
| Removed | Reason | Replacement |
|---------|--------|-------------|
| `.bg-opacity-*` | CSS color modifiers | `.bg-color/opacity` |
| `.text-opacity-*` | CSS color modifiers | `.text-color/opacity` |
| `.border-opacity-*` | CSS color modifiers | `.border-color/opacity` |
| `.blur-0` | Redundant | (no equivalent needed) |
| `.saturate-0` | Rarely used | Custom CSS if needed |

---

## Default Value Changes

### Border Color
```css
/* v3 */
.border { border-color: currentColor; }

/* v4 */
.border { border-color: rgb(229 231 235); /* gray-200 */ }

/* Migrate old behavior */
.border-current { border-color: currentColor; }
```

### Ring Width
```css
/* v3 */
.ring { --tw-ring-width: 3px; }

/* v4 */
.ring { --tw-ring-width: 1px; }

/* Migrate old behavior */
.ring-3 { --tw-ring-width: 3px; }
```

### Default Colors
| Utility | v3 | v4 | Notes |
|---------|-----|-----|-------|
| `.border` | `currentColor` | `gray-200` | Breaking change! |
| `.divide` | `currentColor` | `gray-200` | Breaking change! |
| `.ring` | `blue-500` | `blue-500` | Unchanged |
| `.outline` | `currentColor` | `currentColor` | Unchanged |

---

## Package Structure Changes

### Moved/Renamed Packages
| v3 | v4 | Status |
|-----|-----|--------|
| `tailwindcss` (main) | `tailwindcss` | Unchanged |
| Built-in PostCSS | `@tailwindcss/postcss` | ⚠️ Moved |
| (No Vite plugin) | `@tailwindcss/vite` | ✅ New |
| Built-in CLI | `@tailwindcss/cli` | ⚠️ Moved |

### Installation Changes
```javascript
/* v3 */
npm install -D tailwindcss

/* v4 — Choose one */
npm install -D tailwindcss @tailwindcss/vite       // Vite projects
npm install -D tailwindcss @tailwindcss/postcss    // PostCSS projects
npm install -D tailwindcss @tailwindcss/cli        // CLI usage
```

---

## Configuration System Removal

### Tailwind.config.js No Longer Supported

```javascript
/* ❌ v3 — Still works */
module.exports = {
  theme: {
    colors: {
      primary: '#3b82f6',
    },
  },
};

/* ❌ v4 — File is ignored */
// tailwind.config.js exists but does nothing

/* ✅ v4 — Correct approach */
// @import "tailwindcss";
// @theme {
//   --color-primary: #3b82f6;
// }
```

### Removed Config Options
| Option | v3 | v4 | Migration |
|--------|-----|-----|-----------|
| `content` | ✅ | ❌ | Auto-detected from imports |
| `theme.extend` | ✅ | ❌ | Use additional `@theme` |
| `corePlugins` | ✅ | ❌ | Use `@layer` overrides |
| `plugins` | ✅ | ❌ | Use `@layer components` |
| `presets` | ✅ | ❌ | Not needed with CSS config |

---

## Import Syntax Changes

### Directives Replaced

```css
/* v3 */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* v4 */
@import "tailwindcss";
```

### Meaning of Each

```css
/* v4: Single import now includes all three layers */
@import "tailwindcss";
/* ≈ equivalent to v3's base + components + utilities */
```

---

## Breaking Change Impact Assessment

### High Impact (Likely to break)
- **Border color default** — Affects layouts with explicit borders
- **Ring width default** — Affects focus states and outlines
- **Opacity utilities removed** — Affects color manipulation

### Medium Impact (Needs review)
- **Shadow/rounded renamed** — Utility names changed
- **Package structure** — Installation/imports changed
- **Config file ignored** — Build process changes

### Low Impact (Usually fine)
- **Flexbox aliases** — Shorter names, same functionality
- **Typography updates** — `text-ellipsis` still works the same
- **Ring syntax** — Explicit width selection is better

---

## Migration Checklist

- [ ] Delete `tailwind.config.js`
- [ ] Update import: `@import "tailwindcss"`
- [ ] Create `@theme {}` block for customization
- [ ] Find/replace `.shadow` → `.shadow-sm`
- [ ] Find/replace `.rounded` → `.rounded-sm`
- [ ] Find/replace `.outline-none` → `.outline-hidden`
- [ ] Find/replace `.ring` → `.ring-1`
- [ ] Find/replace `.bg-opacity-*` → `.bg-black/*`
- [ ] Find/replace `.flex-grow-*` → `.grow-*`
- [ ] Find/replace `.flex-shrink-*` → `.shrink-*`
- [ ] Test border colors (likely broken)
- [ ] Test all focus states (ring width changed)
- [ ] Verify responsive breakpoints
- [ ] Test dark mode
- [ ] Performance testing
