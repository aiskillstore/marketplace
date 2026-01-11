---
name: shadcn-aesthetic
description: |
  Modern CSS/SCSS architecture based on shadcn/ui design principles. Use this when generating any CSS, SCSS, or styling code to ensure modern, refined, and accessible design patterns.
---

# Modern CSS Architecture (shadcn Aesthetic)

This skill provides comprehensive guidance for writing modern, refined CSS/SCSS that matches the shadcn/ui aesthetic - clean, minimal, accessible, and beautifully crafted.

## When This Skill Activates

Apply these patterns when:
- Writing any CSS, SCSS, or styling code
- Creating component styles from scratch
- Refactoring existing styles
- Building design systems or theme systems
- Working on Blazor, React, Vue, or any web UI

## Core Principles

1. **Use CSS variables for everything themeable**
2. **HSL color system for easy manipulation**
3. **Consistent spacing scale (4px base)**
4. **Subtle, layered shadows**
5. **Quick, smooth transitions (150ms)**
6. **Proper focus states**
7. **Modern layout primitives (Grid/Flex with gap)**
8. **Dark mode first-class citizen**

---

## Color System

### Variable Structure

Always use HSL-based CSS variables for colors:

```scss
:root {
  // Background colors
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  
  // Card colors
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
  
  // Popover colors
  --popover: 0 0% 100%;
  --popover-foreground: 222.2 84% 4.9%;
  
  // Primary brand colors
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  
  // Secondary colors
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  
  // Muted colors
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  
  // Accent colors
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  
  // Destructive/error colors
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  
  // Border and input
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
  
  // Border radius
  --radius: 0.5rem;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  
  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;
  
  --popover: 222.2 84% 4.9%;
  --popover-foreground: 210 40% 98%;
  
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 47.4% 11.2%;
  
  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;
  
  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;
  
  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;
  
  --destructive: 0 62.8% 30.6%;
  --destructive-foreground: 210 40% 98%;
  
  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --ring: 212.7 26.8% 83.9%;
}
```

### Usage

```scss
// Always use hsl() with var()
.component {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  
  // With opacity
  border: 1px solid hsl(var(--border) / 0.5);
  
  &:hover {
    background-color: hsl(var(--primary) / 0.9);
  }
}
```

### ❌ Anti-Pattern (Don't Do This)

```scss
// Hard-coded hex colors
.button {
  background: #007bff;
  color: #ffffff;
}

// RGB without variables
.card {
  background: rgb(255, 255, 255);
  border: 1px solid rgba(0, 0, 0, 0.1);
}
```

---

## Spacing Scale

Use a consistent spacing scale based on 4px increments:

```scss
:root {
  --spacing-0: 0;
  --spacing-px: 1px;
  --spacing-0-5: 0.125rem;  // 2px
  --spacing-1: 0.25rem;     // 4px
  --spacing-1-5: 0.375rem;  // 6px
  --spacing-2: 0.5rem;      // 8px
  --spacing-2-5: 0.625rem;  // 10px
  --spacing-3: 0.75rem;     // 12px
  --spacing-3-5: 0.875rem;  // 14px
  --spacing-4: 1rem;        // 16px
  --spacing-5: 1.25rem;     // 20px
  --spacing-6: 1.5rem;      // 24px
  --spacing-7: 1.75rem;     // 28px
  --spacing-8: 2rem;        // 32px
  --spacing-9: 2.25rem;     // 36px
  --spacing-10: 2.5rem;     // 40px
  --spacing-11: 2.75rem;    // 44px
  --spacing-12: 3rem;       // 48px
  --spacing-14: 3.5rem;     // 56px
  --spacing-16: 4rem;       // 64px
  --spacing-20: 5rem;       // 80px
  --spacing-24: 6rem;       // 96px
  --spacing-32: 8rem;       // 128px
}
```

### Usage

```scss
.button {
  padding: var(--spacing-2) var(--spacing-4);  // 8px 16px
  gap: var(--spacing-2);                       // 8px
}

.card {
  padding: var(--spacing-6);    // 24px
  margin-bottom: var(--spacing-4); // 16px
}
```

### ❌ Anti-Pattern (Don't Do This)

```scss
// Random pixel values
.button {
  padding: 10px 22px;
  margin: 13px;
}

// Inconsistent spacing
.card {
  padding: 15px;
  margin-bottom: 18px;
}
```

---

## Shadow System

Use subtle, layered shadows for depth:

```scss
:root {
  // Subtle shadows
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  
  // Inner shadow
  --shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);
}
```

### Usage

