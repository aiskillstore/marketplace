---
title: Use Web-First Assertions Instead of Generic Expect
impact: HIGH
impactDescription: Eliminates 50-70% of flaky assertions through auto-waiting and retries
tags: assertions, auto-waiting, stability, web-first
---

## Use Web-First Assertions Instead of Generic Expect

**Impact: HIGH (eliminates 50-70% of flaky assertions through auto-waiting and retries)**

Playwright's web-first assertions automatically wait and retry until the expected condition is met. Using generic `expect()` statements without auto-waiting leads to flaky tests that fail intermittently when elements aren't immediately ready. Web-first assertions make tests both more reliable and more concise.

## When to Use

- **Use web-first assertions for**: All DOM-related checks (visibility, text content, attributes, CSS, element state, counts)
- **Use generic expect for**: API responses, non-DOM JavaScript values, test logic calculations, non-retryable conditions
- **Always prefer web-first when**: Checking anything rendered in the browser, working with locators, verifying UI state
- **Required for**: All projects - web-first assertions are fundamental to Playwright test stability

## Guidelines

### Do

- Use `await expect(locator).toBeVisible()` instead of `expect(await locator.isVisible()).toBe(true)`
- Use `await expect(locator).toHaveText()` instead of `expect(await locator.textContent()).toBe()`
- Use `await expect(locator).toHaveCount()` for checking number of elements
- Use `.not.` for negative assertions (e.g., `.not.toBeVisible()`)
- Use soft assertions (`expect.soft()`) when you want to continue test execution after failures
- Chain locator filters before assertions (e.g., `locator.filter({ hasText: 'Active' })`)
- Set custom timeouts for slow operations (`{ timeout: 30000 }`)

### Don't

- Don't extract DOM values and use generic expect - use web-first assertions directly
- Don't manually wait for selectors before assertions - web-first assertions auto-wait
- Don't use `isVisible()`, `textContent()`, `getAttribute()` with generic expect
- Don't forget to `await` web-first assertions - they return promises
- Don't use web-first assertions for API responses or non-DOM values
- Don't use overly long timeouts by default - configure reasonable defaults in playwright.config.ts

### Tool Usage Patterns

- **Text assertions**: `toHaveText()`, `toContainText()`, `toHaveValue()`
- **Visibility assertions**: `toBeVisible()`, `toBeHidden()`, `toBeAttached()`
- **State assertions**: `toBeEnabled()`, `toBeDisabled()`, `toBeChecked()`, `toBeEditable()`, `toBeFocused()`, `toBeEmpty()`
- **Attribute assertions**: `toHaveAttribute()`, `toHaveClass()`, `toHaveId()`, `toHaveCSS()`
- **Count assertions**: `toHaveCount()`
- **Page assertions**: `toHaveURL()`, `toHaveTitle()`
- **Screenshot assertions**: `toHaveScreenshot()`
- **Configuration**: Set default assertion timeout in playwright.config.ts with `expect.timeout` (default: 5s)

**Incorrect (generic expect without waiting):**

```typescript
import { test, expect } from '@playwright/test';

test('bad - generic expect', async ({ page }) => {
  await page.goto('https://example.com');
  await page.click('button.load-data');
  
  // ❌ No auto-waiting - fails if element not immediately ready
  const text = await page.locator('.result').textContent();
  expect(text).toBe('Success');
  
  // ❌ Checking visibility without retries
  const isVisible = await page.locator('.message').isVisible();
  expect(isVisible).toBe(true);
  
  // ❌ Manual waiting then generic assertion
  await page.waitForSelector('.status');
  const status = await page.locator('.status').textContent();
  expect(status).toContain('Complete');
  
  // ❌ Array operations without auto-waiting
  const items = await page.locator('.item').allTextContents();
  expect(items).toHaveLength(5);
  
  // ❌ Attribute checking without retries
  const className = await page.locator('button').getAttribute('class');
  expect(className).toContain('active');
});
```

**Correct (web-first assertions with auto-waiting):**

