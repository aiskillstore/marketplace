---
title: Use Custom Fixtures for Reusable Test Setup and Teardown
impact: MEDIUM
impactDescription: Reduces code duplication by 60-80% and improves test maintainability
tags: fixtures, reusability, custom-fixtures, merge, test-organization
---

## Use Custom Fixtures for Reusable Test Setup and Teardown

**Impact: MEDIUM (reduces code duplication by 60-80% and improves test maintainability)**

Custom fixtures in Playwright allow you to encapsulate reusable setup and teardown logic, share data across tests, and compose complex test scenarios. By extending Playwright's built-in fixtures, you can create domain-specific test helpers that make tests more readable and maintainable while eliminating code duplication.

## When to Use

- **Use custom fixtures when**: You have setup/teardown logic repeated in 3+ tests, need to share authenticated sessions, require database setup, or manage complex test data
- **Essential for**: Authentication flows, API client configuration, database connections, test data creation, page object initialization, mock server setup
- **Consider alternatives when**: Setup is unique to a single test (use inline setup), or fixture would have only one consumer (may be over-engineering)
- **Required for**: Projects with 20+ tests, multi-user role scenarios, integration tests with external dependencies

## Guidelines

### Do

- Create focused fixtures that handle a single responsibility (auth, database, API)
- Use worker-scoped fixtures for expensive operations (database connections, authentication state)
- Compose fixtures by declaring dependencies on other fixtures
- Provide TypeScript types for all custom fixtures
- Use automatic fixtures only for truly global setup that every test needs
- Document fixture cleanup behavior and dependencies
- Keep fixtures in separate files organized by domain (auth.fixture.ts, db.fixture.ts)
- Merge multiple fixture files using `.extend()` chains

### Don't

- Don't duplicate setup logic across fixtures - use fixture dependencies instead
- Don't create fixtures for one-time setup - inline it in the test
- Don't make fixtures too complex - break them into smaller, composable fixtures
- Don't forget teardown logic - always clean up resources in fixtures
- Don't use test-scoped fixtures for expensive operations - use worker-scoped instead
- Don't ignore type safety - always type your fixture objects

### Tool Usage Patterns

- **Primary tools**: `test.extend<FixtureType>()`, `mergeTests()`, `mergeExpects()` from Playwright
- **Configuration**: No special playwright.config.ts required, but can configure globalSetup/globalTeardown for extreme cases
- **Fixture scopes**: 
  - Test-scoped (default): Fresh instance per test
  - Worker-scoped (`{ scope: 'worker' }`): Shared across tests in same worker process
  - Automatic (`{ auto: true }`): Runs for every test even if not explicitly used
- **Helper patterns**: Use `use()` callback to provide fixture value, setup before `use()`, teardown after `use()`

## Edge Cases and Constraints

### Limitations

- Worker-scoped fixtures cannot depend on test-scoped fixtures
- Automatic fixtures run even when not used, potentially slowing down tests
- Fixture dependencies create initialization chains that can be hard to debug if broken
- Parameterized fixtures require test.use() calls which can be forgotten
- Storage state sharing across workers requires careful synchronization

### Edge Cases

1. **Circular fixture dependencies**: If fixture A depends on B and B depends on A, Playwright will error. Solution: Refactor to remove circular dependency or merge into single fixture.

2. **Fixture cleanup failures**: If teardown logic throws an error, test still passes but resources leak. Solution: Wrap teardown in try-catch and log failures.

3. **Parallel test isolation**: Test-scoped fixtures run in parallel, can cause race conditions with shared resources. Solution: Use worker-scoped fixtures or ensure resources are truly isolated.

4. **Authentication token expiry**: Worker-scoped auth tokens may expire during long test runs. Solution: Refresh tokens before use or make token fixture test-scoped.

5. **Database transaction rollback**: If database fixture uses transactions, nested fixtures may commit/rollback at wrong times. Solution: Use single transaction per test or careful transaction boundary management.

