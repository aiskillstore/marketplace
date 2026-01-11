---
name: Playwright Browser Automation
description: Complete browser automation with Playwright. Auto-detects dev servers, writes clean test scripts to /tmp. Test pages, fill forms, take screenshots, check responsive design, validate UX, test login flows, check links, automate any browser task. Use when user wants to test websites, automate browser interactions, validate web functionality, or perform any browser-based testing.
version: 1.0.0
author: DataFlight
tags: [testing, automation, browser, e2e, playwright, web-testing]
---

# Playwright Browser Automation

General-purpose browser automation skill. I write custom Playwright code for any automation task and execute it via the universal executor.

## Quick Commands Available

For common tasks, these slash commands are faster:
- `/screenshot` - Take a quick screenshot of a webpage
- `/check-links` - Find broken links on a page
- `/test-page` - Basic page health check
- `/test-responsive` - Test across multiple viewports

For custom automation beyond these common tasks, I write specialized Playwright code.

## Critical Workflow

**IMPORTANT - Path Resolution:**
Use `${CLAUDE_PLUGIN_ROOT}` for all paths. This resolves to the plugin installation directory.

### Step 1: Auto-Detect Dev Servers (ALWAYS FIRST for localhost)

```bash
cd ${CLAUDE_PLUGIN_ROOT} && node -e "require('./lib/helpers').detectDevServers().then(servers => console.log(JSON.stringify(servers, null, 2)))"
```

**Decision tree:**
- **1 server found**: Use it automatically, inform user
- **Multiple servers found**: Ask user which one to test
- **No servers found**: Ask for URL or offer to help start dev server

### Step 2: Write Scripts to /tmp

NEVER write test files to plugin directory. Always use `/tmp/playwright-test-*.js`

**Script template:**
```javascript
// /tmp/playwright-test-{descriptive-name}.js
const { chromium } = require('playwright');
const helpers = require('./lib/helpers');

// Parameterized URL (auto-detected or user-provided)
const TARGET_URL = 'http://localhost:3847';

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();

  try {
    await page.goto(TARGET_URL, { waitUntil: 'networkidle' });
    console.log('Page loaded:', await page.title());

    // Test code here...

    await page.screenshot({ path: '/tmp/screenshot.png', fullPage: true });
    console.log('Screenshot saved to /tmp/screenshot.png');
  } catch (error) {
    console.error('Test failed:', error.message);
    await page.screenshot({ path: '/tmp/error-screenshot.png' });
  } finally {
    await browser.close();
  }
})();
```

### Step 3: Execute from Plugin Directory

```bash
cd ${CLAUDE_PLUGIN_ROOT} && node run.js /tmp/playwright-test-{name}.js
```

### Step 4: Default to Visible Browser

ALWAYS use `headless: false` unless user explicitly requests headless mode. This lets users see what's happening.

## Setup (First Time)

```bash
cd ${CLAUDE_PLUGIN_ROOT} && npm run setup
```

Installs Playwright and Chromium browser. Only needed once.

## Common Patterns

### Test a Page (Basic)

```javascript
const { chromium } = require('playwright');
const TARGET_URL = 'http://localhost:3847';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto(TARGET_URL);
  console.log('Title:', await page.title());
  console.log('URL:', page.url());

  await page.screenshot({ path: '/tmp/page.png', fullPage: true });
  await browser.close();
})();
```

### Test Responsive Design

```javascript
const { chromium } = require('playwright');
const TARGET_URL = 'http://localhost:3847';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  const viewports = [
    { name: 'Desktop', width: 1920, height: 1080 },
    { name: 'Tablet', width: 768, height: 1024 },
    { name: 'Mobile', width: 375, height: 667 }
  ];

  for (const viewport of viewports) {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto(TARGET_URL);
    await page.screenshot({ path: `/tmp/${viewport.name.toLowerCase()}.png`, fullPage: true });
    console.log(`${viewport.name} screenshot saved`);
  }

  await browser.close();
})();
```

### Test Login Flow

```javascript
const { chromium } = require('playwright');
const TARGET_URL = 'http://localhost:3847';

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();

  await page.goto(`${TARGET_URL}/login`);

  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  await page.waitForURL('**/dashboard');
  console.log('Login successful, redirected to dashboard');

  await browser.close();
})();
```

### Fill and Submit Form

```javascript
const { chromium } = require('playwright');
const TARGET_URL = 'http://localhost:3847';

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 50 });
  const page = await browser.newPage();

  await page.goto(`${TARGET_URL}/contact`);

  await page.fill('input[name="name"]', 'John Doe');
  await page.fill('input[name="email"]', 'john@example.com');
  await page.fill('textarea[name="message"]', 'Test message');
  await page.click('button[type="submit"]');

  await page.waitForSelector('.success-message');
  console.log('Form submitted successfully');

  await browser.close();
})();
```

