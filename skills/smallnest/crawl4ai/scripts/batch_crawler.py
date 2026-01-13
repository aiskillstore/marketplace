#!/usr/bin/env python3
"""
Crawl4AI batch/multi-URL crawler with concurrent processing
Usage: python batch_crawler.py urls.txt [--max-concurrent 5]
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

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

async def crawl_batch(urls: List[str], max_concurrent: int = 5):
    """
    Crawl multiple URLs efficiently with concurrent processing
    """
    print(f"🚀 Starting batch crawl of {len(urls)} URLs (max {max_concurrent} concurrent)")

    # Configure browser for efficiency
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1280,
        viewport_height=800,
        verbose=False
    )

    # Configure crawler
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        remove_overlay_elements=True,
        wait_for="css:body",
        page_timeout=30000,  # 30 seconds timeout per page
        screenshot=False  # Disable screenshots for batch processing
    )

    results = []
    failed = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Use arun_many for efficient batch processing
        batch_results = await crawler.arun_many(
            urls=urls,
            config=crawler_config,
            max_concurrent=max_concurrent
        )

        for result in batch_results:
            if result.success:
                results.append({
                    "url": result.url,
                    "title": result.metadata.get("title", ""),
                    "description": result.metadata.get("description", ""),
                    "content_length": len(result.markdown),
                    "links_count": len(result.links.get("internal", [])) + len(result.links.get("external", [])),
                    "images_count": len(result.media.get("images", [])),
                })
                print(f"✅ {result.url}")
            else:
                failed.append({
                    "url": result.url,
                    "error": result.error_message
                })
                print(f"❌ {result.url}: {result.error_message}")

    # Save results
    output = {
        "success_count": len(results),
        "failed_count": len(failed),
        "results": results,
        "failed": failed
    }

    with open("batch_results.json", "w") as f:
        json.dump(output, f, indent=2)

    # Save individual markdown files
    markdown_dir = Path("batch_markdown")
    markdown_dir.mkdir(exist_ok=True)

    for i, result in enumerate(batch_results):
        if result.success:
            # Create safe filename from URL
            safe_name = result.url.replace("https://", "").replace("http://", "")
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in safe_name)[:100]

            file_path = markdown_dir / f"{i:03d}_{safe_name}.md"
            with open(file_path, "w") as f:
                f.write(f"# {result.metadata.get('title', result.url)}\n\n")
                f.write(f"URL: {result.url}\n\n")
                f.write(result.markdown)

    print(f"\n📊 Batch Crawl Complete:")
    print(f"   ✅ Success: {len(results)}")
    print(f"   ❌ Failed: {len(failed)}")
    print(f"   💾 Results saved to: batch_results.json")
    print(f"   📁 Markdown files saved to: {markdown_dir}/")

    return output

async def crawl_with_extraction(urls: List[str], schema_file: str = None):
    """
    Batch crawl with structured data extraction
    """
    from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

    schema = None
    if schema_file and Path(schema_file).exists():
        with open(schema_file) as f:
            schema = json.load(f)
        print(f"📋 Using extraction schema from: {schema_file}")
    else:
        # Default schema for general content
        schema = {
            "name": "content",
            "selector": "body",
            "fields": [
                {"name": "headings", "selector": "h1, h2, h3", "type": "text", "all": True},
                {"name": "paragraphs", "selector": "p", "type": "text", "all": True},
                {"name": "links", "selector": "a[href]", "type": "attribute", "attribute": "href", "all": True}
            ]
        }

    extraction_strategy = JsonCssExtractionStrategy(schema=schema)

    crawler_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS
    )

    extracted_data = []

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(
            urls=urls,
            config=crawler_config,
            max_concurrent=5
        )

        for result in results:
            if result.success and result.extracted_content:
                try:
                    data = json.loads(result.extracted_content)
                    extracted_data.append({
                        "url": result.url,
                        "data": data
                    })
                    print(f"✅ Extracted from: {result.url}")
                except json.JSONDecodeError:
                    print(f"⚠️ Failed to parse JSON from: {result.url}")

    # Save extracted data
    with open("batch_extracted.json", "w") as f:
        json.dump(extracted_data, f, indent=2)

    print(f"\n💾 Extracted data saved to: batch_extracted.json")
    return extracted_data

def load_urls(source: str) -> List[str]:
    """Load URLs from file or string"""
    if Path(source).exists():
        with open(source) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        # Treat as comma-separated URLs
        urls = [url.strip() for url in source.split(",") if url.strip()]

    return urls

async def main():
    if len(sys.argv) < 2:
        print("""
Crawl4AI Batch Crawler

Usage:
    # Crawl URLs from file
    python batch_crawler.py urls.txt [--max-concurrent 5]

    # Crawl with extraction
    python batch_crawler.py urls.txt --extract [schema.json]

    # Crawl comma-separated URLs
    python batch_crawler.py "https://example.com,https://example.org"

Options:
    --max-concurrent N    Max concurrent crawls (default: 5)
    --extract [schema]    Extract structured data using schema

Example urls.txt:
    https://example.com
    https://example.org
    # Comments are ignored
    https://another-site.com
""")
        sys.exit(1)

    source = sys.argv[1]
    urls = load_urls(source)

    if not urls:
        print("❌ No URLs found")
        sys.exit(1)

    print(f"📋 Loaded {len(urls)} URLs")

    # Parse options
    max_concurrent = 5
    extract_mode = False
    schema_file = None

    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--max-concurrent" and i + 1 < len(sys.argv):
            max_concurrent = int(sys.argv[i + 1])
        elif arg == "--extract":
            extract_mode = True
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
                schema_file = sys.argv[i + 1]

    if extract_mode:
        await crawl_with_extraction(urls, schema_file)
    else:
        await crawl_batch(urls, max_concurrent)

if __name__ == "__main__":
    asyncio.run(main())