### What Breaks If Ignored

- **Without fixtures**: 60-80% code duplication across tests, setup logic scattered everywhere
- **Without proper cleanup**: Resource leaks (database connections, API sessions, file handles)
- **Without worker scoping**: Slow test execution (re-authenticating 100 times vs once per worker)
- **Without type safety**: Runtime errors from incorrect fixture usage, no autocomplete
- **Without composition**: Deeply nested setup code, hard to maintain, impossible to reuse

**Incorrect (duplicated setup in every test):**

```typescript
import { test, expect } from '@playwright/test';

test('user can view profile', async ({ page }) => {
  // ❌ Duplicated login logic in every test
  await page.goto('https://example.com/login');
  await page.fill('[name="email"]', 'user@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');
  
  await page.goto('/profile');
  await expect(page.locator('.profile-name')).toBeVisible();
});

test('user can update settings', async ({ page }) => {
  // ❌ Same login logic duplicated
  await page.goto('https://example.com/login');
  await page.fill('[name="email"]', 'user@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');
  
  await page.goto('/settings');
  await page.click('[data-testid="edit-profile"]');
});

test('admin can access admin panel', async ({ page }) => {
  // ❌ Similar but slightly different for admin
  await page.goto('https://example.com/login');
  await page.fill('[name="email"]', 'admin@example.com');
  await page.fill('[name="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard');
  
  await page.goto('/admin');
  await expect(page.locator('.admin-panel')).toBeVisible();
});
```

**Correct (using custom fixtures):**

```typescript
// fixtures/auth.fixture.ts
import { test as base, expect, Page } from '@playwright/test';

type AuthFixtures = {
  authenticatedPage: Page;
  adminPage: Page;
};

// ✅ Extend base test with custom fixtures
export const test = base.extend<AuthFixtures>({
  // ✅ Regular user authentication fixture
  authenticatedPage: async ({ page }, use) => {
    // Setup: Login as regular user
    await page.goto('https://example.com/login');
    await page.fill('[name="email"]', 'user@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    
    // Provide authenticated page to test
    await use(page);
    
    // Teardown: Logout happens automatically (page context is disposed)
  },

  // ✅ Admin authentication fixture
  adminPage: async ({ page }, use) => {
    // Setup: Login as admin
    await page.goto('https://example.com/login');
    await page.fill('[name="email"]', 'admin@example.com');
    await page.fill('[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    
    // Provide admin page to test
    await use(page);
    
    // Teardown: Automatic cleanup
  },
});

export { expect };

// tests/profile.spec.ts
import { test, expect } from '../fixtures/auth.fixture';

test('user can view profile', async ({ authenticatedPage }) => {
  // ✅ No login code needed - already authenticated
  await authenticatedPage.goto('/profile');
  await expect(authenticatedPage.locator('.profile-name')).toBeVisible();
});

test('user can update settings', async ({ authenticatedPage }) => {
  // ✅ Reuse authentication fixture
  await authenticatedPage.goto('/settings');
  await authenticatedPage.click('[data-testid="edit-profile"]');
});

test('admin can access admin panel', async ({ adminPage }) => {
  // ✅ Use admin-specific fixture
  await adminPage.goto('/admin');
  await expect(adminPage.locator('.admin-panel')).toBeVisible();
});
```

**Merging multiple fixture files:**

