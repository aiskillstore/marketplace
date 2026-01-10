# Page Object Model (POM) for Testing

## What is Page Object Model?

The Page Object Model (POM) is a design pattern for creating object-oriented representations of pages or components in your web application. Each page is represented as a class that encapsulates:

- **Locators** for UI elements (selectors)
- **Actions** that can be performed on the page (methods)
- **Data validation** specific to that page

Tests then use these page objects instead of directly interacting with raw HTML elements or Playwright/Cypress commands.

## Structure

```
Page (Login)
├── Locators
│   ├── usernameInput = '#username'
│   ├── passwordInput = '#password'
│   └── submitButton = 'button[type="submit"]'
├── Actions
│   ├── enterUsername(username)
│   ├── enterPassword(password)
│   ├── submit()
│   └── loginAs(username, password)
└── Assertions
    ├── isErrorDisplayed()
    └── getErrorMessage()
```

## Why POM Helps AI in Testing

POM introduces **clarity and separability** in test code—very similar to how Clean Architecture does for app code. Instead of an AI writing a monolithic script with a sequence of clicks and assertions, it can first generate a LoginPage class with methods, then write test scenarios that call those methods.

### Multiple Benefits

#### 1. Clarity & Readability

Test scripts become concise and intent-focused:

```typescript
// ❌ Without POM - Hard to understand intent
test('user can log in', async ({ page }) => {
  await page.fill('#username', 'alice');
  await page.fill('#password', 'pass123');
  await page.click('button[type="submit"]');
  await page.waitForNavigation();
  const welcomeText = await page.textContent('.welcome-msg');
  expect(welcomeText).toContain('Welcome, Alice');
});

// ✅ With POM - Clear intent
test('user can log in', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.loginAs('alice', 'pass123');
  await expect(page).toHaveURL(/.*\/dashboard/);
  expect(await loginPage.getWelcomeMessage()).toContain('Alice');
});
```

Copilot and ChatGPT are good at completing boilerplate; with POM, they can suggest the repetitive parts (selectors and methods) in a structured way.

#### 2. Reduced Duplication

The AI doesn't have to rewrite the logic to click the "Login" button in every test—it generates it once in the page object. This ensures consistency and reduces maintenance.

#### 3. Leverage AI Capabilities

Modern AI coding tools are surprisingly adept at POM-style generation. GitHub Copilot and ChatGPT can generate boilerplate POM classes and entire test functions from context. You can prompt: "write a test that logs in and checks welcome message" and it will utilize the page object's methods correctly.

#### 4. Maintainability

If the UI changes, you update the page object class, and all tests benefit automatically.

## Playwright Example

### Step 1: Create Page Object

```typescript
/**
 * LoginPage
 * Represents the login page and encapsulates its interactions
 */
export class LoginPage {
  // Locators
  private readonly usernameInput = '#username';
  private readonly passwordInput = '#password';
  private readonly submitButton = 'button[type="submit"]';
  private readonly errorMessage = '.error-message';
  private readonly rememberMeCheckbox = '#remember-me';

  constructor(private page: Page) {}

  /**
   * Enter username into the username field
   */
  async enterUsername(username: string): Promise<void> {
    await this.page.fill(this.usernameInput, username);
  }

  /**
   * Enter password into the password field
   */
  async enterPassword(password: string): Promise<void> {
    await this.page.fill(this.passwordInput, password);
  }

  /**
   * Click the submit/login button
   */
  async submit(): Promise<void> {
    await this.page.click(this.submitButton);
  }

  /**
   * Higher-level action combining login steps
   */
  async loginAs(username: string, password: string): Promise<void> {
    await this.enterUsername(username);
    await this.enterPassword(password);
    await this.submit();
  }

  /**
   * Variant: login with remember me option
   */
  async loginWithRememberMe(username: string, password: string): Promise<void> {
    await this.enterUsername(username);
    await this.enterPassword(password);
    await this.page.check(this.rememberMeCheckbox);
    await this.submit();
  }

  /**
   * Get error message text
   */
  async getErrorMessage(): Promise<string | null> {
    const errorElement = await this.page.$(this.errorMessage);
    if (!errorElement) return null;
    return await errorElement.textContent();
  }

  /**
   * Check if error is displayed
   */
  async isErrorDisplayed(): Promise<boolean> {
    const errorElement = await this.page.$(this.errorMessage);
    return !!errorElement;
  }

  /**
   * Navigate to login page
   */
  async goto(): Promise<void> {
    await this.page.goto('/login');
  }
}
```

