---
name: web-accessibility
description: Implement web accessibility (a11y) standards following WCAG 2.1 guidelines. Use when building accessible UIs, fixing accessibility issues, or ensuring compliance with disability standards. Handles ARIA attributes, keyboard navigation, screen readers, semantic HTML, and accessibility testing.
metadata:
  tags: accessibility, a11y, WCAG, ARIA, semantic-HTML, screen-reader
  platforms: Claude, ChatGPT, Gemini
---


# Web Accessibility (A11y)


## When to use this skill

- **New UI Component Development**: Designing accessible components
- **Accessibility Audit**: Identifying and fixing accessibility issues in existing sites
- **Form Implementation**: Writing screen reader-friendly forms
- **Modals/Dropdowns**: Focus management and keyboard trap prevention
- **WCAG Compliance**: Meeting legal requirements or standards

## Input Format

### Required Information
- **Framework**: React, Vue, Svelte, Vanilla JS, etc.
- **Component Type**: Button, Form, Modal, Dropdown, Navigation, etc.
- **WCAG Level**: A, AA, AAA (default: AA)

### Optional Information
- **Screen Reader**: NVDA, JAWS, VoiceOver (for testing)
- **Automated Testing Tool**: axe-core, Pa11y, Lighthouse (default: axe-core)
- **Browser**: Chrome, Firefox, Safari (default: Chrome)

### Input Example

```
Make a React modal component accessible:
- Framework: React + TypeScript
- WCAG Level: AA
- Requirements:
  - Focus trap (focus stays inside the modal)
  - Close with ESC key
  - Close by clicking the background
  - Title/description read by screen readers
```

## Instructions

### Step 1: Use Semantic HTML

Use meaningful HTML elements to make the structure clear.

**Tasks**:
- Use semantic tags: `<button>`, `<nav>`, `<main>`, `<header>`, `<footer>`, etc.
- Avoid overusing `<div>` and `<span>`
- Use heading hierarchy (`<h1>` ~ `<h6>`) correctly
- Connect `<label>` with `<input>`

**Example** (❌ Bad vs ✅ Good):
```html
<!-- ❌ Bad example: using only div and span -->
<div class="header">
  <span class="title">My App</span>
  <div class="nav">
    <div class="nav-item" onclick="navigate()">Home</div>
    <div class="nav-item" onclick="navigate()">About</div>
  </div>
</div>

<!-- ✅ Good example: semantic HTML -->
<header>
  <h1>My App</h1>
  <nav aria-label="Main navigation">
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/about">About</a></li>
    </ul>
  </nav>
</header>
```

**Form Example**:
```html
<!-- ❌ Bad example: no label -->
<input type="text" placeholder="Enter your name">

<!-- ✅ Good example: label connected -->
<label for="name">Name:</label>
<input type="text" id="name" name="name" required>

<!-- Or wrap with label -->
<label>
  Email:
  <input type="email" name="email" required>
</label>
```

### Step 2: Implement Keyboard Navigation

Ensure all features are usable without a mouse.

**Tasks**:
- Move focus with Tab and Shift+Tab
- Activate buttons with Enter/Space
- Navigate lists/menus with arrow keys
- Close modals/dropdowns with ESC
- Use `tabindex` appropriately

**Decision Criteria**:
- Interactive elements → `tabindex="0"` (focusable)
- Exclude from focus order → `tabindex="-1"` (programmatic focus only)
- Do not change focus order → avoid using `tabindex="1+"`

