---
title: Use Page Object Model for Reusability and Maintainability
impact: MEDIUM
impactDescription: Reduces test maintenance time by 40-60% and improves test readability
tags: page-object, organization, maintainability, reusability
---

## Use Page Object Model for Reusability and Maintainability

**Impact: MEDIUM (reduces test maintenance time by 40-60% and improves test readability)**

The Page Object Model (POM) pattern encapsulates page interactions into reusable classes, making tests more maintainable and readable. When UI changes occur, you only need to update the page object instead of every test that interacts with that page.

**Incorrect (duplicated selectors and logic in tests):**

```typescript
import { test, expect } from '@playwright/test';

test('user can login', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.fill('[data-testid="email-input"]', 'user@example.com');
  await page.fill('[data-testid="password-input"]', 'password123');
  await page.click('[data-testid="login-button"]');
  await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
});

test('login with invalid credentials shows error', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.fill('[data-testid="email-input"]', 'user@example.com');
  await page.fill('[data-testid="password-input"]', 'wrongpassword');
  await page.click('[data-testid="login-button"]');
  await expect(page.locator('[data-testid="error-message"]')).toContainText('Invalid credentials');
});

test('can navigate to signup from login', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.click('[data-testid="signup-link"]');
  await expect(page).toHaveURL(/.*signup/);
});

// If the login form changes, you need to update all these tests!
```

**Correct (using Page Object Model):**

```typescript
// pages/login.page.ts
import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly signupLink: Locator;
  readonly errorMessage: Locator;
  readonly welcomeMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByTestId('email-input');
    this.passwordInput = page.getByTestId('password-input');
    this.loginButton = page.getByTestId('login-button');
    this.signupLink = page.getByTestId('signup-link');
    this.errorMessage = page.getByTestId('error-message');
    this.welcomeMessage = page.getByTestId('welcome-message');
  }

  async goto() {
    await this.page.goto('https://example.com/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async expectLoginSuccess() {
    await expect(this.welcomeMessage).toBeVisible();
  }

  async expectLoginError(errorText: string) {
    await expect(this.errorMessage).toContainText(errorText);
  }

  async navigateToSignup() {
    await this.signupLink.click();
  }
}

// tests/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/login.page';

test('user can login', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password123');
  await loginPage.expectLoginSuccess();
});

test('login with invalid credentials shows error', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@example.com', 'wrongpassword');
  await loginPage.expectLoginError('Invalid credentials');
});

test('can navigate to signup from login', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.navigateToSignup();
  await expect(page).toHaveURL(/.*signup/);
});

// If the login form changes, you only update the LoginPage class!
```

**Advanced Page Object patterns:**

```typescript
// pages/base.page.ts - Base class for common functionality
export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  async takeScreenshot(name: string) {
    await this.page.screenshot({ path: `screenshots/${name}.png` });
  }
}

// pages/dashboard.page.ts - Extending base page
import { BasePage } from './base.page';
import { Locator } from '@playwright/test';

export class DashboardPage extends BasePage {
  readonly userMenu: Locator;
  readonly logoutButton: Locator;

  constructor(page: Page) {
    super(page);
    this.userMenu = page.getByTestId('user-menu');
    this.logoutButton = page.getByRole('button', { name: 'Logout' });
  }

  async goto() {
    await this.page.goto('https://example.com/dashboard');
    await this.waitForPageLoad();
  }

  async logout() {
    await this.userMenu.click();
    await this.logoutButton.click();
  }
}

// pages/components/header.component.ts - Reusable component
export class HeaderComponent {
  readonly page: Page;
  readonly logo: Locator;
  readonly searchInput: Locator;
  readonly navLinks: Locator;

  constructor(page: Page) {
    this.page = page;
    const header = page.locator('header');
    this.logo = header.getByAltText('Logo');
    this.searchInput = header.getByPlaceholder('Search...');
    this.navLinks = header.getByRole('navigation').getByRole('link');
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
  }

  async navigateTo(linkName: string) {
    await this.navLinks.filter({ hasText: linkName }).click();
  }
}

// Using components in page objects
export class HomePage extends BasePage {
  readonly header: HeaderComponent;
  readonly hero: Locator;

  constructor(page: Page) {
    super(page);
    this.header = new HeaderComponent(page);
    this.hero = page.getByTestId('hero-section');
  }

  async goto() {
    await this.page.goto('https://example.com');
  }
}

// tests/homepage.spec.ts
test('can search from homepage', async ({ page }) => {
  const homePage = new HomePage(page);
  await homePage.goto();
  await homePage.header.search('playwright');
  await expect(page).toHaveURL(/.*search.*playwright/);
});
```

