---
name: css-development-refactor
description: This skill should be used when refactoring existing CSS from inline styles or utility classes to semantic patterns. Triggers on "refactor CSS", "extract styles", "consolidate CSS", "convert inline", "clean up styles", "migrate to semantic". Transforms to semantic classes with dark mode and tests.
---

# CSS Development: Refactor

## Overview

Transforms existing CSS into semantic component patterns:
- Extract inline styles to semantic classes
- Consolidate utility classes from markup into `@apply` compositions
- Add dark mode variants
- Add test coverage
- Preserve existing functionality (behavior-neutral refactoring)

**This is a sub-skill of `css-development`** - typically invoked automatically via the main skill.

## When This Skill Applies

Use when:
- Converting inline styles to semantic classes
- Extracting repeated utility combinations from markup
- Migrating from pure utility-first to semantic components
- Adding dark mode to existing CSS
- Cleaning up scattered or duplicated CSS

## Pattern Reference

This skill refactors toward patterns documented in the main `css-development` skill:

**Semantic naming:** `.button-primary` not `.btn-blue`
**Tailwind composition:** Use `@apply` to compose utilities
**Dark mode:** Include `dark:` variants
**Composition first:** Reuse existing classes before creating new
**Test coverage:** Static CSS + component rendering tests

## Workflow

When this skill is invoked, create a TodoWrite checklist and refactor systematically.

### Announce Usage

"I'm using the css-development:refactor skill to transform this CSS into semantic component patterns."

### Create TodoWrite Checklist

Use the TodoWrite tool:

```
Refactoring CSS:
- [ ] Analyze existing CSS (identify what needs refactoring)
- [ ] Find repeated patterns (look for duplicated utility combinations)
- [ ] Check existing components (see if patterns already exist)
- [ ] Extract to semantic classes (create new classes using @apply)
- [ ] Include dark mode (add dark: variants to new classes)
- [ ] Update markup (replace inline/utility classes with semantic names)
- [ ] Add tests (write static CSS and rendering tests)
- [ ] Document components (add usage comments)
- [ ] Verify behavior unchanged (ensure visual output matches original)
```

### Refactoring Checklist Details

#### Step 1: Analyze Existing CSS

**Action:** Read and understand the CSS that needs refactoring

**Look for:**
- Inline styles in component files
- Repeated utility class combinations in markup
- CSS scattered across multiple files
- Missing dark mode support
- Lack of semantic class names

**Example patterns to refactor:**

```tsx
// Inline styles
<button style={{ background: 'indigo', padding: '1.5rem 2rem' }}>Click</button>

// Repeated utilities in markup
<button class="bg-indigo-500 hover:bg-indigo-700 px-6 py-3 rounded-lg text-white">
  Click me
</button>
<button class="bg-indigo-500 hover:bg-indigo-700 px-6 py-3 rounded-lg text-white">
  Submit
</button>

// Non-semantic CSS
.btn-blue {
  background: blue;
  padding: 12px 24px;
}
```

**Capture:**
- File locations
- Pattern frequency (how many times repeated)
- Current approach (inline, utilities, old CSS)

**Mark as completed** when analysis is done.

---

#### Step 2: Find Repeated Patterns

**Action:** Identify duplicated utility combinations that should become semantic classes

**Use Grep tool** to search for repeated patterns:

```bash
# Search for common utility combinations
grep -r "bg-indigo-500 hover:bg-indigo-700 px-6 py-3" .
grep -r "rounded-lg shadow-md p-6" .
```

**Categorize patterns:**
- **High frequency** (5+ occurrences): Definitely extract
- **Medium frequency** (2-4 occurrences): Probably extract
- **Low frequency** (1 occurrence): Keep as-is or compose existing classes

**For each pattern:**
- Count occurrences
- List file locations
- Identify semantic purpose (is this a button? card? badge?)

**Mark as completed** when patterns are cataloged.

---

#### Step 3: Check Existing Components

**Action:** Read `styles/components.css` to see if patterns already exist

**Before creating new classes, check:**
- Does a similar class already exist?
- Can existing classes be composed?
- Would a variant of an existing class work?

**Example:**
```
Pattern found: bg-indigo-500 hover:bg-indigo-700 px-6 py-3 rounded-lg text-white
Check: Does .button-primary already exist? YES
Solution: Use .button-primary instead of creating new class
```

**Decision for each pattern:**
- ✅ Use existing class as-is
- ✅ Compose existing classes
- ✅ Create variant of existing class
- ⚠️ Create new class (only if no existing solution)

**Mark as completed** when reuse opportunities are identified.

---

#### Step 4: Extract to Semantic Classes

**Action:** Create new semantic classes in `styles/components.css` for patterns that need extraction

**For each pattern being extracted:**

1. **Choose semantic name** following existing patterns
2. **Write CSS class** using `@apply`
3. **Include dark mode** variants
4. **Add documentation** comment

**Example extraction:**

**Before (in markup):**
```tsx
<button class="bg-indigo-500 hover:bg-indigo-700 px-6 py-3 rounded-lg text-white transition-all duration-200">
  Click me
</button>
```

**After (in components.css):**
```css
/* Primary button - Main call-to-action button with hover states
   Usage: <button className="button-primary">Click me</button> */
.button-primary {
  @apply bg-indigo-500 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-800;
  @apply px-6 py-3 rounded-lg text-white;
  @apply transition-all duration-200;
}
```