### Check for Broken Links

```javascript
const { chromium } = require('playwright');
const TARGET_URL = 'http://localhost:3847';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto(TARGET_URL);

  const links = await page.locator('a[href^="http"]').all();
  const results = { working: 0, broken: [] };

  for (const link of links) {
    const href = await link.getAttribute('href');
    try {
      const response = await page.request.head(href);
      if (response.ok()) {
        results.working++;
      } else {
        results.broken.push({ url: href, status: response.status() });
      }
    } catch (e) {
      results.broken.push({ url: href, error: e.message });
    }
  }

  console.log(`Working links: ${results.working}`);
  console.log(`Broken links:`, results.broken);

  await browser.close();
})();
```

### Run Accessibility Audit

```javascript
const { chromium } = require('playwright');
const helpers = require('./lib/helpers');
const TARGET_URL = 'http://localhost:3847';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto(TARGET_URL);

  const results = await helpers.checkAccessibility(page);
  console.log('Accessibility audit complete');
  console.log(`Critical issues: ${results.summary.critical}`);
  console.log(`Serious issues: ${results.summary.serious}`);

  await browser.close();
})();
```

### Measure Performance

```javascript
const { chromium } = require('playwright');
const helpers = require('./lib/helpers');
const TARGET_URL = 'http://localhost:3847';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  const metrics = await helpers.measurePageLoad(page, TARGET_URL);
  console.log('Load time:', metrics.loadTime, 'ms');
  console.log('TTFB:', metrics.metrics.ttfb, 'ms');
  console.log('DOM Content Loaded:', metrics.metrics.domContentLoaded, 'ms');

  const lcp = await helpers.measureLCP(page);
  console.log('LCP:', lcp, 'ms');

  await browser.close();
})();
```

### Mock API Response

```javascript
const { chromium } = require('playwright');
const helpers = require('./lib/helpers');
const TARGET_URL = 'http://localhost:3847';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  // Mock the API before navigating
  await helpers.mockAPIResponse(page, '**/api/users', [
    { id: 1, name: 'Mock User 1' },
    { id: 2, name: 'Mock User 2' }
  ]);

  await page.goto(TARGET_URL);
  // Page will receive mocked data

  await browser.close();
})();
```

### Test Mobile Device

```javascript
const { chromium, devices } = require('playwright');
const TARGET_URL = 'http://localhost:3847';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    ...devices['iPhone 12']
  });
  const page = await context.newPage();

  await page.goto(TARGET_URL);
  await page.screenshot({ path: '/tmp/iphone12.png' });

  await browser.close();
})();
```

## Available Helpers

The `lib/helpers.js` provides 42 utility functions:

**Browser & Context:**
- `launchBrowser(browserType?, options?)` - Launch browser with defaults
- `createContext(browser, options?)` - Create context with viewport/locale
- `createPage(context, options?)` - Create page with timeout
- `saveStorageState(context, path)` - Save session for reuse
- `loadStorageState(browser, path)` - Restore saved session
- `detectDevServers(customPorts?)` - Scan for running dev servers

**Navigation & Waiting:**
- `waitForPageReady(page, options?)` - Smart page ready detection
- `navigateWithRetry(page, url, options?)` - Navigate with automatic retry
- `waitForSPA(page, options?)` - Wait for SPA route changes
- `waitForElement(page, selector, options?)` - Wait for element state

**Safe Interactions:**
- `safeClick(page, selector, options?)` - Click with retry logic
- `safeType(page, selector, text, options?)` - Type with clear option
- `safeSelect(page, selector, value, options?)` - Safe dropdown selection
- `safeCheck(page, selector, checked?, options?)` - Safe checkbox/radio
- `scrollPage(page, direction, distance?)` - Scroll in any direction
- `scrollToElement(page, selector, options?)` - Scroll element into view
- `authenticate(page, credentials, selectors?)` - Handle login flow
- `handleCookieBanner(page, timeout?)` - Dismiss cookie consent

**Form Helpers:**
- `getFormFields(page, formSelector?)` - Extract form field metadata
- `getRequiredFields(page, formSelector?)` - Get required fields
- `getFieldErrors(page, formSelector?)` - Get validation errors
- `validateFieldState(page, selector)` - Check field validity
- `fillFormFromData(page, formSelector, data, options?)` - Auto-fill form
- `submitAndValidate(page, formSelector, options?)` - Submit and check errors

