# Login Flow Testing Examples

## Basic Login Test

```python
import pytest
from playwright.sync_api import Page, expect

class TestLogin:
    """Test suite for login functionality."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to login page before each test."""
        page.goto("https://example.com/login")
        yield
        # Cleanup if needed

    def test_successful_login(self, page: Page):
        """Test successful login with valid credentials."""
        # Fill login form
        page.fill("#username", "testuser@example.com")
        page.fill("#password", "SecurePassword123")

        # Submit form
        page.click("button[type='submit']")

        # Verify successful login
        expect(page).to_have_url("https://example.com/dashboard")
        expect(page.locator(".welcome-message")).to_contain_text("Welcome, Test User")

    def test_invalid_credentials(self, page: Page):
        """Test login fails with invalid credentials."""
        page.fill("#username", "wrong@example.com")
        page.fill("#password", "WrongPassword")
        page.click("button[type='submit']")

        # Verify error message appears
        error = page.locator(".error-message")
        expect(error).to_be_visible()
        expect(error).to_contain_text("Invalid credentials")

        # Verify still on login page
        expect(page).to_have_url("https://example.com/login")

    def test_empty_fields_validation(self, page: Page):
        """Test validation for empty form fields."""
        page.click("button[type='submit']")

        # Check for HTML5 validation or custom error messages
        username_input = page.locator("#username")
        expect(username_input).to_have_attribute("required")

    def test_remember_me_functionality(self, page: Page):
        """Test remember me checkbox persistence."""
        page.fill("#username", "testuser@example.com")
        page.fill("#password", "SecurePassword123")
        page.check("#remember-me")
        page.click("button[type='submit']")

        # Wait for navigation
        page.wait_for_url("https://example.com/dashboard")

        # Check cookie was set
        cookies = page.context.cookies()
        remember_cookie = next((c for c in cookies if c['name'] == 'remember_token'), None)
        assert remember_cookie is not None
        assert remember_cookie['expires'] > 0  # Long-lived cookie
```

## Authentication & Session Testing

```python
from playwright.sync_api import Page, expect
import pytest

@pytest.fixture
def authenticated_page(page: Page):
    """Fixture for authenticated user session."""
    # Login
    page.goto("https://example.com/login")
    page.fill("#username", "testuser@example.com")
    page.fill("#password", "SecurePassword123")
    page.click("button[type='submit']")

    # Wait for login to complete
    page.wait_for_url("https://example.com/dashboard")

    yield page

def test_session_persistence(authenticated_page: Page):
    """Test session persists across page navigation."""
    # Navigate to different pages
    authenticated_page.goto("https://example.com/profile")
    expect(authenticated_page.locator(".user-avatar")).to_be_visible()

    authenticated_page.goto("https://example.com/settings")
    expect(authenticated_page.locator(".user-avatar")).to_be_visible()

def test_logout_functionality(authenticated_page: Page):
    """Test logout clears session."""
    authenticated_page.click(".logout-button")

    # Should redirect to login
    expect(authenticated_page).to_have_url("https://example.com/login")

    # Try to access protected page
    authenticated_page.goto("https://example.com/dashboard")

    # Should redirect back to login
    expect(authenticated_page).to_have_url("https://example.com/login")

def test_session_timeout(page: Page):
    """Test session timeout handling."""
    # Set short-lived session cookie
    page.context.add_cookies([{
        "name": "session",
        "value": "test-session-token",
        "domain": "example.com",
        "path": "/",
        "expires": int(time.time()) + 5  # 5 seconds
    }])

    page.goto("https://example.com/dashboard")

    # Wait for session to expire
    time.sleep(6)

    # Try to perform action
    page.click(".refresh-button")

    # Should show session expired message or redirect
    expect(page.locator(".session-expired-message")).to_be_visible()
```