### Step 2: Create Component Page Objects

```typescript
/**
 * NavigationBar
 * Represents the main navigation component
 */
export class NavigationBar {
  private readonly logoLink = '[data-testid="logo"]';
  private readonly userMenuButton = '[data-testid="user-menu"]';
  private readonly logoutButton = '[data-testid="logout"]';

  constructor(private page: Page) {}

  async clickLogo(): Promise<void> {
    await this.page.click(this.logoLink);
  }

  async openUserMenu(): Promise<void> {
    await this.page.click(this.userMenuButton);
  }

  async logout(): Promise<void> {
    await this.openUserMenu();
    await this.page.click(this.logoutButton);
  }

  async isUserMenuOpen(): Promise<boolean> {
    return await this.page.isVisible('[role="menu"]');
  }
}

/**
 * DashboardPage
 * Represents the main dashboard
 */
export class DashboardPage {
  private readonly welcomeMessage = '.welcome-banner h1';
  private readonly userGreeting = '[data-testid="user-greeting"]';
  private readonly statsCard = '.stats-card';

  constructor(private page: Page) {}

  async getWelcomeMessage(): Promise<string> {
    return await this.page.textContent(this.welcomeMessage) || '';
  }

  async getUserGreeting(): Promise<string> {
    return await this.page.textContent(this.userGreeting) || '';
  }

  async getStatsCards(): Promise<string[]> {
    const elements = await this.page.$$(this.statsCard);
    const texts: string[] = [];
    for (const element of elements) {
      const text = await element.textContent();
      if (text) texts.push(text);
    }
    return texts;
  }

  async isVisible(): Promise<boolean> {
    return await this.page.isVisible(this.welcomeMessage);
  }
}
```

### Step 3: Write Tests Using Page Objects

```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { NavigationBar } from './pages/NavigationBar';

test.describe('Authentication', () => {
  test('user can log in with valid credentials', async ({ page }) => {
    // Arrange
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // Act
    await loginPage.loginAs('alice@example.com', 'SecurePassword123!');

    // Assert
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Verify dashboard loaded
    const dashboard = new DashboardPage(page);
    expect(await dashboard.isVisible()).toBeTruthy();
    expect(await dashboard.getWelcomeMessage()).toContain('Alice');
  });

  test('user sees error with invalid password', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    await loginPage.loginAs('alice@example.com', 'WrongPassword');

    expect(await loginPage.isErrorDisplayed()).toBeTruthy();
    expect(await loginPage.getErrorMessage()).toContain('Invalid credentials');
  });

  test('user can log in and log out', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const navBar = new NavigationBar(page);

    await loginPage.goto();
    await loginPage.loginAs('alice@example.com', 'SecurePassword123!');

    // Verify logged in
    await expect(page).toHaveURL(/.*\/dashboard/);

    // Log out
    await navBar.logout();

    // Verify logged out
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('user can log in with remember me option', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.loginWithRememberMe('alice@example.com', 'SecurePassword123!');

    // Verify session persisted (cookie check)
    const cookies = await page.context().cookies();
    const hasSessionCookie = cookies.some(c => c.name === 'session_token');
    expect(hasSessionCookie).toBeTruthy();
  });
});

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Log in before each dashboard test
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.loginAs('alice@example.com', 'SecurePassword123!');
  });

  test('dashboard displays user stats', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    const stats = await dashboard.getStatsCards();

    expect(stats.length).toBeGreaterThan(0);
    expect(stats[0]).toContain('Total Users'); // Example assertion
  });

  test('user greeting is personalized', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    const greeting = await dashboard.getUserGreeting();

    expect(greeting).toContain('Alice');
  });
});
```

