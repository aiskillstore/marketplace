---
name: css-development-create-component
description: This skill should be used when creating new styled components or adding new CSS classes. Triggers on "create component", "new button", "new card", "add styles", "style component", "build UI element". Guides semantic naming, Tailwind composition, dark mode support, and test coverage.
---

# CSS Development: Create Component

## Overview

Guides you through creating new CSS components following established patterns:
- Semantic class naming
- Tailwind utility composition via `@apply`
- Dark mode support by default
- Test coverage (static CSS + component rendering)
- Composition over creation (reuse existing classes)

**This is a sub-skill of `css-development`** - typically invoked automatically via the main skill.

## When This Skill Applies

Use when:
- Creating a new styled component (button, card, form field, etc.)
- Adding new semantic CSS classes to components.css
- Building reusable UI patterns
- Need to ensure dark mode support and test coverage

## Pattern Reference

This skill follows the patterns documented in the main `css-development` skill. Key patterns:

**Semantic naming:** `.button-primary` not `.btn-blue`
**Tailwind composition:** Use `@apply` to compose utilities
**Dark mode:** Include `dark:` variants by default
**Composition first:** Check if existing classes can be combined
**Test coverage:** Static CSS tests + component rendering tests

## Workflow

When this skill is invoked, create a TodoWrite checklist and work through it step-by-step.

### Announce Usage

First, announce that you're using this skill:

"I'm using the css-development:create-component skill to guide creating this new CSS component."

### Create TodoWrite Checklist

Use the TodoWrite tool to create this checklist:

```
Creating CSS Component:
- [ ] Survey existing components (read components.css)
- [ ] Check if composition solves it (can existing classes combine?)
- [ ] Identify component type (atom/molecule/organism if new class needed)
- [ ] Choose semantic name (follow existing naming patterns)
- [ ] Write component class (use @apply, include dark: variants)
- [ ] Create markup integration (show React/HTML usage)
- [ ] Write static CSS test (verify class exists)
- [ ] Write component rendering test (verify className application)
- [ ] Document component (add usage comment)
```

### Step-by-Step Details

#### Step 1: Survey Existing Components

**Action:** Use the Read tool to read `styles/components.css`

**Purpose:** Understand what already exists to ensure consistency and identify reuse opportunities

**What to look for:**
- Similar components that could be composed
- Existing naming patterns to follow
- Common patterns (button variants, card styles, etc.)

**Mark as in_progress** before starting, **mark as completed** when done.

---

#### Step 2: Check if Composition Solves It

**Action:** Analyze if combining existing classes achieves the goal

**Examples:**
- Want a "primary button with icon"? → Combine `.button-primary` + spacing utilities
- Want a "card with shadow"? → Use `.card` if it exists, add utility class if needed
- Want a "highlighted badge"? → Combine `.badge` + color utilities

**YAGNI principle:** Only create a new class if composition doesn't work or creates excessive duplication in markup.

**Decision:**
- **If composition works:** Document the combination and SKIP remaining steps (no new class needed)
- **If new class needed:** Continue to Step 3

**Mark as completed** when decision is made.

---

#### Step 3: Identify Component Type

**Action:** Determine atomic design level (if creating new class)

**Atoms** - Basic building blocks:
- Single-purpose elements
- Examples: `.button`, `.input`, `.badge`, `.spinner`, `.link`

**Molecules** - Composed components:
- Combine multiple atoms
- Examples: `.card`, `.form-field`, `.empty-state`, `.alert`

**Organisms** - Complex components:
- Multiple molecules + atoms
- Examples: `.page-layout`, `.navigation`, `.session-card`, `.conversation-timeline`

**Why this matters:** Helps scope complexity and dependencies

**Mark as completed** when type is identified.

---

#### Step 4: Choose Semantic Name

**Action:** Choose a descriptive, semantic class name following existing patterns

**Naming patterns from reference codebase:**
- **Base + variant:** `.button-primary`, `.button-secondary`, `.button-danger`
- **Component + sub-element:** `.card-title`, `.card-description`, `.form-field`
- **Context + component:** `.session-card`, `.marketing-hero`, `.dashboard-layout`
- **State modifiers:** `.session-card-active`, `.button-disabled`

**Anti-patterns (avoid):**
- Utility names: `.btn-blue`, `.card-sm`, `.text-big`
- Abbreviations: `.btn`, `.hdr`, `.desc`
- Generic: `.component`, `.item`, `.thing`

**Validation:** Name should clearly indicate purpose and fit existing patterns

**Mark as completed** when name is chosen.

---

#### Step 5: Write Component Class

**Action:** Create the CSS class in `styles/components.css` using Edit tool

**Template:**
```css
/* [Component name] - [Brief description]
   Usage: <[element] className="[class-name]">[content]</[element]> */
.[class-name] {
  @apply [background-utilities] [dark-variants];
  @apply [spacing-utilities];
  @apply [typography-utilities];
  @apply [transition-utilities];
}
```

