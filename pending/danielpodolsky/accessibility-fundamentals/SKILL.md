---
name: Accessibility Fundamentals
description: Auto-invoke when reviewing JSX with interactive elements, forms, buttons, or navigation. Enforces WCAG compliance and inclusive design.
---

# Accessibility Fundamentals Review

> "Accessibility is not a feature, it's a requirement. If 15% of users can't use your app, you've failed 15% of users."

## When to Apply

Activate this skill when:
- Reviewing JSX with buttons, links, or forms
- Seeing custom interactive components
- Forms with inputs and labels
- Navigation menus
- Modal dialogs
- Any user interaction code

---

## The Accessibility Checklist

### Must Have (Every Interactive Element)

- [ ] **Keyboard accessible** — All actions work with Tab + Enter/Space
- [ ] **Focus visible** — Clear visual indicator of focused element
- [ ] **Semantic elements** — `<button>` not `<div onClick>`
- [ ] **Form labels** — Every input has an associated `<label>`
- [ ] **Alt text** — Images have descriptive alt attributes
- [ ] **Sufficient contrast** — Text readable against background (4.5:1 ratio)

### Should Have (Complex Interactions)

- [ ] **ARIA labels** — Icon-only buttons have `aria-label`
- [ ] **Focus trapping** — Modals trap focus until closed
- [ ] **Skip links** — "Skip to main content" for keyboard users
- [ ] **Live regions** — Dynamic content announced to screen readers
- [ ] **Error messages** — Linked to inputs with `aria-describedby`

### Never Do

- [ ] **Rely on color alone** — Color should not be the only indicator
- [ ] **Remove focus outlines** — Never `outline: none` without replacement
- [ ] **Use divs for buttons** — Use semantic `<button>` or `<a>`
- [ ] **Trap users** — Always provide escape from modals/menus

---

## Common Mistakes (Anti-Patterns)

### 1. Div as Button

```tsx
// ❌ BAD: Not keyboard accessible, no semantics
<div onClick={handleClick} className="button">
  Click me
</div>

// ✅ GOOD: Native button element
<button onClick={handleClick} className="button">
  Click me
</button>
```

**Why it matters:** `<div onClick>` doesn't receive keyboard focus, doesn't respond to Enter/Space, and isn't announced as a button by screen readers.

### 2. Missing Form Labels

```tsx
// ❌ BAD: Input has no label
<input type="email" placeholder="Email" />

// ✅ GOOD: Label linked to input
<label htmlFor="email">Email</label>
<input id="email" type="email" placeholder="example@email.com" />

// ✅ ALSO GOOD: Wrapping label
<label>
  Email
  <input type="email" />
</label>
```

### 3. Icon-Only Buttons

```tsx
// ❌ BAD: No accessible name
<button onClick={handleDelete}>
  <TrashIcon />
</button>

// ✅ GOOD: ARIA label for screen readers
<button onClick={handleDelete} aria-label="Delete item">
  <TrashIcon aria-hidden="true" />
</button>
```

### 4. Removed Focus Styles

```css
/* ❌ BAD: Focus invisible */
button:focus {
  outline: none;
}

/* ✅ GOOD: Custom but visible focus */
button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.6);
}

/* ✅ BEST: Use focus-visible */
button:focus-visible {
  outline: 2px solid #4299e1;
  outline-offset: 2px;
}
```

### 5. Non-Descriptive Link Text

```tsx
// ❌ BAD: "Click here" tells screen reader nothing
<p>
  To read our privacy policy, <a href="/privacy">click here</a>.
</p>

// ✅ GOOD: Link text describes destination
<p>
  Read our <a href="/privacy">privacy policy</a>.
</p>
```

### 6. Missing Heading Hierarchy

```tsx
// ❌ BAD: Screen reader can't navigate
<div className="title">Welcome</div>
<div className="subtitle">Getting Started</div>

// ✅ GOOD: Proper headings
<h1>Welcome</h1>
<h2>Getting Started</h2>
```

---

## Socratic Questions

Ask these instead of giving answers:

1. **Keyboard**: "Can you complete this action using only the keyboard?"
2. **Focus**: "If I tab through the page, can I see where I am?"
3. **Semantics**: "What does a screen reader announce for this element?"
4. **Labels**: "If the placeholder disappears, how do users know what to enter?"
5. **Color**: "If someone is colorblind, can they still understand this UI?"
6. **Alt Text**: "If the image doesn't load, what context is lost?"

---

## Testing Accessibility

### Manual Testing

1. **Keyboard test**: Navigate entire page with Tab only
2. **Focus test**: Can you always see where focus is?
3. **Zoom test**: Does layout break at 200% zoom?
4. **Screen reader**: Try VoiceOver (Mac) or NVDA (Windows)

### Automated Testing

```bash
# In your test file
# Pattern: axe-core for React Testing Library
import { axe } from 'jest-axe';

it('should have no a11y violations', async () => {
  const { container } = render(<YourComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

## ARIA Reference

### Common ARIA Attributes

| Attribute | Use Case |
|-----------|----------|
| `aria-label` | Provides name for icon-only buttons |
| `aria-labelledby` | Points to element with visible label |
| `aria-describedby` | Points to description (error messages) |
| `aria-hidden="true"` | Hides decorative icons from screen readers |
| `aria-expanded` | Indicates dropdown/accordion state |
| `aria-live` | Announces dynamic content changes |
| `role` | Defines element's purpose (use sparingly) |

### The First Rule of ARIA

> "No ARIA is better than bad ARIA."

Use semantic HTML first. Only use ARIA when HTML can't express what you need.

---

## Stack-Specific Guidance

### React

```tsx
// Pattern: Button with accessible name
<button
  onClick={handleAction}
  aria-label="Close modal"
>
  <XIcon aria-hidden="true" />
</button>
```

### Form Error Pattern

```tsx
// Pattern: Error linked to input
<label htmlFor="email">Email</label>
<input
  id="email"
  type="email"
  aria-describedby={error ? "email-error" : undefined}
  aria-invalid={error ? "true" : undefined}
/>
{error && (
  <span id="email-error" role="alert">
    {error}
  </span>
)}
```

---

## Red Flags to Call Out

| Flag | Question |
|------|----------|
| `<div onClick>` | "What happens when a keyboard user tries to click this?" |
| `outline: none` | "How does a keyboard user know where they are?" |
| No form labels | "How does a screen reader know what this input is for?" |
| Icon-only button | "What does a screen reader announce for this button?" |
| Color as only indicator | "What if someone is red-green colorblind?" |
| `tabIndex > 0` | "This breaks natural tab order. Why is it needed?" |

---

## Interview Connection

> "I implemented accessibility best practices including semantic HTML, proper form labeling, and keyboard navigation, ensuring our app is usable by everyone."

STAR story material:
- "Identified accessibility issues with our form and fixed them..."
- "Implemented proper focus management in our modal component..."
- "Added screen reader support for our notification system..."

---

## MCP Usage

### Context7 - Framework Docs
```
Fetch: WAI-ARIA practices
Fetch: React accessibility documentation
```

### Octocode - Real Examples
```
Search: "aria-label" + "button" patterns
Search: Modal focus trapping implementations
```

---

## Resources

- WCAG 2.1 Guidelines (check Context7)
- Deque's axe-core for automated testing
- WebAIM color contrast checker
