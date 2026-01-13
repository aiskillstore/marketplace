---
name: playwright-testing
description: Automatically activated when user works with Playwright tests, mentions Playwright configuration, asks about selectors/locators/page objects, or has files matching *.spec.ts in e2e or tests directories. Provides Playwright-specific expertise for E2E and integration testing.
version: 1.1.0
allowed-tools: Read, Grep, Glob, Bash
capabilities:
  - playwright-configuration
  - locator-selection
  - page-object-patterns
  - fixture-creation
  - network-mocking
  - accessibility-testing
  - debugging-traces
  - api-testing
  - cross-browser-testing
---

# Playwright Testing Expertise

You are an expert in Playwright testing framework with deep knowledge of browser automation, selectors, page objects, and best practices for end-to-end testing.

## Your Capabilities

1. **Playwright Configuration**: Projects, browsers, reporters, and fixtures
2. **Locators & Selectors**: Role-based, text, CSS, and chained locators
3. **Page Object Model**: Organizing tests with page objects
4. **Assertions**: Built-in assertions, custom matchers, auto-waiting
5. **Test Fixtures**: Built-in and custom fixtures, test isolation
6. **Debugging**: Traces, screenshots, videos, and Playwright Inspector
7. **API Testing**: Request fixtures and API testing capabilities

## When to Use This Skill

Claude should automatically invoke this skill when:
- The user mentions Playwright, playwright.config, or Playwright features
- Files matching `*.spec.ts` in e2e, tests, or playwright directories are encountered
- The user asks about locators, page objects, or browser automation
- E2E or integration testing is discussed
- Browser testing configuration is needed

## How to Use This Skill

### Accessing Resources

Use `{baseDir}` to reference files in this skill directory:
- Scripts: `{baseDir}/scripts/`
- Documentation: `{baseDir}/references/`
- Templates: `{baseDir}/assets/`

## Available Resources

This skill includes ready-to-use resources in `{baseDir}`:

- **references/playwright-cheatsheet.md** - Quick reference for locators, assertions, actions, and CLI commands
- **assets/page-object.template.ts** - Complete Page Object Model template with base class and examples
- **scripts/check-playwright-setup.sh** - Validates Playwright configuration and browser installation

## Playwright Best Practices

### Test Structure
```typescript
import { test, expect } from '@playwright/test';

test.describe('Contact Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/contact');
  });

  test('should show success message after form submission', async ({ page }) => {
    // Arrange
    await page.getByLabel('Name').fill('Test User');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Message').fill('Hello, this is a test message.');

    // Act
    await page.getByRole('button', { name: 'Submit' }).click();

    // Assert
    await expect(page.getByText('Thank you for your message')).toBeVisible();
    await expect(page.getByLabel('Name')).toBeEmpty();
  });
});
```

### Locator Best Practices

#### Preferred Locators (Most Resilient)
```typescript
// Role-based (best)
page.getByRole('button', { name: 'Submit' });
page.getByRole('textbox', { name: 'Email' });
page.getByRole('heading', { level: 1 });

// Label-based
page.getByLabel('Email address');
page.getByPlaceholder('Enter your email');

// Text-based
page.getByText('Welcome');
page.getByTitle('Close');
```

#### Chaining Locators
```typescript
page.getByRole('listitem')
  .filter({ hasText: 'Product 1' })
  .getByRole('button', { name: 'Add' });
```

#### Test IDs (Last Resort)
```typescript
page.getByTestId('submit-button');
```

### Page Object Pattern
```typescript
// pages/login.page.ts
import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  private readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
    await expect(this.emailInput).toBeVisible();
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async getError(): Promise<string | null> {
    if (await this.errorMessage.isVisible()) {
      return this.errorMessage.textContent();
    }
    return null;
  }
}

// Usage in test
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

test('should login successfully', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@test.com', 'password');
  await expect(page).toHaveURL('/dashboard');
});

test('should show error for invalid credentials', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('invalid@test.com', 'wrongpassword');
  const error = await loginPage.getError();
  expect(error).toContain('Invalid credentials');
});
```

### Auto-Waiting & Assertions
```typescript
// Auto-waits for element
await expect(page.getByRole('alert')).toBeVisible();
await expect(page.getByRole('button')).toBeEnabled();
await expect(page.getByText('Count: 5')).toBeVisible();

// Negative assertions
await expect(page.getByRole('dialog')).toBeHidden();
await expect(page.getByText('Error')).not.toBeVisible();

// With custom timeout
await expect(page.getByText('Loaded')).toBeVisible({ timeout: 10000 });
```

### Fixtures
```typescript
// fixtures.ts
import { test as base } from '@playwright/test';

export const test = base.extend<{
  authenticatedPage: Page;
}>({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@test.com');
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Login' }).click();
    await page.waitForURL('/dashboard');
    await use(page);
  },
});
```

### Storage State Authentication

For efficient authentication without UI login each time:

```typescript
// Setup: Save auth state after login (run once)
// auth.setup.ts
import { test as setup, expect } from '@playwright/test';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('test@example.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL('/dashboard');

  // Save storage state (cookies, localStorage)
  await page.context().storageState({ path: '.auth/user.json' });
});

// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { storageState: '.auth/user.json' },
      dependencies: ['setup'],
    },
  ],
});

// Tests automatically have auth state
test('dashboard loads for authenticated user', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByText('Welcome back')).toBeVisible();
});
```

### Network Mocking & Interception

Mock API responses for reliable, fast tests:

