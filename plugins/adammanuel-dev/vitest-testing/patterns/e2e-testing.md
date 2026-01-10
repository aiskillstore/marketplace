# End-to-End (E2E) Testing Patterns

**Comprehensive patterns for testing complete user workflows from UI to database.**

E2E tests verify that your entire application stack works together correctly by simulating real user interactions. They provide the highest confidence but are the slowest and most expensive tests to maintain.

---

## 🎯 When to Use E2E Tests

### ✅ Use E2E Tests For:
- **Critical user journeys** - Registration, login, checkout, payment
- **Happy paths** of main features
- **Cross-cutting concerns** - Authentication, authorization
- **Visual regressions** - UI consistency
- **Browser-specific behavior** - Different browsers/devices

### ❌ Don't Use E2E Tests For:
- **Every feature variation** - Use unit tests instead
- **Error handling** - Test at unit/integration level
- **Business logic** - Unit tests are faster
- **Edge cases** - Too slow for comprehensive coverage
- **Component variations** - Component tests suffice

**Rule of Thumb:** If it can be tested at a lower level, test it there. E2E tests should only cover what can't be tested elsewhere.

---

## 🛠️ Setup: Playwright with Vitest

### Installation

```bash
npm install -D @playwright/test
npx playwright install
```

### 🎭 Interactive Development with Playwright Skill

**RECOMMENDED:** Use [@skills/playwright-skill/](../../playwright-skill/) for interactive E2E test development!

The playwright-skill provides a REPL-like environment for developing E2E tests in real-time with visible browser feedback:

**Benefits:**
- ✅ **Auto-detects dev servers** - No hardcoded URLs
- ✅ **Visible browser** - Watch tests execute in real-time
- ✅ **Rapid iteration** - Test scripts in `/tmp` for quick changes
- ✅ **Immediate feedback** - See results instantly
- ✅ **Helper utilities** - Common patterns pre-built

**Workflow:**
```bash
# 1. Detect running dev servers
cd ~/.claude/skills/playwright-skill && \
  node -e "require('./lib/helpers').detectDevServers().then(s => console.log(JSON.stringify(s)))"

# Output: [{"url":"http://localhost:3000","port":3000}]

# 2. Write test script to /tmp
# /tmp/playwright-test-checkout.js

# 3. Execute with visible browser
cd ~/.claude/skills/playwright-skill && node run.js /tmp/playwright-test-checkout.js

# 4. Iterate on the script, re-run to test changes
```

**Reference:** [@skills/playwright-skill/SKILL.md](../../playwright-skill/SKILL.md)

---

## 🔄 Interactive E2E Test Development Pattern

**Use playwright-skill for REPL-style test development before converting to Vitest/Playwright tests.**

### Pattern: Develop → Refine → Convert

#### Step 1: Rapid Prototyping with playwright-skill

Quickly test your E2E scenario with immediate visual feedback:

```bash
# Create interactive test script
cat > /tmp/playwright-test-checkout.js << 'EOF'
const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:3000'; // Auto-detected

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();

  try {
    // Navigate to product page
    await page.goto(`${TARGET_URL}/products`);
    console.log('✅ Products page loaded');

    // Add item to cart
    await page.click('[data-product-id="123"] button');
    console.log('✅ Item added to cart');

    // Go to checkout
    await page.click('[data-testid="cart-icon"]');
    await page.click('button:has-text("Checkout")');
    console.log('✅ Navigated to checkout');

    // Fill form and submit
    await page.fill('[name="cardNumber"]', '4242424242424242');
    await page.fill('[name="expiry"]', '12/25');
    await page.click('button:has-text("Place Order")');

    // Verify
    await page.waitForSelector('h1:has-text("Order Confirmed")');
    console.log('✅ Order completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: '/tmp/error-screenshot.png' });
  } finally {
    await browser.close();
  }
})();
EOF

# Run with visible browser for immediate feedback
cd ~/.claude/skills/playwright-skill && node run.js /tmp/playwright-test-checkout.js
```

