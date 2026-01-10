# API Mocking and Network Interception Examples

## API Mocking

```python
from playwright.sync_api import Page, Route
import json

def test_mock_api_response(page: Page):
    """Mock API responses for testing."""

    # Define mock data
    mock_user_data = {
        "id": 123,
        "name": "Test User",
        "email": "test@example.com",
        "premium": True
    }

    # Intercept API call and return mock data
    def handle_route(route: Route):
        if "api/user/profile" in route.request.url:
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(mock_user_data)
            )
        else:
            route.continue_()

    page.route("**/api/**", handle_route)

    # Navigate and verify mocked data appears
    page.goto("https://example.com/profile")
    expect(page.locator(".user-name")).to_contain_text("Test User")
    expect(page.locator(".premium-badge")).to_be_visible()

def test_network_failure_handling(page: Page):
    """Test how app handles network failures."""

    # Fail all API requests
    page.route("**/api/**", lambda route: route.abort())

    page.goto("https://example.com/dashboard")

    # Verify error message is shown
    expect(page.locator(".error-message")).to_be_visible()
    expect(page.locator(".retry-button")).to_be_visible()

def test_slow_network_conditions(page: Page):
    """Test app behavior under slow network."""

    def handle_slow_route(route: Route):
        # Delay response by 3 seconds
        import time
        time.sleep(3)
        route.continue_()

    page.route("**/api/**", handle_slow_route)

    page.goto("https://example.com/products")

    # Verify loading state appears
    expect(page.locator(".loading-spinner")).to_be_visible()

    # Wait for content to load
    page.wait_for_selector(".product-card", timeout=5000)

def test_monitor_network_requests(page: Page):
    """Monitor and validate network requests."""
    requests = []

    # Capture all requests
    page.on("request", lambda request: requests.append(request))

    page.goto("https://example.com")
    page.click("button:text('Load More')")

    # Verify expected requests were made
    api_requests = [r for r in requests if "api" in r.url]
    assert len(api_requests) > 0

    # Check specific request
    load_more_request = next((r for r in api_requests if "products" in r.url), None)
    assert load_more_request is not None
    assert load_more_request.method == "GET"
```