```typescript
import { test, expect } from '@playwright/test';

test('should display mocked user data', async ({ page }) => {
  // Mock API response
  await page.route('**/api/users', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'Test User', email: 'test@example.com' }
      ]),
    });
  });

  await page.goto('/users');
  await expect(page.getByText('Test User')).toBeVisible();
});

test('should handle API errors gracefully', async ({ page }) => {
  // Mock error response
  await page.route('**/api/users', route => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Internal Server Error' }),
    });
  });

  await page.goto('/users');
  await expect(page.getByText('Failed to load users')).toBeVisible();
});

test('should handle network failure', async ({ page }) => {
  // Abort network request
  await page.route('**/api/data', route => route.abort());

  await page.goto('/data');
  await expect(page.getByText('Network error')).toBeVisible();
});

test('should handle slow responses', async ({ page }) => {
  // Simulate slow API
  await page.route('**/api/slow', async route => {
    await new Promise(resolve => setTimeout(resolve, 3000));
    await route.continue();
  });

  await page.goto('/slow-page');
  await expect(page.getByText('Loading...')).toBeVisible();
});

// Modify request/response
test('should modify request headers', async ({ page }) => {
  await page.route('**/api/**', route => {
    route.continue({
      headers: {
        ...route.request().headers(),
        'X-Test-Header': 'test-value',
      },
    });
  });
});
```

### Accessibility Testing

Integrate accessibility audits with @axe-core/playwright:

```typescript
// Install: npm install @axe-core/playwright
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('should pass accessibility audit', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page }).analyze();

  expect(results.violations).toEqual([]);
});

test('should pass accessibility audit for specific section', async ({ page }) => {
  await page.goto('/dashboard');

  const results = await new AxeBuilder({ page })
    .include('#main-content')
    .exclude('#third-party-widget')
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();

  expect(results.violations).toEqual([]);
});

// Check specific rules
test('should have proper color contrast', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page })
    .withRules(['color-contrast'])
    .analyze();

  expect(results.violations).toEqual([]);
});

// Detailed violation reporting
test('accessibility check with detailed report', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page }).analyze();

  if (results.violations.length > 0) {
    console.log('Accessibility violations:');
    results.violations.forEach(violation => {
      console.log(`- ${violation.id}: ${violation.description}`);
      violation.nodes.forEach(node => {
        console.log(`  Element: ${node.html}`);
        console.log(`  Fix: ${node.failureSummary}`);
      });
    });
  }

  expect(results.violations).toEqual([]);
});
```

### Visual Regression Testing

Compare screenshots to detect visual changes:

```typescript
import { test, expect } from '@playwright/test';

test('homepage visual regression', async ({ page }) => {
  await page.goto('/');

  // Full page screenshot comparison
  await expect(page).toHaveScreenshot('homepage.png');
});

test('component visual regression', async ({ page }) => {
  await page.goto('/components');

  // Element-specific screenshot
  const button = page.getByRole('button', { name: 'Submit' });
  await expect(button).toHaveScreenshot('submit-button.png');
});

test('visual with threshold', async ({ page }) => {
  await page.goto('/');

  // Allow small differences
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixels: 100,
    threshold: 0.2,
  });
});

// Update snapshots: npx playwright test --update-snapshots
```

## Playwright Configuration

### Basic Configuration
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile', use: { ...devices['iPhone 13'] } },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## Debugging & Troubleshooting

### Debug Mode
```bash
npx playwright test --debug
npx playwright test --ui
```

### Traces
```typescript
// Capture trace on failure
use: {
  trace: 'on-first-retry',
}

// View trace
npx playwright show-trace trace.zip
```

### Screenshots
```typescript
await page.screenshot({ path: 'screenshot.png', fullPage: true });
```

## Common Issues & Solutions

### Issue: Flaky tests
- Use auto-waiting assertions instead of fixed waits
- Wait for specific elements instead of `networkidle` (which fails with WebSockets, long-polling, analytics):
  ```typescript
  // Bad: networkidle is unreliable
  await page.waitForLoadState('networkidle');

  // Good: wait for specific content
  await expect(page.getByRole('main')).toBeVisible();
  await expect(page.getByTestId('data-loaded')).toBeAttached();
  ```
- Ensure proper test isolation

### Issue: Elements not found
- Use Playwright Inspector to find better locators
- Prefer role-based selectors
- Check for iframes or shadow DOM

### Issue: Slow tests
- Reuse authentication state
- Use `test.describe.parallel()`
- Mock slow API calls

## Examples

### Example 1: Form Testing
When testing forms:
1. Use getByLabel for inputs
2. Use fill() instead of type() for speed
3. Submit with button locator
4. Assert on success message or navigation

### Example 2: Table Testing
When testing tables/lists:
1. Use getByRole('row') for table rows
2. Filter by content with `.filter()`
3. Chain to find actions within rows
4. Assert on row count or content

## Version Compatibility

The patterns in this skill require the following minimum versions:

| Feature | Minimum Version | Notes |
|---------|----------------|-------|
| getByRole with name | 1.27+ | Role-based locators with accessible name |
| toHaveScreenshot | 1.22+ | Visual regression testing |
| storageState | 1.13+ | Authentication state persistence |
| @axe-core/playwright | 4.7+ | Accessibility testing integration |
| route.fulfill | 1.0+ | Network mocking (stable) |
| test.describe.configure | 1.24+ | Parallel/serial test configuration |

### Feature Detection

Check your Playwright version:
```bash
npx playwright --version
```

### Upgrading

```bash
# Update Playwright
npm install -D @playwright/test@latest

# Update browsers
npx playwright install
```

## Important Notes

- Playwright is automatically invoked when relevant
- Always check playwright.config.ts for project settings
- Prefer role-based locators for resilient tests
- Use auto-waiting assertions instead of explicit waits
- Consider mobile and cross-browser testing in CI
