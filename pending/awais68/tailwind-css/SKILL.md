---
name: tailwind-css
description: |
  Use when styling UI components or layouts with Tailwind CSS - mobile-first design, responsive utilities, custom themes, or component styling.
  NOT when plain CSS, CSS-in-JS (styled-components), or non-Tailwind frameworks are involved.
  Triggers: "style component", "responsive design", "mobile-first", "dark theme", "tailwind classes", "dashboard grid".
---

# Tailwind CSS Skill

## Overview

Expert guidance for Tailwind CSS styling with mobile-first responsive design, custom themes, and utility-first approach. Focuses on accessibility, dark mode, and performance optimization.

## When This Skill Applies

This skill triggers when users request:
- **Styling**: "Style this KPI card", "Button component style", "Design a form"
- **Responsive**: "Mobile-first layout", "Responsive dashboard", "Grid with breakpoints"
- **Themes**: "Custom dark theme", "Extend tailwind theme", "Color scheme"
- **Layouts**: "Dashboard grid", "Card layout", "Flexible container"

## Core Rules

### 1. Mobile-First Design

```jsx
// ✅ GOOD: Mobile-first progressive enhancement
<div className="w-full px-4 py-2 sm:w-1/2 sm:px-6 md:w-1/3 md:px-8 lg:w-1/4">
  <KPICard />
</div>

// Breakpoints:
// sm: 640px   - Small tablets/phones
// md: 768px   - Tablets
// lg: 1024px  - Desktops
// xl: 1280px  - Large screens
// 2xl: 1536px - Extra large screens
```

**Requirements:**
- Base styles for mobile (no prefix)
- Progressive enhancement with `sm:`, `md:`, `lg:` prefixes
- Start with mobile layout, enhance for larger screens
- Use responsive breakpoints: `sm:640px`, `md:768px`, `lg:1024px`

### 2. Responsive Utilities

```jsx
// ✅ GOOD: Fluid responsive layouts
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
  {items.map(item => <Item key={item.id} item={item} />)}
</div>

// ✅ GOOD: Responsive spacing
<div className="p-4 sm:p-6 md:p-8 lg:p-12">
  Content
</div>

// ✅ GOOD: Container queries (if needed)
<div className="@container">
  <div className="@lg:grid-cols-2">
    Nested responsive content
  </div>
</div>
```

**Requirements:**
- Use fluid utilities (`w-full`, `flex-1`) for mobile
- Add breakpoints (`sm:`, `md:`, `lg:`) for larger screens
- Consider container queries for nested responsive components
- Test layouts at multiple breakpoints (375px, 768px, 1024px, 1440px)

### 3. Custom Themes

```typescript
// tailwind.config.ts
export default {
  darkMode: 'class', // or 'media'
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        erp: {
          'card': '#ffffff',
          'card-dark': '#1f2937',
        },
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
```

**Requirements:**
- Extend theme in `tailwind.config.ts`, don't override
- Use semantic names (`primary`, `secondary`, `accent`)
- Define custom colors, fonts, spacing in theme
- Support CSS variables for dynamic theming
- Use `darkMode: 'class'` for manual dark mode toggle

### 4. Component Styling

```jsx
// ✅ GOOD: Utility-first approach
export const Button = ({ variant, size, children }) => (
  <button className={`
    font-semibold rounded-lg
    ${variant === 'primary' ? 'bg-blue-500 text-white hover:bg-blue-600' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}
    ${size === 'sm' ? 'px-3 py-1 text-sm' : 'px-4 py-2'}
    transition-colors duration-200
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
  `}>
    {children}
  </button>
);

// ✅ GOOD: CVA or class-variance-authority for variants
import { cva } from 'class-variance-authority';

const buttonVariants = cva(
  'font-semibold rounded-lg transition-colors',
  {
    variants: {
      variant: {
        primary: 'bg-blue-500 text-white hover:bg-blue-600',
        secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
      },
      size: {
        sm: 'px-3 py-1 text-sm',
        md: 'px-4 py-2',
      },
    },
  }
);
```

**Requirements:**
- Prefer inline utility classes over custom CSS
- Use `@apply` sparingly (only for repeated patterns)
- Extract complex variants with CVA or similar libraries
- Follow shadcn/ui patterns for consistent styling
- Use template literals for conditional classes

## Output Requirements

### Code Files

1. **Component Styling**:
   - Inline utility classes in JSX/TSX
   - Conditional classes for variants (dark/light, sizes)
   - Focus states and transitions

2. **Configuration**:
   - `tailwind.config.ts` updates for custom themes
   - `globals.css` for global styles and directives

3. **Dark Mode Support**:
   ```jsx
   <div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
     Content with dark mode
   </div>
   ```

### Integration Requirements

- **shadcn/ui**: Follow shadcn design tokens and patterns
- **Accessibility**: WCAG 2.1 AA compliant colors, focus-visible states
- **Performance**: Enable JIT mode, purge unused classes
- **i18n**: Support RTL layouts when needed

### Documentation

- **PHR**: Create Prompt History Record for styling decisions
- **ADR**: Document theme decisions (color schemes, breakpoints)
- **Comments**: Document non-obvious utility combinations

## Workflow

1. **Analyze Layout Requirements**
   - Identify mobile breakpoints
   - Determine responsive needs
   - Check dark mode requirements

2. **Apply Mobile-First Styles**
   - Base styles without breakpoints
   - Progressive enhancement for larger screens
   - Test on mobile viewport (375px)

3. **Add Responsive Breakpoints**
   - `sm:` for tablets (640px)
   - `md:` for tablets (768px)
   - `lg:` for desktops (1024px)
   - Test at each breakpoint

