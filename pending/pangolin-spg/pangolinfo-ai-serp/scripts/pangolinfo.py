#!/usr/bin/env python3
"""Pangolinfo AI SERP Client

Zero-dependency Python client for Pangolinfo's Google SERP APIs.
Supports:
- Google AI Mode search (multi-turn follow-ups)
- Google SERP with AI Overview extraction
- Optional screenshot capture

Environment:
    PANGOLIN_TOKEN    - Bearer token (skips login)
    PANGOLIN_EMAIL    - Account email (for login)
    PANGOLIN_PASSWORD - Account password (for login)

Migration note:
    Amazon scraping has moved to the separate skill “Pangolinfo Amazon Scraper”.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://scrapeapi.pangolinfo.com"
AUTH_ENDPOINT = f"{API_BASE}/api/v1/auth"
SCRAPE_V2_ENDPOINT = f"{API_BASE}/api/v2/scrape"
TOKEN_CACHE_PATH = Path.home() / ".pangolin_token"

EXIT_SUCCESS = 0
EXIT_API_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_NETWORK_ERROR = 3
EXIT_AUTH_ERROR = 4

AMAZON_MIGRATION_MESSAGE = {
    "success": False,
    "error": "Amazon mode has moved to a separate skill.",
    "action": "Install and use Pangolinfo Amazon Scraper",
}


def load_cached_token():
    if TOKEN_CACHE_PATH.exists():
        token = TOKEN_CACHE_PATH.read_text().strip()
        if token:
            return token
    return None


def save_cached_token(token):
    TOKEN_CACHE_PATH.write_text(token)
    TOKEN_CACHE_PATH.chmod(0o600)


def authenticate(email, password):
    body = json.dumps({"email": email, "password": password}).encode()
    req = urllib.request.Request(
        AUTH_ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Network error during auth: {e}"}), file=sys.stderr)
        sys.exit(EXIT_NETWORK_ERROR)

    if result.get("code") != 0:
        print(
            json.dumps(
                {
                    "error": "Authentication failed",
                    "code": result.get("code"),
                    "message": result.get("message"),
                }
            ),
            file=sys.stderr,
        )
        sys.exit(EXIT_AUTH_ERROR)

    token = result["data"]
    save_cached_token(token)
    return token


def get_token():
    token = os.environ.get("PANGOLIN_TOKEN")
    if token:
        return token

    token = load_cached_token()
    if token:
        return token

    email = os.environ.get("PANGOLIN_EMAIL")
    password = os.environ.get("PANGOLIN_PASSWORD")
    if not email or not password:
        print(
            json.dumps(
                {
                    "error": "No authentication credentials. Set PANGOLIN_TOKEN, or both PANGOLIN_EMAIL and PANGOLIN_PASSWORD.",
                }
            ),
            file=sys.stderr,
        )
        sys.exit(EXIT_AUTH_ERROR)

    return authenticate(email, password)


def refresh_token():
    email = os.environ.get("PANGOLIN_EMAIL")
    password = os.environ.get("PANGOLIN_PASSWORD")
    if not email or not password:
        print(
            json.dumps(
                {
                    "error": "Cannot refresh token: PANGOLIN_EMAIL and PANGOLIN_PASSWORD required.",
                }
            ),
            file=sys.stderr,
        )
        sys.exit(EXIT_AUTH_ERROR)
    return authenticate(email, password)


def build_google_body(query, mode, screenshot, follow_ups, num):
    if mode == "ai-mode":
        url = f"https://www.google.com/search?num={num}&udm=50&q={urllib.parse.quote_plus(query)}"
        body = {"url": url, "parserName": "googleAISearch"}
    else:
        url = f"https://www.google.com/search?num={num}&q={urllib.parse.quote_plus(query)}"
        body = {"url": url, "parserName": "googleSearch"}

    if screenshot:
        body["screenshot"] = True

    if follow_ups:
        body["param"] = follow_ups

    return body


def call_api(token, body, endpoint, max_retries=3):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0",
    }
    payload = json.dumps(body).encode()

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(endpoint, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
                continue
            print(json.dumps({"error": f"HTTP {e.code}: {error_body}"}), file=sys.stderr)
            sys.exit(EXIT_NETWORK_ERROR)
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
                continue
            print(json.dumps({"error": f"Network error: {e}"}), file=sys.stderr)
            sys.exit(EXIT_NETWORK_ERROR)

    return None


def handle_response(result, body, endpoint):
    if result.get("code") == 1004:
        new_token = refresh_token()
        return call_api(new_token, body, endpoint)
    return result


def extract_google_output(result):
    code = result.get("code")
    if code != 0:
        return {"success": False, "error_code": code, "message": result.get("message", "Unknown error")}

    data = result.get("data", {})
    output = {
        "success": True,
        "task_id": data.get("taskId"),
        "results_num": data.get("results_num", 0),
        "ai_overview_count": data.get("ai_overview", 0),
    }

    json_data = data.get("json", {})
    items = json_data.get("items", [])

    ai_overviews = []
    organic_results = []

    for item in items:
        item_type = item.get("type")
        if item_type == "ai_overview":
            overview = {"content": [], "references": []}
            for sub in item.get("items", []):
                if sub.get("type") == "ai_overview_elem":
                    overview["content"].extend(sub.get("content", []))
            for ref in item.get("references", []):
                overview["references"].append({"title": ref.get("title"), "url": ref.get("url"), "domain": ref.get("domain")})
            ai_overviews.append(overview)
        elif item_type == "organic":
            for sub in item.get("items", []):
                organic_results.append({"title": sub.get("title"), "url": sub.get("url"), "text": sub.get("text")})

    if ai_overviews:
        output["ai_overview"] = ai_overviews
    if organic_results:
        output["organic_results"] = organic_results

    screenshot_url = data.get("screenshot")
    if screenshot_url:
        output["screenshot"] = screenshot_url

    return output


def main():
    parser = argparse.ArgumentParser(description="Pangolinfo AI SERP Client")
    parser.add_argument("--q", dest="query", help="Search query")
    parser.add_argument(
        "--mode",
        choices=["ai-mode", "serp", "amazon"],
        default="ai-mode",
        help="API mode: ai-mode (default) | serp | amazon (migrated)",
    )
    parser.add_argument("--screenshot", action="store_true", help="Capture page screenshot (Google only)")
    parser.add_argument("--follow-up", action="append", dest="follow_ups", help="Follow-up question (repeatable, ai-mode only)")
    parser.add_argument("--num", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--auth-only", action="store_true", help="Only authenticate and print token info")
    parser.add_argument("--raw", action="store_true", help="Output raw API response instead of extracted data")

    args = parser.parse_args()

    if args.mode == "amazon":
        # Compatibility stub: keep old flag from combined skill but guide users.
        print(json.dumps(AMAZON_MIGRATION_MESSAGE, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(EXIT_USAGE_ERROR)

    if not args.query and not args.auth_only:
        parser.error("--q is required unless using --auth-only")

    if args.follow_ups and args.mode != "ai-mode":
        parser.error("--follow-up is only supported in ai-mode")

    token = get_token()

    if args.auth_only:
        print(
            json.dumps(
                {
                    "success": True,
                    "message": "Authentication successful",
                    "token_preview": f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "***",
                },
                indent=2,
            )
        )
        sys.exit(EXIT_SUCCESS)

    body = build_google_body(args.query, args.mode, args.screenshot, args.follow_ups, args.num)

    result = call_api(token, body, SCRAPE_V2_ENDPOINT)
    if result is None:
        print(json.dumps({"error": "API call failed after retries"}), file=sys.stderr)
        sys.exit(EXIT_NETWORK_ERROR)

    result = handle_response(result, body, SCRAPE_V2_ENDPOINT)

    if args.raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        output = extract_google_output(result)
        print(json.dumps(output, indent=2, ensure_ascii=False))

    if result.get("code") != 0:
        sys.exit(EXIT_API_ERROR)

    sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    main()