```typescript
// fixtures/auth.fixture.ts
import { test as base, Page } from '@playwright/test';

export type AuthFixtures = {
  authenticatedPage: Page;
};

export const authFixture = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'user@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await use(page);
  },
});

// fixtures/database.fixture.ts
import { test as base } from '@playwright/test';

export type DatabaseFixtures = {
  dbConnection: DatabaseConnection;
  testUser: User;
};

export const databaseFixture = base.extend<DatabaseFixtures>({
  dbConnection: async ({}, use) => {
    const db = await connectToDatabase();
    await use(db);
    await db.close();
  },

  testUser: async ({ dbConnection }, use) => {
    const user = await dbConnection.createUser({
      email: 'test@example.com',
      name: 'Test User',
    });
    await use(user);
    await dbConnection.deleteUser(user.id);
  },
});

// fixtures/api.fixture.ts
import { test as base, APIRequestContext } from '@playwright/test';

export type ApiFixtures = {
  apiContext: APIRequestContext;
  authenticatedApi: APIRequestContext;
};

export const apiFixture = base.extend<ApiFixtures>({
  apiContext: async ({ playwright }, use) => {
    const context = await playwright.request.newContext({
      baseURL: 'https://api.example.com',
    });
    await use(context);
    await context.dispose();
  },

  authenticatedApi: async ({ apiContext }, use) => {
    const response = await apiContext.post('/auth/login', {
      data: { email: 'user@example.com', password: 'password123' },
    });
    const { token } = await response.json();
    
    const authContext = await playwright.request.newContext({
      baseURL: 'https://api.example.com',
      extraHTTPHeaders: { 'Authorization': `Bearer ${token}` },
    });
    
    await use(authContext);
    await authContext.dispose();
  },
});

// fixtures/index.ts - ✅ Merge all fixtures
import { test as base } from '@playwright/test';
import { authFixture, AuthFixtures } from './auth.fixture';
import { databaseFixture, DatabaseFixtures } from './database.fixture';
import { apiFixture, ApiFixtures } from './api.fixture';

// ✅ Merge multiple fixture types
type AllFixtures = AuthFixtures & DatabaseFixtures & ApiFixtures;

// ✅ Combine all fixture extensions
export const test = base
  .extend<AuthFixtures>(authFixture)
  .extend<DatabaseFixtures>(databaseFixture)
  .extend<ApiFixtures>(apiFixture);

export { expect } from '@playwright/test';

// tests/integration.spec.ts
import { test, expect } from '../fixtures';

// ✅ Use all fixtures together
test('create user via API and verify in UI', async ({
  authenticatedPage,
  authenticatedApi,
  testUser,
}) => {
  // Use API fixture to create data
  const response = await authenticatedApi.post('/users', {
    data: { name: 'New User', email: 'new@example.com' },
  });
  const newUser = await response.json();

  // Use authenticated page to verify
  await authenticatedPage.goto(`/users/${newUser.id}`);
  await expect(authenticatedPage.locator('.user-name')).toHaveText('New User');

  // testUser fixture provides pre-created test user
  await authenticatedPage.goto(`/users/${testUser.id}`);
  await expect(authenticatedPage.locator('.user-name')).toHaveText('Test User');
});
```

**Worker-scoped fixtures (shared across tests in same worker):**

```typescript
// fixtures/worker-scoped.fixture.ts
import { test as base } from '@playwright/test';

type WorkerFixtures = {
  // ✅ Worker-scoped: set up once per worker process
  workerStorageState: string;
};

type TestFixtures = {
  // Test-scoped: set up for each test
  authenticatedPage: Page;
};

export const test = base.extend<TestFixtures, WorkerFixtures>({
  // ✅ Worker-scoped fixture - runs once per worker
  workerStorageState: [async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Authenticate once per worker
    await page.goto('/login');
    await page.fill('[name="email"]', 'user@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    
    // Save authentication state
    const storageState = await context.storageState();
    await context.close();
    
    await use(JSON.stringify(storageState));
  }, { scope: 'worker' }],

  // ✅ Test-scoped fixture using worker fixture
  authenticatedPage: async ({ page, workerStorageState }, use) => {
    // Reuse authentication state from worker
    await page.context().addCookies(JSON.parse(workerStorageState).cookies);
    await use(page);
  },
});
```

**Automatic and manual fixtures:**