4. **Apply Dark Mode**
   - Add `dark:` variants for colors/backgrounds
   - Test in both light and dark modes
   - Ensure contrast ratios in both modes

5. **Validate Accessibility**
   - Check color contrast ratios (4.5:1 minimum)
   - Add focus-visible states for interactive elements
   - Ensure touch targets are 44px+ on mobile

## Quality Checklist

Before completing any styling:

- [ ] **No Horizontal Scroll Mobile**: Layout fits 375px without horizontal scroll
- [ ] **Touch Targets**: All interactive elements 44px+ on mobile
- [ ] **Dark/Light Variants**: Dark mode support with `dark:` classes
- [ ] **Utility-First**: Minimal custom CSS, use Tailwind utilities
- [ ] **Purge Unused**: No unused utility classes in production
- [ ] **Focus States**: `focus-visible` or `focus:ring` on all interactive elements
- [ ] **Contrast Ratios**: WCAG 2.1 AA compliant colors (4.5:1 for text)
- [ ] **Responsive Breakpoints**: Tested at sm/md/lg breakpoints
- [ ] **Consistent Spacing**: Use Tailwind's spacing scale (0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 56, 64)
- [ ] **Transitions**: Add `transition-*` classes for smooth state changes

## Common Patterns

### KPI Card (Mobile-First)

```jsx
export const KPICard = ({ title, value, trend, loading }) => (
  <div className="
    w-full p-4 bg-white dark:bg-gray-800
    rounded-lg shadow-sm border border-gray-200 dark:border-gray-700
    sm:p-6 md:p-8
  ">
    {loading ? (
      <Skeleton className="h-20" />
    ) : (
      <>
        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
          {title}
        </h3>
        <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">
          {value}
        </p>
        {trend && (
          <span className={`
            inline-flex items-center mt-2 text-sm
            ${trend > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}
          `}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
        )}
      </>
    )}
  </div>
);
```

### Responsive Dashboard Grid

```jsx
export const DashboardGrid = ({ children }) => (
  <div className="
    w-full grid gap-4
    grid-cols-1
    sm:grid-cols-2
    md:grid-cols-3
    lg:grid-cols-4
    xl:grid-cols-5
    p-4
  ">
    {children}
  </div>
);
```

### Form with Responsive Layout

```jsx
export const ResponsiveForm = () => (
  <form className="
    w-full max-w-lg mx-auto
    p-4 sm:p-6 md:p-8
    bg-white dark:bg-gray-800
    rounded-lg shadow-md
  ">
    <div className="space-y-4 sm:space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Name
        </label>
        <input className="
          w-full px-4 py-2 text-base
          border border-gray-300 dark:border-gray-600
          rounded-lg
          bg-white dark:bg-gray-700
          text-gray-900 dark:text-white
          focus:ring-2 focus:ring-blue-500 focus:border-blue-500
        " />
      </div>
      <button className="
        w-full sm:w-auto
        px-6 py-3 text-base font-semibold
        bg-blue-500 hover:bg-blue-600
        text-white rounded-lg
        transition-colors duration-200
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
      ">
        Submit
      </button>
    </div>
  </form>
);
```

### Dark Mode Toggle Button

```jsx
export const DarkModeToggle = ({ isDark, onToggle }) => (
  <button
    onClick={onToggle}
    className="
      p-2 rounded-lg
      bg-gray-200 dark:bg-gray-700
      hover:bg-gray-300 dark:hover:bg-gray-600
      text-gray-800 dark:text-gray-200
      transition-colors duration-200
      focus:outline-none focus:ring-2 focus:ring-blue-500
    "
    aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
  >
    {isDark ? '☀️' : '🌙'}
  </button>
);
```

## Tailwind Configuration Best Practices

### Breakpoint Strategy

```typescript
// Recommended breakpoint configuration
screens: {
  'xs': '475px',  // Extra small phones
  'sm': '640px',  // Small tablets/phones
  'md': '768px',  // Tablets
  'lg': '1024px', // Desktops
  'xl': '1280px', // Large screens
  '2xl': '1536px', // Extra large screens
}
```

### Color System

```typescript
// Semantic color naming
colors: {
  primary: { 50: '...', 500: '...', 900: '...' },
  success: { 50: '...', 500: '...', 900: '...' },
  warning: { 50: '...', 500: '...', 900: '...' },
  error:   { 50: '...', 500: '...', 900: '...' },
}
```

### Spacing Scale

```typescript
// Use Tailwind's scale: 0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 56, 64, 72, 80, 96
// 1 = 0.25rem (4px), 4 = 1rem (16px), 8 = 2rem (32px)
spacing: {
  '128': '32rem',
  '144': '36rem',
}
```

## Accessibility Guidelines

- **Color Contrast**: Minimum 4.5:1 for text, 3:1 for large text
- **Focus States**: Always include `focus:ring-2` or `focus-visible`
- **Touch Targets**: Minimum 44x44px for mobile interactive elements
- **Skip Links**: Add `sr-only` skip links for keyboard users
- **ARIA Labels**: Use `aria-label` for icon-only buttons

## Performance Optimization

1. **JIT Mode**: Enabled by default in Tailwind CSS 3+
2. **Purge Unused**: Only used classes in production
3. **CSS Minification**: Tailwind CLI or PostCSS optimization
4. **Inline Critical CSS**: Extract critical CSS for above-fold content
5. **Lazy Load Components**: Code split heavy components

## References

- Tailwind CSS Documentation: https://tailwindcss.com/docs
- Tailwind UI Patterns: https://tailwindui.com
- shadcn/ui Components: https://ui.shadcn.com
- Web Content Accessibility Guidelines (WCAG 2.1): https://www.w3.org/WAI/WCAG21/quickref/
