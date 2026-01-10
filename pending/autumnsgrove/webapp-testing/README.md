# Web Application Testing with Playwright

Professional web application testing and automation using Playwright with support for multiple browsers, mobile emulation, screenshot capture, network interception, and comprehensive test assertions.

## Overview

Playwright is a powerful framework for web testing and automation that supports all modern browsers (Chromium, Firefox, WebKit). It provides reliable, fast, and capable automation with auto-waiting, network control, and comprehensive testing capabilities.

Use this skill for E2E testing across browsers, UI automation, form testing and validation, visual regression testing, API mocking and interception, and mobile responsive testing.

## Installation

Install Playwright and pytest integration:

```bash
pip install playwright pytest-playwright
playwright install
```

This installs Playwright and downloads browser binaries for Chromium, Firefox, and WebKit.

## What's Included

### SKILL.md
Comprehensive guide covering all Playwright testing capabilities including multi-browser testing, element interaction, assertions, screenshot/video capture, network interception, mobile device emulation, and Page Object Model pattern.

### scripts/
- `playwright_helper.py` - Utility functions for common Playwright operations
- `test_examples.py` - Complete test suite examples demonstrating best practices

### examples/
- `login-testing.md` - Authentication flows and session management
- `form-testing.md` - Form validation, file uploads, dropdowns
- `ecommerce-testing.md` - Shopping cart, checkout flows, coupons
- `api-mocking.md` - Network interception, mocking, monitoring
- `mobile-testing.md` - Device emulation, touch events, responsive design
- `page-object-model.md` - POM pattern implementation

### references/
- `setup-configuration.md` - Installation, project structure, configuration
- `best-practices.md` - Selector strategies, wait patterns, flaky test prevention
- `common-pitfalls.md` - Race conditions, selector brittleness, cleanup issues
- `ci-cd-integration.md` - GitHub Actions, Docker, deployment pipelines

## Quick Start

### Basic Test Setup

```python
import pytest
from playwright.sync_api import Page, expect

def test_homepage_loads(page: Page):
    """Test that homepage loads successfully."""
    page.goto("https://example.com")
    expect(page).to_have_title("Example Domain")
    expect(page.locator("h1")).to_contain_text("Example Domain")

def test_navigation(page: Page):
    """Test navigation between pages."""
    page.goto("https://example.com")
    page.click("text=More information")
    expect(page).to_have_url("https://www.iana.org/domains/reserved")
```

### Form Testing

```python
def test_login_form(page: Page):
    """Test login form submission."""
    page.goto("https://example.com/login")

    # Fill form fields
    page.fill("#username", "testuser@example.com")
    page.fill("#password", "SecurePassword123")
    page.check("#remember-me")

    # Submit and verify
    page.click("button[type='submit']")
    expect(page).to_have_url("https://example.com/dashboard")
    expect(page.locator(".welcome-message")).to_be_visible()
```

### API Mocking

```python
def test_with_mocked_api(page: Page):
    """Test with mocked API response."""
    # Mock API response
    page.route("**/api/user", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"name": "Test User", "premium": true}'
    ))

    page.goto("https://example.com/profile")
    expect(page.locator(".user-name")).to_contain_text("Test User")
```

### Mobile Emulation

```python
@pytest.fixture
def mobile_page(playwright):
    """Create mobile browser context."""
    iphone = playwright.devices['iPhone 12']
    browser = playwright.chromium.launch()
    context = browser.new_context(**iphone)
    page = context.new_page()
    yield page
    context.close()
    browser.close()

def test_mobile_menu(mobile_page: Page):
    """Test mobile navigation."""
    mobile_page.goto("https://example.com")
    expect(mobile_page.locator(".hamburger-menu")).to_be_visible()
    mobile_page.click(".hamburger-menu")
    expect(mobile_page.locator(".mobile-menu")).to_be_visible()
```

## Key Features

### Multi-Browser Testing
- Chromium (Chrome, Edge, Brave)
- Firefox (Mozilla Firefox)
- WebKit (Safari engine)
- Cross-browser compatibility testing
- Parallel execution across browsers

### Element Interaction
- Click, double-click, right-click
- Type text with realistic keyboard simulation
- Select dropdowns and checkboxes
- Hover and focus interactions
- Drag and drop operations
- File uploads and downloads

