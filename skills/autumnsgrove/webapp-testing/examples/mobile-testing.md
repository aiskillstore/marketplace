# Mobile Device Emulation Examples

## Mobile Testing Setup

```python
from playwright.sync_api import Page, expect
import pytest

@pytest.fixture
def mobile_page(playwright):
    """Create a mobile emulated browser context."""
    iphone_12 = playwright.devices['iPhone 12']
    browser = playwright.chromium.launch()
    context = browser.new_context(**iphone_12)
    page = context.new_page()
    yield page
    context.close()
    browser.close()

def test_mobile_navigation(mobile_page: Page):
    """Test mobile navigation menu."""
    mobile_page.goto("https://example.com")

    # Hamburger menu should be visible on mobile
    expect(mobile_page.locator(".hamburger-menu")).to_be_visible()

    # Desktop menu should be hidden
    expect(mobile_page.locator(".desktop-nav")).to_be_hidden()

    # Open mobile menu
    mobile_page.click(".hamburger-menu")
    expect(mobile_page.locator(".mobile-menu")).to_be_visible()

def test_touch_interactions(mobile_page: Page):
    """Test touch-specific interactions."""
    mobile_page.goto("https://example.com/gallery")

    # Swipe gesture
    mobile_page.locator(".gallery").swipe_left()

    # Tap (touch event)
    mobile_page.tap(".image-thumbnail")

    # Long press
    mobile_page.locator(".context-menu-trigger").tap(timeout=1000)

def test_responsive_images(mobile_page: Page):
    """Test responsive image loading."""
    mobile_page.goto("https://example.com")

    # Check that mobile-optimized images are loaded
    hero_image = mobile_page.locator(".hero-image")
    src = hero_image.get_attribute("src")

    assert "mobile" in src or "small" in src

def test_viewport_orientation(playwright):
    """Test landscape vs portrait orientation."""
    iphone = playwright.devices['iPhone 12']

    # Portrait mode
    browser = playwright.chromium.launch()
    context = browser.new_context(**iphone)
    page = context.new_page()

    page.goto("https://example.com")
    expect(page.locator(".portrait-layout")).to_be_visible()

    # Switch to landscape
    page.set_viewport_size({"width": 844, "height": 390})
    expect(page.locator(".landscape-layout")).to_be_visible()

    context.close()
    browser.close()
```
