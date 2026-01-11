# Playwright Installation & Configuration

## Installation

### Python Installation

```bash
# Install Playwright
pip install playwright pytest-playwright

# Install browsers
playwright install

# Install specific browser only
playwright install chromium
```

### JavaScript/TypeScript Installation

```bash
# Using npm
npm init playwright@latest

# Using yarn
yarn create playwright

# Install browsers
npx playwright install
```

## Project Structure

```
project/
├── tests/
│   ├── __init__.py
│   ├── test_login.py
│   ├── test_checkout.py
│   └── test_navigation.py
├── pages/
│   ├── __init__.py
│   ├── base_page.py
│   ├── login_page.py
│   └── product_page.py
├── fixtures/
│   ├── __init__.py
│   └── test_data.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── playwright.config.ts  # For TypeScript
├── pytest.ini            # For Python
└── requirements.txt
```

## Configuration

### Python Configuration (pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    smoke: Quick smoke tests
    regression: Full regression suite
    slow: Tests that take longer
addopts =
    --headed
    --browser chromium
    --browser firefox
    --screenshot on
    --video retain-on-failure
```

### TypeScript Configuration (playwright.config.ts)

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
    baseURL: 'http://localhost:3000',
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
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```
