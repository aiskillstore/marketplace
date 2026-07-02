# Modern CSS Guide

Features that eliminate the need for preprocessors and JavaScript.

## Nesting (replaces Sass)

```css
.card {
  background: white;

  & h2 { font-size: 1.5rem; }
  & p { color: #666; }
  &:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
}
```

## @layer (specificity management)

```css
@layer tokens, base, components, utilities;
```

Ordered from low to high specificity. Layers always win over un-layered styles.

## :has() (parent selector)

```css
.card:has(.badge) { border: 2px solid blue; }
form:has(:invalid) { border-color: red; }
```

## clamp() (fluid values)

```css
font-size: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
width: clamp(300px, 80%, 1200px);
```

## color-mix()

```css
.btn-hover { background: color-mix(in oklch, var(--color-primary), black 15%); }
```

## light-dark()

```css
:root { color-scheme: light dark; }
body {
  background: light-dark(white, #121212);
  color: light-dark(#1a1a1a, #e0e0e0);
}
```

## Container Queries

```css
.card-container { container-type: inline-size; }
@container (min-width: 400px) {
  .card { display: grid; grid-template-columns: 1fr 2fr; }
}
```

## @property (animatable custom properties)

```css
@property --angle {
  syntax: "<angle>";
  initial-value: 0deg;
  inherits: false;
}
```

## @starting-style (entry animations)

```css
dialog {
  transition: opacity 0.3s, display 0.3s allow-discrete;
  @starting-style { opacity: 0; }
}
```

## text-wrap: balance

```css
h1, h2, h3 { text-wrap: balance; }
/* Only for six lines or fewer */
```

## :is() and :where() (selector shortcuts)

```css
:is(h1, h2, h3) { text-wrap: balance; }
:where(a, button) { cursor: pointer; }
```

## OKLCH colors

```css
--primary: oklch(54% 0.23 255);
--primary-hover: oklch(from var(--primary) calc(l - 10%) c h);
```