**Use Edit tool** to add each new class to components.css

**Mark as completed** when all semantic classes are created.

---

#### Step 5: Include Dark Mode

**Action:** Ensure all new/refactored classes have `dark:` variants

**For each class created in Step 4:**
- Add `dark:` variants for backgrounds
- Add `dark:` variants for text colors
- Add `dark:` variants for borders
- Test in dark mode (if possible)

**Pattern:**
```css
.component {
  @apply bg-white dark:bg-gray-800;
  @apply text-gray-900 dark:text-white;
  @apply border-gray-200 dark:border-gray-700;
}
```

**Mark as completed** when dark mode coverage is added.

---

#### Step 6: Update Markup

**Action:** Replace inline styles and utility classes with semantic class names

**For each file using the old pattern:**

1. **Read the file** with Read tool
2. **Use Edit tool** to replace old pattern with semantic class
3. **Verify** the replacement is correct

**Example:**

**Before:**
```tsx
<button class="bg-indigo-500 hover:bg-indigo-700 px-6 py-3 rounded-lg text-white">
  Click me
</button>
```

**After:**
```tsx
<button class="button-primary">
  Click me
</button>
```

**Handle custom classes:**
```tsx
<!-- If there were additional custom classes, preserve them -->
<button class="button-primary w-full mt-4">
  Click me
</button>
```

**Track changes:**
- Count files updated
- Count instances replaced
- Note any edge cases

**Mark as completed** when all markup is updated.

---

#### Step 7: Add Tests

**Action:** Add test coverage for refactored components

**Static CSS test** in `styles/__tests__/components.test.ts`:
```typescript
it('should have button-primary class', () => {
  const content = readFileSync('styles/components.css', 'utf-8');
  expect(content).toContain('.button-primary');
});

it('should have dark mode variants in button-primary', () => {
  const content = readFileSync('styles/components.css', 'utf-8');
  expect(content).toContain('dark:bg-indigo');
});
```

**Component rendering test** (if applicable):
```typescript
it('applies button-primary class after refactor', () => {
  render(<Button variant="primary">Click</Button>);
  expect(screen.getByRole('button')).toHaveClass('button-primary');
});
```

**Run tests** to ensure they pass:
```bash
npm test
```

**Mark as completed** when tests are added and passing.

---

#### Step 8: Document Components

**Action:** Ensure all refactored classes have documentation

**Documentation includes:**
- Comment in CSS explaining purpose
- Usage example
- Migration notes (if helpful)

**Example:**
```css
/* Primary button - Main CTA button (refactored from inline utilities)
   Usage: <button className="button-primary">Click me</button>
   Replaces: bg-indigo-500 hover:bg-indigo-700 px-6 py-3 rounded-lg text-white */
.button-primary {
  @apply bg-indigo-500 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-800;
  @apply px-6 py-3 rounded-lg text-white;
  @apply transition-all duration-200;
}
```

**Mark as completed** when documentation is added.

---

#### Step 9: Verify Behavior Unchanged

**Action:** Ensure visual output and behavior match the original

**Verification steps:**

1. **Run tests** (if project has them):
   ```bash
   npm test
   ```

2. **Visual inspection** (if possible):
   - Start dev server
   - Check refactored components look the same
   - Test in light and dark mode
   - Test interactive states (hover, focus, active)

3. **Check for regressions:**
   - Compare before/after screenshots (if available)
   - Verify no console errors
   - Check responsive behavior

**If behavior changed:**
- Identify the difference
- Fix the semantic class to match original behavior
- Re-test

**Behavior must be preserved** - refactoring should be visually neutral

**Mark as completed** when behavior is verified unchanged.

---

### Completion

When all checklist items are completed:

1. **Generate summary** of refactoring work:

```markdown
## CSS Refactoring Summary

### Changes Made

**Semantic classes created:**
- `.button-primary` (extracted from 8 instances across 5 files)
- `.card` (extracted from 12 instances across 7 files)
- `.badge-success` (extracted from 4 instances across 3 files)

**Files modified:**
- `styles/components.css` (+45 lines, 3 new classes)
- `components/Button.tsx` (replaced utilities with .button-primary)
- `components/Card.tsx` (replaced utilities with .card)
- `components/Badge.tsx` (replaced utilities with .badge-success)
- `styles/__tests__/components.test.ts` (+12 lines, 3 new tests)

**Dark mode support:**
- ✅ All refactored classes include dark: variants
- ✅ Tested in both light and dark mode

**Test coverage:**
- ✅ Static CSS tests added for all new classes
- ✅ Component rendering tests updated
- ✅ All tests passing

**Behavior verification:**
- ✅ Visual output matches original
- ✅ No console errors
- ✅ Interactive states work correctly

### Impact

**Code reduction:**
- Removed 247 lines of repeated utility classes from markup
- Added 45 lines of semantic CSS
- Net reduction: 202 lines

**Maintainability:**
- Styling centralized in components.css
- Changes now made in one place instead of many
- Consistent component appearance

**Dark mode:**
- Added dark mode support that didn't exist before
- All components now work in light and dark themes
```

2. **Suggest next steps:**
   - Commit the refactoring
   - Document the new patterns for the team
   - Continue refactoring other components

3. **Offer validation:**
   "Would you like me to validate the refactored CSS using the css-development:validate skill?"

**Mark as completed** when summary is presented.
