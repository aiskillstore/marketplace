"""
Playwright Test Examples

This module contains comprehensive, real-world test examples demonstrating
various Playwright testing patterns and scenarios.
"""

import pytest
import json
import time
from pathlib import Path
from playwright.sync_api import Page, BrowserContext, expect, Route
from playwright_helper import PlaywrightHelper, TestDataGenerator, PageObjectBase


# ============================================================================
# Page Object Models
# ============================================================================

class LoginPage(PageObjectBase):
    """Login page object."""

    # Selectors
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    SUBMIT_BUTTON = "button[type='submit']"
    ERROR_MESSAGE = ".error-message"
    REMEMBER_ME = "#remember-me"
    FORGOT_PASSWORD = "a:text('Forgot Password')"

    def login(self, username: str, password: str, remember_me: bool = False) -> None:
        """Perform login."""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        if remember_me:
            self.page.check(self.REMEMBER_ME)
        self.click(self.SUBMIT_BUTTON)

    def get_error_message(self) -> str:
        """Get login error message."""
        return self.get_text(self.ERROR_MESSAGE)

    def click_forgot_password(self) -> None:
        """Click forgot password link."""
        self.click(self.FORGOT_PASSWORD)


class ProductPage(PageObjectBase):
    """Product page object."""

    # Selectors
    PRODUCT_TITLE = ".product-title"
    PRODUCT_PRICE = ".product-price"
    ADD_TO_CART = ".add-to-cart-btn"
    QUANTITY_INPUT = "#quantity"
    SIZE_SELECT = "#size-select"
    COLOR_OPTIONS = ".color-option"
    CART_BADGE = ".cart-badge"

    def add_to_cart(
        self,
        quantity: int = 1,
        size: str = None,
        color: str = None
    ) -> None:
        """Add product to cart."""
        if quantity > 1:
            self.page.fill(self.QUANTITY_INPUT, str(quantity))

        if size:
            self.page.select_option(self.SIZE_SELECT, size)

        if color:
            self.page.click(f"{self.COLOR_OPTIONS}[data-color='{color}']")

        self.click(self.ADD_TO_CART)

    def get_price(self) -> float:
        """Get product price as float."""
        price_text = self.get_text(self.PRODUCT_PRICE)
        return float(price_text.replace("$", "").replace(",", ""))

    def get_cart_count(self) -> int:
        """Get cart item count."""
        badge_text = self.get_text(self.CART_BADGE)
        return int(badge_text) if badge_text else 0


# ============================================================================
# Login and Authentication Tests
# ============================================================================

