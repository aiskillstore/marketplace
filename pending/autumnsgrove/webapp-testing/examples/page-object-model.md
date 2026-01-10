# Page Object Model Pattern Examples

## Base Page Implementation

```python
# pages/base_page.py
from playwright.sync_api import Page, expect

class BasePage:
    """Base page class with common functionality."""

    def __init__(self, page: Page):
        self.page = page

    def navigate_to(self, url: str):
        """Navigate to URL."""
        self.page.goto(url)

    def click_element(self, selector: str):
        """Click element with auto-wait."""
        self.page.click(selector)

    def fill_input(self, selector: str, text: str):
        """Fill input field."""
        self.page.fill(selector, text)

    def get_text(self, selector: str) -> str:
        """Get element text content."""
        return self.page.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        """Check if element is visible."""
        return self.page.locator(selector).is_visible()
```

## Login Page Object

```python
# pages/login_page.py
class LoginPage(BasePage):
    """Login page object."""

    # Selectors
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    SUBMIT_BUTTON = "button[type='submit']"
    ERROR_MESSAGE = ".error-message"
    REMEMBER_ME_CHECKBOX = "#remember-me"

    def login(self, username: str, password: str, remember_me: bool = False):
        """Perform login action."""
        self.fill_input(self.USERNAME_INPUT, username)
        self.fill_input(self.PASSWORD_INPUT, password)

        if remember_me:
            self.page.check(self.REMEMBER_ME_CHECKBOX)

        self.click_element(self.SUBMIT_BUTTON)

    def get_error_message(self) -> str:
        """Get login error message."""
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_visible(self) -> bool:
        """Check if error message is visible."""
        return self.is_visible(self.ERROR_MESSAGE)
```

## Product Page Object

```python
# pages/product_page.py
class ProductPage(BasePage):
    """Product page object."""

    ADD_TO_CART_BUTTON = ".add-to-cart"
    PRODUCT_TITLE = ".product-title"
    PRODUCT_PRICE = ".product-price"
    QUANTITY_INPUT = "#quantity"
    SIZE_SELECT = "#size"

    def add_to_cart(self, quantity: int = 1, size: str = None):
        """Add product to cart."""
        if quantity > 1:
            self.fill_input(self.QUANTITY_INPUT, str(quantity))

        if size:
            self.page.select_option(self.SIZE_SELECT, size)

        self.click_element(self.ADD_TO_CART_BUTTON)

    def get_product_title(self) -> str:
        """Get product title."""
        return self.get_text(self.PRODUCT_TITLE)

    def get_price(self) -> str:
        """Get product price."""
        return self.get_text(self.PRODUCT_PRICE)
```

## Using Page Objects in Tests

```python
# Test using Page Objects
def test_login_with_page_object(page: Page):
    """Test login using page object pattern."""
    login_page = LoginPage(page)
    login_page.navigate_to("https://example.com/login")
    login_page.login("testuser@example.com", "SecurePassword123")

    # Verify successful login
    expect(page).to_have_url("https://example.com/dashboard")

def test_add_product_to_cart(page: Page):
    """Test adding product using page object."""
    product_page = ProductPage(page)
    product_page.navigate_to("https://example.com/product/123")

    # Verify product details
    assert "Product Name" in product_page.get_product_title()

    # Add to cart
    product_page.add_to_cart(quantity=2, size="Large")

    # Verify cart updated
    expect(page.locator(".cart-badge")).to_contain_text("2")
```