```scss
.card {
  box-shadow: var(--shadow-sm);
  
  &:hover {
    box-shadow: var(--shadow-md);
  }
}

.dropdown {
  box-shadow: var(--shadow-lg);
}

.input {
  box-shadow: var(--shadow-sm);
  
  &:focus {
    box-shadow: var(--shadow-sm), 0 0 0 2px hsl(var(--ring) / 0.2);
  }
}
```

### ❌ Anti-Pattern (Don't Do This)

```scss
// Heavy, dated shadows
.card {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

// Single-layer shadows
.button {
  box-shadow: 2px 2px 5px #999;
}
```

---

## Typography Scale

Use a harmonious type scale:

```scss
:root {
  // Font sizes
  --text-xs: 0.75rem;      // 12px
  --text-sm: 0.875rem;     // 14px
  --text-base: 1rem;       // 16px
  --text-lg: 1.125rem;     // 18px
  --text-xl: 1.25rem;      // 20px
  --text-2xl: 1.5rem;      // 24px
  --text-3xl: 1.875rem;    // 30px
  --text-4xl: 2.25rem;     // 36px
  --text-5xl: 3rem;        // 48px
  
  // Line heights
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;
  
  // Font weights
  --font-thin: 100;
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  --font-extrabold: 800;
  
  // Font families
  --font-sans: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
}
```

### Usage

```scss
.heading {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  letter-spacing: -0.025em;
}

.body-text {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
}

.small-text {
  font-size: var(--text-sm);
  color: hsl(var(--muted-foreground));
}
```

### ❌ Anti-Pattern (Don't Do This)

```scss
// Random font sizes
h1 { font-size: 28px; }
h2 { font-size: 22px; }
p { font-size: 15px; }

// Hard-coded weights
.title { font-weight: 600; }
```

---

## Transitions & Animations

Use quick, smooth transitions:

```scss
:root {
  // Timing functions
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  
  // Durations
  --duration-75: 75ms;
  --duration-100: 100ms;
  --duration-150: 150ms;
  --duration-200: 200ms;
  --duration-300: 300ms;
  --duration-500: 500ms;
}
```

### Usage

```scss
.button {
  transition: all var(--duration-150) var(--ease-in-out);
  
  &:hover {
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
}

// For specific properties
.dropdown {
  transition-property: opacity, transform;
  transition-duration: var(--duration-150);
  transition-timing-function: var(--ease-out);
}
```

### ❌ Anti-Pattern (Don't Do This)

```scss
// Slow, dated transitions
.button {
  transition: all 0.3s ease;
}

// Transitioning too many properties
.card {
  transition: all 0.5s;
}
```

---

## Focus States

Modern, accessible focus rings:

```scss
.button, .input, .link {
  // Remove default outline
  outline: none;
  
  // Add custom focus ring
  &:focus-visible {
    outline: 2px solid hsl(var(--ring));
    outline-offset: 2px;
  }
}

// For inputs with borders
.input {
  &:focus-visible {
    outline: none;
    border-color: hsl(var(--ring));
    box-shadow: 0 0 0 2px hsl(var(--ring) / 0.2);
  }
}

// For cards and containers
.card {
  &:focus-visible {
    outline: 2px solid hsl(var(--ring));
    outline-offset: 2px;
    border-radius: var(--radius);
  }
}
```

### ❌ Anti-Pattern (Don't Do This)

```scss
// Removing outline without replacement
button {
  outline: none;
}

// Ugly focus states
input:focus {
  border: 2px solid blue;
}
```

---

## Modern Layout Patterns

### Grid Layouts

```scss
// Auto-fit grid
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-6);
}

// Fixed columns with gap
.two-column {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--spacing-8);
}

// Complex grid
.dashboard-layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  grid-template-rows: 60px 1fr;
  gap: var(--spacing-4);
  height: 100vh;
}
```

### Flex Layouts

```scss
// Modern flex with gap (not margin)
.button-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

// Flex with proper wrapping
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

// Center content
.centered {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}
```

### ❌ Anti-Pattern (Don't Do This)

```scss
// Using margins instead of gap
.buttons button {
  margin-right: 8px;
  
  &:last-child {
    margin-right: 0;
  }
}

// Floats
.columns {
  float: left;
  width: 50%;
}
```

---

## Component Patterns

### Button

