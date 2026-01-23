---
title: Use Auto-Waiting Instead of Manual Waits
impact: CRITICAL
impactDescription: Eliminates 70-90% of flaky tests caused by timing issues
tags: auto-waiting, stability, flakiness
---

## Use Auto-Waiting Instead of Manual Waits

**Impact: CRITICAL (eliminates 70-90% of flaky tests caused by timing issues)**

Playwright has built-in auto-waiting for all actions and assertions. Manual waits with `setTimeout`, `waitForTimeout`, or arbitrary delays lead to flaky tests that either fail intermittently or waste time waiting longer than necessary. Auto-waiting makes tests both faster and more reliable.

## When to Use

- **Use auto-waiting (always)**: For all standard interactions (clicks, fills, checks), element visibility assertions, text content checks, and navigation
- **Use explicit waits when**: Waiting for network idle state, specific API responses, custom JavaScript conditions, or third-party scripts to load
- **Avoid manual timeouts**: Never use `setTimeout`, `waitForTimeout`, or `sleep` unless absolutely necessary for specific edge cases
- **Required for**: All projects - auto-waiting is fundamental to Playwright's reliability

## Guidelines

### Do

- Rely on built-in auto-waiting for clicks, fills, and other actions
- Use web-first assertions (toBeVisible, toHaveText) which auto-retry
- Use `waitForLoadState()` for specific load states (load, domcontentloaded, networkidle)
- Use `waitForResponse()` or `waitForRequest()` for specific network events
- Use `waitForFunction()` for custom JavaScript conditions
- Trust Playwright's actionability checks (visible, enabled, stable, receives events)

### Don't

- Don't use `page.waitForTimeout()` or `setTimeout()` - leads to flaky tests
- Don't manually wait for selectors before actions - auto-waiting handles it
- Don't add arbitrary delays "just in case" - makes tests slower
- Don't wait for `networkidle` unless specifically needed (it's slow)
- Don't check element existence and then act on it - actions do both
- Don't over-complicate with manual polling loops - use `waitForFunction()`

### Tool Usage Patterns

- **Auto-waiting actions**: `click()`, `fill()`, `check()`, `selectOption()`, `hover()`, `focus()`, `press()`, `type()`
- **Auto-retrying assertions**: `expect().toBeVisible()`, `toHaveText()`, `toHaveValue()`, `toBeChecked()`, `toBeEnabled()`
- **Explicit waits (when needed)**:
  - `page.waitForLoadState('networkidle')` - Wait for no network activity for 500ms
  - `page.waitForResponse(urlOrPredicate)` - Wait for specific API response
  - `page.waitForRequest(urlOrPredicate)` - Wait for specific API request
  - `page.waitForFunction(pageFunction)` - Wait for custom JavaScript condition
  - `page.waitForSelector()` - Rarely needed, use actions or assertions instead
- **Configuration**: Set default timeout in playwright.config.ts with `timeout` option (default: 30s)

**Incorrect (using manual waits):**

```typescript
import { test, expect } from '@playwright/test';

test('bad - manual waits', async ({ page }) => {
  await page.goto('https://example.com');
  
  // ❌ Arbitrary timeout - too short causes flakiness, too long wastes time
  await page.waitForTimeout(3000);
  await page.click('button');
  
  // ❌ Using setTimeout in tests
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // ❌ Manual wait for element
  await page.waitForSelector('.result');
  await expect(page.locator('.result')).toHaveText('Success');
});
```

**Correct (using auto-waiting):**

```typescript
import { test, expect } from '@playwright/test';

test('good - auto-waiting', async ({ page }) => {
  await page.goto('https://example.com');
  
  // ✅ Auto-waits for element to be actionable (visible, enabled, stable)
  await page.click('button');
  
  // ✅ Assertions auto-wait for condition to be met
  await expect(page.locator('.result')).toHaveText('Success');
  
  // ✅ Actions auto-wait for navigation when needed
  await page.getByRole('link', { name: 'Submit' }).click();
  await expect(page).toHaveURL(/.*success/);
});

test('when explicit waiting is needed', async ({ page }) => {
  await page.goto('https://example.com');
  
  // ✅ Wait for specific network state
  await page.waitForLoadState('networkidle');
  
  // ✅ Wait for API response
  await page.waitForResponse(resp => 
    resp.url().includes('/api/data') && resp.status() === 200
  );
  
  // ✅ Wait for function to return truthy value
  await page.waitForFunction(() => window.dataLoaded === true);
});
```

## Edge Cases and Constraints

### Limitations

- Auto-waiting has a default 30s timeout - very slow operations may need custom timeout
- `networkidle` waits for 500ms of no network activity, but some SPAs have continuous polling
- Auto-waiting can't detect custom application loading states (e.g., skeleton loaders)
- Third-party scripts loading asynchronously may not be covered by standard auto-waiting
- Canvas or WebGL rendering completion requires custom `waitForFunction()`

### Edge Cases

1. **Infinite loading spinners**: If spinner doesn't disappear due to bug, test times out. Solution: Add assertion that spinner is NOT visible with reasonable timeout.