**Example** (React Dropdown):
```typescript
import React, { useState, useRef, useEffect } from 'react';

interface DropdownProps {
  label: string;
  options: { value: string; label: string }[];
  onChange: (value: string) => void;
}

function AccessibleDropdown({ label, options, onChange }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  // Keyboard handler
  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setSelectedIndex((prev) => (prev + 1) % options.length);
        }
        break;

      case 'ArrowUp':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setSelectedIndex((prev) => (prev - 1 + options.length) % options.length);
        }
        break;

      case 'Enter':
      case ' ':
        e.preventDefault();
        if (isOpen) {
          onChange(options[selectedIndex].value);
          setIsOpen(false);
          buttonRef.current?.focus();
        } else {
          setIsOpen(true);
        }
        break;

      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        buttonRef.current?.focus();
        break;
    }
  };

  return (
    <div className="dropdown">
      <button
        ref={buttonRef}
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-labelledby="dropdown-label"
      >
        {label}
      </button>

      {isOpen && (
        <ul
          ref={listRef}
          role="listbox"
          aria-labelledby="dropdown-label"
          onKeyDown={handleKeyDown}
          tabIndex={-1}
        >
          {options.map((option, index) => (
            <li
              key={option.value}
              role="option"
              aria-selected={index === selectedIndex}
              onClick={() => {
                onChange(option.value);
                setIsOpen(false);
              }}
            >
              {option.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

### Step 3: Add ARIA Attributes

Provide additional context for screen readers.

**Tasks**:
- `aria-label`: Define the element's name
- `aria-labelledby`: Reference another element as a label
- `aria-describedby`: Provide additional description
- `aria-live`: Announce dynamic content changes
- `aria-hidden`: Hide from screen readers

**Checklist**:
- [x] All interactive elements have clear labels
- [x] Button purpose is clear (e.g., "Submit form" not "Click")
- [x] State change announcements (aria-live)
- [x] Decorative images use alt="" or aria-hidden="true"

**Example** (Modal):
```tsx
function AccessibleModal({ isOpen, onClose, title, children }) {
  const modalRef = useRef<HTMLDivElement>(null);

  // Focus trap when modal opens
  useEffect(() => {
    if (isOpen) {
      modalRef.current?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby="modal-description"
      ref={modalRef}
      tabIndex={-1}
      onKeyDown={(e) => {
        if (e.key === 'Escape') {
          onClose();
        }
      }}
    >
      <div className="modal-overlay" onClick={onClose} aria-hidden="true" />

      <div className="modal-content">
        <h2 id="modal-title">{title}</h2>
        <div id="modal-description">
          {children}
        </div>

        <button onClick={onClose} aria-label="Close modal">
          <span aria-hidden="true">×</span>
        </button>
      </div>
    </div>
  );
}
```

**aria-live Example** (Notifications):
```tsx
function Notification({ message, type }: { message: string; type: 'success' | 'error' }) {
  return (
    <div
      role="alert"
      aria-live="assertive"  // Immediate announcement (error), "polite" announces in turn
      aria-atomic="true"     // Read the entire content
      className={`notification notification-${type}`}
    >
      {type === 'error' && <span aria-label="Error">⚠️</span>}
      {type === 'success' && <span aria-label="Success">✅</span>}
      {message}
    </div>
  );
}
```

### Step 4: Color Contrast and Visual Accessibility

Ensure sufficient contrast ratios for users with visual impairments.

**Tasks**:
- WCAG AA: text 4.5:1, large text 3:1
- WCAG AAA: text 7:1, large text 4.5:1
- Do not convey information by color alone (use icons, patterns alongside)
- Clearly indicate focus (outline)

**Example** (CSS):
```css
/* ✅ Sufficient contrast (text #000 on #FFF = 21:1) */
.button {
  background-color: #0066cc;
  color: #ffffff;  /* contrast ratio 7.7:1 */
}

/* ✅ Focus indicator */
button:focus,
a:focus {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
}

/* ❌ outline: none is forbidden! */
button:focus {
  outline: none;  /* Never use this */
}

/* ✅ Indicate state with color + icon */
.error-message {
  color: #d32f2f;
  border-left: 4px solid #d32f2f;
}

.error-message::before {
  content: '⚠️';
  margin-right: 8px;
}
```

### Step 5: Accessibility Testing

Validate accessibility with automated and manual testing.

**Tasks**:
- Automated scan with axe DevTools
- Check Lighthouse Accessibility score
- Test all features with keyboard only
- Screen reader testing (NVDA, VoiceOver)

**Example** (Jest + axe-core):
```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import AccessibleButton from './AccessibleButton';

expect.extend(toHaveNoViolations);

describe('AccessibleButton', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <AccessibleButton onClick={() => {}}>
        Click Me
      </AccessibleButton>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should be keyboard accessible', () => {
    const handleClick = jest.fn();
    const { getByRole } = render(
      <AccessibleButton onClick={handleClick}>
        Click Me
      </AccessibleButton>
    );

    const button = getByRole('button');

    // Enter key
    button.focus();
    fireEvent.keyDown(button, { key: 'Enter' });
    expect(handleClick).toHaveBeenCalled();

    // Space key
    fireEvent.keyDown(button, { key: ' ' });
    expect(handleClick).toHaveBeenCalledTimes(2);
  });
});
```

## Output format

### Basic Checklist

```markdown
## Accessibility Checklist

### Semantic HTML
- [x] Use semantic HTML tags (`<button>`, `<nav>`, `<main>`, etc.)
- [x] Heading hierarchy is correct (h1 → h2 → h3)
- [x] All form labels are connected

### Keyboard Navigation
- [x] All interactive elements accessible via Tab
- [x] Buttons activated with Enter/Space
- [x] Modals/dropdowns closed with ESC
- [x] Focus indicator is clear (outline)

### ARIA
- [x] `role` used appropriately
- [x] `aria-label` or `aria-labelledby` provided
- [x] `aria-live` used for dynamic content
- [x] Decorative elements use `aria-hidden="true"`

### Visual
- [x] Color contrast meets WCAG AA (4.5:1)
- [x] Information not conveyed by color alone
- [x] Text size can be adjusted
- [x] Responsive design

