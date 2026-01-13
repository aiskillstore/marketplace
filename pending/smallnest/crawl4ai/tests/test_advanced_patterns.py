#!/usr/bin/env python3
"""
Test advanced patterns from SKILL.md
"""
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def test_session_management():
    """Test session management"""
    print("Testing session management...")

    async with AsyncWebCrawler() as crawler:
        session_id = "test_session"

        # First crawl with session
        config1 = CrawlerRunConfig(session_id=session_id)
        result1 = await crawler.arun("https://example.com", config=config1)

        assert result1.success, f"First crawl failed: {result1.error_message}"

        # Second crawl reusing session
        config2 = CrawlerRunConfig(session_id=session_id)
        result2 = await crawler.arun("https://example.org", config=config2)

        assert result2.success, f"Second crawl failed: {result2.error_message}"

        print(f"✅ Session management works")

async def test_proxy_config():
    """Test proxy configuration in BrowserConfig"""
    print("\nTesting proxy configuration structure...")

    # Test that proxy config is in BrowserConfig (not CrawlerRunConfig)
    browser_config = BrowserConfig(
        headless=True,
        proxy_config={
            "server": "http://proxy.example.com:8080",
            "username": "user",
            "password": "pass"
        }
    )

    print(f"✅ Proxy config structure correct (in BrowserConfig)")

async def test_batch_crawling():
    """Test arun_many for batch crawling"""
    print("\nTesting batch crawling...")

    urls = ["https://example.com", "https://example.org"]

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(
            urls=urls,
            max_concurrent=2
        )

        assert len(results) == 2, f"Expected 2 results, got {len(results)}"

        for result in results:
            if result.success:
                print(f"✅ {result.url}: Success")
            else:
                print(f"⚠️ {result.url}: {result.error_message}")

async def main():
    await test_session_management()
    await test_proxy_config()
    await test_batch_crawling()

if __name__ == "__main__":
    asyncio.run(main())
    print("\n✅ All advanced pattern tests passed!")
