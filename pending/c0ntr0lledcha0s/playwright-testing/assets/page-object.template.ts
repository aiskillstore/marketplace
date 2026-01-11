/**
 * Page Object Template for Playwright
 * 
 * Usage:
 * 1. Copy this file to your pages/ directory
 * 2. Rename to match your page (e.g., login.page.ts)
 * 3. Update class name, locators, and methods
 * 
 * @example
 * import { LoginPage } from './pages/login.page';
 * 
 * test('login test', async ({ page }) => {
 *   const loginPage = new LoginPage(page);
 *   await loginPage.goto();
 *   await loginPage.login('user@test.com', 'password');
 * });
 */

import { Page, Locator, expect } from '@playwright/test';

export class PageNamePage {
  // Page reference
  private readonly page: Page;

  // Locators - define all element selectors here
  readonly heading: Locator;
  readonly primaryButton: Locator;
  readonly inputField: Locator;
  readonly errorMessage: Locator;
  readonly successMessage: Locator;
  readonly loadingSpinner: Locator;

  constructor(page: Page) {
    this.page = page;

    // Initialize locators using best practices:
    // 1. Role-based (best)
    // 2. Label-based
    // 3. Text-based
    // 4. Test ID (last resort)
    this.heading = page.getByRole('heading', { level: 1 });
    this.primaryButton = page.getByRole('button', { name: 'Submit' });
    this.inputField = page.getByLabel('Input Field');
    this.errorMessage = page.getByRole('alert');
    this.successMessage = page.getByText('Success');
    this.loadingSpinner = page.getByTestId('loading-spinner');
  }

  /**
   * Navigate to this page
   */
  async goto() {
    await this.page.goto('/page-path');
    // Wait for page to be ready
    await expect(this.heading).toBeVisible();
  }

  /**
   * Wait for page to finish loading
   */
  async waitForLoad() {
    await expect(this.loadingSpinner).toBeHidden();
  }

  /**
   * Fill form and submit
   */
  async submitForm(value: string) {
    await this.inputField.fill(value);
    await this.primaryButton.click();
  }

  /**
   * Get error message text
   */
  async getError(): Promise<string | null> {
    if (await this.errorMessage.isVisible()) {
      return this.errorMessage.textContent();
    }
    return null;
  }

  /**
   * Check if success message is displayed
   */
  async isSuccess(): Promise<boolean> {
    return this.successMessage.isVisible();
  }

  /**
   * Perform complex action
   */
  async performAction(data: { field1: string; field2: string }) {
    // Fill multiple fields
    await this.page.getByLabel('Field 1').fill(data.field1);
    await this.page.getByLabel('Field 2').fill(data.field2);
    
    // Submit
    await this.primaryButton.click();
    
    // Wait for result
    await expect(this.successMessage.or(this.errorMessage)).toBeVisible();
  }

  /**
   * Get list of items on the page
   */
  async getItems(): Promise<string[]> {
    const items = this.page.getByRole('listitem');
    const count = await items.count();
    const texts: string[] = [];
    
    for (let i = 0; i < count; i++) {
      const text = await items.nth(i).textContent();
      if (text) texts.push(text);
    }
    
    return texts;
  }

  /**
   * Click item in a list by name
   */
  async clickItem(name: string) {
    await this.page.getByRole('listitem')
      .filter({ hasText: name })
      .click();
  }
}

/**
 * Example: Login Page Object
 */
export class LoginPage {
  private readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly forgotPasswordLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
    this.forgotPasswordLink = page.getByRole('link', { name: 'Forgot password' });
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

  async clickForgotPassword() {
    await this.forgotPasswordLink.click();
  }
}

/**
 * Example: Dashboard Page Object with table
 */
export class DashboardPage {
  private readonly page: Page;
  readonly welcomeMessage: Locator;
  readonly userTable: Locator;
  readonly addButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.welcomeMessage = page.getByText(/Welcome/);
    this.userTable = page.getByRole('table');
    this.addButton = page.getByRole('button', { name: 'Add User' });
  }

  async goto() {
    await this.page.goto('/dashboard');
    await expect(this.welcomeMessage).toBeVisible();
  }

  async getUserCount(): Promise<number> {
    const rows = this.userTable.getByRole('row');
    // Subtract 1 for header row
    return (await rows.count()) - 1;
  }

  async editUser(name: string) {
    await this.userTable
      .getByRole('row', { name })
      .getByRole('button', { name: 'Edit' })
      .click();
  }

  async deleteUser(name: string) {
    await this.userTable
      .getByRole('row', { name })
      .getByRole('button', { name: 'Delete' })
      .click();
    
    // Confirm deletion
    await this.page.getByRole('button', { name: 'Confirm' }).click();
  }
}
