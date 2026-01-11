# Playwright Best Practices

## 1. Selector Strategies

```python
# ✅ GOOD: Use test IDs (most reliable)
page.click("[data-testid='submit-button']")

# ✅ GOOD: Use semantic selectors
page.click("button:text('Submit')")
page.click("role=button[name='Submit']")

# ⚠️ OK: Use CSS selectors with meaningful classes
page.click(".submit-button")

# ❌ BAD: Fragile selectors tied to structure
page.click("div > div > button:nth-child(3)")

# ❌ BAD: Position-based selectors
page.click(".button:nth-of-type(5)")
```

## 2. Wait Strategies

```python
# ✅ GOOD: Playwright auto-waits (preferred)
page.click("button")  # Automatically waits for element

# ✅ GOOD: Wait for specific state
page.wait_for_selector(".results", state="visible")

# ✅ GOOD: Wait for network idle
page.wait_for_load_state("networkidle")

# ✅ GOOD: Wait for specific URL
page.wait_for_url("https://example.com/dashboard")

# ⚠️ USE SPARINGLY: Fixed timeouts
import time
time.sleep(2)  # Only when absolutely necessary

# ✅ GOOD: Custom wait conditions
page.wait_for_function("() => document.querySelectorAll('.item').length > 10")
```

## 3. Test Isolation

```python
import pytest
from playwright.sync_api import Page

@pytest.fixture
def isolated_page(context):
    """Create isolated page with clean state."""
    page = context.new_page()
    yield page
    page.close()

def test_with_clean_state(isolated_page: Page):
    """Each test gets fresh page instance."""
    isolated_page.goto("https://example.com")
    # Test runs in isolation

# Clear cookies/storage between tests
@pytest.fixture(autouse=True)
def clear_state(page: Page):
    """Clear cookies and storage before each test."""
    yield
    page.context.clear_cookies()
    page.evaluate("localStorage.clear()")
    page.evaluate("sessionStorage.clear()")
```

## 4. Flaky Test Prevention

```python
# ✅ GOOD: Use Playwright's auto-waiting
page.click("button")  # Waits for actionable state

# ✅ GOOD: Use strict mode to catch multiple elements
page.locator("button").click()  # Fails if multiple buttons

# ✅ GOOD: Wait for specific conditions
expect(page.locator(".result")).to_have_count(5)

# ✅ GOOD: Use soft assertions for multiple checks
expect.soft(page.locator(".title")).to_be_visible()
expect.soft(page.locator(".description")).to_be_visible()
expect.soft(page.locator(".price")).to_contain_text("$")

# ❌ BAD: Race conditions
page.click("button")
result = page.locator(".result").inner_text()  # May not be ready

# ✅ GOOD: Ensure element exists first
page.click("button")
page.wait_for_selector(".result")
result = page.locator(".result").inner_text()
```

## 5. Performance Testing Considerations

```python
from playwright.sync_api import Page
import time

def test_page_load_performance(page: Page):
    """Test page load performance metrics."""
    start_time = time.time()
    page.goto("https://example.com")
    load_time = time.time() - start_time

    # Assert page loads within acceptable time
    assert load_time < 3.0, f"Page load took {load_time}s, expected < 3s"

    # Get performance metrics
    metrics = page.evaluate("""() => {
        const timing = performance.timing;
        return {
            domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
            loadComplete: timing.loadEventEnd - timing.navigationStart,
            firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
        };
    }""")

    assert metrics['domContentLoaded'] < 2000  # 2 seconds
    assert metrics['firstPaint'] < 1000  # 1 second
```

## 6. Accessibility Testing

```python
from playwright.sync_api import Page, expect

def test_keyboard_navigation(page: Page):
    """Test keyboard accessibility."""
    page.goto("https://example.com")

    # Tab through interactive elements
    page.keyboard.press("Tab")
    focused = page.evaluate("document.activeElement.tagName")
    assert focused in ["BUTTON", "A", "INPUT"]

    # Press Enter to activate
    page.keyboard.press("Enter")

def test_aria_labels(page: Page):
    """Test ARIA labels are present."""
    page.goto("https://example.com")

    # Check for aria-label
    button = page.locator("button[aria-label='Submit form']")
    expect(button).to_be_visible()

    # Check for role attributes
    navigation = page.locator("nav[role='navigation']")
    expect(navigation).to_be_visible()

def test_screen_reader_content(page: Page):
    """Test screen reader accessible content."""
    page.goto("https://example.com")

    # Check for alt text on images
    images = page.locator("img")
    count = images.count()
    for i in range(count):
        alt = images.nth(i).get_attribute("alt")
        assert alt is not None, f"Image {i} missing alt text"
```

## 7. Parallel Test Execution

```python
# pytest configuration for parallel tests
# pytest.ini
"""
[pytest]
addopts = -n auto  # Use all CPU cores
"""

# Run tests in parallel
# pytest -n 4  # Use 4 workers

# Mark tests that can't run in parallel
import pytest

@pytest.mark.serial
def test_database_migration(page):
    """This test modifies shared state."""
    pass

# Worker-specific fixtures
@pytest.fixture(scope="session")
def worker_id(worker_id):
    """Get unique worker ID for parallel tests."""
    return worker_id

def test_with_worker_isolation(page, worker_id):
    """Use worker ID for unique test data."""
    username = f"testuser_{worker_id}"
    page.goto("https://example.com/signup")
    page.fill("#username", username)
```

## 8. Debugging Failed Tests

```python
# Enable headed mode for debugging
# pytest --headed

# Slow down execution
# pytest --slowmo=1000  # 1 second delay

# Enable debug mode with Playwright Inspector
# PWDEBUG=1 pytest tests/test_login.py

# Trace on failure
def test_with_trace(page: Page, context):
    """Enable tracing for debugging."""
    context.tracing.start(screenshots=True, snapshots=True)

    try:
        page.goto("https://example.com")
        # Test code here
    finally:
        context.tracing.stop(path="trace.zip")

# Video recording on failure
# Set in pytest.ini or playwright.config.ts
# video: "retain-on-failure"

# Screenshot on failure (automatic with pytest-playwright)
def test_with_auto_screenshot(page: Page):
    """Screenshots automatically saved on failure."""
    page.goto("https://example.com")
    assert False  # Screenshot will be saved
```

## Essential Selectors

```python
# Text content
page.click("text=Submit")
page.click("button:text('Submit')")
page.click("button:has-text('Submit')")

# CSS selectors
page.click("#submit-button")
page.click(".submit-button")
page.click("button[type='submit']")

# XPath
page.click("xpath=//button[@type='submit']")

# Role-based (accessibility)
page.click("role=button[name='Submit']")

# Data attributes
page.click("[data-testid='submit-btn']")

# Chaining
page.locator(".form").locator("button:text('Submit')").click()
```
