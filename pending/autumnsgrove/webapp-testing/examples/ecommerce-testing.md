# E-commerce Testing Examples

## Shopping Cart and Checkout

```python
from playwright.sync_api import Page, expect

class TestCheckoutFlow:
    """Complete e-commerce checkout testing."""

    def test_add_to_cart(self, page: Page):
        """Test adding products to cart."""
        page.goto("https://example.com/products")

        # Add first product
        page.click(".product-card:nth-child(1) .add-to-cart")

        # Verify cart badge updates
        cart_badge = page.locator(".cart-badge")
        expect(cart_badge).to_contain_text("1")

        # Add second product
        page.click(".product-card:nth-child(2) .add-to-cart")
        expect(cart_badge).to_contain_text("2")

    def test_cart_quantity_update(self, page: Page):
        """Test updating item quantities in cart."""
        page.goto("https://example.com/cart")

        # Increase quantity
        page.click(".quantity-increase")
        expect(page.locator(".item-quantity")).to_have_value("2")

        # Verify total updates
        total = page.locator(".cart-total")
        expect(total).to_contain_text("$")

    def test_complete_checkout(self, page: Page):
        """Test full checkout process."""
        # Add product to cart
        page.goto("https://example.com/products/123")
        page.click(".add-to-cart")

        # Go to cart
        page.click(".cart-icon")
        expect(page).to_have_url("https://example.com/cart")

        # Proceed to checkout
        page.click("button:text('Proceed to Checkout')")

        # Fill shipping information
        page.fill("#first-name", "John")
        page.fill("#last-name", "Doe")
        page.fill("#address", "123 Main St")
        page.fill("#city", "New York")
        page.fill("#zip", "10001")
        page.select_option("#country", "US")

        # Continue to payment
        page.click("button:text('Continue to Payment')")

        # Fill payment details (test mode)
        page.fill("#card-number", "4242424242424242")
        page.fill("#expiry", "12/25")
        page.fill("#cvv", "123")

        # Place order
        page.click("button:text('Place Order')")

        # Verify order confirmation
        expect(page).to_have_url("https://example.com/order/confirmation")
        expect(page.locator(".order-success")).to_be_visible()
        expect(page.locator(".order-number")).to_contain_text("#")

    def test_coupon_code_application(self, page: Page):
        """Test applying discount coupons."""
        page.goto("https://example.com/cart")

        # Get original total
        original_total = page.locator(".total-amount").inner_text()

        # Apply coupon
        page.fill("#coupon-code", "SAVE10")
        page.click("button:text('Apply')")

        # Verify discount applied
        expect(page.locator(".discount-applied")).to_be_visible()
        expect(page.locator(".discount-amount")).to_contain_text("-")

        # Verify new total is less
        new_total = page.locator(".total-amount").inner_text()
        assert float(new_total.replace("$", "")) < float(original_total.replace("$", ""))
```