## Advanced POM Patterns

### Composable Page Objects

```typescript
/**
 * Modal Page Object
 * Represents a reusable modal component
 */
export class Modal {
  private readonly backdrop = '.modal-backdrop';
  private readonly closeButton = '.modal-close';
  private readonly title = '.modal-title';

  constructor(private page: Page) {}

  async close(): Promise<void> {
    await this.page.click(this.closeButton);
  }

  async getTitle(): Promise<string> {
    return await this.page.textContent(this.title) || '';
  }

  async isVisible(): Promise<boolean> {
    return await this.page.isVisible(this.backdrop);
  }
}

/**
 * DeleteConfirmationModal
 * Extends Modal for delete confirmation
 */
export class DeleteConfirmationModal extends Modal {
  private readonly confirmButton = '[data-testid="confirm-delete"]';
  private readonly cancelButton = '[data-testid="cancel-delete"]';
  private readonly warningMessage = '.warning-message';

  async confirm(): Promise<void> {
    await this.page.click(this.confirmButton);
  }

  async cancel(): Promise<void> {
    await this.page.click(this.cancelButton);
  }

  async getWarningMessage(): Promise<string> {
    return await this.page.textContent(this.warningMessage) || '';
  }
}

// Usage in test
test('user can delete with confirmation', async ({ page }) => {
  const listPage = new ItemListPage(page);
  await listPage.goto();

  await listPage.deleteItem(0); // Opens modal

  const modal = new DeleteConfirmationModal(page);
  expect(await modal.isVisible()).toBeTruthy();
  expect(await modal.getWarningMessage()).toContain('Cannot be undone');

  await modal.confirm();
  // Verify item deleted
});
```

### Page Objects with Accessibility Testing

```typescript
/**
 * AccessibleLoginPage
 * Includes accessibility assertions
 */
export class AccessibleLoginPage extends LoginPage {
  async verifyAccessibility(): Promise<void> {
    // Verify labels are associated with inputs
    const usernameLabel = await this.page.getAttribute(
      this.usernameInput,
      'aria-label'
    );
    expect(usernameLabel).toBeTruthy();

    // Verify button is keyboard accessible
    const button = await this.page.$('button[type="submit"]');
    expect(await button?.getAttribute('tabindex')).not.toBe('-1');
  }

  async navigateWithKeyboard(): Promise<void> {
    // Tab to username field
    await this.page.keyboard.press('Tab');
    await this.enterUsername('alice');

    // Tab to password field
    await this.page.keyboard.press('Tab');
    await this.enterPassword('password');

    // Tab to submit button
    await this.page.keyboard.press('Tab');

    // Submit with Enter key
    await this.page.keyboard.press('Enter');
  }
}
```

## Cypress Example

```typescript
/**
 * LoginPage for Cypress
 */
export class CypressLoginPage {
  // Locators using Cypress selectors
  private username = '[data-cy="username-input"]';
  private password = '[data-cy="password-input"]';
  private submit = '[data-cy="login-submit"]';
  private error = '[data-cy="error-message"]';

  loginAs(username: string, password: string): void {
    cy.get(this.username).type(username);
    cy.get(this.password).type(password);
    cy.get(this.submit).click();
  }

  getErrorMessage(): Chainable<string> {
    return cy.get(this.error).invoke('text');
  }

  isErrorDisplayed(): Chainable<number> {
    return cy.get(this.error).its('length');
  }
}

// Usage
describe('Login', () => {
  it('user can login', () => {
    const loginPage = new CypressLoginPage();
    cy.visit('/login');

    loginPage.loginAs('alice@example.com', 'password123');

    cy.url().should('include', '/dashboard');
  });
});
```

## File Structure for POM Tests

