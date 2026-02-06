#!/usr/bin/env python3
"""
DataForSEO API wrapper
"""
import urllib.request
import urllib.parse
import json
import base64
import sys
from credential import get_dataforseo_credentials

API_BASE = "https://api.dataforseo.com/v3"


def api_post(endpoint: str, data: list) -> dict:
    """Make POST request to DataForSEO API"""
    login, password = get_dataforseo_credentials()
    if not login or not password:
        print("error: DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD not set", file=sys.stderr)
        print("Run: export DATAFORSEO_LOGIN=your_login", file=sys.stderr)
        print("     export DATAFORSEO_PASSWORD=your_password", file=sys.stderr)
        sys.exit(1)
    
    url = f"{API_BASE}/{endpoint}"
    auth = base64.b64encode(f"{login}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"error: HTTP {e.code} - {error_body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


def format_count(n) -> str:
    """Format numbers (1234567 -> 1.2M)"""
    if n is None:
        return "0"
    n = int(n)
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def get_result(response: dict) -> list:
    """Extract result from API response"""
    if not response.get("tasks"):
        return []
    task = response["tasks"][0]
    if task.get("status_code") != 20000:
        print(f"error: {task.get('status_message', 'Unknown error')}", file=sys.stderr)
        return []
    return task.get("result", [])


def print_keywords_list(keywords: list):
    """Print list of keywords"""
    print(f"keywords[{len(keywords)}]{{keyword,volume,difficulty}}:")
    for kw in keywords:
        keyword = kw.get("keyword", "N/A")
        volume = format_count(kw.get("search_volume"))
        difficulty = kw.get("keyword_difficulty", "N/A")
        print(f"  {keyword},{volume},{difficulty}")


def print_serp_list(items: list):
    """Print SERP results"""
    organic = [i for i in items if i.get("type") == "organic"]
    print(f"serp[{len(organic)}]{{position,title,domain}}:")
    for item in organic[:20]:
        pos = item.get("rank_absolute", "N/A")
        title = (item.get("title") or "")[:50]
        domain = item.get("domain", "N/A")
        print(f"  {pos},{title},{domain}")


def print_backlinks_list(items: list):
    """Print backlinks"""
    print(f"backlinks[{len(items)}]{{from,to,rank,dofollow}}:")
    for item in items:
        url_from = (item.get("url_from") or "")[:50]
        url_to = (item.get("url_to") or "")[:30]
        rank = item.get("rank", "N/A")
        dofollow = item.get("dofollow", False)
        print(f"  {url_from},{url_to},{rank},{dofollow}")
