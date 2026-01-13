#!/usr/bin/env python3
"""
Test markdown generation examples from SKILL.md
"""
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def test_basic_markdown():
    """Test basic markdown extraction"""
    print("Testing basic markdown extraction...")

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")

        # result.markdown is StringCompatibleMarkdown
        markdown_str = str(result.markdown)
        assert len(markdown_str) > 0, "Markdown is empty"
        print(f"✅ Basic markdown length: {len(markdown_str)}")

async def test_fit_markdown_with_filters():
    """Test Fit Markdown with content filters"""
    print("\nTesting Fit Markdown with filters...")

    # Test BM25 filter
    bm25_filter = BM25ContentFilter(
        user_query="example domain",
        bm25_threshold=1.0
    )

    md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
    config = CrawlerRunConfig(markdown_generator=md_generator)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com", config=config)

        # Access both raw and fit markdown
        assert hasattr(result.markdown, 'raw_markdown'), "Missing raw_markdown attribute"
        assert hasattr(result.markdown, 'fit_markdown'), "Missing fit_markdown attribute"

        print(f"✅ Raw markdown length: {len(result.markdown.raw_markdown)}")
        print(f"✅ Fit markdown length: {len(result.markdown.fit_markdown or '')}")

async def test_pruning_filter():
    """Test Pruning filter"""
    print("\nTesting Pruning filter...")

    pruning_filter = PruningContentFilter(threshold=0.4, threshold_type="fixed")
    md_generator = DefaultMarkdownGenerator(content_filter=pruning_filter)
    config = CrawlerRunConfig(markdown_generator=md_generator)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com", config=config)

        assert result.success, f"Crawl failed: {result.error_message}"
        print(f"✅ Pruning filter works")

async def test_markdown_options():
    """Test markdown generator options"""
    print("\nTesting markdown generator options...")

    generator = DefaultMarkdownGenerator(
        options={
            "ignore_links": False,
            "ignore_images": False,
            "image_alt_text": True
        }
    )

    config = CrawlerRunConfig(markdown_generator=generator)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com", config=config)

        assert result.success, f"Crawl failed: {result.error_message}"
        print(f"✅ Markdown options work")

async def main():
    await test_basic_markdown()
    await test_fit_markdown_with_filters()
    await test_pruning_filter()
    await test_markdown_options()

if __name__ == "__main__":
    asyncio.run(main())
    print("\n✅ All markdown generation tests passed!")