### Testing
- [x] 0 axe DevTools violations
- [x] Lighthouse Accessibility score 90+
- [x] Keyboard test passed
- [x] Screen reader test completed
```

## Constraints

### Mandatory Rules (MUST)

1. **Keyboard Accessibility**: All features must be usable without a mouse
   - Support Tab, Enter, Space, arrow keys, and ESC
   - Implement focus trap (for modals)

2. **Alternative Text**: All images must have an `alt` attribute
   - Meaningful images: descriptive alt text
   - Decorative images: `alt=""` (screen reader ignores)

3. **Clear Labels**: All form inputs must have an associated label
   - `<label for="...">` or `aria-label`
   - Do not use placeholder alone as a substitute for a label

### Prohibited Actions (MUST NOT)

1. **Do Not Remove Outline**: Never use `outline: none`
   - Disastrous for keyboard users
   - Must provide a custom focus style instead

2. **Do Not Use tabindex > 0**: Avoid changing focus order
   - Keep DOM order logical
   - Exception: only when there is a special reason

3. **Do Not Convey Information by Color Alone**: Accompany with icons or text
   - Consider users with color blindness
   - e.g., "Click red item" → "Click ⚠️ Error item"

## Examples

### Example 1: Accessible Form

```tsx
function AccessibleContactForm() {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

  return (
    <form onSubmit={handleSubmit} noValidate>
      <h2 id="form-title">Contact Us</h2>
      <p id="form-description">Please fill out the form below to get in touch.</p>

      {/* Name */}
      <div className="form-group">
        <label htmlFor="name">
          Name <span aria-label="required">*</span>
        </label>
        <input
          type="text"
          id="name"
          name="name"
          required
          aria-required="true"
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'name-error' : undefined}
        />
        {errors.name && (
          <span id="name-error" role="alert" className="error">
            {errors.name}
          </span>
        )}
      </div>

      {/* Email */}
      <div className="form-group">
        <label htmlFor="email">
          Email <span aria-label="required">*</span>
        </label>
        <input
          type="email"
          id="email"
          name="email"
          required
          aria-required="true"
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : 'email-hint'}
        />
        <span id="email-hint" className="hint">
          We'll never share your email.
        </span>
        {errors.email && (
          <span id="email-error" role="alert" className="error">
            {errors.email}
          </span>
        )}
      </div>

      {/* Submit button */}
      <button type="submit" disabled={submitStatus === 'loading'}>
        {submitStatus === 'loading' ? 'Submitting...' : 'Submit'}
      </button>

      {/* Success/failure messages */}
      {submitStatus === 'success' && (
        <div role="alert" aria-live="polite" className="success">
          ✅ Form submitted successfully!
        </div>
      )}

      {submitStatus === 'error' && (
        <div role="alert" aria-live="assertive" className="error">
          ⚠️ An error occurred. Please try again.
        </div>
      )}
    </form>
  );
}
```

### Example 2: Accessible Tab UI

```tsx
function AccessibleTabs({ tabs }: { tabs: { id: string; label: string; content: React.ReactNode }[] }) {
  const [activeTab, setActiveTab] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'ArrowRight':
        e.preventDefault();
        setActiveTab((index + 1) % tabs.length);
        break;
      case 'ArrowLeft':
        e.preventDefault();
        setActiveTab((index - 1 + tabs.length) % tabs.length);
        break;
      case 'Home':
        e.preventDefault();
        setActiveTab(0);
        break;
      case 'End':
        e.preventDefault();
        setActiveTab(tabs.length - 1);
        break;
    }
  };

  return (
    <div>
      {/* Tab List */}
      <div role="tablist" aria-label="Content sections">
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            role="tab"
            id={`tab-${tab.id}`}
            aria-selected={activeTab === index}
            aria-controls={`panel-${tab.id}`}
            tabIndex={activeTab === index ? 0 : -1}
            onClick={() => setActiveTab(index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      {tabs.map((tab, index) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== index}
          tabIndex={0}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
}
```

## Best practices

1. **Semantic HTML First**: ARIA is a last resort
   - Using the correct HTML element makes ARIA unnecessary
   - e.g., `<button>` vs `<div role="button">`

2. **Focus Management**: Manage focus on page transitions in SPAs
   - Move focus to main content on new page load
   - Provide skip links ("Skip to main content")

3. **Error Messages**: Clear and helpful error messages
   - "Invalid input" ❌ → "Email must be in format: example@domain.com" ✅

## References

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN ARIA](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA)
- [WebAIM](https://webaim.org/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [A11y Project](https://www.a11yproject.com/)

## Metadata

### Version
- **Current Version**: 1.0.0
- **Last Updated**: 2025-01-01
- **Compatible Platforms**: Claude, ChatGPT, Gemini

### Related Skills
- [ui-component-patterns](../ui-component-patterns/SKILL.md): UI component implementation
- [responsive-design](../responsive-design/SKILL.md): Responsive design

### Tags
`#accessibility` `#a11y` `#WCAG` `#ARIA` `#screen-reader` `#keyboard-navigation` `#frontend`
