---
name: tailwind-patterns
description: "Quick reference for Tailwind CSS utility patterns, responsive design, and configuration. Triggers on: tailwind, utility classes, responsive design, tailwind config, dark mode css, tw classes."
compatibility: "For projects using Tailwind CSS v3+."
allowed-tools: "Read Write"
---

# Tailwind Patterns

Quick reference for Tailwind CSS utility patterns.

## Responsive Breakpoints

| Prefix | Min Width |
|--------|-----------|
| `sm:` | 640px |
| `md:` | 768px |
| `lg:` | 1024px |
| `xl:` | 1280px |
| `2xl:` | 1536px |

```html
<div class="w-full md:w-1/2 lg:w-1/3">
  <!-- Full on mobile, half on tablet, third on desktop -->
</div>
```

## Common Layout Patterns

```html
<!-- Centered container -->
<div class="container mx-auto px-4">

<!-- Flexbox row -->
<div class="flex items-center justify-between gap-4">

<!-- Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

<!-- Stack -->
<div class="flex flex-col gap-4">
```

## Card

```html
<div class="bg-white rounded-lg shadow-md p-6">
  <h3 class="text-lg font-semibold mb-2">Title</h3>
  <p class="text-gray-600">Content</p>
</div>
```

## Button

```html
<button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
  Button
</button>
```

## Form Input

```html
<input type="text"
  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  placeholder="Enter text">
```

## Dark Mode

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
```

```js
// tailwind.config.js
module.exports = { darkMode: 'class' }
```

## State Modifiers

| Modifier | Triggers On |
|----------|-------------|
| `hover:` | Mouse hover |
| `focus:` | Element focused |
| `active:` | Being clicked |
| `disabled:` | Disabled state |
| `group-hover:` | Parent hovered |

## Spacing Scale

| Class | Size |
|-------|------|
| `p-1` | 4px |
| `p-2` | 8px |
| `p-4` | 16px |
| `p-6` | 24px |
| `p-8` | 32px |

## Arbitrary Values

```html
<div class="w-[137px] h-[calc(100vh-64px)]">
```

## Additional Resources

For detailed patterns, load:
- `./references/component-patterns.md` - Navbar, cards, forms, alerts, loading states