class TestLogin:
    """Test suite for login functionality."""

    BASE_URL = "https://example.com"

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test."""
        self.helper = PlaywrightHelper(page)
        self.login_page = LoginPage(page)
        yield

    def test_successful_login(self, page: Page):
        """Test successful login with valid credentials."""
        self.login_page.navigate_to(f"{self.BASE_URL}/login")

        # Perform login
        self.login_page.login(
            username="testuser@example.com",
            password="SecurePassword123"
        )

        # Verify redirect to dashboard
        expect(page).to_have_url(f"{self.BASE_URL}/dashboard")

        # Verify welcome message
        expect(page.locator(".welcome-message")).to_contain_text("Welcome")

        # Take screenshot of successful login
        self.helper.take_screenshot("successful_login")

    def test_invalid_credentials(self, page: Page):
        """Test login fails with invalid credentials."""
        self.login_page.navigate_to(f"{self.BASE_URL}/login")

        # Attempt login with wrong credentials
        self.login_page.login(
            username="wrong@example.com",
            password="WrongPassword"
        )

        # Verify error message
        error_message = self.login_page.get_error_message()
        assert "Invalid credentials" in error_message or "incorrect" in error_message.lower()

        # Verify still on login page
        expect(page).to_have_url(f"{self.BASE_URL}/login")

    def test_empty_fields_validation(self, page: Page):
        """Test validation for empty form fields."""
        self.login_page.navigate_to(f"{self.BASE_URL}/login")

        # Try to submit empty form
        self.login_page.click(LoginPage.SUBMIT_BUTTON)

        # Check for HTML5 validation
        username_input = page.locator(LoginPage.USERNAME_INPUT)
        expect(username_input).to_have_attribute("required")

    def test_remember_me_functionality(self, page: Page):
        """Test remember me checkbox sets long-lived cookie."""
        self.login_page.navigate_to(f"{self.BASE_URL}/login")

        # Login with remember me
        self.login_page.login(
            username="testuser@example.com",
            password="SecurePassword123",
            remember_me=True
        )

        # Wait for navigation
        page.wait_for_url(f"{self.BASE_URL}/dashboard")

        # Check for long-lived cookie
        cookies = page.context.cookies()
        remember_cookie = next(
            (c for c in cookies if 'remember' in c['name'].lower()),
            None
        )

        if remember_cookie:
            # Cookie should have expiry date (not session cookie)
            assert remember_cookie.get('expires', 0) > 0

    def test_forgot_password_link(self, page: Page):
        """Test forgot password link navigation."""
        self.login_page.navigate_to(f"{self.BASE_URL}/login")

        # Click forgot password
        self.login_page.click_forgot_password()

        # Verify navigation to password reset page
        expect(page).to_have_url(f"{self.BASE_URL}/forgot-password")


# ============================================================================
# Form Testing
# ============================================================================

class TestForms:
    """Test suite for form functionality."""

    def test_contact_form_submission(self, page: Page):
        """Test complete contact form submission."""
        helper = PlaywrightHelper(page)
        page.goto("https://example.com/contact")

        # Generate test data
        test_data = {
            "#name": TestDataGenerator.random_name(),
            "#email": TestDataGenerator.random_email(),
            "#phone": TestDataGenerator.random_phone(),
            "#message": TestDataGenerator.random_text(200)
        }

        # Fill form using helper
        helper.fill_form(test_data)

        # Select from dropdown
        page.select_option("#subject", "General Inquiry")

        # Submit form
        page.click("button[type='submit']")

        # Verify success message
        expect(page.locator(".success-message")).to_be_visible(timeout=10000)
        helper.take_screenshot("contact_form_success")

    def test_multi_step_form(self, page: Page):
        """Test multi-step form wizard."""
        helper = PlaywrightHelper(page)
        page.goto("https://example.com/signup")

        # Step 1: Personal Information
        helper.fill_form({
            "#first-name": "John",
            "#last-name": "Doe",
            "#email": TestDataGenerator.random_email()
        })
        page.click("button:text('Next')")

        # Wait for step 2
        helper.wait_for_element(".step-2", state="visible")

        # Step 2: Address
        helper.fill_form({
            "#address": "123 Main St",
            "#city": "New York",
            "#zip": "10001"
        })
        page.select_option("#country", "US")
        page.click("button:text('Next')")

        # Step 3: Preferences
        helper.wait_for_element(".step-3", state="visible")
        page.check("#newsletter")
        page.check("#terms")

        # Submit
        page.click("button:text('Submit')")

        # Verify completion
        expect(page.locator(".completion-message")).to_be_visible(timeout=10000)

    def test_file_upload(self, page: Page):
        """Test file upload functionality."""
        helper = PlaywrightHelper(page)
        page.goto("https://example.com/upload")

        # Create temporary test file
        test_file = Path("test-upload.txt")
        test_file.write_text("This is a test file for upload testing.")

        try:
            # Upload file
            page.set_input_files("#file-input", str(test_file))

            # Verify file name appears
            expect(page.locator(".file-name")).to_contain_text("test-upload.txt")

            # Submit upload
            page.click("button:text('Upload')")

            # Verify success
            expect(page.locator(".upload-success")).to_be_visible()
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()

    def test_dynamic_form_fields(self, page: Page):
        """Test dynamically added/removed form fields."""
        page.goto("https://example.com/dynamic-form")

        # Initial field count
        initial_count = page.locator(".phone-field").count()

        # Add new field
        page.click("button:text('Add Phone')")

        # Verify field added
        expect(page.locator(".phone-field")).to_have_count(initial_count + 1)

        # Fill new field
        new_field = page.locator(".phone-field").last
        new_field.locator("input").fill("+1-555-9999")

        # Remove a field
        page.locator(".remove-phone").first.click()

        # Verify field removed
        expect(page.locator(".phone-field")).to_have_count(initial_count)


# ============================================================================
# E-commerce Testing
# ============================================================================

class TestEcommerce:
    """Test suite for e-commerce functionality."""

    def test_product_search(self, page: Page):
        """Test product search functionality."""
        helper = PlaywrightHelper(page)
        page.goto("https://example.com/products")

        # Perform search
        page.fill("#search-input", "laptop")
        page.click("button:text('Search')")

        # Wait for results
        helper.wait_for_element(".product-card")

        # Verify results contain search term
        product_cards = page.locator(".product-card")
        count = product_cards.count()

        assert count > 0, "No products found"

        # Check first few products
        for i in range(min(3, count)):
            product = product_cards.nth(i)
            product_text = product.text_content().lower()
            assert "laptop" in product_text

    def test_add_to_cart_flow(self, page: Page):
        """Test complete add to cart flow."""
        product_page = ProductPage(page)
        product_page.navigate_to("https://example.com/product/123")

        # Wait for product to load
        product_page.wait_for_element(ProductPage.PRODUCT_TITLE)

        # Get initial cart count
        initial_cart_count = product_page.get_cart_count()

        # Add product with options
        product_page.add_to_cart(
            quantity=2,
            size="Large",
            color="Blue"
        )

        # Verify cart updated
        page.wait_for_timeout(1000)  # Wait for cart update
        new_cart_count = product_page.get_cart_count()
        assert new_cart_count == initial_cart_count + 2

    def test_cart_operations(self, page: Page):
        """Test cart update and remove operations."""
        helper = PlaywrightHelper(page)
        page.goto("https://example.com/cart")

        # Wait for cart to load
        helper.wait_for_element(".cart-item")

        # Get initial item count
        initial_items = page.locator(".cart-item").count()

        if initial_items > 0:
            # Update quantity
            qty_input = page.locator(".quantity-input").first
            qty_input.fill("3")
            qty_input.press("Enter")

            # Wait for update
            page.wait_for_timeout(1000)

            # Verify quantity updated
            expect(qty_input).to_have_value("3")

            # Remove item
            page.locator(".remove-item").first.click()

            # Verify item removed
            page.wait_for_timeout(1000)
            expect(page.locator(".cart-item")).to_have_count(initial_items - 1)

    def test_checkout_process(self, page: Page):
        """Test complete checkout process."""
        helper = PlaywrightHelper(page)

        # Add product first
        page.goto("https://example.com/product/123")
        page.click(".add-to-cart-btn")

        # Go to cart
        page.click(".cart-icon")
        expect(page).to_have_url("https://example.com/cart")

        # Proceed to checkout
        page.click("button:text('Checkout')")

        # Fill shipping info
        shipping_data = {
            "#first-name": "John",
            "#last-name": "Doe",
            "#email": TestDataGenerator.random_email(),
            "#address": "123 Main St",
            "#city": "New York",
            "#zip": "10001"
        }
        helper.fill_form(shipping_data)
        page.select_option("#country", "US")

        # Continue to payment
        page.click("button:text('Continue')")

        # Fill payment info (test mode)
        payment_data = {
            "#card-number": "4242424242424242",
            "#expiry": "12/25",
            "#cvv": "123"
        }
        helper.fill_form(payment_data)

        # Place order
        page.click("button:text('Place Order')")

        # Verify order confirmation
        expect(page).to_have_url("https://example.com/order/confirmation")
        expect(page.locator(".order-number")).to_be_visible()

        # Take screenshot of confirmation
        helper.take_screenshot("order_confirmation")

    def test_coupon_application(self, page: Page):
        """Test applying discount coupon."""
        page.goto("https://example.com/cart")

        # Get original total
        original_total = page.locator(".total-amount").text_content()

        # Apply coupon
        page.fill("#coupon-code", "SAVE10")
        page.click("button:text('Apply')")

        # Verify discount applied
        expect(page.locator(".discount-applied")).to_be_visible()
        expect(page.locator(".discount-amount")).to_contain_text("-")

        # Verify total decreased
        new_total = page.locator(".total-amount").text_content()

        original_value = float(original_total.replace("$", "").replace(",", ""))
        new_value = float(new_total.replace("$", "").replace(",", ""))

        assert new_value < original_value


# ============================================================================
# API Mocking and Network Tests
# ============================================================================

class TestNetworkInterception:
    """Test suite for network interception and mocking."""

    def test_mock_user_profile_api(self, page: Page):
        """Test with mocked user profile API."""
        # Mock data
        mock_user = {
            "id": 123,
            "name": "Test User",
            "email": "test@example.com",
            "avatar": "https://example.com/avatar.jpg",
            "premium": True
        }

        # Intercept API call
        def handle_route(route: Route):
            if "api/user/profile" in route.request.url:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps(mock_user)
                )
            else:
                route.continue_()

        page.route("**/api/**", handle_route)

        # Navigate to profile page
        page.goto("https://example.com/profile")

        # Verify mocked data appears
        expect(page.locator(".user-name")).to_contain_text("Test User")
        expect(page.locator(".premium-badge")).to_be_visible()

    def test_api_error_handling(self, page: Page):
        """Test how app handles API errors."""
        # Mock error response
        def handle_route(route: Route):
            if "api/products" in route.request.url:
                route.fulfill(
                    status=500,
                    content_type="application/json",
                    body=json.dumps({"error": "Internal server error"})
                )
            else:
                route.continue_()

        page.route("**/api/**", handle_route)

        # Navigate to products page
        page.goto("https://example.com/products")

        # Verify error message shown
        expect(page.locator(".error-message")).to_be_visible()
        expect(page.locator(".retry-button")).to_be_visible()

    def test_offline_mode(self, page: Page):
        """Test app behavior in offline mode."""
        # Abort all network requests
        page.route("**/*", lambda route: route.abort())

        page.goto("https://example.com")

        # Verify offline message
        expect(page.locator(".offline-indicator")).to_be_visible()

    def test_monitor_api_calls(self, page: Page):
        """Test monitoring and validating API calls."""
        requests = []

        # Capture all requests
        page.on("request", lambda request: requests.append({
            "url": request.url,
            "method": request.method,
            "headers": request.headers
        }))

        # Navigate and interact
        page.goto("https://example.com/products")
        page.click("button:text('Load More')")

        # Wait for requests
        page.wait_for_timeout(2000)

        # Verify API calls were made
        api_requests = [r for r in requests if "/api/" in r["url"]]
        assert len(api_requests) > 0

        # Verify specific request
        products_request = next(
            (r for r in api_requests if "products" in r["url"]),
            None
        )
        assert products_request is not None
        assert products_request["method"] == "GET"


# ============================================================================
# Mobile Device Emulation Tests
# ============================================================================

class TestMobileDevices:
    """Test suite for mobile device testing."""

    @pytest.fixture
    def mobile_page(self, playwright):
        """Create mobile emulated browser context."""
        iphone_12 = playwright.devices['iPhone 12']
        browser = playwright.chromium.launch()
        context = browser.new_context(**iphone_12)
        page = context.new_page()
        yield page
        context.close()
        browser.close()

    def test_mobile_navigation_menu(self, mobile_page: Page):
        """Test mobile navigation menu."""
        mobile_page.goto("https://example.com")

        # Hamburger menu should be visible
        expect(mobile_page.locator(".hamburger-menu")).to_be_visible()

        # Desktop nav should be hidden
        expect(mobile_page.locator(".desktop-nav")).to_be_hidden()

        # Open mobile menu
        mobile_page.click(".hamburger-menu")

        # Verify menu opens
        expect(mobile_page.locator(".mobile-menu")).to_be_visible()

        # Take screenshot
        helper = PlaywrightHelper(mobile_page)
        helper.take_screenshot("mobile_menu_open")

    def test_touch_gestures(self, mobile_page: Page):
        """Test touch interactions."""
        mobile_page.goto("https://example.com/gallery")

        # Tap on image
        mobile_page.tap(".gallery-image:first-child")

        # Verify lightbox opens
        expect(mobile_page.locator(".lightbox")).to_be_visible()

        # Swipe to next image
        mobile_page.locator(".lightbox").swipe_left()

    def test_responsive_layout(self, playwright):
        """Test layout changes across viewport sizes."""
        browser = playwright.chromium.launch()

        # Desktop viewport
        desktop_context = browser.new_context(viewport={"width": 1920, "height": 1080})
        desktop_page = desktop_context.new_page()
        desktop_page.goto("https://example.com")

        # Desktop layout should be visible
        expect(desktop_page.locator(".desktop-layout")).to_be_visible()

        # Mobile viewport
        mobile_context = browser.new_context(viewport={"width": 375, "height": 667})
        mobile_page = mobile_context.new_page()
        mobile_page.goto("https://example.com")

        # Mobile layout should be visible
        expect(mobile_page.locator(".mobile-layout")).to_be_visible()

        # Cleanup
        desktop_context.close()
        mobile_context.close()
        browser.close()


# ============================================================================
# Visual Regression Tests
# ============================================================================

class TestVisualRegression:
    """Test suite for visual regression testing."""

    def test_homepage_screenshot_comparison(self, page: Page):
        """Compare homepage screenshot with baseline."""
        helper = PlaywrightHelper(page)
        page.goto("https://example.com")

        # Wait for page to be fully loaded
        page.wait_for_load_state("networkidle")

        # Take screenshot
        helper.take_screenshot("homepage_full", full_page=True)

        # Note: Actual comparison would require additional library
        # This is a placeholder for the pattern
        # assert helper.compare_screenshots("homepage_full", threshold=0.05)

    def test_button_hover_state(self, page: Page):
        """Capture button hover state."""
        helper = PlaywrightHelper(page)
        page.goto("https://example.com")

        # Hover over button
        page.hover(".primary-button")

        # Wait for transition
        page.wait_for_timeout(500)

        # Take screenshot of hovered state
        helper.take_element_screenshot(".primary-button", "button_hover_state")

    def test_modal_screenshot(self, page: Page):
        """Capture modal dialog screenshot."""
        helper = PlaywrightHelper(page)
        page.goto("https://example.com")

        # Open modal
        page.click("button:text('Open Modal')")

        # Wait for modal animation
        expect(page.locator(".modal")).to_be_visible()
        page.wait_for_timeout(500)

        # Screenshot modal
        helper.take_element_screenshot(".modal", "modal_dialog")


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Test suite for performance testing."""

    def test_page_load_time(self, page: Page):
        """Test page load performance."""
        helper = PlaywrightHelper(page)

        start_time = time.time()
        page.goto("https://example.com")
        page.wait_for_load_state("networkidle")
        load_time = time.time() - start_time

        # Assert page loads within acceptable time
        assert load_time < 5.0, f"Page load took {load_time}s, expected < 5s"

        # Get performance metrics
        metrics = helper.get_performance_metrics()

        # Verify metrics
        assert metrics["domContentLoaded"] < 3000  # 3 seconds
        assert metrics["firstContentfulPaint"] < 2000  # 2 seconds

        print(f"Page Load Metrics: {json.dumps(metrics, indent=2)}")

    def test_action_response_time(self, page: Page):
        """Test UI action response time."""
        helper = PlaywrightHelper(page)
        page.goto("https://example.com/search")

        # Measure search response time
        action_time = helper.measure_action_time(
            lambda: page.fill("#search", "test query")
        )

        assert action_time < 1.0, f"Action took {action_time}s, expected < 1s"