```scss
.button {
  // Base styles
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  
  // Typography
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  line-height: var(--leading-none);
  
  // Spacing
  padding: var(--spacing-2) var(--spacing-4);
  
  // Visual
  border-radius: var(--radius);
  border: 1px solid transparent;
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  box-shadow: var(--shadow-sm);
  
  // Interaction
  cursor: pointer;
  transition: all var(--duration-150) var(--ease-in-out);
  user-select: none;
  
  // States
  &:hover {
    background-color: hsl(var(--primary) / 0.9);
    box-shadow: var(--shadow-md);
  }
  
  &:active {
    transform: translateY(1px);
    box-shadow: var(--shadow-sm);
  }
  
  &:focus-visible {
    outline: 2px solid hsl(var(--ring));
    outline-offset: 2px;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }
  
  // Variants
  &--secondary {
    background-color: hsl(var(--secondary));
    color: hsl(var(--secondary-foreground));
    
    &:hover {
      background-color: hsl(var(--secondary) / 0.8);
    }
  }
  
  &--outline {
    background-color: transparent;
    border-color: hsl(var(--input));
    color: hsl(var(--foreground));
    box-shadow: none;
    
    &:hover {
      background-color: hsl(var(--accent));
      color: hsl(var(--accent-foreground));
    }
  }
  
  &--ghost {
    background-color: transparent;
    box-shadow: none;
    
    &:hover {
      background-color: hsl(var(--accent));
      color: hsl(var(--accent-foreground));
    }
  }
  
  // Sizes
  &--sm {
    padding: var(--spacing-1-5) var(--spacing-3);
    font-size: var(--text-xs);
  }
  
  &--lg {
    padding: var(--spacing-3) var(--spacing-8);
    font-size: var(--text-base);
  }
}
```

### Input

```scss
.input {
  // Base styles
  display: flex;
  width: 100%;
  
  // Typography
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
  
  // Spacing
  padding: var(--spacing-2) var(--spacing-3);
  
  // Visual
  border-radius: var(--radius);
  border: 1px solid hsl(var(--input));
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
  box-shadow: var(--shadow-sm);
  
  // Interaction
  transition: all var(--duration-150) var(--ease-in-out);
  
  // Placeholder
  &::placeholder {
    color: hsl(var(--muted-foreground));
  }
  
  // States
  &:hover {
    border-color: hsl(var(--input) / 0.8);
  }
  
  &:focus {
    outline: none;
    border-color: hsl(var(--ring));
    box-shadow: 0 0 0 2px hsl(var(--ring) / 0.2);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background-color: hsl(var(--muted));
  }
  
  // Error state
  &--error {
    border-color: hsl(var(--destructive));
    
    &:focus {
      border-color: hsl(var(--destructive));
      box-shadow: 0 0 0 2px hsl(var(--destructive) / 0.2);
    }
  }
}
```

### Card

```scss
.card {
  // Base styles
  display: flex;
  flex-direction: column;
  
  // Spacing
  padding: var(--spacing-6);
  gap: var(--spacing-4);
  
  // Visual
  border-radius: calc(var(--radius) + 2px);
  border: 1px solid hsl(var(--border));
  background-color: hsl(var(--card));
  color: hsl(var(--card-foreground));
  box-shadow: var(--shadow-sm);
  
  // Interaction
  transition: box-shadow var(--duration-150) var(--ease-in-out);
  
  &:hover {
    box-shadow: var(--shadow-md);
  }
  
  // Sub-components
  &__header {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-1-5);
  }
  
  &__title {
    font-size: var(--text-2xl);
    font-weight: var(--font-semibold);
    line-height: var(--leading-tight);
    letter-spacing: -0.025em;
  }
  
  &__description {
    font-size: var(--text-sm);
    color: hsl(var(--muted-foreground));
  }
  
  &__content {
    flex: 1;
  }
  
  &__footer {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    padding-top: var(--spacing-4);
    border-top: 1px solid hsl(var(--border));
  }
}
```

### Badge

```scss
.badge {
  // Base styles
  display: inline-flex;
  align-items: center;
  
  // Typography
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  line-height: var(--leading-none);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  
  // Spacing
  padding: var(--spacing-1) var(--spacing-2-5);
  
  // Visual
  border-radius: calc(var(--radius) - 2px);
  border: 1px solid transparent;
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  
  // Variants
  &--secondary {
    background-color: hsl(var(--secondary));
    color: hsl(var(--secondary-foreground));
  }
  
  &--outline {
    background-color: transparent;
    border-color: hsl(var(--border));
    color: hsl(var(--foreground));
  }
  
  &--destructive {
    background-color: hsl(var(--destructive));
    color: hsl(var(--destructive-foreground));
  }
}
```

---

## Dark Mode Strategy

### CSS Variable Approach

```scss
// Define light mode in :root
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  // ... all other variables
}

// Override for dark mode
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  // ... all other variables
}

// Components automatically adapt
.card {
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
}
```

### ❌ Anti-Pattern (Don't Do This)

```scss
// Media query approach (harder to control)
.card {
  background: white;
  color: black;
  
  @media (prefers-color-scheme: dark) {
    background: black;
    color: white;
  }
}
```

