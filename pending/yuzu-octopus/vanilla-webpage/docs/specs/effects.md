# Effects Spec

## Glassmorphism

```css
.glass {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-xl);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

Requires a visible background behind the element.

## Neumorphism

```css
.neumorphic {
  background: #e0e0e0;
  border-radius: var(--radius-lg);
  box-shadow: 8px 8px 15px #bebebe, -8px -8px 15px #ffffff;
}
```

Background must match page background.

## Gradient Text

```css
.gradient-text {
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

## Border Animation

```css
@property --angle { syntax: "<angle>"; initial-value: 0deg; inherits: false; }
.animated-border::before {
  background: conic-gradient(from var(--angle), #667eea, #764ba2, #667eea);
  animation: rotate 3s linear infinite;
}
```

## Scroll Snap

```css
.carousel { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; }
.carousel-card { flex: 0 0 100%; scroll-snap-align: start; }
```

## Rules

- Glassmorphism needs `backdrop-filter` — provide fallback for older browsers
- Neumorphism background must match page background exactly
- `@property` required to animate custom properties
- Scroll snap: use `mandatory` for strict snapping, `proximity` for loose
