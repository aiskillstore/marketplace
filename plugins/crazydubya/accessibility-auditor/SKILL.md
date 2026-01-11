---
name: accessibility-auditor
description: Reviews UI components for WCAG compliance, ARIA attributes, keyboard navigation, and screen reader support. Use when building frontend components or user requests accessibility improvements.
allowed-tools: Read, Grep, Glob
---

# Accessibility Auditor

Audits web applications for accessibility compliance (WCAG 2.1 Level AA) and suggests improvements.

## When to Use
- Building or reviewing UI components
- User requests accessibility improvements
- Preparing for accessibility audit
- User mentions "accessibility", "a11y", "WCAG", "screen reader", or "keyboard navigation"

## Instructions

### 1. Semantic HTML Check

**Use proper HTML elements:**
```html
<!-- Bad -->
<div onclick="submit()">Submit</div>

<!-- Good -->
<button onclick="submit()">Submit</button>
```

**Semantic structure:**
- `<header>`, `<nav>`, `<main>`, `<footer>`
- `<article>`, `<section>`, `<aside>`
- `<h1>` through `<h6>` in proper hierarchy
- `<button>` for actions, `<a>` for navigation

### 2. ARIA Attributes

**When to use ARIA:**
- Custom widgets (tabs, accordions, modals)
- Dynamic content updates
- Complex interactions
- When semantic HTML isn't sufficient

**Common ARIA attributes:**
```html
<!-- Landmark roles -->
<nav role="navigation" aria-label="Main">

<!-- Widget roles -->
<div role="button" tabindex="0" aria-pressed="false">

<!-- Live regions -->
<div role="alert" aria-live="assertive">Error occurred</div>

<!-- Labels and descriptions -->
<button aria-label="Close dialog">×</button>
<input aria-describedby="password-help" />
```

**First rule of ARIA:** Don't use ARIA if semantic HTML works

### 3. Keyboard Navigation

**All interactive elements must be keyboard accessible:**
```javascript
// Add keyboard support to custom elements
<div
  role="button"
  tabindex="0"
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Click me
</div>
```

**Tab order:**
- Use `tabindex="0"` for custom interactive elements
- Avoid `tabindex > 0` (creates confusing tab order)
- Use `tabindex="-1"` for programmatic focus only

**Focus management:**
- Visible focus indicators
- Trap focus in modals
- Return focus when closing dialogs
- Skip links for main content

### 4. Alt Text and Images

**Informative images:**
```html
<img src="chart.png" alt="Sales increased 25% in Q3" />
```

**Decorative images:**
```html
<img src="decoration.png" alt="" />
<!-- or -->
<img src="decoration.png" role="presentation" />
```

**Complex images:**
```html
<figure>
  <img src="complex-chart.png" alt="Quarterly sales chart" />
  <figcaption>
    Detailed description of the chart data...
  </figcaption>
</figure>
```

### 5. Color and Contrast

**Contrast ratios (WCAG AA):**
- Normal text: 4.5:1 minimum
- Large text (18pt+): 3:1 minimum
- UI components: 3:1 minimum

**Don't rely on color alone:**
```html
<!-- Bad: Color only -->
<span style="color: red;">Error</span>

<!-- Good: Icon + color -->
<span style="color: red;">
  <svg aria-hidden="true"><!-- error icon --></svg>
  <span class="sr-only">Error: </span>
  Invalid input
</span>
```

### 6. Forms and Labels

**Every input needs a label:**
```html
<!-- Explicit label -->
<label for="email">Email</label>
<input id="email" type="email" />

<!-- Implicit label -->
<label>
  Email
  <input type="email" />
</label>

<!-- aria-label for icon buttons -->
<button aria-label="Search">
  <svg><!-- search icon --></svg>
</button>
```

**Error messages:**
```html
<input
  id="password"
  aria-invalid="true"
  aria-describedby="password-error"
/>
<div id="password-error" role="alert">
  Password must be at least 8 characters
</div>
```

### 7. Headings and Document Structure

**Proper heading hierarchy:**
```html
<h1>Page Title</h1>
  <h2>Section 1</h2>
    <h3>Subsection 1.1</h3>
    <h3>Subsection 1.2</h3>
  <h2>Section 2</h2>
```

**Don't skip levels:** h1 → h2 → h3 (not h1 → h3)

### 8. Dynamic Content

**Announce updates to screen readers:**
```html
<!-- Polite: wait for user to pause -->
<div role="status" aria-live="polite">
  5 new messages
</div>

<!-- Assertive: interrupt immediately -->
<div role="alert" aria-live="assertive">
  Your session will expire in 1 minute
</div>
```

**Loading states:**
```html
<button aria-busy="true" aria-label="Loading...">
  <span aria-hidden="true">Loading</span>
</button>
```

### 9. Screen Reader Testing

**Screen reader only text:**
```css
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

**Hide decorative elements:**
```html
<svg aria-hidden="true"><!-- icon --></svg>
```

### 10. Common Issues to Check

**Missing:**
- [ ] Alt text on images
- [ ] Labels on form inputs
- [ ] Proper heading hierarchy
- [ ] Keyboard focus indicators
- [ ] ARIA labels on icon buttons

**Improper:**
- [ ] Low contrast text
- [ ] Non-semantic markup (divs as buttons)
- [ ] Missing focus management in modals
- [ ] Keyboard traps
- [ ] Auto-playing media

**Testing:**
- [ ] Keyboard only navigation
- [ ] Screen reader (NVDA, JAWS, VoiceOver)
- [ ] Color blindness simulation
- [ ] Zoom to 200%
- [ ] Automated tools (axe, Lighthouse)

### 11. Automated Testing

**Tools:**
```bash
# Lighthouse
npx lighthouse https://example.com --only-categories=accessibility

# axe-core
npm install --save-dev @axe-core/cli
npx axe https://example.com

# pa11y
npm install --save-dev pa11y
npx pa11y https://example.com
```

**In tests:**
```javascript
import { axe } from 'jest-axe';

test('should have no accessibility violations', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### 12. WCAG 2.1 Level AA Checklist

**Perceivable:**
- [ ] Text alternatives for non-text content
- [ ] Captions for audio/video
- [ ] Content adaptable (semantic markup)
- [ ] Sufficient color contrast

**Operable:**
- [ ] Keyboard accessible
- [ ] No keyboard traps
- [ ] Adequate time limits (adjustable)
- [ ] No seizure-inducing flashing
- [ ] Skip navigation links
- [ ] Descriptive page titles
- [ ] Focus order makes sense
- [ ] Link purpose clear from context

**Understandable:**
- [ ] Language of page specified (`<html lang="en">`)
- [ ] Predictable navigation
- [ ] Input assistance (labels, instructions, error messages)

**Robust:**
- [ ] Valid HTML
- [ ] Name, role, value for custom widgets
- [ ] Compatible with assistive technologies

## Best Practices

- Build accessibility in from start
- Test with real assistive technologies
- Use semantic HTML first, ARIA second
- Maintain logical document structure
- Provide multiple ways to access content
- Test keyboard navigation thoroughly
- Don't disable zoom
- Use landmarks and headings

## Supporting Files
- `reference/wcag-checklist.md`: Full WCAG 2.1 AA checklist
- `reference/aria-patterns.md`: Common ARIA widget patterns