**Watch the browser:**
- See what works
- Identify timing issues
- Find correct selectors
- Debug failures visually

#### Step 2: Iterate Quickly

```bash
# Edit /tmp/playwright-test-checkout.js directly
# Add console.log() for debugging
# Change selectors if needed
# Add wait conditions

# Re-run instantly
cd ~/.claude/skills/playwright-skill && node run.js /tmp/playwright-test-checkout.js
```

#### Step 3: Convert to Vitest/Playwright Test

Once the script works reliably, convert to formal Playwright test:

```typescript
// e2e/checkout.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Checkout Flow', () => {
  test('completes purchase successfully', async ({ page }) => {
    // Production-ready version of your /tmp script
    await page.goto('/products')

    await page.click('[data-product-id="123"] button')
    await page.click('[data-testid="cart-icon"]')
    await page.click('button:has-text("Checkout")')

    await page.fill('[name="cardNumber"]', '4242424242424242')
    await page.fill('[name="expiry"]', '12/25')
    await page.click('button:has-text("Place Order")')

    await expect(page.locator('h1')).toContainText('Order Confirmed')
  })
})
```

### Why This Pattern Works

**Benefits:**
1. **Visual debugging** - See failures immediately
2. **Fast iteration** - No test suite overhead
3. **Selector discovery** - Find the right selectors easily
4. **Timing calibration** - Identify needed waits
5. **Error visualization** - Screenshots on failure

**When to Use:**
- ✅ Developing new E2E tests
- ✅ Debugging failing E2E tests
- ✅ Exploring unfamiliar UIs
- ✅ Prototyping user flows

**When to Skip:**
- ❌ Simple tests you know will work
- ❌ Already have working selectors
- ❌ CI/CD execution (use formal tests)

---

### Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
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
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

---

## 🎬 Basic E2E Patterns

### Pattern 1: User Registration Flow

```typescript
import { test, expect } from '@playwright/test'

test.describe('User Registration E2E', () => {
  test('allows new user to register and login', async ({ page }) => {
    // Navigate to registration
    await page.goto('/register')

    // Fill registration form
    await page.fill('[name="name"]', 'John Doe')
    await page.fill('[name="email"]', `test-${Date.now()}@example.com`)
    await page.fill('[name="password"]', 'SecurePassword123!')

    // Submit form
    await page.click('button[type="submit"]')

    // Should redirect to dashboard
    await page.waitForURL('**/dashboard')

    // Verify logged in
    await expect(page.locator('h1')).toContainText('Welcome, John Doe')
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
  })

  test('shows validation errors for invalid email', async ({ page }) => {
    await page.goto('/register')

    await page.fill('[name="email"]', 'invalid-email')
    await page.click('button[type="submit"]')

    await expect(page.locator('.error-message'))
      .toContainText('Invalid email format')
  })
})
```

### Pattern 2: E-Commerce Checkout Flow

```typescript
test.describe('E2E: Checkout Flow', () => {
  test('completes full purchase journey', async ({ page }) => {
    // 1. Browse products
    await page.goto('/products')
    await expect(page.locator('h1')).toContainText('Products')

    // 2. Add item to cart
    const product = page.locator('[data-product-id="123"]')
    await product.locator('button:has-text("Add to Cart")').click()

    // 3. View cart
    await page.click('[data-testid="cart-icon"]')
    await expect(page.locator('.cart-item')).toHaveCount(1)

    // 4. Proceed to checkout
    await page.click('button:has-text("Checkout")')
    await page.waitForURL('**/checkout')

    // 5. Fill shipping info
    await page.fill('[name="address"]', '123 Main St')
    await page.fill('[name="city"]', 'New York')
    await page.fill('[name="zip"]', '10001')

    // 6. Fill payment info
    await page.fill('[name="cardNumber"]', '4242424242424242')
    await page.fill('[name="expiry"]', '12/25')
    await page.fill('[name="cvv"]', '123')

    // 7. Place order
    await page.click('button:has-text("Place Order")')

    // 8. Verify confirmation
    await expect(page.locator('h1')).toContainText('Order Confirmed')
    await expect(page.locator('[data-testid="order-number"]')).toBeVisible()

    // 9. Verify email sent (check UI notification)
    await expect(page.locator('.notification'))
      .toContainText('Confirmation email sent')
  })

  test('handles payment failure gracefully', async ({ page }) => {
    // Setup: Use card that will be declined
    await page.goto('/checkout')

    await page.fill('[name="cardNumber"]', '4000000000000002') // Declined card

    await page.click('button:has-text("Place Order")')

    // Verify error handling
    await expect(page.locator('.error-message'))
      .toContainText('Payment declined')

    // Verify user can retry
    await expect(page.locator('button:has-text("Try Again")')).toBeVisible()
  })
})
```