### Assertions & Verification
- Element visibility and state checks
- Text content verification
- Attribute validation
- URL and navigation assertions
- Custom expect matchers
- Soft assertions for multiple checks

### Screenshot & Video Capture
- Full page screenshots
- Element-specific captures
- Video recording of test sessions
- Visual comparison testing
- Trace files for debugging

### Network Interception
- Mock API responses
- Intercept and modify requests
- Monitor network traffic
- Test offline scenarios
- Performance monitoring

### Mobile Device Emulation
- 100+ device presets (iPhone, Pixel, iPad, etc.)
- Custom viewport configurations
- Touch event simulation
- Geolocation testing
- Orientation changes

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest tests/

# Run specific browser
pytest --browser chromium --browser firefox

# Run in headed mode (see browser)
pytest --headed

# Debug mode
PWDEBUG=1 pytest tests/test_login.py

# Parallel execution
pytest -n auto

# Generate test code
playwright codegen https://example.com
```

### Configuration

Create `pytest.ini`:

```ini
[pytest]
# Playwright specific
addopts = --browser chromium --headed
testpaths = tests
```

See `references/setup-configuration.md` for complete configuration options.

## Page Object Model

Organize tests using the Page Object pattern for maintainability:

```python
class LoginPage:
    """Login page object."""

    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.submit_button = page.locator("button[type='submit']")

    def login(self, username: str, password: str):
        """Perform login."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()

# Use in tests
def test_login(page: Page):
    login_page = LoginPage(page)
    login_page.login("test@example.com", "password123")
    expect(page).to_have_url("/dashboard")
```

See `examples/page-object-model.md` for complete implementation.

## Best Practices

### Use Reliable Selectors

```python
# ✅ GOOD: Test IDs and semantic selectors
page.click("[data-testid='submit-button']")
page.click("button:text('Submit')")
page.click("role=button[name='Submit']")

# ❌ BAD: Fragile structural selectors
page.click("div > div > button:nth-child(3)")
```

### Leverage Auto-Waiting

```python
# ✅ GOOD: Playwright auto-waits
page.click("button")
expect(page.locator(".result")).to_be_visible()

# ⚠️ Avoid: Manual waits
time.sleep(2)  # Only when absolutely necessary
```

### Ensure Test Isolation

```python
# ✅ GOOD: Clean state between tests
@pytest.fixture(autouse=True)
def clear_state(page: Page):
    yield
    page.context.clear_cookies()
    page.evaluate("localStorage.clear()")
```

## Quality Standards

Ensure tests meet these criteria:
- Tests are independent and can run in any order
- Selectors are reliable (test IDs, semantic selectors)
- Proper error handling and assertions
- Screenshots/videos captured on failure
- No hardcoded waits (use auto-waiting)
- Clean state management between tests

## Common Use Cases

### E2E Testing
Test complete user workflows from login to checkout.

### Form Validation
Verify form validation, error messages, and submission.

### Visual Regression
Compare screenshots to detect visual changes.

### API Integration Testing
Mock backend APIs to test frontend in isolation.

### Cross-Browser Compatibility
Ensure functionality works across all major browsers.

### Mobile Responsiveness
Test responsive designs on various device sizes.

## Troubleshooting

**Tests are flaky:**
- Use Playwright's auto-waiting instead of manual sleeps
- Ensure proper wait conditions (`wait_for_selector`, `wait_for_url`)
- Use `expect()` assertions which auto-retry

**Selectors not finding elements:**
- Verify element exists with browser DevTools
- Use Playwright Inspector: `PWDEBUG=1 pytest test.py`
- Try multiple selector strategies (text, role, test-id)

**Tests slow in CI:**
- Enable parallel execution: `pytest -n auto`
- Use headed mode only for debugging
- Consider browser context reuse for related tests

For more troubleshooting tips, see `references/common-pitfalls.md`.

## Documentation

See `SKILL.md` for comprehensive documentation, detailed workflows, and advanced techniques.

## External Resources

- Official Documentation: https://playwright.dev
- Python API: https://playwright.dev/python/docs/intro
- Best Practices: https://playwright.dev/docs/best-practices
- Community Discord: https://aka.ms/playwright/discord

## Requirements

- Python 3.8+
- playwright
- pytest-playwright
- pytest (for test execution)
