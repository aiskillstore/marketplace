# Tailwind CSS V4: Configuration Guide

## Core Principle: CSS is Configuration

In Tailwind V4, **the CSS file is the configuration**. There is no separate JavaScript file. Everything lives in `@theme {}` blocks within your CSS.

```css
@import "tailwindcss";

@theme {
  /* All configuration happens here */
  --color-primary: oklch(0.6 0.2 243);
  --breakpoint-xl: 80rem;
  --font-display: "Satoshi", sans-serif;
}
```

---

## Anatomy of @theme Block

### Required: CSS Variables with -- Prefix

```css
@import "tailwindcss";

@theme {
  /* ✅ Correct: Always use -- prefix */
  --color-primary: oklch(0.6 0.2 243);
  
  /* ❌ Wrong: Will be ignored */
  color-primary: oklch(0.6 0.2 243);
}
```

### Available Theme Variables

All Tailwind defaults are available as CSS custom properties:

```css
@theme {
  /* Colors (all OKLch-based) */
  --color-primary-50: ...;
  --color-primary-500: ...;
  --color-primary-900: ...;
  
  /* Spacing */
  --spacing-0: 0;
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Typography */
  --font-serif: ui-serif, Georgia, serif;
  --font-mono: ui-monospace, SFMono-Regular, monospace;
  --font-display: "Custom Font", sans-serif;
  
  /* Sizes */
  --width-xs: 20rem;
  --width-sm: 24rem;
  --width-md: 28rem;
  --width-lg: 32rem;
  --width-xl: 36rem;
  
  /* Breakpoints */
  --breakpoint-sm: 40rem;
  --breakpoint-md: 48rem;
  --breakpoint-lg: 64rem;
  --breakpoint-xl: 80rem;
  --breakpoint-2xl: 96rem;
  
  /* Durations */
  --duration-75: 75ms;
  --duration-100: 100ms;
  --duration-150: 150ms;
  --duration-200: 200ms;
  --duration-300: 300ms;
  --duration-500: 500ms;
  --duration-700: 700ms;
  --duration-1000: 1000ms;
  
  /* Easing */
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## Pattern 1: Simple Color Override

```css
@import "tailwindcss";

@theme {
  /* Override just primary colors */
  --color-primary-50: oklch(0.99 0 0);
  --color-primary-100: oklch(0.97 0.01 243);
  --color-primary-200: oklch(0.94 0.04 243);
  --color-primary-300: oklch(0.89 0.10 243);
  --color-primary-400: oklch(0.82 0.15 243);
  --color-primary-500: oklch(0.70 0.20 243);
  --color-primary-600: oklch(0.60 0.22 243);
  --color-primary-700: oklch(0.50 0.20 243);
  --color-primary-800: oklch(0.42 0.18 243);
  --color-primary-900: oklch(0.35 0.15 243);
}
```

**Usage in HTML:**
```html
<button class="bg-primary-600 hover:bg-primary-700 text-white">
  Button
</button>
```

---

## Pattern 2: Multi-Theme with Data Attributes

```css
@import "tailwindcss";

@theme {
  /* Light theme defaults */
  --color-bg: oklch(1 0 0);          /* white */
  --color-text: oklch(0.3 0 0);      /* dark gray */
  --color-accent: oklch(0.6 0.2 243); /* blue */
}

@layer base {
  /* Dark theme variant */
  [data-theme="dark"] {
    --color-bg: oklch(0.2 0 0);       /* dark */
    --color-text: oklch(0.9 0 0);     /* light */
    --color-accent: oklch(0.7 0.2 260); /* lighter blue */
  }
  
  /* Ocean theme variant */
  [data-theme="ocean"] {
    --color-bg: oklch(0.95 0.05 260);
    --color-text: oklch(0.2 0 0);
    --color-accent: oklch(0.55 0.18 260);
  }
  
  /* Apply theme colors */
  body {
    @apply bg-bg text-text;
  }
}
```

**Usage in HTML:**
```html
<html data-theme="ocean">
  <body><!-- themed --></body>
</html>
```

---

## Pattern 3: Complex Spacing Scale

```css
@import "tailwindcss";

@theme {
  /* Expanded spacing scale */
  --spacing-0: 0;
  --spacing-px: 1px;
  --spacing-0-5: 0.125rem;    /* 2px */
  --spacing-1: 0.25rem;        /* 4px */
  --spacing-1-5: 0.375rem;     /* 6px */
  --spacing-2: 0.5rem;         /* 8px */
  --spacing-2-5: 0.625rem;     /* 10px */
  --spacing-3: 0.75rem;        /* 12px */
  --spacing-3-5: 0.875rem;     /* 14px */
  --spacing-4: 1rem;           /* 16px */
  /* ... continue as needed */
  
  /* Container sizes */
  --width-prose: 65ch;
  --width-full: 100%;
  --width-min: min-content;
  --width-max: max-content;
  --width-fit: fit-content;
  --width-screen: 100vw;
}
```

**Usage:**
```html
<div class="p-2-5 max-w-prose">
  <!-- Uses custom 10px padding -->
</div>
```

---

## Pattern 4: Custom Typography System

```css
@import "tailwindcss";

@theme {
  /* Display fonts */
  --font-display: "Satoshi", "Sohne", sans-serif;
  
  /* Body fonts */
  --font-body: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  
  /* Monospace fonts */
  --font-mono: "JetBrains Mono", monospace;
  
  /* Font sizes (12px scale) */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */
  --text-5xl: 3rem;       /* 48px */
}

@layer base {
  body {
    @apply font-body text-base;
  }
  
  h1 {
    @apply font-display text-5xl font-bold;
  }
  
  h2 {
    @apply font-display text-4xl font-bold;
  }
}
```

---

## Pattern 5: Responsive Breakpoints

```css
@import "tailwindcss";