```typescript
import { test, expect } from '@playwright/test';

test('good - web-first assertions', async ({ page }) => {
  await page.goto('https://example.com');
  await page.click('button.load-data');
  
  // ✅ Auto-waits and retries until text matches
  await expect(page.locator('.result')).toHaveText('Success');
  
  // ✅ Auto-waits for element to be visible
  await expect(page.locator('.message')).toBeVisible();
  
  // ✅ Auto-waits and checks text content
  await expect(page.locator('.status')).toContainText('Complete');
  
  // ✅ Auto-waits for correct count
  await expect(page.locator('.item')).toHaveCount(5);
  
  // ✅ Auto-waits and checks attribute
  await expect(page.locator('button')).toHaveClass(/active/);
  
  // ✅ Checks element state with retries
  await expect(page.locator('button')).toBeEnabled();
  await expect(page.locator('input')).toBeEditable();
  await expect(page.locator('input')).toBeFocused();
});
```

## Edge Cases and Constraints

### Limitations

- Web-first assertions have default 5s timeout (shorter than action timeout of 30s)
- Soft assertions collect failures but still fail the test at the end
- Screenshot assertions may be flaky across different environments (OS, browser versions)
- `toHaveCSS()` requires exact RGB color values, not color names
- Regex patterns in assertions must account for whitespace and formatting differences

### Edge Cases

1. **Dynamic text with whitespace**: Text content may have extra spaces, newlines, or formatting. Solution: Use `toContainText()` with trimmed strings or regex patterns.

2. **Multiple elements matching selector**: When locator matches multiple elements, some assertions behave differently. Solution: Use `.first()`, `.last()`, `.nth()`, or filter to narrow down.

3. **Element exists but is covered by overlay**: `toBeVisible()` may pass but element can't be interacted with. Solution: Check z-index or use `toBeInViewport()` in addition to `toBeVisible()`.

4. **Text updates during retry period**: If text changes frequently, assertion may never stabilize. Solution: Use longer timeout or wait for stable state first.

5. **Negative assertions completing immediately**: `.not.toBeVisible()` succeeds as soon as element is hidden, not waiting full timeout. Solution: This is usually desired behavior, but be aware it's not symmetric with positive assertions.

6. **CSS assertions on computed styles**: Some CSS properties are computed and may not match expected values. Solution: Use browser DevTools to verify actual computed style values.

### What Breaks If Ignored

- **Using generic expect for DOM**: 50-70% increase in flaky tests, immediate failures without retries
- **Not awaiting assertions**: Assertions don't execute, tests pass incorrectly
- **Manual waits before assertions**: Tests are slower, more complex code, still prone to race conditions
- **Wrong assertion type**: Using `toHaveText()` when you need `toContainText()` causes failures on whitespace differences

## Common Mistakes

### Mistake 1: Extracting value then using generic expect

```typescript
// ❌ Bad: Extract value and use generic expect
test('bad pattern', async ({ page }) => {
  await page.goto('https://example.com');
  const text = await page.locator('h1').textContent();
  expect(text).toBe('Welcome'); // ❌ No retries if element loads slowly
});
```

**Why this is wrong**: Extracts value at one point in time, no retries if element isn't ready.

**How to fix**:

```typescript
// ✅ Good: Use web-first assertion
test('good pattern', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page.locator('h1')).toHaveText('Welcome'); // ✅ Auto-retries
});
```

### Mistake 2: Forgetting to await assertions

```typescript
// ❌ Bad: Missing await
test('missing await', async ({ page }) => {
  await page.goto('https://example.com');
  expect(page.locator('h1')).toHaveText('Welcome'); // ❌ Returns promise, doesn't execute!
});
```

**Why this is wrong**: Assertion returns a promise that's never awaited, test passes incorrectly.

**How to fix**:

```typescript
// ✅ Good: Always await web-first assertions
test('with await', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page.locator('h1')).toHaveText('Welcome'); // ✅ Properly awaited
});
```

### Mistake 3: Using web-first assertions for API responses

```typescript
// ❌ Bad: Web-first assertion for non-DOM
test('wrong assertion type', async ({ request }) => {
  const response = await request.get('https://api.example.com/data');
  await expect(response.status()).toBe(200); // ❌ Unnecessary await, wrong pattern
});
```

