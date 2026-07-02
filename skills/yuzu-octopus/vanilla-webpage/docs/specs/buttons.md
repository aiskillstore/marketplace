# Buttons Spec

## Three-Tier System

| Level | Use | Treatment |
|-------|-----|-----------|
| Primary | Main action (ONE per view) | Solid fill, high contrast |
| Secondary | Alternative actions | Outlined or subtle fill |
| Tertiary | Minor actions | Text-only or ghost |

## Tokens

```css
:root {
  --btn-height: 2.75rem;       /* 44px — touch target minimum */
  --btn-padding-x: var(--space-5);
  --btn-radius: var(--radius-md);
  --btn-font-weight: 500;

  --btn-primary-bg: var(--color-primary);
  --btn-primary-text: var(--color-text-inverse);

  --btn-secondary-bg: transparent;
  --btn-secondary-text: var(--color-text);
  --btn-secondary-border: var(--color-border);
}
```

## Code

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: var(--btn-height);
  padding: 0 var(--btn-padding-x);
  border-radius: var(--btn-radius);
  font-weight: var(--btn-font-weight);
  font-size: var(--text-base);
  cursor: pointer;
  border: none;
  transition: background 0.15s, transform 0.15s;
}

.btn-primary { background: var(--btn-primary-bg); color: var(--btn-primary-text); }
.btn-secondary { background: var(--btn-secondary-bg); color: var(--btn-secondary-text); border: 1px solid var(--btn-secondary-border); }
.btn-tertiary { background: transparent; color: var(--color-primary); }

.btn:hover { transform: translateY(-1px); }
.btn:active { transform: translateY(0); }
.btn:focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px; }
```

## Rules

- **ONE primary button per view** — prevents action hierarchy confusion
- Min height 44px (touch target)
- `:focus-visible` ring for keyboard users
- `prefers-reduced-motion: reduce` disables transform animation