---

## Border Radius System

```scss
:root {
  --radius-none: 0;
  --radius-sm: 0.125rem;    // 2px
  --radius-base: 0.25rem;   // 4px
  --radius-md: 0.375rem;    // 6px
  --radius-lg: 0.5rem;      // 8px
  --radius-xl: 0.75rem;     // 12px
  --radius-2xl: 1rem;       // 16px
  --radius-3xl: 1.5rem;     // 24px
  --radius-full: 9999px;
  
  // Default radius (customize per theme)
  --radius: var(--radius-lg);
}

// Usage
.button {
  border-radius: var(--radius);
}

.card {
  border-radius: calc(var(--radius) + 2px); // Slightly larger
}

.avatar {
  border-radius: var(--radius-full); // Circle
}
```

---

## Z-Index System

```scss
:root {
  --z-0: 0;
  --z-10: 10;
  --z-20: 20;
  --z-30: 30;
  --z-40: 40;
  --z-50: 50;
  --z-dropdown: 1000;
  --z-sticky: 1100;
  --z-fixed: 1200;
  --z-modal-backdrop: 1300;
  --z-modal: 1400;
  --z-popover: 1500;
  --z-tooltip: 1600;
  --z-toast: 1700;
}

.dropdown {
  z-index: var(--z-dropdown);
}

.modal {
  z-index: var(--z-modal);
}
```

---

## Accessibility Patterns

### Keyboard Navigation

```scss
// Show focus states only for keyboard navigation
.button {
  &:focus {
    outline: none;
  }
  
  &:focus-visible {
    outline: 2px solid hsl(var(--ring));
    outline-offset: 2px;
  }
}
```

### Screen Reader Only

```scss
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

### High Contrast Support

```scss
@media (prefers-contrast: high) {
  .button {
    border-width: 2px;
  }
  
  .input {
    border-width: 2px;
  }
}
```

### Reduced Motion

```scss
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Complete Example: Modern Component

```scss
// Alert Component
.alert {
  // Layout
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  
  // Spacing
  padding: var(--spacing-4);
  
  // Visual
  border-radius: var(--radius);
  border: 1px solid hsl(var(--border));
  background-color: hsl(var(--background));
  
  // Typography
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  
  // Icon
  &__icon {
    flex-shrink: 0;
    width: 1rem;
    height: 1rem;
    margin-top: 0.125rem;
  }
  
  // Content
  &__content {
    flex: 1;
  }
  
  &__title {
    font-weight: var(--font-medium);
    margin-bottom: var(--spacing-1);
  }
  
  &__description {
    color: hsl(var(--muted-foreground));
  }
  
  // Variants
  &--info {
    border-color: hsl(210 100% 90%);
    background-color: hsl(210 100% 97%);
    
    .alert__icon {
      color: hsl(210 100% 45%);
    }
  }
  
  &--success {
    border-color: hsl(142 76% 85%);
    background-color: hsl(142 76% 96%);
    
    .alert__icon {
      color: hsl(142 76% 36%);
    }
  }
  
  &--warning {
    border-color: hsl(38 92% 85%);
    background-color: hsl(38 92% 95%);
    
    .alert__icon {
      color: hsl(38 92% 50%);
    }
  }
  
  &--error {
    border-color: hsl(0 84% 85%);
    background-color: hsl(0 84% 97%);
    
    .alert__icon {
      color: hsl(0 84% 60%);
    }
  }
}

// Dark mode
.dark {
  .alert {
    &--info {
      border-color: hsl(210 100% 20%);
      background-color: hsl(210 100% 10%);
      
      .alert__icon {
        color: hsl(210 100% 70%);
      }
    }
    
    // ... other variants
  }
}
```

---

## Quality Checklist

Before finalizing any CSS, verify:

- [ ] Using CSS variables for colors
- [ ] HSL color format with opacity support
- [ ] Consistent spacing scale (4px base)
- [ ] Subtle, layered shadows
- [ ] Quick transitions (150ms default)
- [ ] Proper focus-visible states
- [ ] Modern layout (Grid/Flex with gap)
- [ ] Dark mode support
- [ ] Reduced motion support
- [ ] High contrast support
- [ ] Semantic class names (BEM or similar)
- [ ] No hard-coded colors
- [ ] No random pixel values
- [ ] Keyboard accessible
- [ ] Screen reader friendly

---

## Reference Resources

When in doubt, reference these patterns:
1. shadcn/ui components: https://ui.shadcn.com
2. Radix UI primitives: https://www.radix-ui.com
3. Tailwind CSS utilities: https://tailwindcss.com

Remember: **Subtle beats flashy. Consistent beats clever. Accessible beats everything.**