**Accessibility:**
- `checkAccessibility(page, options?)` - Run axe-core audit
- `getARIAInfo(page, selector)` - Extract ARIA attributes
- `checkFocusOrder(page, options?)` - Verify tab order
- `getFocusableElements(page)` - List focusable elements

**Performance:**
- `measurePageLoad(page, url, options?)` - Comprehensive load metrics
- `measureLCP(page)` - Largest Contentful Paint
- `measureFCP(page)` - First Contentful Paint
- `measureCLS(page)` - Cumulative Layout Shift

**Network:**
- `mockAPIResponse(page, urlPattern, response, options?)` - Mock API
- `blockResources(page, resourceTypes)` - Block images/fonts/etc
- `captureRequests(page, urlPattern?)` - Capture network requests
- `captureResponses(page, urlPattern?)` - Capture responses
- `waitForAPI(page, urlPattern, options?)` - Wait for API call

**Visual:**
- `takeScreenshot(page, name, options?)` - Timestamped screenshot
- `compareScreenshots(baseline, current, options?)` - Visual diff
- `takeElementScreenshot(page, selector, name, options?)` - Element screenshot

**Mobile:**
- `emulateDevice(browser, deviceName)` - Emulate iPhone/Pixel/etc
- `setGeolocation(context, coords)` - Set GPS coordinates
- `simulateTouchEvent(page, type, coords)` - Trigger touch events
- `swipe(page, direction, distance?, options?)` - Swipe gesture

**Multi-page:**
- `handlePopup(page, triggerAction, options?)` - Handle popup windows
- `handleNewTab(page, triggerAction, options?)` - Handle new tabs
- `closeAllPopups(context)` - Close extra pages
- `handleDialog(page, action, text?)` - Handle alert/confirm/prompt

**Data Extraction:**
- `extractTexts(page, selector)` - Get text from elements
- `extractTableData(page, tableSelector)` - Parse table to JSON
- `extractMetaTags(page)` - Get meta tag info
- `extractOpenGraph(page)` - Get OG metadata
- `extractJsonLD(page)` - Get structured data
- `extractLinks(page, options?)` - Get all links

**Console Monitoring:**
- `captureConsoleLogs(page, options?)` - Capture console output
- `capturePageErrors(page)` - Capture JS errors
- `getConsoleErrors(consoleCapture)` - Get collected errors
- `assertNoConsoleErrors(consoleCapture)` - Fail if errors exist

**Files:**
- `uploadFile(page, selector, filePath, options?)` - Upload file
- `uploadMultipleFiles(page, selector, filePaths)` - Upload multiple
- `downloadFile(page, triggerAction, options?)` - Download and save
- `waitForDownload(page, triggerAction)` - Wait for download

**Utilities:**
- `retryWithBackoff(fn, maxRetries?, initialDelay?)` - Retry with backoff
- `delay(ms)` - Promise-based delay

## Inline Execution

For quick one-off tasks, execute code inline:

```bash
cd ${CLAUDE_PLUGIN_ROOT} && node run.js "
const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();
await page.goto('http://localhost:3847');
console.log('Title:', await page.title());
await page.screenshot({ path: '/tmp/quick.png' });
await browser.close();
"
```

**When to use:**
- **Inline**: Quick tasks (screenshot, check element, get title)
- **Files**: Complex tests, responsive design, anything to re-run

## Tips

- **CRITICAL: Detect servers FIRST** - Always run `detectDevServers()` before localhost testing
- **Use /tmp for scripts** - Write to `/tmp/playwright-test-*.js`, never plugin directory
- **Parameterize URLs** - Put URL in `TARGET_URL` constant at top
- **Visible browser default** - Always `headless: false` unless explicitly requested
- **Slow down for debugging** - Use `slowMo: 100` to see actions
- **Smart waits** - Use `waitForURL`, `waitForSelector` instead of timeouts
- **Error handling** - Always use try-catch for robust automation

## Troubleshooting

**Playwright not installed:**
```bash
cd ${CLAUDE_PLUGIN_ROOT} && npm run setup
```

**Module not found:**
Run from plugin directory via `run.js` wrapper

**Browser doesn't open:**
Check `headless: false` and ensure display available

**Element not found:**
Add wait: `await page.waitForSelector('.element', { timeout: 10000 })`

## Advanced Usage

For comprehensive Playwright API documentation, see [API_REFERENCE.md](../../API_REFERENCE.md):

- Selectors & Locators best practices
- Network interception & API mocking
- Authentication & session management
- Visual regression testing
- Mobile device emulation
- Performance testing
- CI/CD integration