```
tests/
├── e2e/
│   ├── auth.spec.ts
│   ├── dashboard.spec.ts
│   └── user-profile.spec.ts
├── pages/
│   ├── LoginPage.ts
│   ├── DashboardPage.ts
│   ├── UserProfilePage.ts
│   ├── components/
│   │   ├── NavigationBar.ts
│   │   ├── Modal.ts
│   │   └── DataTable.ts
│   └── base/
│       └── BasePage.ts
├── fixtures/
│   ├── users.json
│   └── test-data.ts
└── helpers/
    ├── test-utils.ts
    └── api-helpers.ts
```

## Best Practices

### 1. Single Responsibility

Each page object should represent one logical page or component:

```typescript
// ✅ Good - One page object
export class ProductListPage { }

// ❌ Avoid - Too many responsibilities
export class ProductListAndDetailPage { }
```

### 2. Encapsulate Locators

Keep selectors private and expose actions:

```typescript
// ✅ Good
export class LoginPage {
  private readonly usernameInput = '#username'; // Private
  async enterUsername(value: string) { } // Public action
}

// ❌ Avoid
export class LoginPage {
  usernameInput = '#username'; // Exposed locator
}
```

### 3. Use Data Test IDs

Prefer stable selectors over CSS/XPath that might break with styling:

```typescript
// ✅ Good
private readonly submitButton = '[data-testid="login-submit"]';

// ❌ Fragile
private readonly submitButton = 'form > div > button.btn.btn-primary';
```

### 4. Return Page Objects for Navigation

When actions navigate to another page, return a new page object:

```typescript
async login(): Promise<DashboardPage> {
  await this.submit();
  return new DashboardPage(this.page);
}

// Usage
const dashboard = await loginPage.login();
expect(await dashboard.getWelcomeMessage()).toContain('Welcome');
```

### 5. Wait for Elements

Always wait appropriately:

```typescript
// ✅ Good
async getUserGreeting(): Promise<string> {
  await this.page.waitForSelector(this.userGreeting);
  return await this.page.textContent(this.userGreeting) || '';
}

// ❌ Unreliable
async getUserGreeting(): Promise<string> {
  return await this.page.textContent(this.userGreeting) || '';
}
```

## Tips for AI-Generated POM Code

1. **Start with page structure** - Define all locators first
2. **Create action methods** - High-level methods (loginAs) before low-level (enterUsername)
3. **Add assertions** - Include verification methods in page objects
4. **Use inheritance** - Create BasePage for common functionality
5. **Generate tests from POMs** - Once pages are defined, tests follow naturally
6. **Name methods by intent** - Use "loginAs" not "fillAndClick"

## Common Mistakes to Avoid

### ❌ Mixing Test Logic with Page Objects

```typescript
// Wrong - test logic in page object
async loginAndVerifyDashboard() {
  await this.loginAs('user', 'pass');
  expect(await this.page.url()).toContain('/dashboard');
}
```

### ✅ Keep Page Objects Pure

```typescript
// Right - page object just interacts, test does assertions
async login() {
  await this.loginAs('user', 'pass');
}

// In test:
await loginPage.login();
expect(page.url()).toContain('/dashboard');
```

### ❌ Hardcoding Test Data

```typescript
// Wrong
async login() {
  await this.loginAs('testuser@example.com', 'hardcodedPassword');
}
```

### ✅ Pass Test Data to Methods

```typescript
// Right
async login(username: string, password: string) {
  await this.loginAs(username, password);
}

// In test:
await loginPage.login('testuser@example.com', 'password123');
```

## Key Takeaways

- **Page Objects encapsulate UI interactions** making tests more readable
- **High-level action methods** (like `loginAs`) hide implementation details
- **Reduced duplication** when same actions are needed in multiple tests
- **Easier to maintain** - UI changes only require updating page objects
- **AI naturally generates** POM-style code when shown examples
- **Composable** - Page objects can extend or use other page objects
- **Testable** - Page objects themselves can be unit tested
