# Forms Spec

## Tokens

```css
:root {
  --input-height: 2.75rem;     /* 44px — touch target */
  --input-padding: var(--space-3);
  --input-border: var(--color-border);
  --input-radius: var(--radius-md);
  --input-focus-ring: 0 0 0 3px var(--color-focus);
}
```

## Code

```css
.form-group { margin-bottom: var(--space-4); }
.form-group label {
  display: block;
  margin-bottom: var(--space-1);
  font-weight: 500;
  font-size: var(--text-sm);
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  height: var(--input-height);
  padding: 0 var(--input-padding);
  border: 1px solid var(--input-border);
  border-radius: var(--input-radius);
  font-size: var(--text-base);
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  box-shadow: var(--input-focus-ring);
  border-color: var(--color-primary);
}

.error { color: var(--color-error); font-size: var(--text-sm); margin-top: var(--space-1); }
```

## Rules

- **Labels always above inputs** — never placeholders as labels
- Use `autocomplete` attributes for common fields (name, email, password)
- Use `inputmode` for mobile keyboards (email, tel, numeric)
- Min height 44px for touch targets
- Error messages below the input, not in a toast