**Why this is wrong**: Web-first assertions are for DOM elements, API responses don't need retries.

**How to fix**:

```typescript
// ✅ Good: Use generic expect for API responses
test('correct pattern', async ({ request }) => {
  const response = await request.get('https://api.example.com/data');
  expect(response.status()).toBe(200); // ✅ No await needed
  
  const data = await response.json();
  expect(data.items).toHaveLength(10); // ✅ Generic expect for data
});
```

### Mistake 4: Not using .not for negative assertions

```typescript
// ❌ Bad: Extract boolean and check with generic expect
test('bad negative check', async ({ page }) => {
  await page.goto('https://example.com');
  const isVisible = await page.locator('.error').isVisible();
  expect(isVisible).toBe(false); // ❌ No retries
});
```

**Why this is wrong**: Extracts boolean at one point, doesn't retry until condition is met.

**How to fix**:

```typescript
// ✅ Good: Use .not with web-first assertion
test('good negative check', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page.locator('.error')).not.toBeVisible(); // ✅ Retries
});
```

### Mistake 5: Using wrong text assertion method

```typescript
// ❌ Bad: Using toHaveText with partial text
test('strict text check', async ({ page }) => {
  await page.goto('https://example.com');
  // Element has "  Welcome to our site  " (with spaces)
  await expect(page.locator('h1')).toHaveText('Welcome'); // ❌ Fails - toHaveText is exact
});
```

**Why this is wrong**: `toHaveText()` requires exact match (ignoring outer whitespace), fails on partial matches.

**How to fix**:

```typescript
// ✅ Good: Use toContainText for partial matches
test('partial text check', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page.locator('h1')).toContainText('Welcome'); // ✅ Partial match OK
  
  // Or use toHaveText with exact text
  await expect(page.locator('h1')).toHaveText('Welcome to our site'); // ✅ Exact match
});
```

**Common web-first assertions:**

```typescript
test('web-first assertion examples', async ({ page }) => {
  await page.goto('https://example.com');
  
  // Text assertions
  await expect(page.locator('h1')).toHaveText('Welcome');
  await expect(page.locator('.message')).toContainText('success');
  await expect(page.locator('.count')).toHaveText(/\d+ items/);
  
  // Visibility assertions
  await expect(page.locator('.modal')).toBeVisible();
  await expect(page.locator('.loading')).toBeHidden();
  await expect(page.locator('.error')).not.toBeVisible();
  
  // State assertions
  await expect(page.locator('button')).toBeEnabled();
  await expect(page.locator('button')).toBeDisabled();
  await expect(page.locator('input')).toBeEditable();
  await expect(page.locator('input')).toBeEmpty();
  await expect(page.locator('input')).toBeFocused();
  await expect(page.locator('checkbox')).toBeChecked();
  
  // Attribute assertions
  await expect(page.locator('a')).toHaveAttribute('href', '/home');
  await expect(page.locator('button')).toHaveClass('btn-primary');
  await expect(page.locator('input')).toHaveValue('test@example.com');
  await expect(page.locator('div')).toHaveId('main-content');
  
  // Count assertions
  await expect(page.locator('.item')).toHaveCount(10);
  await expect(page.locator('.error')).toHaveCount(0);
  
  // CSS assertions
  await expect(page.locator('.box')).toHaveCSS('color', 'rgb(255, 0, 0)');
  await expect(page.locator('.container')).toHaveCSS('display', 'flex');
  
  // URL and title assertions
  await expect(page).toHaveURL('https://example.com/success');
  await expect(page).toHaveURL(/.*success$/);
  await expect(page).toHaveTitle('Success Page');
  await expect(page).toHaveTitle(/Success/);
  
  // Screenshot comparison
  await expect(page.locator('.chart')).toHaveScreenshot('chart.png');
  await expect(page).toHaveScreenshot('full-page.png');
});
```

**Soft assertions for multiple checks:**

```typescript
test('soft assertions', async ({ page }) => {
  await page.goto('https://example.com/form');
  
  // ✅ Continue test execution even if assertions fail
  await expect.soft(page.locator('.username')).toHaveText('John');
  await expect.soft(page.locator('.email')).toHaveText('john@example.com');
  await expect.soft(page.locator('.status')).toHaveText('Active');
  
  // Test continues and reports all failures at the end
  await page.click('button.submit');
});
```

