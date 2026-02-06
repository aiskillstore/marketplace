#!/usr/bin/env python3
"""
SEO audit script (no API required)
Usage: python3 scripts/seo_audit.py "https://example.com"
"""
import argparse
import urllib.request
import urllib.parse
import re
import time
import sys


def fetch_url(url: str, timeout: int = 30) -> tuple:
    """Fetch URL and return (content, headers, load_time)"""
    try:
        start = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "SEO-Audit/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            headers = dict(resp.headers)
            load_time = time.time() - start
            return content, headers, load_time
    except Exception as e:
        return None, None, None


def extract_meta(html: str) -> dict:
    """Extract meta tags from HTML"""
    result = {}
    
    # Title
    title_match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
    result["title"] = title_match.group(1).strip() if title_match else None
    
    # Meta description
    desc_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
    if not desc_match:
        desc_match = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']', html, re.I)
    result["description"] = desc_match.group(1).strip() if desc_match else None
    
    # OG tags
    og_match = re.search(r'<meta[^>]+property=["\']og:title["\']', html, re.I)
    result["og_tags"] = bool(og_match)
    
    # JSON-LD
    jsonld_count = len(re.findall(r'application/ld\+json', html, re.I))
    result["jsonld_count"] = jsonld_count
    
    # H1 (handle inline tags like <br>)
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.DOTALL)
    if h1_match:
        h1_text = re.sub(r"<[^>]+>", " ", h1_match.group(1))  # Remove inner tags
        h1_text = re.sub(r"\s+", " ", h1_text).strip()  # Normalize whitespace
        result["h1"] = h1_text[:100]
    else:
        result["h1"] = None
    
    return result


def check_robots(url: str) -> dict:
    """Check robots.txt"""
    parsed = urllib.parse.urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    content, _, _ = fetch_url(robots_url)
    
    result = {"exists": False, "ai_bots": []}
    if content:
        result["exists"] = True
        ai_bots = ["GPTBot", "PerplexityBot", "ClaudeBot", "anthropic-ai", "ChatGPT-User"]
        for bot in ai_bots:
            if bot.lower() in content.lower():
                result["ai_bots"].append(bot)
    return result


def check_sitemap(url: str) -> bool:
    """Check if sitemap.xml exists"""
    parsed = urllib.parse.urlparse(url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    content, _, _ = fetch_url(sitemap_url)
    if not content:
        return False
    # Check for common sitemap indicators
    return "<urlset" in content.lower() or "<sitemapindex" in content.lower() or "<?xml" in content.lower()


def main():
    parser = argparse.ArgumentParser(description="SEO audit")
    parser.add_argument("url", help="URL to audit")
    args = parser.parse_args()
    
    url = args.url
    if not url.startswith("http"):
        url = f"https://{url}"
    
    print(f"=== SEO Audit: {url} ===")
    print()
    
    # Fetch page
    content, headers, load_time = fetch_url(url)
    if not content:
        print("error: Could not fetch URL")
        sys.exit(1)
    
    # Meta tags
    print("## Meta Tags")
    meta = extract_meta(content)
    title = meta["title"]
    print(f"title: {title[:60] if title else 'MISSING'}{'...' if title and len(title) > 60 else ''}")
    print(f"title_length: {len(title) if title else 0} chars")
    desc = meta["description"]
    print(f"description: {desc[:80] if desc else 'MISSING'}{'...' if desc and len(desc) > 80 else ''}")
    print(f"description_length: {len(desc) if desc else 0} chars")
    print(f"og_tags: {'yes' if meta['og_tags'] else 'no'}")
    print(f"h1: {meta['h1'] if meta['h1'] else 'MISSING'}")
    print()
    
    # Schema
    print("## Schema Markup")
    print(f"json_ld_blocks: {meta['jsonld_count']}")
    print()
    
    # Performance
    print("## Performance")
    print(f"load_time: {load_time:.2f}s")
    print(f"status: {'good' if load_time < 3 else 'slow'}")
    print()
    
    # robots.txt
    print("## robots.txt")
    robots = check_robots(url)
    print(f"exists: {'yes' if robots['exists'] else 'no'}")
    if robots["ai_bots"]:
        print(f"ai_bots_mentioned: {', '.join(robots['ai_bots'])}")
    else:
        print("ai_bots_mentioned: none")
    print()
    
    # Sitemap
    print("## Sitemap")
    has_sitemap = check_sitemap(url)
    print(f"sitemap_xml: {'yes' if has_sitemap else 'no'}")
    print()
    
    print("=== Audit Complete ===")


if __name__ == "__main__":
    main()