**Page Object with fixtures:**

```typescript
// fixtures/pages.fixture.ts
import { test as base } from '@playwright/test';
import { LoginPage } from '../pages/login.page';
import { DashboardPage } from '../pages/dashboard.page';
import { HomePage } from '../pages/home.page';

type PageFixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  homePage: HomePage;
};

export const test = base.extend<PageFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
  
  homePage: async ({ page }, use) => {
    await use(new HomePage(page));
  },
});

export { expect } from '@playwright/test';

// tests/with-fixtures.spec.ts
import { test, expect } from '../fixtures/pages.fixture';

test('login and navigate', async ({ loginPage, dashboardPage }) => {
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password123');
  await dashboardPage.expectToBeOnDashboard();
});
```

**Best practices for Page Objects:**

```typescript
export class ProductPage {
  readonly page: Page;
  
  // ✅ Use descriptive names for locators
  readonly addToCartButton: Locator;
  readonly productTitle: Locator;
  readonly productPrice: Locator;
  
  constructor(page: Page) {
    this.page = page;
    // ✅ Define locators in constructor
    this.addToCartButton = page.getByRole('button', { name: 'Add to Cart' });
    this.productTitle = page.getByTestId('product-title');
    this.productPrice = page.getByTestId('product-price');
  }
  
  // ✅ Methods represent user actions
  async addToCart() {
    await this.addToCartButton.click();
  }
  
  // ✅ Return values when needed for chaining or assertions
  async getProductTitle(): Promise<string> {
    return await this.productTitle.textContent() || '';
  }
  
  // ✅ Include assertion methods for common checks
  async expectProductInStock() {
    await expect(this.addToCartButton).toBeEnabled();
    await expect(this.page.getByText('In Stock')).toBeVisible();
  }
  
  // ✅ Support method chaining for fluent API
  async selectQuantity(quantity: number) {
    await this.page.selectOption('[name="quantity"]', quantity.toString());
    return this; // Enable chaining
  }
  
  async selectSize(size: string) {
    await this.page.getByRole('button', { name: size }).click();
    return this; // Enable chaining
  }
}

// Usage with chaining
test('configure product', async ({ page }) => {
  const productPage = new ProductPage(page);
  await productPage.goto();
  await productPage
    .selectSize('Large')
    .selectQuantity(2);
  await productPage.addToCart();
});
```

Benefits of Page Object Model:
- **Maintainability**: UI changes only require updates in one place
- **Reusability**: Page objects can be used across multiple tests
- **Readability**: Tests read like user actions, not implementation details
- **Type safety**: TypeScript provides autocomplete and compile-time checks
- **Separation of concerns**: Test logic separated from page structure
- **DRY principle**: Don't Repeat Yourself - avoid duplicating selectors and logic

When to use Page Objects:
- ✅ Complex applications with multiple pages
- ✅ Frequently changing UI
- ✅ Shared functionality across tests
- ✅ Large test suites

When it might be overkill:
- ❌ Very simple applications with few pages
- ❌ One-off scripts or exploratory tests
- ❌ When page interactions appear in only one test

Reference: [Playwright Page Object Model](https://playwright.dev/docs/pom)