# ============================================================================
# Accessibility Tests
# ============================================================================

class TestAccessibility:
    """Test suite for accessibility testing."""

    def test_keyboard_navigation(self, page: Page):
        """Test keyboard navigation through form."""
        page.goto("https://example.com/form")

        # Tab through form fields
        page.keyboard.press("Tab")
        first_focused = page.evaluate("document.activeElement.id")

        page.keyboard.press("Tab")
        second_focused = page.evaluate("document.activeElement.id")

        # Verify different elements are focused
        assert first_focused != second_focused

    def test_aria_labels(self, page: Page):
        """Test ARIA labels presence."""
        page.goto("https://example.com")

        # Check navigation has role
        navigation = page.locator("nav[role='navigation']")
        expect(navigation).to_be_visible()

        # Check buttons have labels
        submit_button = page.locator("button[aria-label='Submit form']")
        expect(submit_button).to_have_attribute("aria-label")

    def test_alt_text_on_images(self, page: Page):
        """Test all images have alt text."""
        page.goto("https://example.com")

        # Get all images
        images = page.locator("img")
        count = images.count()

        # Check each image has alt attribute
        for i in range(count):
            img = images.nth(i)
            alt = img.get_attribute("alt")
            assert alt is not None, f"Image {i} missing alt text"


