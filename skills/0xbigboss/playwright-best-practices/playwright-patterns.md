# Playwright Patterns Reference

Code examples for patterns summarized in `SKILL.md`. Load this file when you need to see or produce a concrete implementation.

## Locator Chaining and Filtering

```ts
// Scope within a region
const card = page.getByRole('listitem').filter({ hasText: 'Product A' });
await card.getByRole('button', { name: 'Add to cart' }).click();

// Filter by child locator
const row = page.getByRole('row').filter({
  has: page.getByRole('cell', { name: 'John' })
});

// Combine conditions
const visibleSubmit = page.getByRole('button', { name: 'Submit' }).and(page.locator(':visible'));
const primaryOrSecondary = page.getByRole('button', { name: 'Save' }).or(page.getByRole('button', { name: 'Update' }));
```

### Strictness

Locators throw if multiple elements match. Use `first()`, `last()`, `nth()` only when intentional:

```ts
// Throws if multiple buttons match — forces you to be precise
await page.getByRole('button', { name: 'Delete' }).click();

// Explicit selection when multiple matches are expected
await page.getByRole('listitem').first().click();
await page.getByRole('row').nth(2).getByRole('button').click();
```

## Web-First Assertions

```ts
// BAD: No auto-wait, flaky
expect(await page.getByText('Success').isVisible()).toBe(true);

// GOOD: Auto-waits up to timeout
await expect(page.getByText('Success')).toBeVisible();
await expect(page.getByRole('button')).toBeEnabled();
await expect(page.getByTestId('status')).toHaveText('Submitted');
await expect(page).toHaveURL(/dashboard/);
await expect(page).toHaveTitle('Dashboard');

// Collections
await expect(page.getByRole('listitem')).toHaveCount(5);
await expect(page.getByRole('listitem')).toHaveText(['Item 1', 'Item 2', 'Item 3']);

// Soft assertions — continue on failure, report all at end
await expect.soft(locator).toBeVisible();
await expect.soft(locator).toHaveText('Expected');
```

## Page Object Model

Encapsulate page interactions. Define locators as readonly properties in constructor so they are computed once and reused.

```ts
// pages/base.page.ts
import { type Page, type Locator, expect } from '@playwright/test';
import debug from 'debug';

export abstract class BasePage {
  protected readonly log: debug.Debugger;

  constructor(
    protected readonly page: Page,
    protected readonly timeout = 30_000
  ) {
    this.log = debug(`test:page:${this.constructor.name}`);
  }

  protected async safeClick(locator: Locator, description?: string) {
    this.log('clicking: %s', description ?? locator);
    await expect(locator).toBeVisible({ timeout: this.timeout });
    await expect(locator).toBeEnabled({ timeout: this.timeout });
    await locator.click();
  }

  protected async safeFill(locator: Locator, value: string) {
    await expect(locator).toBeVisible({ timeout: this.timeout });
    await locator.fill(value);
  }

  abstract isLoaded(): Promise<void>;
}
```

```ts
// pages/login.page.ts
import { type Locator, type Page, expect } from '@playwright/test';
import { BasePage } from './base.page';

export class LoginPage extends BasePage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
    await this.isLoaded();
  }

  async isLoaded() {
    await expect(this.emailInput).toBeVisible();
  }

  async login(email: string, password: string) {
    await this.safeFill(this.emailInput, email);
    await this.safeFill(this.passwordInput, password);
    await this.safeClick(this.submitButton, 'Sign in button');
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toHaveText(message);
  }
}
```

## Fixtures

Prefer fixtures over `beforeEach`/`afterEach`. Fixtures encapsulate setup + teardown, run on-demand, and compose with dependencies.

```ts
// fixtures/index.ts
import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/login.page';
import { DashboardPage } from '../pages/dashboard.page';

type TestFixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
};

export const test = base.extend<TestFixtures>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await use(loginPage);
  },

  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
});

export { expect };
```

### Worker-Scoped Fixtures

Use for expensive setup shared across tests (database connections, authenticated users). Runs once per worker, not once per test.

```ts
// fixtures/auth.fixture.ts
import { test as base } from '@playwright/test';

type WorkerFixtures = {
  authenticatedUser: { token: string; userId: string };
};

export const test = base.extend<{}, WorkerFixtures>({
  authenticatedUser: [async ({}, use) => {
    const user = await createTestUser();
    const token = await authenticateUser(user);

    await use({ token, userId: user.id });

    // Cleanup after all tests in worker complete
    await deleteTestUser(user.id);
  }, { scope: 'worker' }],
});
```

