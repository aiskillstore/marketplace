# Accessibility Guide

## The 80/20 Rule

Semantic HTML gives you 80% of accessibility for free. The remaining 20% is focus management, color contrast, and motion preferences.

## Semantic HTML First

```html
<!-- Good: semantic -->
<nav aria-label="Main">...</nav>
<main>...</main>
<button>Submit</button>
<label for="email">Email</label>
<input type="email" id="email">

<!-- Bad: div soup -->
<div class="nav">...</div>
<div class="content">...</div>
<div class="btn">Submit</div>
<div class="input">Email</div>
```

## Focus Management

```css
:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}

/* Remove outline for mouse users, keep for keyboard */
:focus:not(:focus-visible) { outline: none; }
```

## Color Contrast (WCAG AA)

- Normal text: 4.5:1 minimum
- Large text (18px+ or 14px+ bold): 3:1 minimum
- UI components: 3:1 minimum

Use [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) to verify.

## Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## Form Accessibility

```html
<form>
  <!-- Always use visible labels -->
  <label for="name">Name</label>
  <input type="text" id="name" autocomplete="name" required>

  <!-- Use autocomplete for common fields -->
  <label for="email">Email</label>
  <input type="email" id="email" autocomplete="email" inputmode="email">

  <!-- Use inputmode for mobile keyboards -->
  <label for="phone">Phone</label>
  <input type="tel" id="phone" inputmode="tel" autocomplete="tel">
</form>
```

## ARIA (only when needed)

```html
<!-- Use when semantic HTML isn't enough -->
<button aria-expanded="false" aria-controls="menu">Menu</button>
<div id="menu" aria-hidden="true">...</div>

<!-- Live regions for dynamic updates -->
<div aria-live="polite" id="status"></div>
```

## Checklist

- [ ] Semantic HTML elements used
- [ ] All images have alt text (or alt="" for decorative)
- [ ] Focus visible on all interactive elements
- [ ] Color contrast meets WCAG AA
- [ ] prefers-reduced-motion respected
- [ ] Form labels are visible and associated
- [ ] ARIA attributes updated via JS when state changes
- [ ] Tested with keyboard navigation
