#!/usr/bin/env python3
"""
Google Search Scraper using Crawl4AI
Usage: python google_search.py "<search query>" [max_results]

Example: python google_search.py "2026年Go语言展望" 20
"""

import asyncio
import sys
import json
import urllib.parse
from typing import List, Dict

try:
    from crawl4ai.__version__ import __version__
    from packaging import version
    MIN_CRAWL4AI_VERSION = "0.7.4"
    if version.parse(__version__) < version.parse(MIN_CRAWL4AI_VERSION):
        print(f"⚠️  Warning: Crawl4AI {MIN_CRAWL4AI_VERSION}+ recommended (you have {__version__})")
except ImportError:
    print(f"ℹ️  Crawl4AI {MIN_CRAWL4AI_VERSION}+ required")

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy


async def search_google_css(query: str, max_results: int = 20) -> List[Dict]:
    """
    使用 CSS 选择器策略提取 Google 搜索结果（最快，无需 LLM）
    """

    # 构建搜索 URL
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"

    print(f"🔍 Searching: {query}")
    print(f"📊 Max results: {max_results}")
    print(f"🌐 URL: {search_url}")

    # 定义 Google 搜索结果的 CSS schema
    # Google 的 HTML 结构会变化，这里使用常用的选择器
    schema = {
        "name": "search_results",
        "baseSelector": "div.g, div[data-hveid], div.tF2Cxc, div.yuRUbf",
        "fields": [
            {
                "name": "title",
                "selector": "h3, h3.LC20lb, div[role='heading']",
                "type": "text"
            },
            {
                "name": "link",
                "selector": "a",
                "type": "attribute",
                "attribute": "href"
            },
            {
                "name": "description",
                "selector": "div.VwiC3b, div.s, div.ITZIwc, span.aCOpRe",
                "type": "text"
            },
            {
                "name": "site_name",
                "selector": "div.NJo7tc, span.VuuXrf, cite",
                "type": "text"
            }
        ]
    }

    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=1080,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    crawler_config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(schema=schema, verbose=True),
        cache_mode=CacheMode.BYPASS,
        wait_for="css:div.g, div.search, body",
        page_timeout=30000,
        js_code=[
            # 等待页面加载完成
            "const waitFor = (ms) => new Promise(resolve => setTimeout(resolve, ms));",
            "await waitFor(2000);"
        ]
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=search_url, config=crawler_config)

        if result.success:
            print("✅ Successfully fetched search results")

            if result.extracted_content:
                try:
                    data = json.loads(result.extracted_content)
                    # 处理列表和字典两种格式
                    if isinstance(data, list):
                        results = data
                    else:
                        results = data.get("search_results", data.get("results", []))

                    # 过滤掉空结果和无效结果
                    seen = set()
                    valid_results = []
                    for r in results:
                        if r.get("title") and r.get("link"):
                            # 清理 URL（Google 有时会在 URL 前加 /url?q=）
                            link = r["link"]
                            if link.startswith("/url?q="):
                                from urllib.parse import urlparse, parse_qs
                                parsed = urlparse(link)
                                link = parse_qs(parsed.query).get("q", [link])[0]
                            r["link"] = link

                            # 使用 URL 作为唯一标识去重
                            if link not in seen:
                                seen.add(link)
                                valid_results.append(r)

                    print(f"📋 Extracted {len(valid_results)} valid results")
                    return valid_results[:max_results]

                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse extracted content: {e}")
                    print("Raw output:", result.extracted_content[:500] if result.extracted_content else "None")
                    return []
            else:
                print("⚠️ No extracted content, trying alternative method...")
                return await search_google_llm_fallback(query, max_results)
        else:
            print(f"❌ Failed: {result.error_message}")
            print("Trying fallback method...")
            return await search_google_llm_fallback(query, max_results)