# ============================================================================
# Parallel Testing Example
# ============================================================================

@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_cross_browser_compatibility(browser_name, playwright):
    """Test across multiple browsers."""
    browser = getattr(playwright, browser_name).launch()
    context = browser.new_context()
    page = context.new_page()

    try:
        page.goto("https://example.com")
        expect(page.locator("h1")).to_be_visible()
        print(f"{browser_name}: Homepage loaded successfully")
    finally:
        context.close()
        browser.close()


# ============================================================================
# Data-Driven Testing
# ============================================================================

@pytest.mark.parametrize("username,password,expected_error", [
    ("", "", "required"),
    ("user@example.com", "short", "password"),
    ("invalid-email", "Password123", "email"),
    ("test@test.com", "", "required")
])
def test_login_validation_messages(page: Page, username, password, expected_error):
    """Data-driven test for login validation."""
    login_page = LoginPage(page)
    login_page.navigate_to("https://example.com/login")

    login_page.login(username, password)

    # Check for expected error message
    error = page.locator(".error-message, .validation-error").text_content()
    assert expected_error.lower() in error.lower()


# ============================================================================
# Fixtures for Authenticated Testing
# ============================================================================

@pytest.fixture
def authenticated_page(page: Page):
    """Fixture providing authenticated user session."""
    # Login
    login_page = LoginPage(page)
    login_page.navigate_to("https://example.com/login")
    login_page.login("testuser@example.com", "SecurePassword123")

    # Wait for authentication
    page.wait_for_url("https://example.com/dashboard")

    yield page

    # Logout cleanup
    if page.locator(".logout-button").is_visible():
        page.click(".logout-button")