---

## 🔐 Testing Authentication Flows

```typescript
test.describe('E2E: Authentication', () => {
  test('complete authentication cycle', async ({ page, context }) => {
    // 1. Register
    await page.goto('/register')
    const email = `user-${Date.now()}@example.com`

    await page.fill('[name="email"]', email)
    await page.fill('[name="password"]', 'SecurePass123!')
    await page.click('button:has-text("Register")')

    // 2. Verify email (simulate)
    // In real test, check email service or use test endpoint
    await page.goto('/verify?token=test-token')

    // 3. Login
    await page.goto('/login')
    await page.fill('[name="email"]', email)
    await page.fill('[name="password"]', 'SecurePass123!')
    await page.click('button:has-text("Login")')

    // 4. Verify logged in
    await expect(page.locator('[data-testid="user-profile"]')).toBeVisible()

    // 5. Test session persistence
    await page.reload()
    await expect(page.locator('[data-testid="user-profile"]')).toBeVisible()

    // 6. Logout
    await page.click('[data-testid="logout-button"]')
    await expect(page.locator('button:has-text("Login")')).toBeVisible()

    // 7. Verify session cleared
    await page.reload()
    await expect(page.url()).toContain('/login')
  })

  test('protects restricted pages', async ({ page }) => {
    // Try to access protected page without login
    await page.goto('/dashboard')

    // Should redirect to login
    await expect(page.url()).toContain('/login')
    await expect(page.locator('.message'))
      .toContainText('Please log in to continue')
  })
})
```

---

## 📱 Testing Across Devices

```typescript
import { devices } from '@playwright/test'

test.describe('E2E: Responsive Design', () => {
  test('works on mobile device', async ({ page, context }) => {
    // Use mobile viewport
    await context.setViewportSize(devices['iPhone 13'].viewport)

    await page.goto('/')

    // Verify mobile navigation
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible()
    await expect(page.locator('[data-testid="desktop-menu"]')).not.toBeVisible()

    // Test mobile-specific interactions
    await page.click('[data-testid="hamburger-menu"]')
    await expect(page.locator('[data-testid="mobile-nav-drawer"]')).toBeVisible()
  })

  test('works on tablet', async ({ page, context }) => {
    await context.setViewportSize(devices['iPad Pro'].viewport)

    await page.goto('/')

    // Verify tablet layout
    await expect(page.locator('[data-testid="tablet-layout"]')).toBeVisible()
  })
})
```

---

## 🎨 Page Object Pattern for E2E

Encapsulate page interactions for maintainability.

```typescript
// pages/login.page.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login')
  }

  async fillEmail(email: string) {
    await this.page.fill('[name="email"]', email)
  }

  async fillPassword(password: string) {
    await this.page.fill('[name="password"]', password)
  }

  async submit() {
    await this.page.click('button[type="submit"]')
  }

  async login(email: string, password: string) {
    await this.fillEmail(email)
    await this.fillPassword(password)
    await this.submit()
  }

  async getErrorMessage() {
    return this.page.locator('.error-message').textContent()
  }

  async isLoggedIn() {
    return this.page.locator('[data-testid="user-menu"]').isVisible()
  }
}

// Usage in tests
test('logs in successfully', async ({ page }) => {
  const loginPage = new LoginPage(page)

  await loginPage.goto()
  await loginPage.login('user@example.com', 'password123')

  await expect(page).toHaveURL('**/dashboard')
  expect(await loginPage.isLoggedIn()).toBe(true)
})
```