async def search_google_llm_fallback(query: str, max_results: int = 20) -> List[Dict]:
    """
    使用 LLM 作为备选方案提取搜索结果
    注意：这需要配置 LLM API 密钥
    """

    print("🤖 Using LLM fallback extraction...")

    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"

    # 尝试使用简单的 LLM 提取
    extraction_strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        instruction=f"""
        Extract the top {max_results} search results from this Google search page for "{query}".

        For each search result, extract:
        1. Title - the blue link text
        2. Link - the URL (clean the URL, remove /url?q= prefix if present)
        3. Description - the gray text snippet below the title
        4. Site name - the green text showing the website name

        Return as JSON with a "results" array containing objects with these fields.
        Skip any ads or sponsored content.
        """
    )

    crawler_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS,
        page_timeout=30000
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=search_url, config=crawler_config)

        if result.success and result.extracted_content:
            try:
                data = json.loads(result.extracted_content)
                return data.get("results", [])
            except json.JSONDecodeError:
                print("⚠️ LLM output could not be parsed as JSON")
                return []
        else:
            print(f"❌ Fallback also failed: {result.error_message}")
            return []


async def search_google_with_html_parsing(query: str, max_results: int = 20) -> List[Dict]:
    """
    直接解析 HTML 作为最后的备选方案
    """

    print("🔧 Using direct HTML parsing...")

    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"

    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=1080,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_for="css:body",
        page_timeout=30000,
        js_code=[
            "const waitFor = (ms) => new Promise(resolve => setTimeout(resolve, ms));",
            "await waitFor(3000);"
        ]
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=search_url, config=crawler_config)

        if result.success and result.html:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(result.html, 'html.parser')
            results = []

            # Google 搜索结果通常在 div.g 中
            for div in soup.select('div.g, div.tF2Cxc'):
                try:
                    # 提取标题
                    title_elem = div.select_one('h3')
                    title = title_elem.get_text() if title_elem else ""

                    # 提取链接
                    link_elem = div.select_one('a')
                    link = link_elem.get('href', '') if link_elem else ""

                    # 清理 Google 重定向链接
                    if link.startswith('/url?q='):
                        from urllib.parse import urlparse, parse_qs, unquote
                        parsed = urlparse(link)
                        link = unquote(parse_qs(parsed.query).get('q', [link])[0])

                    # 提取描述
                    desc_elem = div.select_one('div.VwiC3b, div.s, span.aCOpRe')
                    description = desc_elem.get_text() if desc_elem else ""

                    # 提取网站名称
                    site_elem = div.select_one('div.NJo7tc, span.VuuXrf, cite')
                    site_name = site_elem.get_text() if site_elem else ""

                    if title and link and not link.startswith('#'):
                        results.append({
                            "title": title.strip(),
                            "link": link.strip(),
                            "description": description.strip(),
                            "site_name": site_name.strip()
                        })

                        if len(results) >= max_results:
                            break

                except Exception as e:
                    continue

            print(f"📋 Parsed {len(results)} results from HTML")
            return results
        else:
            print(f"❌ HTML parsing failed")
            return []


async def main():
    if len(sys.argv) < 2:
        print("Usage: python google_search.py \"<search query>\" [max_results]")
        print("Example: python google_search.py \"2026年Go语言展望\" 20")
        sys.exit(1)

    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    # 方法1: CSS 提取
    results = await search_google_css(query, max_results)

    # 如果 CSS 提取失败，尝试 HTML 解析
    if not results:
        results = await search_google_with_html_parsing(query, max_results)

    # 输出结果
    if results:
        output = {
            "query": query,
            "total_results": len(results),
            "results": results
        }

        print("\n" + "="*60)
        print(f"✅ Successfully extracted {len(results)} search results")
        print("="*60)

        # 保存到文件
        output_file = "google_search_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Results saved to: {output_file}")
        print("\n📋 Preview (first 3 results):")
        print(json.dumps(results[:3], ensure_ascii=False, indent=2))

        # 打印完整 JSON 到 stdout
        print("\n" + "="*60)
        print("FULL JSON OUTPUT:")
        print("="*60)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print("❌ No results extracted. Please check:")
        print("  1. Your internet connection")
        print("  2. Whether Google is blocking the request (try with headless=False)")
        print("  3. The CSS selectors (Google might have changed their HTML)")


if __name__ == "__main__":
    asyncio.run(main())