**Required elements:**
1. **Documentation comment** - What it is, how to use it
2. **Dark mode variants** - Include `dark:` for colors/backgrounds
3. **Logical grouping** - Group related utilities (background, spacing, typography, transitions)
4. **Interactive states** - Include hover/focus/active if applicable

**Example:**
```css
/* Primary button - Main call-to-action button with hover lift effect
   Usage: <button className="button-primary">Click me</button> */
.button-primary {
  @apply bg-indigo-500 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-800;
  @apply px-6 py-3 rounded-lg font-medium text-white;
  @apply transition-all duration-200 hover:-translate-y-0.5;
  @apply focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2;
}
```

**Use Edit tool to add to existing file** (don't overwrite entire file)

**Mark as completed** when class is written to file.

---

#### Step 6: Create Markup Integration

**Action:** Document how to use the component in different frameworks

**Show usage examples for:**
- React (if project uses React)
- Vanilla HTML (always show this)
- Vue or other frameworks (if project uses them)

**Example documentation:**

```markdown
## Using the button-primary Component

**React:**
```tsx
const Button = ({ variant = 'primary', className = '', children, ...props }) => {
  const classes = `button-${variant} ${className}`.trim();
  return <button className={classes} {...props}>{children}</button>;
};

// Usage
<Button variant="primary">Click me</Button>
<Button variant="primary" className="w-full">Full width</Button>
```

**Vanilla HTML:**
```html
<button class="button-primary">Click me</button>
<button class="button-primary custom-class">With custom class</button>
```
```

**Where to put this:** In project documentation, README, or as a comment in the component file

**Mark as completed** when markup examples are documented.

---

#### Step 7: Write Static CSS Test

**Action:** Add test to `styles/__tests__/components.test.ts` (or create if doesn't exist)

**Purpose:** Verify the CSS class exists in the components.css file

**Test pattern:**
```typescript
import { readFileSync } from 'fs';
import { describe, it, expect } from 'vitest';

describe('components.css', () => {
  const content = readFileSync('styles/components.css', 'utf-8');

  it('should have button-primary component class', () => {
    expect(content).toContain('.button-primary');
  });

  it('should have button-primary dark mode variants', () => {
    expect(content).toContain('dark:bg-indigo');
  });
});
```

**Key checks:**
- Class exists in file
- Dark mode variants present (search for `dark:`)
- Documentation comment exists (optional but good)

**Run test:**
```bash
npm test styles/__tests__/components.test.ts
# or
vitest styles/__tests__/components.test.ts
```

**Expected:** Test passes (green)

**Mark as completed** when test is written and passing.

---

#### Step 8: Write Component Rendering Test

**Action:** Add component rendering test (framework-specific)

**Purpose:** Verify className application works in actual components

**React example:**
```typescript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Button } from '@/components/atoms/Button';

describe('Button component', () => {
  it('applies button-primary class', () => {
    render(<Button variant="primary">Click</Button>);
    expect(screen.getByRole('button')).toHaveClass('button-primary');
  });

  it('accepts and applies custom className', () => {
    render(<Button variant="primary" className="custom-class">Click</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('button-primary', 'custom-class');
  });
});
```

**Key checks:**
- Semantic class is applied
- Custom className can be added
- Classes don't conflict

**Run test:**
```bash
npm test components/atoms/Button.test.tsx
# or
vitest components/atoms/Button.test.tsx
```

**Expected:** Test passes (green)

**Mark as completed** when test is written and passing.

---

#### Step 9: Document Component

**Action:** Ensure component has usage documentation

**Documentation should include:**
1. **Comment in CSS** - Already done in Step 5
2. **Markup examples** - Already done in Step 6
3. **Component API** (for framework components) - Props, variants, etc.

**Additional documentation (optional but recommended):**
- Add to component style guide if project has one
- Add to Storybook if project uses it
- Add visual examples or screenshots

**Minimum requirement:** CSS comment + markup examples exist

**Mark as completed** when documentation is verified.

---

### Completion

When all checklist items are completed:

1. **Run all tests** to ensure everything passes:
   ```bash
   npm test
   ```

2. **Show summary** of what was created:
   - Component class name and file location
   - Test file locations
   - Documentation locations

3. **Suggest next steps:**
   - Commit the changes
   - Create related variants if needed
   - Use the component in actual UI

**Example summary:**
```
Created button-primary component!

Files created/modified:
- styles/components.css (added .button-primary)
- styles/__tests__/components.test.ts (added static CSS test)
- components/atoms/Button.test.tsx (added rendering test)
- components/atoms/Button.tsx (markup integration)

Next steps:
- Commit these changes: git add . && git commit -m "feat: add button-primary component"
- Use in your UI: <Button variant="primary">Click me</Button>
- Create variants if needed: button-secondary, button-danger, etc.
```