---

## 🎭 Test Data Management for E2E

```typescript
// helpers/test-data.ts
export class E2ETestData {
  static async createTestUser(page: Page) {
    const user = {
      email: `test-${Date.now()}@example.com`,
      password: 'TestPass123!',
      name: 'Test User'
    }

    // Create via API (faster than UI)
    await page.request.post('/api/users', {
      data: user
    })

    return user
  }

  static async createTestProduct(page: Page) {
    return await page.request.post('/api/products', {
      data: {
        name: 'Test Product',
        price: 29.99,
        stock: 100
      }
    })
  }

  static async cleanup(page: Page) {
    // Clean up test data after test
    await page.request.delete('/api/test-data/cleanup')
  }
}

// Usage
test('checkout flow with setup', async ({ page }) => {
  // Setup test data via API (fast)
  const user = await E2ETestData.createTestUser(page)
  const product = await E2ETestData.createTestProduct(page)

  // Test UI workflow
  await page.goto('/login')
  // ... test checkout ...

  // Cleanup
  await E2ETestData.cleanup(page)
})
```

---

## 📋 Best Practices

### ✅ Do

- **Test critical paths only** - 5-10% of total tests
- **Use Page Object pattern** - Encapsulate interactions
- **Setup via API** - Faster than UI
- **Take screenshots on failure** - Debug failed runs
- **Run in CI/CD** - Not on every save
- **Test cross-browser** - Chrome, Firefox, Safari
- **Use unique test data** - Avoid conflicts

### ❌ Don't

- **Test every scenario** - Too slow and expensive
- **Duplicate unit test coverage** - Test at lower level
- **Use E2E for validation logic** - Unit tests better
- **Run E2E locally constantly** - Too slow
- **Hardcode test data** - Use factories
- **Skip cleanup** - Pollutes test database
- **Test implementation details** - Test user behavior

---

## 🔗 Related Patterns

