#!/usr/bin/env python3
"""
Test basic crawling examples from SKILL.md
"""
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def test_basic_crawl():
    """Test basic crawling setup"""
    print("Testing basic crawl setup...")

    # Test from SKILL.md Section 1
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=1080,
        user_agent="custom-agent"
    )

    crawler_config = CrawlerRunConfig(
        page_timeout=30000,
        screenshot=True,
        remove_overlay_elements=True
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://example.com",
            config=crawler_config
        )

        # Verify result attributes
        assert result.success, f"Crawl failed: {result.error_message}"
        assert hasattr(result, 'html'), "Missing html attribute"
        assert hasattr(result, 'markdown'), "Missing markdown attribute"
        assert hasattr(result, 'links'), "Missing links attribute"

        # Test markdown as string (StringCompatibleMarkdown)
        markdown_str = str(result.markdown)
        assert len(markdown_str) > 0, "Markdown is empty"

        print(f"✅ Success: {result.success}")
        print(f"✅ HTML length: {len(result.html)}")
        print(f"✅ Markdown length: {len(markdown_str)}")
        print(f"✅ Links found: {len(result.links)}")

if __name__ == "__main__":
    asyncio.run(test_basic_crawl())
    print("\n✅ All basic crawling tests passed!")
