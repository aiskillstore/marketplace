#!/usr/bin/env python3
"""
Basic Crawl4AI crawler template
Usage: python basic_crawler.py <url>
"""

import asyncio
import sys

# Version check
MIN_CRAWL4AI_VERSION = "0.7.4"
try:
    from crawl4ai.__version__ import __version__
    from packaging import version
    if version.parse(__version__) < version.parse(MIN_CRAWL4AI_VERSION):
        print(f"⚠️  Warning: Crawl4AI {MIN_CRAWL4AI_VERSION}+ recommended (you have {__version__})")
except ImportError:
    print(f"ℹ️  Crawl4AI {MIN_CRAWL4AI_VERSION}+ required")

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def crawl_basic(url: str):
    """Basic crawling with markdown output"""

    # Configure browser
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=1080
    )

    # Configure crawler
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        remove_overlay_elements=True,
        wait_for_images=True,
        screenshot=True
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=crawler_config
        )

        if result.success:
            print(f"✅ Crawled: {result.url}")
            print(f"   Title: {result.metadata.get('title', 'N/A')}")
            print(f"   Links found: {len(result.links.get('internal', []))} internal, {len(result.links.get('external', []))} external")
            print(f"   Media found: {len(result.media.get('images', []))} images, {len(result.media.get('videos', []))} videos")
            print(f"   Content length: {len(result.markdown)} chars")

            # Save markdown
            with open("output.md", "w") as f:
                f.write(result.markdown)
            print("📄 Saved to output.md")

            # Save screenshot if available
            if result.screenshot:
                # Check if screenshot is base64 string or bytes
                if isinstance(result.screenshot, str):
                    import base64
                    screenshot_data = base64.b64decode(result.screenshot)
                else:
                    screenshot_data = result.screenshot
                with open("screenshot.png", "wb") as f:
                    f.write(screenshot_data)
                print("📸 Saved screenshot.png")
        else:
            print(f"❌ Failed: {result.error_message}")

        return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python basic_crawler.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    asyncio.run(crawl_basic(url))
