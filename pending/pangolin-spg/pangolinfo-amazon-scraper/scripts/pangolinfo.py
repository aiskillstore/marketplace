#!/usr/bin/env python3
"""Pangolinfo Amazon Scraper Client

Zero-dependency Python client for Pangolinfo's Amazon scraping API.
Supports multiple parser types (product detail, keyword, category, best sellers, etc.).

Environment:
    PANGOLIN_TOKEN    - Bearer token (skips login)
    PANGOLIN_EMAIL    - Account email (for login)
    PANGOLIN_PASSWORD - Account password (for login)
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
SCRAPE_V1_ENDPOINT = f"{API_BASE}/api/v1/scrape"
TOKEN_CACHE_PATH = Path.home() / ".pangolin_token"

EXIT_SUCCESS = 0
EXIT_API_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_NETWORK_ERROR = 3
EXIT_AUTH_ERROR = 4

AMAZON_PARSERS = [
    "amzProductDetail",
    "amzKeyword",
    "amzProductOfCategory",
    "amzProductOfSeller",
    "amzBestSellers",
    "amzNewReleases",
    "amzFollowSeller",
]


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


def build_amazon_body(url, query, parser, zipcode, fmt):
    if not url and query:
        url = f"https://www.amazon.com/s?k={urllib.parse.quote_plus(query)}"
        if parser == "amzProductDetail":
            parser = "amzKeyword"

    if not url:
        print(json.dumps({"error": "Amazon mode requires --url or --q"}), file=sys.stderr)
        sys.exit(EXIT_USAGE_ERROR)

    return {
        "url": url,
        "format": fmt,
        "parserName": parser,
        "bizContext": {"zipcode": zipcode},
    }


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
        token = get_token() if new_token is None else new_token
        return call_api(token, body, endpoint)
    return result


def extract_amazon_output(result):
    code = result.get("code")
    if code != 0:
        return {"success": False, "error_code": code, "message": result.get("message", "Unknown error")}

    data = result.get("data", {})
    output = {"success": True, "task_id": data.get("taskId"), "url": data.get("url")}

    json_data = data.get("json")
    if isinstance(json_data, list):
        output["products"] = json_data
        output["results_count"] = len(json_data)
    elif isinstance(json_data, dict):
        output["product"] = json_data
        output["results_count"] = 1
    else:
        output["data"] = json_data
        output["results_count"] = 0

    return output


def main():
    parser = argparse.ArgumentParser(description="Pangolinfo Amazon Scraper Client")
    parser.add_argument("--q", dest="query", help="Keyword query (builds an Amazon search URL)")
    parser.add_argument("--url", dest="target_url", help="Target Amazon URL")
    parser.add_argument(
        "--parser",
        choices=AMAZON_PARSERS,
        default="amzProductDetail",
        help="Amazon parser name (default: amzProductDetail)",
    )
    parser.add_argument("--zipcode", default="10041", help="Amazon zipcode for localized pricing (default: 10041)")
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=["json", "rawHtml", "markdown"],
        default="json",
        help="Amazon response format (default: json)",
    )
    parser.add_argument("--auth-only", action="store_true", help="Only authenticate and print token info")
    parser.add_argument("--raw", action="store_true", help="Output raw API response instead of extracted data")

    args = parser.parse_args()

    if not args.query and not args.target_url and not args.auth_only:
        parser.error("--q or --url is required unless using --auth-only")

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

    body = build_amazon_body(args.target_url, args.query, args.parser, args.zipcode, args.fmt)

    result = call_api(token, body, SCRAPE_V1_ENDPOINT)
    if result is None:
        print(json.dumps({"error": "API call failed after retries"}), file=sys.stderr)
        sys.exit(EXIT_NETWORK_ERROR)

    result = handle_response(result, body, SCRAPE_V1_ENDPOINT)

    if args.raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        output = extract_amazon_output(result)
        print(json.dumps(output, indent=2, ensure_ascii=False))

    if result.get("code") != 0:
        sys.exit(EXIT_API_ERROR)

    sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    main()
