# Playwright Quick Reference

## Locators (Priority Order)

### 1. Role-based (Best)
```typescript
page.getByRole('button', { name: 'Submit' });
page.getByRole('textbox', { name: 'Email' });
page.getByRole('checkbox', { name: 'Agree' });
page.getByRole('link', { name: 'Home' });
page.getByRole('heading', { level: 1 });
page.getByRole('listitem');
page.getByRole('row');
page.getByRole('cell');
```

### 2. Label/Text-based
```typescript
page.getByLabel('Email address');
page.getByPlaceholder('Enter email');
page.getByText('Welcome');
page.getByTitle('Close dialog');
page.getByAltText('Company logo');
```

### 3. Test ID (Last Resort)
```typescript
page.getByTestId('submit-button');
```

### 4. Chaining
```typescript
page.getByRole('listitem')
  .filter({ hasText: 'Product 1' })
  .getByRole('button', { name: 'Add' });

page.getByRole('row', { name: 'John' })
  .getByRole('button', { name: 'Edit' });
```

---

## Common Assertions

### Visibility
```typescript
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();
await expect(locator).toBeAttached();
await expect(locator).toBeDetached();
```

### Content
```typescript
await expect(locator).toHaveText('expected');
await expect(locator).toContainText('partial');
await expect(locator).toBeEmpty();
await expect(locator).toHaveValue('input value');
```

### State
```typescript
await expect(locator).toBeEnabled();
await expect(locator).toBeDisabled();
await expect(locator).toBeChecked();
await expect(locator).toBeFocused();
await expect(locator).toBeEditable();
```

### Attributes & CSS
```typescript
await expect(locator).toHaveAttribute('href', '/home');
await expect(locator).toHaveClass('active');
await expect(locator).toHaveCSS('color', 'rgb(255, 0, 0)');
await expect(locator).toHaveId('submit-btn');
```

### Page
```typescript
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle('Dashboard');
await expect(page).toHaveScreenshot('page.png');
```

### Count
```typescript
await expect(locator).toHaveCount(5);
```

---

## Actions

### Input
```typescript
await locator.fill('text');           // Clear and type
await locator.type('text');           // Type char by char
await locator.clear();                // Clear input
await locator.press('Enter');         // Press key
await locator.pressSequentially('text'); // Type slowly
```

### Click
```typescript
await locator.click();
await locator.dblclick();
await locator.click({ button: 'right' });
await locator.click({ force: true });
await locator.click({ position: { x: 10, y: 10 } });
```

### Select/Check
```typescript
await locator.selectOption('value');
await locator.selectOption({ label: 'Option' });
await locator.check();
await locator.uncheck();
await locator.setChecked(true);
```

### Drag & Drop
```typescript
await source.dragTo(target);
```

### File Upload
```typescript
await locator.setInputFiles('file.pdf');
await locator.setInputFiles(['file1.pdf', 'file2.pdf']);
```

### Hover
```typescript
await locator.hover();
```

---

## Waiting

### Auto-wait (Built-in)
All actions auto-wait for:
- Element visible
- Element stable
- Element enabled
- Element not obscured

### Explicit Waits
```typescript
// Wait for element
await locator.waitFor();
await locator.waitFor({ state: 'visible' });
await locator.waitFor({ state: 'hidden' });

// Wait for navigation
await page.waitForURL('/dashboard');
await page.waitForLoadState('domcontentloaded');

// Wait for response
await page.waitForResponse('**/api/data');

// Wait for event
await page.waitForEvent('dialog');
```

---

## Network

### Mock Response
```typescript
await page.route('**/api/users', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify({ data: [] }),
  });
});
```

### Abort Request
```typescript
await page.route('**/tracking', route => route.abort());
```

### Modify Headers
```typescript
await page.route('**/*', route => {
  route.continue({
    headers: { ...route.request().headers(), 'X-Custom': 'value' }
  });
});
```

### Wait for API
```typescript
const responsePromise = page.waitForResponse('**/api/save');
await page.click('button');
const response = await responsePromise;
```

---

## Test Hooks

```typescript
test.beforeAll(async () => { /* once before all tests */ });
test.afterAll(async () => { /* once after all tests */ });
test.beforeEach(async ({ page }) => { /* before each test */ });
test.afterEach(async ({ page }) => { /* after each test */ });
```

---

## Test Modifiers

```typescript
test.skip('skipped test', async () => {});
test.only('only this test', async () => {});
test.fixme('known broken', async () => {});
test.slow('needs more time', async () => {});

test('conditional skip', async ({ browserName }) => {
  test.skip(browserName === 'webkit', 'Not supported');
});
```

---

## CLI Commands

```bash
# Run tests
npx playwright test
npx playwright test --project=chromium
npx playwright test --grep "login"
npx playwright test tests/auth.spec.ts

# Debug
npx playwright test --debug
npx playwright test --ui
npx playwright test --headed

# Generate code
npx playwright codegen localhost:3000

# Reports
npx playwright show-report
npx playwright show-trace trace.zip

# Update snapshots
npx playwright test --update-snapshots
```

---

## Configuration Quick Reference

```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  retries: 2,
  workers: 4,
  reporter: [['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
});
```
