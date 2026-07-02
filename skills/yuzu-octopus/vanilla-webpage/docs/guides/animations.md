# CSS Animations Guide

## Transitions (simple state changes)

```css
.btn {
  background: #667eea;
  transition: background 0.2s, transform 0.2s;
}
.btn:hover { background: #5a6fd6; transform: translateY(-2px); }
```

## Keyframes (complex animations)

```css
@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate { animation: fade-in 0.3s ease; }
```

## @starting-style (entry animations for new elements)

```css
dialog {
  opacity: 1;
  transform: scale(1);
  transition: opacity 0.3s, transform 0.3s, display 0.3s allow-discrete;

  @starting-style {
    opacity: 0;
    transform: scale(0.95);
  }
}
```

Works with `<dialog>`, Popover API, and elements added to the DOM.

## Scroll-driven animations

```css
.reveal {
  animation: fade-in linear both;
  animation-timeline: view();
  animation-range: entry 0% cover 40%;
}
```

No JavaScript Intersection Observer needed.

## Reduced motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Always include this.** It's an accessibility requirement.

## Performance tips

- Animate `transform` and `opacity` only (GPU-accelerated)
- Avoid animating `width`, `height`, `top`, `left` (causes layout recalculation)
- Use `will-change` sparingly (only for elements that will animate)
