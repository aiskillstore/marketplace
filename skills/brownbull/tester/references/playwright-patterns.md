# Playwright Testing Patterns for GabeDA

Best practices and patterns for writing reliable E2E tests with Playwright.

## Table of Contents
1. [Test Organization](#test-organization)
2. [Locator Strategies](#locator-strategies)
3. [Waiting Patterns](#waiting-patterns)
4. [Authentication Patterns](#authentication-patterns)
5. [API Mocking](#api-mocking)
6. [Debugging](#debugging)
7. [Common Pitfalls](#common-pitfalls)

## Test Organization

### File Structure

```
tests/
├── e2e/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   ├── registration.spec.ts
│   │   └── logout.spec.ts
│   ├── dashboard/
│   │   ├── company-info.spec.ts
│   │   ├── company-switcher.spec.ts
│   │   └── stats.spec.ts
│   └── companies/
│       ├── create-company.spec.ts
│       └── manage-members.spec.ts
├── integration/
├── smoke/
└── fixtures/
    └── auth.ts
```

### Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup before each test
    await page.goto('http://localhost:5173/');
  });

  test('Scenario - action - expected result', async ({ page }) => {
    // Arrange
    // Setup test data and preconditions

    // Act
    // Perform the action being tested

    // Assert
    // Verify the expected outcome
  });

  test.afterEach(async ({ page }) => {
    // Cleanup after each test
  });
});
```

## Locator Strategies

### Recommended Locator Priority

1. **Test IDs** (most reliable)
```typescript
await page.locator('[data-testid="submit-button"]').click();
```

2. **Role-based** (accessible)
```typescript
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('heading', { name: 'Dashboard' });
```

3. **Label text** (forms)
```typescript
await page.getByLabel('Email').fill('test@example.com');
```

4. **Placeholder** (inputs)
```typescript
await page.getByPlaceholder('Enter your email').fill('test@example.com');
```

5. **Text content** (last resort)
```typescript
await page.getByText('Dashboard').click();
```

### Avoid These Locators

❌ **CSS classes** (can change frequently)
```typescript
// BAD
await page.locator('.btn-primary').click();
```

❌ **XPath** (fragile)
```typescript
// BAD
await page.locator('//div[@class="container"]/button[1]').click();
```

❌ **Index-based** (breaks when order changes)
```typescript
// BAD
await page.locator('button').nth(2).click();
```

### Chaining Locators

```typescript
// Find button within a specific section
const section = page.locator('[data-testid="company-section"]');
await section.locator('button:has-text("Create")').click();

// Find by role within parent
const form = page.getByRole('form', { name: 'Login' });
await form.getByLabel('Email').fill('test@example.com');
```

## Waiting Patterns

### Automatic Waiting (Preferred)

Playwright automatically waits for:
- Element to be visible
- Element to be enabled
- Element to be stable

```typescript
// These automatically wait
await page.click('button');
await page.fill('input', 'value');
await expect(page.locator('h1')).toBeVisible();
```

### Explicit Waits

**Wait for URL**
```typescript
await page.waitForURL('**/dashboard');
await page.waitForURL(/\/companies\/[a-z0-9-]+/);
```

**Wait for network idle**
```typescript
await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
```

**Wait for specific request**
```typescript
await page.waitForResponse(
  response => response.url().includes('/api/accounts/profile/') && response.status() === 200
);
```

**Wait for element state**
```typescript
await page.locator('button').waitFor({ state: 'visible' });
await page.locator('input').waitFor({ state: 'enabled' });
```

### Avoid Fixed Timeouts

❌ **BAD**
```typescript
await page.waitForTimeout(3000); // Flaky!
```

✅ **GOOD**
```typescript
await page.waitForSelector('[data-testid="loaded"]');
await page.waitForLoadState('networkidle');
```

## Authentication Patterns

### Setup Fixture

**File**: `tests/fixtures/auth.ts`

```typescript
import { test as base, expect } from '@playwright/test';
import type { Page } from '@playwright/test';

type AuthFixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Login
    await page.goto('http://localhost:5173/');
    await page.fill('input[type="email"]', 'testuser@gabeda.com');
    await page.fill('input[type="password"]', 'gabe123123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Use authenticated page
    await use(page);

    // Cleanup
    await page.evaluate(() => localStorage.clear());
  },
});

export { expect };
```

### Using Auth Fixture

```typescript
import { test, expect } from '../fixtures/auth';

test('Dashboard - authenticated user - displays company', async ({ authenticatedPage }) => {
  // Already logged in via fixture
  await expect(authenticatedPage.locator('h1')).toContainText('Dashboard');
});
```

### Storage State (Reuse Authentication)

**Setup** - Save auth state once:

```typescript
import { test as setup } from '@playwright/test';

setup('authenticate', async ({ page }) => {
  await page.goto('http://localhost:5173/');
  await page.fill('input[type="email"]', 'testuser@gabeda.com');
  await page.fill('input[type="password"]', 'gabe123123');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');

  // Save auth state
  await page.context().storageState({ path: 'tests/.auth/user.json' });
});
```

**Use** - Load auth state in tests:

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    {
      name: 'authenticated',
      dependencies: ['setup'],
      use: {
        storageState: 'tests/.auth/user.json',
      },
    },
  ],
});
```

## API Mocking

### Mock API Response

```typescript
test('Dashboard - API error - shows error message', async ({ page }) => {
  // Mock failing API call
  await page.route('**/api/accounts/profile/', route => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Server error' }),
    });
  });

  await page.goto('http://localhost:5173/dashboard');

  await expect(page.locator('[role="alert"]')).toContainText('Server error');
});
```

### Mock with Delay

```typescript
test('Dashboard - slow API - shows loading state', async ({ page }) => {
  await page.route('**/api/accounts/companies/*/stats/', async route => {
    // Delay response by 2 seconds
    await new Promise(resolve => setTimeout(resolve, 2000));

    route.fulfill({
      status: 200,
      body: JSON.stringify({
        total_uploads: 42,
        total_members: 5,
        analytics_generated: 10,
      }),
    });
  });

  await page.goto('http://localhost:5173/dashboard');

  // Check loading skeleton appears
  await expect(page.locator('[data-testid="loading-skeleton"]')).toBeVisible();
});
```

### Intercept and Modify

```typescript
test('Dashboard - modifies API response', async ({ page }) => {
  await page.route('**/api/accounts/profile/', async route => {
    const response = await route.fetch();
    const json = await response.json();

    // Modify response
    json.company = {
      ...json.company,
      name: 'Modified Company Name',
    };

    route.fulfill({
      response,
      json,
    });
  });

  await page.goto('http://localhost:5173/dashboard');

  await expect(page.locator('h2')).toContainText('Modified Company Name');
});
```

## Debugging

### Visual Debugging

```typescript
// Take screenshot
await page.screenshot({ path: 'debug.png', fullPage: true });

// Highlight element before action
await page.locator('button').highlight();
await page.locator('button').click();
```

### Console Logging

```typescript
// Listen to console messages
page.on('console', msg => {
  console.log('Browser console:', msg.type(), msg.text());
});

// Listen to page errors
page.on('pageerror', error => {
  console.error('Page error:', error.message);
});
```

### Network Debugging

```typescript
// Log all requests
page.on('request', request => {
  console.log('Request:', request.method(), request.url());
});

// Log all responses
page.on('response', response => {
  console.log('Response:', response.status(), response.url());
});
```

### Run in Headed Mode

```bash
# See browser window during test
npx playwright test --headed

# Debug mode with Playwright Inspector
npx playwright test --debug

# Slow motion (500ms between actions)
npx playwright test --headed --slow-mo=500
```

### Trace Viewer

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    trace: 'on-first-retry', // or 'on'
  },
});
```

```bash
# View trace
npx playwright show-trace trace.zip
```

## Common Pitfalls

### 1. Race Conditions

❌ **BAD**
```typescript
await page.click('button');
await page.locator('h1').textContent(); // Might execute before navigation
```

✅ **GOOD**
```typescript
await page.click('button');
await page.waitForURL('**/dashboard');
await expect(page.locator('h1')).toContainText('Dashboard');
```

### 2. Flaky Selectors

❌ **BAD**
```typescript
await page.click('button:nth-child(2)'); // Breaks if order changes
```

✅ **GOOD**
```typescript
await page.click('[data-testid="create-company-btn"]');
// or
await page.getByRole('button', { name: 'Create Company' }).click();
```

### 3. Not Waiting for Actions

❌ **BAD**
```typescript
page.click('button'); // Missing await!
await expect(page.locator('h1')).toBeVisible();
```

✅ **GOOD**
```typescript
await page.click('button');
await expect(page.locator('h1')).toBeVisible();
```

### 4. Hard-coded Waits

❌ **BAD**
```typescript
await page.waitForTimeout(3000);
await page.click('button');
```

✅ **GOOD**
```typescript
await page.locator('button').waitFor({ state: 'visible' });
await page.click('button');
```

### 5. Shared State Between Tests

❌ **BAD**
```typescript
let companyId: string;

test('create company', async ({ page }) => {
  companyId = await createCompany();
});

test('view company', async ({ page }) => {
  await page.goto(`/companies/${companyId}`); // Depends on previous test!
});
```

✅ **GOOD**
```typescript
test('view company', async ({ page }) => {
  // Each test is independent
  const companyId = await createCompany();
  await page.goto(`/companies/${companyId}`);
});
```

## Performance Tips

### Parallelize Tests

```typescript
// playwright.config.ts
export default defineConfig({
  workers: 4, // Run 4 tests in parallel
  fullyParallel: true,
});
```

### Reuse Browser Context

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    browserName: 'chromium',
    launchOptions: {
      // Reuse browser instance
      headless: true,
    },
  },
});
```

### Use API for Setup

```typescript
test('Dashboard - with existing companies', async ({ page, request }) => {
  // Use API to create test data (faster than UI)
  const response = await request.post('http://127.0.0.1:8000/api/accounts/companies/', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    data: {
      rut: '76.123.456-7',
      name: 'Test Company',
      industry: 'retail',
    },
  });

  // Now test UI
  await page.goto('http://localhost:5173/dashboard');
  await expect(page.locator('h2')).toContainText('Test Company');
});
```

## Configuration Example

**File**: `playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```
