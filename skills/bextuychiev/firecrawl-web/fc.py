#!/usr/bin/env python3
"""Firecrawl web skill for Claude Code."""

import argparse
import base64
import json
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import Firecrawl


def scrape_markdown(url: str, only_main: bool = False) -> str:
    """Scrape a URL and return markdown content."""
    app = Firecrawl()
    result = app.scrape(
        url,
        formats=["markdown"],
        only_main_content=only_main if only_main else None
    )
    return result.markdown


def take_screenshot(url: str, output_path: str = None) -> str:
    """Take a screenshot of a URL."""
    app = Firecrawl()
    result = app.scrape(url, formats=["screenshot"])

    screenshot_data = result.screenshot

    # Handle URL response (Firecrawl returns a GCS URL)
    if screenshot_data.startswith("http://") or screenshot_data.startswith("https://"):
        if output_path:
            urllib.request.urlretrieve(screenshot_data, output_path)
            return f"Screenshot saved to {output_path}"
        return f"[Screenshot URL: {screenshot_data}]"

    # Handle base64 data URI response
    if screenshot_data.startswith("data:image"):
        screenshot_data = screenshot_data.split(",", 1)[1]

    if output_path:
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(screenshot_data))
        return f"Screenshot saved to {output_path}"

    return f"[Screenshot: {len(screenshot_data)} bytes base64]"


def extract_data(url: str, schema: dict, prompt: str = None) -> dict:
    """Extract structured data from a URL using a schema."""
    app = Firecrawl()

    format_spec = {"type": "json", "schema": schema}
    if prompt:
        format_spec["prompt"] = prompt

    result = app.scrape(url, formats=[format_spec])
    return result.json


def search_web(query: str, limit: int = 5) -> list:
    """Search the web and return results with content."""
    app = Firecrawl()
    results = app.search(query, limit=limit)
    return results.web or []


def crawl_docs(url: str, limit: int = 50) -> list:
    """Crawl a documentation site."""
    app = Firecrawl()
    result = app.crawl(
        url,
        limit=limit,
        scrape_options={"formats": ["markdown"], "onlyMainContent": True}
    )
    return result.data


def main():
    # Load .env from current directory and home directory
    load_dotenv()
    load_dotenv(Path.home() / ".env")

    parser = argparse.ArgumentParser(description="Firecrawl web tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Markdown command
    md_parser = subparsers.add_parser("markdown", help="Get page as markdown")
    md_parser.add_argument("url", help="URL to scrape")
    md_parser.add_argument("--main-only", action="store_true", help="Exclude nav/footer")

    # Screenshot command
    ss_parser = subparsers.add_parser("screenshot", help="Screenshot a webpage")
    ss_parser.add_argument("url", help="URL to capture")
    ss_parser.add_argument("--output", "-o", help="Save to file (PNG)")

    # Extract command
    ex_parser = subparsers.add_parser("extract", help="Extract structured data")
    ex_parser.add_argument("url", help="URL to extract from")
    ex_parser.add_argument("--schema", required=True, help="Path to JSON schema file")
    ex_parser.add_argument("--prompt", help="Extraction guidance")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search the web")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=5, help="Number of results")

    # Crawl command
    crawl_parser = subparsers.add_parser("crawl", help="Crawl a docs site")
    crawl_parser.add_argument("url", help="Starting URL")
    crawl_parser.add_argument("--limit", type=int, default=50, help="Max pages")
    crawl_parser.add_argument("--output", "-o", help="Save to directory")

    args = parser.parse_args()

    # Handle commands
    if args.command == "markdown":
        content = scrape_markdown(args.url, args.main_only)
        print(content)

    elif args.command == "screenshot":
        result = take_screenshot(args.url, args.output)
        print(result)

    elif args.command == "extract":
        with open(args.schema) as f:
            schema = json.load(f)
        data = extract_data(args.url, schema, args.prompt)
        print(json.dumps(data, indent=2))

    elif args.command == "search":
        results = search_web(args.query, args.limit)
        for r in results:
            print(f"## {r.title}")
            print(f"URL: {r.url}")
            print(r.description or "No description")
            print("\n---\n")

    elif args.command == "crawl":
        pages = crawl_docs(args.url, args.limit)

        if args.output:
            Path(args.output).mkdir(parents=True, exist_ok=True)
            for i, page in enumerate(pages):
                filename = f"{args.output}/page_{i:03d}.md"
                with open(filename, "w") as f:
                    f.write(page.markdown or "")
            print(f"Saved {len(pages)} pages to {args.output}/")
        else:
            for page in pages:
                title = page.metadata.title if page.metadata else "Untitled"
                print(f"## {title}")
                print(page.markdown[:1000] if page.markdown else "")
                print("\n---\n")


if __name__ == "__main__":
    main()
