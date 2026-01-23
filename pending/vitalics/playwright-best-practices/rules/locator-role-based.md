---
title: Prefer Role-Based Locators Over CSS/XPath
impact: HIGH
impactDescription: Reduces test brittleness by 60-80% and improves accessibility
tags: locators, accessibility, maintainability, resilience
---

## Prefer Role-Based Locators Over CSS/XPath

**Impact: HIGH (reduces test brittleness by 60-80% and improves accessibility)**

Role-based locators using `getByRole()` are the most resilient locator strategy in Playwright. They target elements by their accessibility role and name, making tests resistant to DOM structure changes and implementation details while simultaneously ensuring your application is accessible to screen readers and assistive technologies.

**Incorrect (fragile CSS/XPath selectors):**

```typescript
import { test, expect } from '@playwright/test';

test('bad - fragile selectors', async ({ page }) => {
  await page.goto('https://example.com');
  
  // ❌ Brittle CSS selector tied to DOM structure
  await page.click('div.container > div.row > button.btn-primary');
  
  // ❌ XPath tied to exact DOM hierarchy
  await page.click('//div[@class="form"]/div[2]/button[1]');
  
  // ❌ Generic class names that may change
  await page.fill('.input-field', 'username');
  
  // ❌ Using nth-child which breaks when order changes
  await page.click('button:nth-child(3)');
  
  // ❌ ID that might be auto-generated or change
  await page.click('#submit-btn-12345');
});
```

**Correct (role-based locators):**

```typescript
import { test, expect } from '@playwright/test';

test('good - role-based locators', async ({ page }) => {
  await page.goto('https://example.com');
  
  // ✅ Role-based: finds button by accessible name
  await page.getByRole('button', { name: 'Submit' }).click();
  
  // ✅ Works with partial/regex matching
  await page.getByRole('button', { name: /submit/i }).click();
  
  // ✅ Role + level for headings
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Welcome');
  
  // ✅ Link by accessible name
  await page.getByRole('link', { name: 'Learn more' }).click();
  
  // ✅ Textbox by label association
  await page.getByRole('textbox', { name: 'Username' }).fill('john@example.com');
  
  // ✅ Checkbox by label
  await page.getByRole('checkbox', { name: 'I agree to terms' }).check();
  
  // ✅ Combination of role and state
  await page.getByRole('button', { name: 'Delete', pressed: true }).click();
});

test('role locator hierarchy', async ({ page }) => {
  await page.goto('https://example.com/form');
  
  // ✅ Scope role locators within sections
  const nav = page.getByRole('navigation');
  await nav.getByRole('link', { name: 'Products' }).click();
  
  // ✅ Find within specific landmarks
  const main = page.getByRole('main');
  await main.getByRole('button', { name: 'Add to Cart' }).click();
  
  // ✅ Multiple items in a list
  const listItems = page.getByRole('listitem');
  await expect(listItems).toHaveCount(5);
  
  // ✅ Table cells
  const row = page.getByRole('row', { name: /John Doe/ });
  await expect(row.getByRole('cell').nth(2)).toHaveText('Active');
});
```

**When to use other locators:**

```typescript
test('fallback locator strategies', async ({ page }) => {
  await page.goto('https://example.com');
  
  // ✅ Use getByLabel for form fields
  await page.getByLabel('Email address').fill('user@example.com');
  
  // ✅ Use getByPlaceholder when no label exists
  await page.getByPlaceholder('Search...').fill('playwright');
  
  // ✅ Use getByText for unique text content
  await page.getByText('Exact text match').click();
  await page.getByText(/partial match/i).click();
  
  // ✅ Use getByTestId for dynamic content without semantic roles
  await page.getByTestId('user-profile-card').click();
  
  // ✅ Use getByAltText for images
  await expect(page.getByAltText('Company logo')).toBeVisible();
  
  // ✅ Use getByTitle for elements with title attributes
  await page.getByTitle('Close dialog').click();
});
```

**Common roles and their usage:**

```typescript
test('common ARIA roles', async ({ page }) => {
  // Buttons and links
  await page.getByRole('button', { name: 'Submit' }).click();
  await page.getByRole('link', { name: 'Home' }).click();
  
  // Form controls
  await page.getByRole('textbox', { name: 'Email' }).fill('test@example.com');
  await page.getByRole('checkbox', { name: 'Remember me' }).check();
  await page.getByRole('radio', { name: 'Option A' }).check();
  await page.getByRole('combobox', { name: 'Country' }).selectOption('US');
  await page.getByRole('slider', { name: 'Volume' }).fill('75');
  
  // Structure
  await page.getByRole('navigation').isVisible();
  await page.getByRole('main').isVisible();
  await page.getByRole('banner').isVisible(); // header
  await page.getByRole('contentinfo').isVisible(); // footer
  await page.getByRole('complementary').isVisible(); // aside
  
  // Content
  await page.getByRole('heading', { name: 'Title' }).isVisible();
  await page.getByRole('img', { name: 'Logo' }).isVisible();
  await page.getByRole('list').isVisible();
  await page.getByRole('listitem').count();
  
  // Tables
  await page.getByRole('table').isVisible();
  await page.getByRole('row', { name: /John/ }).click();
  await page.getByRole('cell', { name: 'Active' }).isVisible();
  await page.getByRole('columnheader', { name: 'Name' }).click();
  
  // Dialogs
  await page.getByRole('dialog').isVisible();
  await page.getByRole('alertdialog').isVisible();
  
  // Status
  await page.getByRole('status').toHaveText('Saved');
  await page.getByRole('alert').toHaveText('Error occurred');
  await page.getByRole('progressbar').isVisible();
});
```

Benefits of role-based locators:
- **Resilient**: Survive CSS class changes, DOM restructuring, and styling updates
- **Accessible**: Ensure your app works with screen readers and assistive technologies
- **Readable**: Tests clearly express user intent ("click the Submit button")
- **Semantic**: Based on how users and assistive technologies perceive the page
- **Future-proof**: Less likely to break during refactoring

Priority order for locators:
1. `getByRole()` - Best for semantic HTML elements
2. `getByLabel()` - Great for form fields
3. `getByPlaceholder()` - Form fields without labels
4. `getByText()` - Unique text content
5. `getByTestId()` - Last resort for dynamic/non-semantic content

Avoid: CSS selectors, XPath, `nth-child`, auto-generated IDs, or implementation-specific classes.

Reference: [Playwright Locators](https://playwright.dev/docs/locators)