2. **Elements covered by overlays**: Auto-waiting checks if element receives events, but complex z-index issues may not be caught. Solution: Use `force: true` option cautiously or fix the overlay.

3. **Animations delaying actionability**: Element must be stable for 500ms before action. Very long animations can cause timeouts. Solution: Use `page.emulateMedia({ reducedMotion: 'reduce' })` or disable animations in test environment.

4. **Polling APIs creating "networkidle" race**: If app polls every 2 seconds, `networkidle` never triggers. Solution: Don't use `networkidle` for apps with polling, or use `waitForResponse()` for specific initial load.

5. **Detached elements**: Element removed from DOM while auto-waiting. Solution: Playwright retries and throws "Element is not attached to the DOM" error - fix race condition in test or app.

6. **Shadow DOM elements**: Auto-waiting works but selector must pierce shadow DOM. Solution: Use `>>>` combinator or proper role-based selectors.

### What Breaks If Ignored

- **Using manual waits**: 70-90% more flaky tests, tests wait too long (wasted CI time) or too short (intermittent failures)
- **Not trusting auto-waiting**: Redundant manual checks, slower tests, more complex code
- **Using networkidle everywhere**: Tests become 2-5x slower, may never complete for apps with polling
- **Arbitrary timeouts**: Tests fail on slow CI runners but pass locally (or vice versa)

## Common Mistakes

### Mistake 1: Using waitForTimeout instead of auto-waiting

```typescript
// ❌ Bad: Arbitrary delay
test('bad timing', async ({ page }) => {
  await page.goto('https://example.com');
  await page.waitForTimeout(5000); // ❌ Why 5 seconds? Too short or too long?
  await page.click('button');
});
```

**Why this is wrong**: If button appears in 1 second, you waste 4 seconds. If it takes 6 seconds, test fails.

**How to fix**:

```typescript
// ✅ Good: Auto-waits for button to be actionable
test('good auto-wait', async ({ page }) => {
  await page.goto('https://example.com');
  await page.click('button'); // Waits automatically until clickable
});
```

### Mistake 2: Manual selector check before action

```typescript
// ❌ Bad: Redundant manual check
test('redundant check', async ({ page }) => {
  await page.goto('https://example.com');
  
  // ❌ Unnecessary - click() does this automatically
  await page.waitForSelector('button');
  await page.click('button');
});
```

**Why this is wrong**: Doubles the waiting time and adds unnecessary code.

**How to fix**:

```typescript
// ✅ Good: Just do the action
test('direct action', async ({ page }) => {
  await page.goto('https://example.com');
  await page.click('button'); // Auto-waits for button to exist and be actionable
});
```

### Mistake 3: Using networkidle for everything

```typescript
// ❌ Bad: Waiting for networkidle on every page
test('slow networkidle', async ({ page }) => {
  await page.goto('https://example.com');
  await page.waitForLoadState('networkidle'); // ❌ Slow and often unnecessary
  
  await page.click('button');
  await page.waitForLoadState('networkidle'); // ❌ Even slower
});
```

**Why this is wrong**: Waits for 500ms of no network activity - very slow, especially for apps with analytics or polling.

**How to fix**:

```typescript
// ✅ Good: Use specific waits
test('specific waits', async ({ page }) => {
  await page.goto('https://example.com');
  // Default 'load' state is usually sufficient
  
  await page.click('button');
  // Wait for specific response, not all network activity
  await page.waitForResponse(resp => resp.url().includes('/api/data'));
  
  await expect(page.locator('.result')).toBeVisible();
});
```

### Mistake 4: Not handling legitimate delays

```typescript
// ❌ Bad: Expecting instant response from slow operation
test('timeout on slow API', async ({ page }) => {
  await page.goto('https://example.com');
  await page.click('button'); // Triggers 60-second API call
  
  // ❌ Default 30s timeout will fail
  await expect(page.locator('.result')).toBeVisible();
});
```

**Why this is wrong**: Some operations legitimately take longer than default timeout.

**How to fix**:

```typescript
// ✅ Good: Increase timeout for specific operation
test('handle slow operation', async ({ page }) => {
  await page.goto('https://example.com');
  await page.click('button');
  
  // Increase timeout for this specific assertion
  await expect(page.locator('.result')).toBeVisible({ timeout: 90000 });
});

// Or set timeout for entire test
test('slow test', async ({ page }) => {
  test.setTimeout(120000); // 2 minutes
  await page.goto('https://example.com');
  await page.click('button');
  await expect(page.locator('.result')).toBeVisible();
});
```

Playwright automatically waits for:
- Elements to be visible, enabled, and stable before actions
- Navigation to complete after clicks on links
- Assertions to pass (with retries) before failing
- Network requests when using route interception

Only use explicit waits when you need to wait for something specific that auto-waiting doesn't cover, such as network idle state, custom JavaScript conditions, or specific API responses.

Reference: [Playwright Auto-Waiting](https://playwright.dev/docs/actionability)