**Custom timeout for specific assertions:**

```typescript
test('custom assertion timeouts', async ({ page }) => {
  await page.goto('https://example.com');
  
  // ✅ Default timeout (from config, usually 5s)
  await expect(page.locator('.fast-element')).toBeVisible();
  
  // ✅ Extended timeout for slow operations
  await expect(page.locator('.slow-loading-data')).toBeVisible({ 
    timeout: 30000 
  });
  
  // ✅ Short timeout for elements that should appear quickly
  await expect(page.locator('.cached-data')).toBeVisible({ 
    timeout: 1000 
  });
});
```

**Negation with .not:**

```typescript
test('negative assertions', async ({ page }) => {
  await page.goto('https://example.com');
  
  // ✅ Assert element is not visible
  await expect(page.locator('.error-message')).not.toBeVisible();
  
  // ✅ Assert element doesn't have text
  await expect(page.locator('.status')).not.toHaveText('Failed');
  
  // ✅ Assert element is not checked
  await expect(page.locator('input[type="checkbox"]')).not.toBeChecked();
  
  // ✅ Multiple negative conditions
  await expect(page.locator('button')).not.toBeDisabled();
  await expect(page.locator('.alert')).not.toBeAttached();
});
```

**Combine with locator assertions:**

```typescript
test('locator assertions in chains', async ({ page }) => {
  await page.goto('https://example.com');
  
  // ✅ Filter locators before asserting
  const rows = page.locator('tr');
  await expect(rows.filter({ hasText: 'Active' })).toHaveCount(3);
  
  // ✅ Assert on nth element
  await expect(rows.nth(0)).toContainText('Header');
  
  // ✅ Assert within a specific section
  const nav = page.locator('nav');
  await expect(nav.getByRole('link')).toHaveCount(5);
  await expect(nav.getByRole('link', { name: 'Home' })).toBeVisible();
});
```

**When to use generic expect:**

```typescript
test('appropriate use of generic expect', async ({ page, request }) => {
  // ✅ OK for API responses (not DOM elements)
  const response = await request.get('https://api.example.com/data');
  expect(response.status()).toBe(200);
  const data = await response.json();
  expect(data.items).toHaveLength(10);
  
  // ✅ OK for non-DOM JavaScript values
  const url = page.url();
  expect(url).toContain('example.com');
  
  // ✅ OK for test logic/calculations
  const numbers = [1, 2, 3, 4, 5];
  const sum = numbers.reduce((a, b) => a + b, 0);
  expect(sum).toBe(15);
  
  // ❌ NOT OK for DOM elements - use web-first assertions instead
  // const text = await page.locator('h1').textContent();
  // expect(text).toBe('Title'); // Bad!
  
  // ✅ Good - web-first assertion for DOM
  await expect(page.locator('h1')).toHaveText('Title');
});
```

**Benefits of web-first assertions:**
- **Auto-waiting**: Automatically retries until condition is met (up to timeout)
- **Stability**: Eliminates race conditions and timing issues
- **Concise**: No need for manual `waitFor*` calls before assertions
- **Clear intent**: Assertion names clearly express what you're checking
- **Better errors**: Failure messages include retry history and screenshots
- **Type-safe**: TypeScript integration catches errors at compile time

**Migration pattern:**

```typescript
// Before (flaky)
const text = await page.locator('.status').textContent();
expect(text).toBe('Ready');

// After (stable)
await expect(page.locator('.status')).toHaveText('Ready');

// Before (verbose)
await page.waitForSelector('.message');
const isVisible = await page.locator('.message').isVisible();
expect(isVisible).toBe(true);

// After (concise)
await expect(page.locator('.message')).toBeVisible();
```

Always prefer web-first assertions (starting with `await expect(page...` or `await expect(locator...)`) over generic expect for any DOM-related checks. Reserve generic `expect()` for API responses, non-DOM JavaScript values, and test logic.

Reference: [Playwright Assertions](https://playwright.dev/docs/test-assertions)