### Automatic Fixtures

Run for every test without explicit declaration in the test body:

```ts
export const test = base.extend<{ autoLog: void }>({
  autoLog: [async ({ page }, use) => {
    page.on('console', msg => console.log(`[browser] ${msg.text()}`));
    await use();
  }, { auto: true }],
});
```

## Authentication

Save authenticated state to reuse across tests. Never log in via UI in every test — it's slow and fragile.

```ts
// auth.setup.ts
import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: authFile });
});
```

```ts
// playwright.config.ts — wire up setup project
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

### API Authentication (Faster)

Bypass the UI entirely when your API supports it:

```ts
setup('authenticate via API', async ({ request }) => {
  const response = await request.post('/api/auth/login', {
    data: { email: process.env.TEST_USER_EMAIL, password: process.env.TEST_USER_PASSWORD },
  });
  expect(response.ok()).toBeTruthy();
  await request.storageState({ path: authFile });
});
```

## Network Mocking

Always set up routes before navigation — routes must be registered before the page makes requests.

```ts
test('displays mocked data', async ({ page }) => {
  await page.route('**/api/users', route => route.fulfill({
    json: [{ id: 1, name: 'Test User' }],
  }));

  await page.goto('/users');
  await expect(page.getByText('Test User')).toBeVisible();
});

// Modify real response — fetch it then augment before fulfilling
test('injects item into response', async ({ page }) => {
  await page.route('**/api/items', async route => {
    const response = await route.fetch();
    const json = await response.json();
    json.push({ id: 999, name: 'Injected' });
    await route.fulfill({ response, json });
  });
  await page.goto('/items');
});

// HAR recording — record once, replay in CI
test('uses recorded responses', async ({ page }) => {
  await page.routeFromHAR('./fixtures/api.har', {
    url: '**/api/**',
    update: false, // set true to re-record
  });
  await page.goto('/');
});
```

## Test Isolation

Each test gets a fresh browser context. Never share mutable state between tests.

```ts
// BAD: Tests depend on each other — order-sensitive, fragile
let userId: string;
test('create user', async ({ request }) => {
  userId = (await (await request.post('/api/users', { data: { name: 'Test' } })).json()).id;
});
test('delete user', async ({ request }) => {
  await request.delete(`/api/users/${userId}`); // Breaks if run alone
});

// GOOD: Each test is self-contained
test('can delete created user', async ({ request }) => {
  const { id } = await (await request.post('/api/users', { data: { name: 'Test' } })).json();
  const deleteResponse = await request.delete(`/api/users/${id}`);
  expect(deleteResponse.ok()).toBeTruthy();
});
```

## Configuration

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  // Minimal reporter prevents context overflow in CI/agent contexts
  reporter: process.env.CI || process.env.CLAUDE
    ? [['line'], ['html', { open: 'never' }]]
    : 'list',

  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },

  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
    },
  ],

  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## Project Structure

```
tests/
  fixtures/           # Custom fixtures (extend base test)
  pages/              # Page Object Models
  helpers/            # Utility functions (API clients, data factories)
  auth.setup.ts       # Authentication setup project
  *.spec.ts           # Test files
playwright/
  .auth/              # Auth state storage (gitignored)
playwright.config.ts
```

Organize tests by feature or user journey. Colocate page objects with tests when possible.

## Helpers

Keep helpers separate from page objects. Page objects model UI structure; helpers handle data setup and cross-cutting concerns.

```ts
// helpers/user.helper.ts
import type { Page } from '@playwright/test';
import debug from 'debug';

const log = debug('test:helper:user');

export class UserHelper {
  constructor(private page: Page) {}

  async createUser(data: { name: string; email: string }) {
    log('creating user: %s', data.email);
    const response = await this.page.request.post('/api/users', { data });
    return response.json();
  }

  async deleteUser(id: string) {
    log('deleting user: %s', id);
    await this.page.request.delete(`/api/users/${id}`);
  }
}

// helpers/data.factory.ts
export function createTestUser(overrides: Partial<User> = {}): User {
  return {
    id: crypto.randomUUID(),
    email: `test-${Date.now()}@example.com`,
    name: 'Test User',
    ...overrides,
  };
}
```

## Debugging

```bash
npx playwright test --debug           # Step through with inspector
npx playwright test --trace on        # Record trace for all tests
npx playwright test --ui              # Interactive UI mode
npx playwright codegen localhost:3000 # Generate locators interactively
npx playwright show-report            # View HTML report
```

Enable debug logs: `DEBUG=test:* npx playwright test`
