---
title: Use test.describe for Logical Test Grouping
impact: MEDIUM
impactDescription: Improves test organization and makes test reports more readable
tags: organization, fixtures, describe, maintainability
---

## Use test.describe for Logical Test Grouping

**Impact: MEDIUM (improves test organization and makes test reports more readable)**

Use `test.describe` to group related tests together. This improves test organization, makes reports easier to read, and allows you to share hooks and configuration across related tests. Well-organized tests are easier to maintain and debug.

**Incorrect (flat test structure):**

```typescript
import { test, expect } from '@playwright/test';

test('login with valid credentials', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="username"]', 'user@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});

test('login with invalid password', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="username"]', 'user@example.com');
  await page.fill('[name="password"]', 'wrongpassword');
  await page.click('button[type="submit"]');
  await expect(page.locator('.error')).toBeVisible();
});

test('logout redirects to home', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('[data-testid="logout"]');
  await expect(page).toHaveURL('/');
});

test('profile update succeeds', async ({ page }) => {
  await page.goto('/profile');
  await page.fill('[name="name"]', 'New Name');
  await page.click('button[type="submit"]');
  await expect(page.locator('.success')).toBeVisible();
});
```

**Correct (grouped with test.describe):**

```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.describe('Login', () => {
    test.beforeEach(async ({ page }) => {
      // Shared setup for all login tests
      await page.goto('/login');
    });

    test('succeeds with valid credentials', async ({ page }) => {
      await page.fill('[name="username"]', 'user@example.com');
      await page.fill('[name="password"]', 'password123');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL('/dashboard');
    });

    test('fails with invalid password', async ({ page }) => {
      await page.fill('[name="username"]', 'user@example.com');
      await page.fill('[name="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');
      await expect(page.locator('.error')).toBeVisible();
    });

    test('shows validation for empty fields', async ({ page }) => {
      await page.click('button[type="submit"]');
      await expect(page.locator('.validation-error')).toHaveCount(2);
    });
  });

  test.describe('Logout', () => {
    test.beforeEach(async ({ page }) => {
      // Authenticate before each logout test
      await page.goto('/login');
      await page.fill('[name="username"]', 'user@example.com');
      await page.fill('[name="password"]', 'password123');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL('/dashboard');
    });

    test('redirects to home page', async ({ page }) => {
      await page.click('[data-testid="logout"]');
      await expect(page).toHaveURL('/');
    });

    test('clears session data', async ({ page, context }) => {
      await page.click('[data-testid="logout"]');
      const cookies = await context.cookies();
      expect(cookies.find(c => c.name === 'sessionId')).toBeUndefined();
    });
  });
});

test.describe('User Profile', () => {
  test.beforeEach(async ({ page }) => {
    // Authenticate and navigate to profile for all profile tests
    await page.goto('/login');
    await page.fill('[name="username"]', 'user@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.goto('/profile');
  });

  test('updates name successfully', async ({ page }) => {
    await page.fill('[name="name"]', 'New Name');
    await page.click('button[type="submit"]');
    await expect(page.locator('.success')).toBeVisible();
  });

  test('validates email format', async ({ page }) => {
    await page.fill('[name="email"]', 'invalid-email');
    await page.click('button[type="submit"]');
    await expect(page.locator('.error')).toContainText('valid email');
  });
});

// You can also configure describe blocks
test.describe('Mobile view', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('shows mobile navigation', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.mobile-menu')).toBeVisible();
  });
});
```

Benefits of using `test.describe`:
- **Logical grouping**: Related tests are visually grouped in code and test reports
- **Shared setup**: Use `beforeEach`/`afterEach` hooks for common setup/teardown
- **Better reports**: Test results show hierarchical structure making failures easier to locate
- **Configuration**: Apply specific configuration (timeout, retries, fixtures) to groups
- **Selective execution**: Run specific groups with `test.describe.only()` or skip with `test.describe.skip()`

Naming conventions:
- Use descriptive names that represent the feature or functionality being tested
- Group by feature, component, or user flow
- Nest describe blocks for sub-features or scenarios
- Keep test names concise since the describe context provides clarity

Reference: [Playwright Test Describe](https://playwright.dev/docs/api/class-test#test-describe)