- **[Testing Pyramid](../principles/testing-pyramid.md)** - E2E at top (5-10%)
- **[Component Testing](component-testing.md)** - Alternative for UI testing
- **[Integration Testing](integration-testing.md)** - Middle layer
- **[Page Object Model](https://playwright.dev/docs/pom)** - Pattern for E2E

---

## 🎮 Interactive E2E Development Examples

### Example 1: Developing Login Test

**Using playwright-skill for rapid iteration:**

```bash
# Create interactive test
cat > /tmp/playwright-test-login.js << 'EOF'
const { chromium } = require('playwright');
const helpers = require('/Users/adammanuel/.claude/skills/playwright-skill/lib/helpers');

(async () => {
  // Auto-detect dev server
  const servers = await helpers.detectDevServers();
  const TARGET_URL = servers[0]?.url || 'http://localhost:3000';

  console.log(`Testing login at: ${TARGET_URL}`);

  const browser = await chromium.launch({ headless: false, slowMo: 200 });
  const page = await browser.newPage();

  try {
    await page.goto(`${TARGET_URL}/login`);

    // Try different selectors interactively
    console.log('Looking for email input...');
    await helpers.safeType(page, '[name="email"]', 'test@example.com');

    console.log('Looking for password input...');
    await helpers.safeType(page, '[name="password"]', 'password123');

    console.log('Looking for submit button...');
    await helpers.safeClick(page, 'button[type="submit"]');

    // Watch for redirect
    await page.waitForURL('**/dashboard', { timeout: 5000 });
    console.log('✅ Login successful!');

    await helpers.takeScreenshot(page, 'login-success');

  } catch (error) {
    console.error('❌ Error:', error.message);
    await page.screenshot({ path: '/tmp/login-error.png' });
    console.log('Error screenshot saved');
  } finally {
    await browser.close();
  }
})();
EOF

# Run and watch
cd ~/.claude/skills/playwright-skill && node run.js /tmp/playwright-test-login.js
```

**Iterate until it works, then convert:**

```typescript
// e2e/login.spec.ts
import { test, expect } from '@playwright/test'

test('user can log in successfully', async ({ page }) => {
  await page.goto('/login')

  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('button[type="submit"]')

  await expect(page).toHaveURL(/.*dashboard/)
})
```

### Example 2: Debugging Flaky Selectors

**Use playwright-skill to find stable selectors:**

```bash
cat > /tmp/playwright-debug-selectors.js << 'EOF'
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto('http://localhost:3000/products');

  // Try different selector strategies
  console.log('Testing selectors...');

  try {
    // Option 1: Test data attribute
    const btn1 = await page.locator('[data-testid="add-to-cart"]').count();
    console.log(`data-testid found: ${btn1} elements`);
  } catch (e) {
    console.log('data-testid not found');
  }

  try {
    // Option 2: Role-based
    const btn2 = await page.getByRole('button', { name: /add to cart/i }).count();
    console.log(`Role-based found: ${btn2} elements`);
  } catch (e) {
    console.log('Role-based not found');
  }

  try {
    // Option 3: Text content
    const btn3 = await page.locator('button:has-text("Add to Cart")').count();
    console.log(`Text-based found: ${btn3} elements`);
  } catch (e) {
    console.log('Text-based not found');
  }

  // Pause for manual inspection
  await page.pause();

  await browser.close();
})();
EOF

cd ~/.claude/skills/playwright-skill && node run.js /tmp/playwright-debug-selectors.js
```

### Example 3: Testing Multi-Step Form

**Develop complex interactions visually:**

```bash
cat > /tmp/playwright-test-registration.js << 'EOF'
const { chromium } = require('playwright');
const helpers = require('/Users/adammanuel/.claude/skills/playwright-skill/lib/helpers');

(async () => {
  const servers = await helpers.detectDevServers();
  const TARGET_URL = servers[0]?.url || 'http://localhost:3000';

  const browser = await chromium.launch({ headless: false, slowMo: 150 });
  const page = await browser.newPage();

  try {
    // Step 1: Personal Info
    await page.goto(`${TARGET_URL}/register/step1`);
    await page.fill('[name="firstName"]', 'John');
    await page.fill('[name="lastName"]', 'Doe');
    await page.click('button:has-text("Next")');
    console.log('✅ Step 1 complete');

    // Step 2: Account Info
    await page.waitForURL('**/step2');
    await page.fill('[name="email"]', `test-${Date.now()}@example.com`);
    await page.fill('[name="password"]', 'SecurePass123!');
    await page.click('button:has-text("Next")');
    console.log('✅ Step 2 complete');

    // Step 3: Confirmation
    await page.waitForURL('**/step3');
    await page.check('[name="terms"]');
    await page.click('button:has-text("Complete Registration")');
    console.log('✅ Step 3 complete');

    // Verify success
    await page.waitForSelector('.success-message');
    console.log('✅ Registration successful!');

    await helpers.takeScreenshot(page, 'registration-complete');

  } catch (error) {
    console.error('❌ Failed at:', error.message);
    await page.screenshot({ path: '/tmp/registration-error.png' });
  } finally {
    await browser.close();
  }
})();
EOF

cd ~/.claude/skills/playwright-skill && node run.js /tmp/playwright-test-registration.js
```

**Refine the timing, then convert to formal test.**

---

**Next Steps:**
- Install [Playwright](https://playwright.dev/)
- Use [@skills/playwright-skill/](../../playwright-skill/) for interactive development
- Review [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- Explore [Visual Testing](https://playwright.dev/docs/test-snapshots)
