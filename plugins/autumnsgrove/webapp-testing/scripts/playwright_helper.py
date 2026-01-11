"""
Playwright Helper Utilities

This module provides common utilities and helper functions for Playwright testing,
including custom assertions, setup/teardown helpers, and screenshot utilities.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from playwright.sync_api import Page, BrowserContext, expect, ElementHandle


class PlaywrightHelper:
    """Collection of helper methods for Playwright tests."""

    def __init__(self, page: Page):
        """Initialize helper with page instance."""
        self.page = page
        self.screenshots_dir = Path("test-results/screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    # Screenshot Utilities

    def take_screenshot(self, name: str, full_page: bool = True) -> str:
        """
        Take a screenshot with timestamp.

        Args:
            name: Base name for the screenshot
            full_page: Whether to capture full page or viewport only

        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        self.page.screenshot(path=str(filepath), full_page=full_page)
        print(f"Screenshot saved: {filepath}")

        return str(filepath)

    def take_element_screenshot(self, selector: str, name: str) -> str:
        """
        Take screenshot of specific element.

        Args:
            selector: Element selector
            name: Base name for screenshot

        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        element = self.page.locator(selector)
        element.screenshot(path=str(filepath))

        return str(filepath)

    def compare_screenshots(self, name: str, threshold: float = 0.1) -> bool:
        """
        Compare current screenshot with baseline (placeholder implementation).

        Args:
            name: Screenshot name
            threshold: Difference threshold (0-1)

        Returns:
            True if screenshots match within threshold
        """
        # This is a placeholder - actual implementation would require
        # image comparison library like Pillow or pixelmatch
        baseline_path = Path(f"test-results/baseline/{name}.png")
        current_path = self.take_screenshot(name)

        if not baseline_path.exists():
            print(f"No baseline found, saving current as baseline: {baseline_path}")
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            os.rename(current_path, baseline_path)
            return True

        # Placeholder return - implement actual comparison
        print(f"Comparing {current_path} with {baseline_path}")
        return True

    # Wait Utilities

    def wait_for_element(
        self,
        selector: str,
        state: str = "visible",
        timeout: int = 30000
    ) -> None:
        """
        Wait for element to reach specified state.

        Args:
            selector: Element selector
            state: Target state (visible, hidden, attached, detached)
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_selector(selector, state=state, timeout=timeout)

    def wait_for_text(
        self,
        selector: str,
        text: str,
        timeout: int = 30000
    ) -> None:
        """
        Wait for element to contain specific text.

        Args:
            selector: Element selector
            text: Expected text content
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_function(
            f"() => document.querySelector('{selector}')?.textContent?.includes('{text}')",
            timeout=timeout
        )

    def wait_for_url_change(self, expected_url: str, timeout: int = 30000) -> None:
        """
        Wait for URL to change to expected value.

        Args:
            expected_url: Expected URL
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_url(expected_url, timeout=timeout)

    def wait_for_network_idle(self, timeout: int = 30000) -> None:
        """
        Wait for network to be idle.

        Args:
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    def wait_for_condition(
        self,
        condition: Callable[[], bool],
        timeout: int = 30000,
        interval: int = 100
    ) -> bool:
        """
        Wait for custom condition to be true.

        Args:
            condition: Callable that returns boolean
            timeout: Timeout in milliseconds
            interval: Check interval in milliseconds

        Returns:
            True if condition met, False if timeout
        """
        start_time = time.time() * 1000
        while (time.time() * 1000 - start_time) < timeout:
            if condition():
                return True
            time.sleep(interval / 1000)
        return False

    # Form Utilities

    def fill_form(self, form_data: Dict[str, Any]) -> None:
        """
        Fill multiple form fields.

        Args:
            form_data: Dictionary of selector: value pairs
        """
        for selector, value in form_data.items():
            if isinstance(value, bool):
                if value:
                    self.page.check(selector)
                else:
                    self.page.uncheck(selector)
            elif isinstance(value, list):
                # Handle multi-select
                self.page.select_option(selector, value)
            else:
                self.page.fill(selector, str(value))

    def get_form_data(self, form_selector: str) -> Dict[str, str]:
        """
        Extract all form field values.

        Args:
            form_selector: Form element selector

        Returns:
            Dictionary of field names and values
        """
        return self.page.evaluate(f"""() => {{
            const form = document.querySelector('{form_selector}');
            const formData = new FormData(form);
            const data = {{}};
            for (let [key, value] of formData.entries()) {{
                data[key] = value;
            }}
            return data;
        }}""")

    def clear_form(self, form_selector: str) -> None:
        """
        Clear all inputs in a form.

        Args:
            form_selector: Form element selector
        """
        inputs = self.page.locator(f"{form_selector} input")
        count = inputs.count()
        for i in range(count):
            input_elem = inputs.nth(i)
            input_type = input_elem.get_attribute("type")

            if input_type in ["checkbox", "radio"]:
                input_elem.uncheck()
            else:
                input_elem.fill("")

    # Custom Assertions

    def assert_element_count(
        self,
        selector: str,
        expected_count: int,
        message: Optional[str] = None
    ) -> None:
        """
        Assert element count matches expected.

        Args:
            selector: Element selector
            expected_count: Expected number of elements
            message: Optional custom error message
        """
        locator = self.page.locator(selector)
        expect(locator).to_have_count(
            expected_count,
            message=message or f"Expected {expected_count} elements matching '{selector}'"
        )

    def assert_text_matches(
        self,
        selector: str,
        pattern: str,
        message: Optional[str] = None
    ) -> None:
        """
        Assert element text matches regex pattern.

        Args:
            selector: Element selector
            pattern: Regex pattern
            message: Optional custom error message
        """
        import re
        text = self.page.locator(selector).text_content()
        assert re.search(pattern, text), (
            message or f"Text '{text}' does not match pattern '{pattern}'"
        )

    def assert_attribute_value(
        self,
        selector: str,
        attribute: str,
        expected_value: str
    ) -> None:
        """
        Assert element attribute has expected value.

        Args:
            selector: Element selector
            attribute: Attribute name
            expected_value: Expected attribute value
        """
        locator = self.page.locator(selector)
        expect(locator).to_have_attribute(attribute, expected_value)

    def assert_class_present(self, selector: str, class_name: str) -> None:
        """
        Assert element has specific CSS class.

        Args:
            selector: Element selector
            class_name: CSS class name to check
        """
        locator = self.page.locator(selector)
        expect(locator).to_have_class(class_name)

    def assert_url_contains(self, substring: str) -> None:
        """
        Assert current URL contains substring.

        Args:
            substring: Expected URL substring
        """
        current_url = self.page.url
        assert substring in current_url, (
            f"URL '{current_url}' does not contain '{substring}'"
        )

    # Element Utilities

    def get_element_count(self, selector: str) -> int:
        """
        Get count of elements matching selector.

        Args:
            selector: Element selector

        Returns:
            Number of matching elements
        """
        return self.page.locator(selector).count()

    def is_element_visible(self, selector: str) -> bool:
        """
        Check if element is visible.

        Args:
            selector: Element selector

        Returns:
            True if visible, False otherwise
        """
        try:
            return self.page.locator(selector).is_visible()
        except:
            return False

    def is_element_enabled(self, selector: str) -> bool:
        """
        Check if element is enabled.

        Args:
            selector: Element selector

        Returns:
            True if enabled, False otherwise
        """
        try:
            return self.page.locator(selector).is_enabled()
        except:
            return False

    def get_text(self, selector: str) -> str:
        """
        Get element text content.

        Args:
            selector: Element selector

        Returns:
            Text content
        """
        return self.page.locator(selector).text_content() or ""

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get element attribute value.

        Args:
            selector: Element selector
            attribute: Attribute name

        Returns:
            Attribute value or None
        """
        return self.page.locator(selector).get_attribute(attribute)

    def scroll_to_element(self, selector: str) -> None:
        """
        Scroll element into view.

        Args:
            selector: Element selector
        """
        self.page.locator(selector).scroll_into_view_if_needed()

    # Cookie and Storage Utilities

    def get_cookie(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific cookie by name.

        Args:
            name: Cookie name

        Returns:
            Cookie data or None
        """
        cookies = self.page.context.cookies()
        return next((c for c in cookies if c['name'] == name), None)

    def set_cookie(
        self,
        name: str,
        value: str,
        domain: Optional[str] = None,
        path: str = "/"
    ) -> None:
        """
        Set cookie.

        Args:
            name: Cookie name
            value: Cookie value
            domain: Cookie domain (defaults to current domain)
            path: Cookie path
        """
        if domain is None:
            from urllib.parse import urlparse
            domain = urlparse(self.page.url).netloc

        self.page.context.add_cookies([{
            "name": name,
            "value": value,
            "domain": domain,
            "path": path
        }])

    def clear_cookies(self) -> None:
        """Clear all cookies."""
        self.page.context.clear_cookies()

    def get_local_storage(self, key: str) -> Optional[str]:
        """
        Get localStorage item.

        Args:
            key: Storage key

        Returns:
            Storage value or None
        """
        return self.page.evaluate(f"localStorage.getItem('{key}')")

    def set_local_storage(self, key: str, value: str) -> None:
        """
        Set localStorage item.

        Args:
            key: Storage key
            value: Storage value
        """
        self.page.evaluate(f"localStorage.setItem('{key}', '{value}')")

    def clear_local_storage(self) -> None:
        """Clear localStorage."""
        self.page.evaluate("localStorage.clear()")

    # Network Utilities

    def intercept_request(
        self,
        url_pattern: str,
        handler: Callable
    ) -> None:
        """
        Intercept network requests matching pattern.

        Args:
            url_pattern: URL pattern to match
            handler: Route handler function
        """
        self.page.route(url_pattern, handler)

    def mock_api_response(
        self,
        url_pattern: str,
        response_data: Dict[str, Any],
        status: int = 200
    ) -> None:
        """
        Mock API response with JSON data.

        Args:
            url_pattern: URL pattern to match
            response_data: Response data dictionary
            status: HTTP status code
        """
        def handle_route(route):
            route.fulfill(
                status=status,
                content_type="application/json",
                body=json.dumps(response_data)
            )

        self.page.route(url_pattern, handle_route)

    def abort_requests(self, url_pattern: str) -> None:
        """
        Abort requests matching pattern.

        Args:
            url_pattern: URL pattern to match
        """
        self.page.route(url_pattern, lambda route: route.abort())

    # Performance Utilities

    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get page performance metrics.

        Returns:
            Dictionary of performance metrics
        """
        return self.page.evaluate("""() => {
            const timing = performance.timing;
            const paint = performance.getEntriesByType('paint');
            return {
                domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                loadComplete: timing.loadEventEnd - timing.navigationStart,
                firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
                firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
                responseTime: timing.responseEnd - timing.requestStart,
                domInteractive: timing.domInteractive - timing.navigationStart
            };
        }""")

    def measure_action_time(self, action: Callable) -> float:
        """
        Measure execution time of an action.

        Args:
            action: Callable to execute

        Returns:
            Execution time in seconds
        """
        start_time = time.time()
        action()
        return time.time() - start_time

    # Debugging Utilities

    def highlight_element(self, selector: str, duration: int = 2000) -> None:
        """
        Highlight element with border for debugging.

        Args:
            selector: Element selector
            duration: Highlight duration in milliseconds
        """
        self.page.evaluate(f"""() => {{
            const element = document.querySelector('{selector}');
            if (element) {{
                const originalBorder = element.style.border;
                element.style.border = '3px solid red';
                setTimeout(() => {{
                    element.style.border = originalBorder;
                }}, {duration});
            }}
        }}""")

    def log_console_messages(self) -> None:
        """Enable logging of browser console messages."""
        self.page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

    def pause_for_inspection(self, message: str = "Paused for inspection") -> None:
        """
        Pause execution for manual inspection (only in headed mode).

        Args:
            message: Message to display
        """
        print(f"\n{message}")
        print("Press Enter to continue...")
        input()


class TestDataGenerator:
    """Generate test data for form filling and testing."""

    @staticmethod
    def random_email() -> str:
        """Generate random email address."""
        import random
        import string
        username = ''.join(random.choices(string.ascii_lowercase, k=10))
        return f"{username}@example.com"

    @staticmethod
    def random_phone() -> str:
        """Generate random phone number."""
        import random
        return f"+1-555-{random.randint(1000, 9999)}"

    @staticmethod
    def random_name() -> str:
        """Generate random name."""
        import random
        first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    @staticmethod
    def random_text(length: int = 100) -> str:
        """
        Generate random text.

        Args:
            length: Text length

        Returns:
            Random text string
        """
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + ' ', k=length))


class PageObjectBase:
    """Base class for Page Object Model pattern."""

    def __init__(self, page: Page):
        """Initialize page object with page instance."""
        self.page = page
        self.helper = PlaywrightHelper(page)

    def navigate_to(self, url: str) -> None:
        """Navigate to URL."""
        self.page.goto(url)

    def click(self, selector: str) -> None:
        """Click element."""
        self.page.click(selector)

    def fill(self, selector: str, value: str) -> None:
        """Fill input field."""
        self.page.fill(selector, value)

    def get_text(self, selector: str) -> str:
        """Get element text."""
        return self.page.locator(selector).text_content() or ""

    def is_visible(self, selector: str) -> bool:
        """Check if element is visible."""
        return self.page.locator(selector).is_visible()

    def wait_for_element(self, selector: str, timeout: int = 30000) -> None:
        """Wait for element to be visible."""
        self.page.wait_for_selector(selector, timeout=timeout)