```typescript
// fixtures/automatic.fixture.ts
import { test as base } from '@playwright/test';

type AutoFixtures = {
  // ✅ Automatic fixture: always runs, even if not used
  globalSetup: void;
  
  // Manual fixture: only runs when explicitly used
  databaseConnection: DatabaseConnection;
};

export const test = base.extend<AutoFixtures>({
  // ✅ Automatic fixture with 'auto' option
  globalSetup: [async ({}, use) => {
    console.log('Setting up global configuration');
    // Set environment variables, configure mocks, etc.
    process.env.TEST_MODE = 'true';
    
    await use();
    
    // Cleanup
    delete process.env.TEST_MODE;
    console.log('Cleaned up global configuration');
  }, { auto: true }],

  // ✅ Manual fixture: only runs when test needs it
  databaseConnection: async ({}, use) => {
    console.log('Connecting to database');
    const db = await connectToDatabase();
    await use(db);
    await db.close();
    console.log('Closed database connection');
  },
});

// Test 1: globalSetup runs, databaseConnection doesn't
test('test without database', async ({ page }) => {
  // globalSetup runs automatically
  // databaseConnection does NOT run (not needed)
  await page.goto('/');
});

// Test 2: both run
test('test with database', async ({ page, databaseConnection }) => {
  // globalSetup runs automatically
  // databaseConnection runs because it's used
  await databaseConnection.query('SELECT * FROM users');
});
```

**Fixture dependencies:**

```typescript
// fixtures/dependent.fixture.ts
import { test as base } from '@playwright/test';

type DependentFixtures = {
  apiToken: string;
  apiClient: ApiClient;
  authenticatedUser: User;
};

export const test = base.extend<DependentFixtures>({
  // ✅ Base fixture: generates API token
  apiToken: async ({}, use) => {
    const response = await fetch('https://api.example.com/auth/token', {
      method: 'POST',
      body: JSON.stringify({ client_id: 'test' }),
    });
    const { token } = await response.json();
    
    await use(token);
    
    // Revoke token after test
    await fetch(`https://api.example.com/auth/revoke/${token}`, {
      method: 'DELETE',
    });
  },

  // ✅ Dependent fixture: uses apiToken
  apiClient: async ({ apiToken }, use) => {
    const client = new ApiClient({
      baseURL: 'https://api.example.com',
      headers: { 'Authorization': `Bearer ${apiToken}` },
    });
    
    await use(client);
  },

  // ✅ Depends on apiClient
  authenticatedUser: async ({ apiClient }, use) => {
    const user = await apiClient.getCurrentUser();
    await use(user);
  },
});

// Test uses highest-level fixture, dependencies run automatically
test('user can access profile', async ({ authenticatedUser, page }) => {
  // apiToken → apiClient → authenticatedUser all run in order
  await page.goto(`/profile/${authenticatedUser.id}`);
});
```

**Parameterized fixtures:**

```typescript
// fixtures/parameterized.fixture.ts
import { test as base } from '@playwright/test';

type UserRole = 'admin' | 'user' | 'guest';

type RoleFixtures = {
  userRole: UserRole;
  roleBasedPage: Page;
};

export const test = base.extend<RoleFixtures>({
  userRole: ['user', { option: true }], // ✅ Default value with option flag

  roleBasedPage: async ({ page, userRole }, use) => {
    // ✅ Login based on role parameter
    const credentials = {
      admin: { email: 'admin@example.com', password: 'admin123' },
      user: { email: 'user@example.com', password: 'user123' },
      guest: { email: 'guest@example.com', password: 'guest123' },
    };

    const creds = credentials[userRole];
    await page.goto('/login');
    await page.fill('[name="email"]', creds.email);
    await page.fill('[name="password"]', creds.password);
    await page.click('button[type="submit"]');
    
    await use(page);
  },
});

// ✅ Override fixture parameter per test
test('admin dashboard', async ({ roleBasedPage }) => {
  test.use({ userRole: 'admin' });
  await roleBasedPage.goto('/admin');
});

test('user dashboard', async ({ roleBasedPage }) => {
  test.use({ userRole: 'user' });
  await roleBasedPage.goto('/dashboard');
});

