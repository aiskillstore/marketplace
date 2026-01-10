# Common Pitfalls and Solutions

## 1. Race Conditions

```python
# ❌ BAD: Not waiting for dynamic content
page.click("button")
result = page.locator(".result").inner_text()  # May fail

# ✅ GOOD: Wait for element to appear
page.click("button")
page.wait_for_selector(".result")
result = page.locator(".result").inner_text()

# ✅ BETTER: Use Playwright's auto-waiting
page.click("button")
result = page.locator(".result").text_content()  # Auto-waits
```

## 2. Selector Brittleness

```python
# ❌ BAD: Structure-dependent selectors
page.click("div > div > span > button")

# ✅ GOOD: Content-based selectors
page.click("button:text('Submit')")

# ✅ GOOD: Test IDs
page.click("[data-testid='submit-btn']")

# ✅ GOOD: Semantic selectors
page.click("role=button[name='Submit']")
```

## 3. Test Interdependencies

```python
# ❌ BAD: Tests depend on each other
def test_create_user(page):
    # Creates user "testuser"
    pass

def test_login_user(page):
    # Depends on test_create_user running first
    page.fill("#username", "testuser")  # May fail if run alone

# ✅ GOOD: Each test is independent
@pytest.fixture
def created_user(page):
    """Create user for test."""
    # Setup code
    yield user_data
    # Cleanup code

def test_login_user(page, created_user):
    """Test has its own user."""
    page.fill("#username", created_user['username'])
```

## 4. Resource Cleanup

```python
# ✅ GOOD: Always clean up resources
@pytest.fixture
def upload_file(page):
    """Upload file and clean up after test."""
    file_path = "test-upload.txt"

    # Create test file
    with open(file_path, "w") as f:
        f.write("test content")

    yield file_path

    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)

# ✅ GOOD: Clean up browser contexts
def test_with_context_cleanup(browser):
    """Properly manage browser contexts."""
    context = browser.new_context()
    page = context.new_page()

    try:
        page.goto("https://example.com")
        # Test code
    finally:
        context.close()
```

## 5. Cookie and Session Management

```python
# ✅ GOOD: Manage session state explicitly
@pytest.fixture
def authenticated_context(browser):
    """Create context with authentication."""
    context = browser.new_context()
    page = context.new_page()

    # Login and save state
    page.goto("https://example.com/login")
    page.fill("#username", "test@example.com")
    page.fill("#password", "password")
    page.click("button[type='submit']")
    page.wait_for_url("https://example.com/dashboard")

    # Save authentication state
    context.storage_state(path="auth.json")

    yield context
    context.close()

def test_with_saved_auth(browser):
    """Use saved authentication state."""
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()
    page.goto("https://example.com/dashboard")
    # Already authenticated
    context.close()
```
