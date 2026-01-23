#!/usr/bin/env python3
"""Firecrawl API v2 tool for web scraping, crawling, searching, and extracting."""

import json
import os
import sys
import time
import requests

API_BASE = "https://api.firecrawl.dev/v1"


def get_api_key():
    """Get the Firecrawl API key from environment."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        return None, "FIRECRAWL_API_KEY environment variable not set"
    return api_key, None


def scrape(url: str, formats: list[str], only_main_content: bool, api_key: str) -> dict:
    """Scrape a single URL and return content in specified formats."""
    response = requests.post(
        f"{API_BASE}/scrape",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "url": url,
            "formats": formats,
            "onlyMainContent": only_main_content,
        },
        timeout=120,
    )
    return response.json()


def crawl(url: str, limit: int, formats: list[str], api_key: str) -> dict:
    """Crawl a website and return all pages."""
    # Start the crawl job
    response = requests.post(
        f"{API_BASE}/crawl",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "url": url,
            "limit": limit,
            "scrapeOptions": {
                "formats": formats,
            },
        },
        timeout=30,
    )

    result = response.json()
    if not result.get("success"):
        return result

    job_id = result.get("id")
    if not job_id:
        return {"success": False, "error": "No job ID returned from crawl request"}

    # Poll for completion
    max_attempts = 60  # 5 minutes max
    for _ in range(max_attempts):
        status_response = requests.get(
            f"{API_BASE}/crawl/{job_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        status = status_response.json()

        if status.get("status") == "completed":
            return status
        elif status.get("status") == "failed":
            return {"success": False, "error": status.get("error", "Crawl failed")}

        time.sleep(5)

    return {"success": False, "error": "Crawl timed out"}


def map_urls(url: str, search_query: str, api_key: str) -> dict:
    """Get all URLs from a website, optionally filtered by search query."""
    payload = {"url": url}
    if search_query:
        payload["search"] = search_query

    response = requests.post(
        f"{API_BASE}/map",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    return response.json()


def search(query: str, limit: int, api_key: str) -> dict:
    """Search the web and return scraped results."""
    response = requests.post(
        f"{API_BASE}/search",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "limit": limit,
        },
        timeout=120,
    )
    return response.json()


def extract(url: str, prompt: str, schema_str: str, api_key: str) -> dict:
    """Extract structured data from a URL using AI."""
    payload = {
        "urls": [url],
    }

    if prompt:
        payload["prompt"] = prompt

    if schema_str:
        try:
            payload["schema"] = json.loads(schema_str)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid JSON schema: {schema_str}"}

    # Start extract job
    response = requests.post(
        f"{API_BASE}/extract",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    result = response.json()
    if not result.get("success"):
        return result

    job_id = result.get("id")
    if not job_id:
        # Synchronous response
        return result

    # Poll for completion
    max_attempts = 60
    for _ in range(max_attempts):
        status_response = requests.get(
            f"{API_BASE}/extract/{job_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        status = status_response.json()

        if status.get("status") == "completed":
            return status
        elif status.get("status") == "failed":
            return {"success": False, "error": status.get("error", "Extract failed")}

        time.sleep(2)

    return {"success": False, "error": "Extract timed out"}


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Usage: firecrawl.py <action> <url_or_query> [formats] [limit] [only_main_content] [prompt] [schema]"
        }))
        sys.exit(1)

    action = sys.argv[1]
    url_or_query = sys.argv[2]
    formats_str = sys.argv[3] if len(sys.argv) > 3 else "markdown"
    limit = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 10
    only_main_content = sys.argv[5].lower() == "true" if len(sys.argv) > 5 else True
    prompt = sys.argv[6] if len(sys.argv) > 6 else ""
    schema = sys.argv[7] if len(sys.argv) > 7 else ""

    # Parse formats
    formats = [f.strip() for f in formats_str.split(",")]

    # Get API key
    api_key, error = get_api_key()
    if error:
        print(json.dumps({"success": False, "error": error}))
        sys.exit(1)

    try:
        if action == "scrape":
            result = scrape(url_or_query, formats, only_main_content, api_key)
        elif action == "crawl":
            result = crawl(url_or_query, limit, formats, api_key)
        elif action == "map":
            # For map, prompt can be used as search query
            result = map_urls(url_or_query, prompt, api_key)
        elif action == "search":
            result = search(url_or_query, limit, api_key)
        elif action == "extract":
            result = extract(url_or_query, prompt, schema, api_key)
        else:
            result = {"success": False, "error": f"Unknown action: {action}"}

        # Add metadata to output
        output = {
            "success": result.get("success", True),
            "action": action,
            "url": url_or_query,
            "data": result.get("data", result),
        }

        if "error" in result:
            output["error"] = result["error"]
            output["success"] = False

        print(json.dumps(output, indent=2))

    except requests.exceptions.RequestException as e:
        print(json.dumps({
            "success": False,
            "action": action,
            "url": url_or_query,
            "error": f"Request failed: {str(e)}"
        }))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "action": action,
            "url": url_or_query,
            "error": f"Unexpected error: {str(e)}"
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