// ✅ Or use in describe block
test.describe('Admin tests', () => {
  test.use({ userRole: 'admin' });

  test('can access admin panel', async ({ roleBasedPage }) => {
    await roleBasedPage.goto('/admin');
  });

  test('can manage users', async ({ roleBasedPage }) => {
    await roleBasedPage.goto('/admin/users');
  });
});
```

**Complex fixture composition example:**

```typescript
// fixtures/complete.fixture.ts
import { test as base, Page } from '@playwright/test';
import { connectDB, Database } from './db';
import { ApiClient } from './api-client';

// ✅ Define all fixture types
type CompleteFixtures = {
  // Database
  database: Database;
  testUser: User;
  
  // API
  apiClient: ApiClient;
  
  // Authentication
  authToken: string;
  authenticatedPage: Page;
  
  // Page Objects
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
};

export const test = base.extend<CompleteFixtures>({
  // ✅ Level 1: Database connection
  database: async ({}, use) => {
    const db = await connectDB();
    await use(db);
    await db.disconnect();
  },

  // ✅ Level 2: Test user (depends on database)
  testUser: async ({ database }, use) => {
    const user = await database.users.create({
      email: `test-${Date.now()}@example.com`,
      password: 'password123',
      role: 'user',
    });
    
    await use(user);
    
    await database.users.delete(user.id);
  },

  // ✅ Level 3: Auth token (depends on testUser)
  authToken: async ({ testUser }, use) => {
    const response = await fetch('https://api.example.com/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: testUser.email,
        password: 'password123',
      }),
    });
    
    const { token } = await response.json();
    await use(token);
  },

  // ✅ Level 4: API client (depends on authToken)
  apiClient: async ({ authToken }, use) => {
    const client = new ApiClient({
      baseURL: 'https://api.example.com',
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    
    await use(client);
  },

  // ✅ Level 4: Authenticated page (depends on authToken)
  authenticatedPage: async ({ page, authToken }, use) => {
    await page.goto('/login');
    // Inject token directly (faster than UI login)
    await page.evaluate((token) => {
      localStorage.setItem('authToken', token);
    }, authToken);
    await page.goto('/dashboard');
    
    await use(page);
  },

  // ✅ Page objects (depend on authenticatedPage)
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  dashboardPage: async ({ authenticatedPage }, use) => {
    await use(new DashboardPage(authenticatedPage));
  },
});

export { expect } from '@playwright/test';

// tests/complete.spec.ts
import { test, expect } from '../fixtures/complete.fixture';

test('complete workflow with all fixtures', async ({
  testUser,
  apiClient,
  authenticatedPage,
  dashboardPage,
  database,
}) => {
  // ✅ All fixtures available and properly initialized
  
  // Use API client
  const profile = await apiClient.get(`/users/${testUser.id}`);
  expect(profile.email).toBe(testUser.email);
  
  // Use authenticated page
  await dashboardPage.goto();
  await expect(dashboardPage.welcomeMessage).toContainText(testUser.email);
  
  // Verify in database
  const dbUser = await database.users.findById(testUser.id);
  expect(dbUser.lastLogin).toBeDefined();
  
  // All fixtures are automatically cleaned up after test
});
```

## Common Mistakes

### Mistake 1: Creating fixtures that are too broad

```typescript
// ❌ Bad: One giant fixture doing everything
export const test = base.extend({
  everything: async ({ page }, use) => {
    // Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'user@example.com');
    // Database setup
    const db = await connectDB();
    // API setup
    const api = new ApiClient();
    // Mock setup
    await page.route('**/api/**', route => route.fulfill({ body: '{}' }));
    
    await use({ page, db, api }); // ❌ Too many responsibilities
    
    await db.close();
  },
});
```

**Why this is wrong**: Violates single responsibility, makes fixture hard to reuse, forces tests to initialize everything even if they only need one part.

**How to fix**:

```typescript
// ✅ Good: Separate, focused fixtures
export const test = base
  .extend<{ authenticatedPage: Page }>({ /* auth only */ })
  .extend<{ database: Database }>({ /* db only */ })
  .extend<{ apiClient: ApiClient }>({ /* api only */ });