def test_user_profile_with_auth(authenticated_page: Page):
    """Test that requires authentication."""
    authenticated_page.goto("https://example.com/profile")

    # Verify user is authenticated
    expect(authenticated_page.locator(".user-avatar")).to_be_visible()
    expect(authenticated_page.locator(".user-email")).to_contain_text("@")


# ============================================================================
# Custom Test Reporter
# ============================================================================

class TestReporter:
    """Custom test reporter for detailed logging."""

    @staticmethod
    def log_test_start(test_name: str):
        """Log test start."""
        print(f"\n{'='*60}")
        print(f"Starting test: {test_name}")
        print(f"{'='*60}")

    @staticmethod
    def log_test_end(test_name: str, passed: bool):
        """Log test end."""
        status = "PASSED" if passed else "FAILED"
        print(f"\n{test_name}: {status}")
        print(f"{'='*60}\n")


# Example usage with reporter
def test_with_custom_reporter(page: Page):
    """Example test with custom reporter."""
    reporter = TestReporter()
    reporter.log_test_start("test_with_custom_reporter")

    try:
        page.goto("https://example.com")
        expect(page.locator("h1")).to_be_visible()
        reporter.log_test_end("test_with_custom_reporter", True)
    except Exception as e:
        reporter.log_test_end("test_with_custom_reporter", False)
        raise e
