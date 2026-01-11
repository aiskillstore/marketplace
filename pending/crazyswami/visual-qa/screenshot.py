#!/usr/bin/env python3
"""
Visual QA Screenshot Script

Takes full-page screenshots with proper animation handling:
1. Scrolls through entire page in increments to trigger GSAP/ScrollTrigger animations
2. Waits for animations to complete
3. Captures full-page screenshot

Usage:
    python3 screenshot.py --url https://csrdevelopment.com/about/
    python3 screenshot.py --all
    python3 screenshot.py --all --output /custom/path
"""

import argparse
import os
import sys
from datetime import datetime
from typing import List, Dict

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Playwright not installed")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# Configuration
DEFAULT_BASE_URL = "https://local2.hustletogether.com"
DEFAULT_OUTPUT = "/root/screenshots"

# Multiple viewports within each device category for thorough testing
DEVICES = {
    # Desktop viewports
    "desktop-1920": {"width": 1920, "height": 1080},   # Full HD
    "desktop-1440": {"width": 1440, "height": 900},    # MacBook Pro 15"
    "desktop-1280": {"width": 1280, "height": 800},    # MacBook Air / smaller laptops
    # Tablet viewports
    "tablet-portrait": {"width": 768, "height": 1024},  # iPad portrait
    "tablet-landscape": {"width": 1024, "height": 768}, # iPad landscape
    "tablet-mini": {"width": 744, "height": 1133},      # iPad Mini
    # Mobile viewports
    "mobile-iphone14": {"width": 390, "height": 844},   # iPhone 14/13/12
    "mobile-iphone14pro": {"width": 393, "height": 852}, # iPhone 14 Pro
    "mobile-iphoneSE": {"width": 375, "height": 667},   # iPhone SE / older
    "mobile-android": {"width": 412, "height": 915},    # Pixel 7 / Samsung Galaxy
}

PAGES = [
    {"path": "/", "name": "home"},
    {"path": "/about/", "name": "about"},
    {"path": "/portfolio/", "name": "portfolio"},
    {"path": "/contact/", "name": "contact"},
    {"path": "/privacy-policy/", "name": "privacy-policy"},
    {"path": "/terms/", "name": "terms"},
]


def scroll_and_trigger_animations(page, scroll_increment: int = 300, pause_ms: int = 200):
    """
    Scroll through entire page in increments to trigger all GSAP/ScrollTrigger animations.
    This ensures elements like curtain-reveal, scroll-trigger-text, etc. are activated.
    """
    # Get total page height
    total_height = page.evaluate("document.body.scrollHeight")
    viewport_height = page.evaluate("window.innerHeight")
    current_position = 0

    # Scroll down incrementally
    while current_position < total_height:
        page.evaluate(f"window.scrollTo(0, {current_position})")
        page.wait_for_timeout(pause_ms)
        current_position += scroll_increment

        # Update total height in case lazy content loaded
        total_height = page.evaluate("document.body.scrollHeight")

    # Scroll to very bottom to ensure everything loaded
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(500)

    # Scroll back to top for screenshot
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)


def wait_for_animations(page, timeout_ms: int = 3000):
    """Wait for GSAP animations to complete"""
    # Wait for common animation classes to have opacity 1
    try:
        page.wait_for_function("""
            () => {
                const animatedElements = document.querySelectorAll('.hero-text, .page-title, .portfolio-card, .scroll-card');
                if (animatedElements.length === 0) return true;

                for (const el of animatedElements) {
                    const style = window.getComputedStyle(el);
                    if (parseFloat(style.opacity) < 0.9) return false;
                }
                return true;
            }
        """, timeout=timeout_ms)
    except:
        # Timeout is OK - some pages may not have these elements
        pass


def take_screenshot(
    page,
    url: str,
    page_name: str,
    device_name: str,
    viewport: Dict[str, int],
    output_dir: str,
    timestamp: str
) -> str:
    """Take a single screenshot with full animation handling"""

    # Set viewport
    page.set_viewport_size(viewport)

    # Navigate to page
    page.goto(url, wait_until="networkidle", timeout=60000)

    # Initial wait for page load animations
    page.wait_for_timeout(1500)

    # Scroll through entire page to trigger all animations
    scroll_and_trigger_animations(page)

    # Wait for animations to settle
    wait_for_animations(page)
    page.wait_for_timeout(500)

    # Generate filename
    filename = f"{timestamp}_{page_name}_{device_name}.png"
    filepath = os.path.join(output_dir, filename)

    # Take full-page screenshot
    page.screenshot(path=filepath, full_page=True)

    return filepath


def run_single_page(url: str, output_dir: str) -> List[str]:
    """Take screenshots of a single URL at all breakpoints"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Extract page name from URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    page_name = path.replace("/", "-") if path else "home"

    screenshots = []

    print(f"Taking screenshots of: {url}")
    print(f"Output directory: {output_dir}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        for device_name, viewport in DEVICES.items():
            try:
                filepath = take_screenshot(
                    page, url, page_name, device_name, viewport, output_dir, timestamp
                )
                screenshots.append(filepath)
                print(f"✓ {device_name}: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"✗ {device_name}: Error - {e}")

        context.close()
        browser.close()

    return screenshots


def run_all_pages(output_dir: str, base_url: str = DEFAULT_BASE_URL) -> List[str]:
    """Take screenshots of all pages at all breakpoints"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    screenshots = []
    total = len(PAGES) * len(DEVICES)
    current = 0

    print(f"Taking {total} screenshots ({len(PAGES)} pages × {len(DEVICES)} devices)")
    print(f"Base URL: {base_url}")
    print(f"Output directory: {output_dir}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        for page_info in PAGES:
            url = f"{base_url}{page_info['path']}"
            page_name = page_info['name']

            print(f"📄 {page_name.upper()}")

            for device_name, viewport in DEVICES.items():
                current += 1
                try:
                    filepath = take_screenshot(
                        page, url, page_name, device_name, viewport, output_dir, timestamp
                    )
                    screenshots.append(filepath)
                    print(f"   ✓ {device_name} ({current}/{total})")
                except Exception as e:
                    print(f"   ✗ {device_name}: {e}")

        context.close()
        browser.close()

    return screenshots


def main():
    parser = argparse.ArgumentParser(
        description='Visual QA - Screenshot automation with animation handling'
    )
    parser.add_argument('--all', action='store_true',
                        help='Screenshot all pages')
    parser.add_argument('--url', type=str,
                        help='Screenshot a specific URL')
    parser.add_argument('--output', type=str, default=DEFAULT_OUTPUT,
                        help=f'Output directory (default: {DEFAULT_OUTPUT})')
    parser.add_argument('--base-url', type=str, default=DEFAULT_BASE_URL,
                        help=f'Base URL for --all mode (default: {DEFAULT_BASE_URL})')

    args = parser.parse_args()

    if args.all:
        screenshots = run_all_pages(args.output, args.base_url)
        print(f"\n✓ Complete! {len(screenshots)} screenshots saved to {args.output}")
    elif args.url:
        screenshots = run_single_page(args.url, args.output)
        print(f"\n✓ Complete! {len(screenshots)} screenshots saved.")
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python3 screenshot.py --all")
        print("  python3 screenshot.py --url https://csrdevelopment.com/about/")
        print("  python3 screenshot.py --all --output /custom/path")


if __name__ == "__main__":
    main()