```

### Mistake 2: Forgetting to clean up resources

```typescript
// ❌ Bad: No cleanup
export const test = base.extend({
  database: async ({}, use) => {
    const db = await connectDB();
    await use(db);
    // ❌ Missing: await db.close();
  },
});
```

**Why this is wrong**: Leaks database connections, file handles, or other resources. With 100 tests, could exhaust connection pool.

**How to fix**:

```typescript
// ✅ Good: Always clean up
export const test = base.extend({
  database: async ({}, use) => {
    const db = await connectDB();
    await use(db);
    await db.close(); // ✅ Cleanup
  },
});
```

### Mistake 3: Using test-scoped fixtures for expensive operations

```typescript
// ❌ Bad: Authenticating for every single test
export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    // ❌ This runs for EACH test - very slow
    await page.goto('/login');
    await page.fill('[name="email"]', 'user@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await use(page);
  },
});
```

**Why this is wrong**: If you have 100 tests, this authenticates 100 times instead of once per worker.

**How to fix**:

```typescript
// ✅ Good: Worker-scoped for expensive operations
export const test = base.extend<{}, { storageState: string }>({
  storageState: [async ({ browser }, use) => {
    // ✅ Runs once per worker
    const context = await browser.newContext();
    const page = await context.newPage();
    await page.goto('/login');
    await page.fill('[name="email"]', 'user@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    const state = await context.storageState();
    await context.close();
    await use(JSON.stringify(state));
  }, { scope: 'worker' }],
  
  authenticatedPage: async ({ page, storageState }, use) => {
    await page.context().addCookies(JSON.parse(storageState).cookies);
    await use(page);
  },
});
```

### Mistake 4: Not typing fixtures properly

```typescript
// ❌ Bad: No types, using 'any'
export const test = base.extend({
  myFixture: async ({}, use) => {
    const data: any = { foo: 'bar' }; // ❌ No type safety
    await use(data);
  },
});
```

**Why this is wrong**: Loses TypeScript benefits, no autocomplete, runtime errors.

**How to fix**:

```typescript
// ✅ Good: Properly typed
type MyFixture = {
  foo: string;
  bar: number;
};

type MyFixtures = {
  myFixture: MyFixture;
};

export const test = base.extend<MyFixtures>({
  myFixture: async ({}, use) => {
    const data: MyFixture = { foo: 'bar', bar: 123 };
    await use(data);
  },
});
```

## Benefits and Best Practices

Benefits of custom fixtures:
- **Eliminate duplication**: Write setup/teardown logic once, reuse everywhere
- **Composability**: Combine multiple fixtures for complex scenarios
- **Dependency management**: Fixtures can depend on other fixtures
- **Automatic cleanup**: Teardown logic runs automatically after each test
- **Type safety**: TypeScript ensures correct fixture usage
- **Test isolation**: Each test gets fresh fixture instances
- **Worker optimization**: Share expensive setup across tests with worker-scoped fixtures
- **Readability**: Tests focus on behavior, not setup

When to use custom fixtures:
- ✅ Authentication/authorization logic used in multiple tests
- ✅ Database setup and teardown
- ✅ API client configuration
- ✅ Test data creation and cleanup
- ✅ Page object initialization
- ✅ Mock server setup
- ✅ Browser context customization
- ✅ Shared configuration or state

Best practices:
- Create focused fixtures that do one thing well
- Use worker-scoped fixtures for expensive operations
- Compose fixtures by depending on other fixtures
- Use automatic fixtures sparingly (only for truly global setup)
- Parameterize fixtures when you need variations
- Provide TypeScript types for all fixtures
- Document fixture dependencies and cleanup behavior
- Keep fixtures in separate files and merge them

Reference: [Playwright Custom Fixtures](https://playwright.dev/docs/test-fixtures)