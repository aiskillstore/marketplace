---
title: Ensure Test Isolation for Parallel Execution
impact: CRITICAL
impactDescription: Prevents race conditions and enables safe parallel execution
tags: parallel, isolation, stability, performance
---

## Ensure Test Isolation for Parallel Execution

**Impact: CRITICAL (prevents race conditions and enables safe parallel execution)**

Playwright runs tests in parallel by default. Tests must be completely isolated from each other to prevent flaky failures caused by shared state, resource conflicts, or race conditions. Proper isolation allows you to run tests in parallel safely, dramatically reducing total execution time.

**Incorrect (shared state causing conflicts):**

```typescript
import { test, expect } from '@playwright/test';

// ❌ Global shared state between tests
let sharedUserId: string;
let testCounter = 0;

test('first test creates user', async ({ page }) => {
  await page.goto('https://example.com/signup');
  await page.fill('[name="email"]', 'test@example.com'); // ❌ Same email in parallel tests
  await page.click('button[type="submit"]');
  sharedUserId = await page.locator('[data-testid="user-id"]').textContent();
});

test('second test uses shared state', async ({ page }) => {
  // ❌ Depends on first test's execution and shared variable
  await page.goto(`https://example.com/user/${sharedUserId}`);
  await expect(page.locator('h1')).toHaveText('Profile');
});

test('modifies shared database record', async ({ page }) => {
  // ❌ Multiple tests modifying same record causes conflicts
  await page.goto('https://example.com/admin');
  await page.click('[data-testid="user-1"] button.delete');
  await expect(page.locator('.success')).toBeVisible();
});

test('uses shared file system', async ({ page }) => {
  // ❌ File conflicts when tests run in parallel
  await page.goto('https://example.com/upload');
  const [fileChooser] = await Promise.all([
    page.waitForEvent('filechooser'),
    page.click('button.upload')
  ]);
  await fileChooser.setFiles('./test-data/shared-file.txt'); // ❌ Shared file
});

test('increments counter', async ({ page }) => {
  // ❌ Race condition with shared counter
  testCounter++;
  await page.goto(`https://example.com/test/${testCounter}`);
});
```

**Correct (fully isolated tests):**

```typescript
import { test, expect } from '@playwright/test';
import { randomUUID } from 'crypto';

test('isolated user creation', async ({ page }) => {
  // ✅ Each test uses unique data
  const uniqueEmail = `test-${randomUUID()}@example.com`;
  
  await page.goto('https://example.com/signup');
  await page.fill('[name="email"]', uniqueEmail);
  await page.click('button[type="submit"]');
  
  const userId = await page.locator('[data-testid="user-id"]').textContent();
  
  // ✅ Complete test within single test case
  await page.goto(`https://example.com/user/${userId}`);
  await expect(page.locator('h1')).toHaveText('Profile');
});

test('isolated database operations', async ({ page, request }) => {
  // ✅ Create unique test data for this test
  const uniqueUser = await request.post('https://example.com/api/users', {
    data: {
      email: `test-${randomUUID()}@example.com`,
      name: 'Test User'
    }
  });
  const userData = await uniqueUser.json();
  
  await page.goto('https://example.com/admin');
  await page.click(`[data-testid="user-${userData.id}"] button.delete`);
  await expect(page.locator('.success')).toBeVisible();
  
  // ✅ Cleanup is scoped to this test's data
});

test('isolated file uploads', async ({ page }) => {
  // ✅ Create unique file for this test
  const fs = require('fs');
  const path = require('path');
  const uniqueFileName = `test-${randomUUID()}.txt`;
  const filePath = path.join(__dirname, 'tmp', uniqueFileName);
  
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, 'test content');
  
  await page.goto('https://example.com/upload');
  const [fileChooser] = await Promise.all([
    page.waitForEvent('filechooser'),
    page.click('button.upload')
  ]);
  await fileChooser.setFiles(filePath);
  
  await expect(page.locator('.upload-success')).toBeVisible();
  
  // ✅ Cleanup unique file
  fs.unlinkSync(filePath);
});

// ✅ Each test gets its own browser context (isolated cookies, storage)
test('isolated authentication', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.fill('[name="username"]', `user-${randomUUID()}@example.com`);
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // ✅ Session is isolated to this test's browser context
  await expect(page).toHaveURL('/dashboard');
});
```

**Use fixtures for test isolation:**

```typescript
import { test as base, expect } from '@playwright/test';

// ✅ Custom fixture provides isolated test data
type TestFixtures = {
  uniqueUser: { email: string; id: string };
  authenticatedPage: Page;
};

const test = base.extend<TestFixtures>({
  uniqueUser: async ({ request }, use) => {
    // Setup: Create unique user for this test
    const email = `test-${randomUUID()}@example.com`;
    const response = await request.post('/api/users', {
      data: { email, password: 'test123' }
    });
    const user = await response.json();
    
    // Provide to test
    await use(user);
    
    // Teardown: Clean up this test's data
    await request.delete(`/api/users/${user.id}`);
  },

  authenticatedPage: async ({ page, uniqueUser }, use) => {
    // Setup: Authenticate with unique user
    await page.goto('/login');
    await page.fill('[name="email"]', uniqueUser.email);
    await page.fill('[name="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    
    // Provide authenticated page to test
    await use(page);
    
    // Teardown: Logout happens automatically (context is isolated)
  }
});

test('uses isolated fixture', async ({ authenticatedPage, uniqueUser }) => {
  // ✅ Each test gets fresh authenticated user and page
  await authenticatedPage.goto('/profile');
  await expect(authenticatedPage.locator('[data-testid="email"]'))
    .toHaveText(uniqueUser.email);
});
```

**Configure parallel execution:**

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  // ✅ Run tests in parallel (default)
  fullyParallel: true,
  
  // ✅ Number of parallel workers
  workers: process.env.CI ? 2 : undefined, // Use 2 in CI, CPU count locally
  
  // ✅ Each test gets isolated browser context
  use: {
    // Contexts are automatically isolated
  },
  
  projects: [
    {
      name: 'chromium',
      use: { 
        // ✅ Each project runs in parallel
        ...devices['Desktop Chrome'] 
      },
    },
  ],
});

// ✅ Tests within a file run in parallel by default
test.describe.configure({ mode: 'parallel' }); // Explicit parallel mode

// ✅ Force serial execution only when necessary
test.describe.serial('sequential flow', () => {
  let sharedState: string;
  
  test('step 1', async ({ page }) => {
    sharedState = 'value';
  });
  
  test('step 2', async ({ page }) => {
    // Uses sharedState from step 1
  });
});
```

**Isolation checklist:**
- ✅ Each test uses unique test data (emails, usernames, IDs)
- ✅ No global variables shared between tests
- ✅ Tests don't depend on execution order
- ✅ Each test can run independently
- ✅ Database/API operations use unique identifiers
- ✅ File operations use unique filenames
- ✅ Browser contexts are isolated (automatic in Playwright)
- ✅ Fixtures handle setup and cleanup per test
- ✅ Tests clean up their own data
- ✅ No hardcoded/shared credentials or resources

**When to use serial execution:**
Only use `test.describe.serial()` when tests genuinely must run in sequence (e.g., testing a multi-step user journey where each step depends on the previous state). Most tests should be isolated and parallelizable.

Reference: [Playwright Parallelism](https://playwright.dev/docs/test-parallel)