@theme {
  /* Mobile-first breakpoints */
  --breakpoint-sm: 36rem;    /* 576px */
  --breakpoint-md: 48rem;    /* 768px */
  --breakpoint-lg: 62rem;    /* 992px */
  --breakpoint-xl: 80rem;    /* 1280px */
  --breakpoint-2xl: 96rem;   /* 1536px */
  --breakpoint-3xl: 120rem;  /* 1920px */
}
```

**Usage in HTML:**
```html
<div class="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 3xl:grid-cols-4">
  <!-- Responsive grid -->
</div>
```

---

## Pattern 6: Animation & Transition Easing

```css
@import "tailwindcss";

@theme {
  /* Standard durations */
  --duration-fast: 100ms;
  --duration-default: 150ms;
  --duration-slow: 200ms;
  --duration-slower: 300ms;
  
  /* Custom easing functions */
  --ease-smooth: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-elastic: cubic-bezier(0.17, 0.67, 0.83, 0.67);
  --ease-sharp: cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

@layer components {
  .transition-smooth {
    @apply transition duration-default ease-smooth;
  }
}
```

---

## Pattern 7: Component-Scoped Theming

```css
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.6 0.2 243);
  --color-secondary: oklch(0.7 0.15 28);
}

@layer components {
  /* Button component with theme-aware colors */
  .btn-primary {
    @apply px-4 py-2 rounded-sm bg-primary text-white
           font-semibold transition-all
           hover:opacity-90 active:scale-95;
  }
  
  .btn-secondary {
    @apply px-4 py-2 rounded-sm bg-secondary text-white
           font-semibold transition-all
           hover:opacity-90 active:scale-95;
  }
  
  /* Card with inherited theme */
  .card {
    @apply p-6 rounded-lg bg-white shadow-md
           border border-gray-200;
  }
  
  .card.dark {
    @apply bg-gray-900 text-white border-gray-700;
  }
}
```

---

## Pattern 8: Using CSS Variables in @theme

```css
@import "tailwindcss";

/* Define base variables */
:root {
  --hue-primary: 243;
  --hue-secondary: 28;
  --saturation: 0.2;
  --lightness-light: 0.7;
  --lightness-dark: 0.5;
}

@theme {
  /* Use CSS variables in @theme */
  --color-primary: oklch(0.7 var(--saturation) var(--hue-primary));
  --color-secondary: oklch(0.6 var(--saturation) var(--hue-secondary));
}

/* Override via data attribute */
@layer base {
  [data-theme="dark"] {
    --lightness-light: 0.5;
    --lightness-dark: 0.3;
  }
}
```

---

## Pattern 9: Enterprise Multi-Brand Setup

```css
@import "tailwindcss";

/* Default brand (Brand A) */
@theme {
  --color-brand-primary: oklch(0.6 0.2 243);   /* Blue */
  --color-brand-secondary: oklch(0.7 0.15 28); /* Orange */
  --font-brand: "Inter", sans-serif;
}

/* Brand B variant */
@layer base {
  [data-brand="brand-b"] {
    --color-brand-primary: oklch(0.55 0.18 260);   /* Purple */
    --color-brand-secondary: oklch(0.65 0.2 130);  /* Green */
    --font-brand: "Poppins", sans-serif;
  }
}

/* Brand C variant */
@layer base {
  [data-brand="brand-c"] {
    --color-brand-primary: oklch(0.5 0.22 25);     /* Red */
    --color-brand-secondary: oklch(0.7 0.15 55);   /* Yellow */
    --font-brand: "Sohne", sans-serif;
  }
}

/* Apply brand colors globally */
@layer components {
  .btn-brand {
    @apply px-4 py-2 rounded-sm bg-brand-primary text-white;
  }
}
```

**Usage:**
```html
<!-- Switch brands with data attribute -->
<html data-brand="brand-b">
  <body>
    <button class="btn-brand">Branded Button</button>
  </body>
</html>
```

---

## Anti-Patterns to Avoid

### ❌ Don't: Mix JavaScript Config with CSS Config
```javascript
/* ❌ This doesn't work in v4 */
module.exports = {
  theme: {
    colors: { primary: '#3b82f6' },
  },
};
```

### ❌ Don't: Omit -- Prefix in @theme
```css
/* ❌ This is ignored */
@theme {
  color-primary: oklch(...);
}

/* ✅ Correct */
@theme {
  --color-primary: oklch(...);
}
```

### ❌ Don't: Put Theme Variables Outside @theme
```css
/* ❌ Won't work as expected */
:root {
  --color-primary: oklch(0.6 0.2 243);
}

/* ✅ Correct: Use @theme */
@theme {
  --color-primary: oklch(0.6 0.2 243);
}
```

### ❌ Don't: Assume Backward Compatibility
```html
<!-- ❌ v3 syntax: shadow → shadow-sm in v4 -->
<div class="shadow"></div>

<!-- ✅ Correct for v4 -->
<div class="shadow-sm"></div>
```

---

## Quick Reference: Variable Naming

```
Color:      --color-<name>-<shade>
Spacing:    --spacing-<size>
Typography: --text-<size>, --font-<family>
Sizing:     --width-<name>, --height-<name>
Breakpoint: --breakpoint-<name>
Duration:   --duration-<name>
Easing:     --ease-<name>
Radius:     --rounded-<size>
Shadow:     --shadow-<size>
Border:     --border-<size>
```

---

## Testing Your Configuration

```bash
# Build CSS with your configuration
npm run build

# Check output CSS file
cat dist/styles.css | grep --color-primary

# Verify theme variables are applied
npm run dev  # Start development server
# Open DevTools → Console → getComputedStyle(document.documentElement)
```

