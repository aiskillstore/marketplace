#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Find 1Password credential by URL and optionally filter by username.

Usage:
    ./find_credential.py <url> [username]

Examples:
    ./find_credential.py twitter.com
    ./find_credential.py twitter.com clementwalter
    ./find_credential.py github.com myuser
"""

import json
import subprocess
import sys

DOMAIN_ALIASES = {
    "x.com": ["x.com", "twitter.com"],
    "twitter.com": ["x.com", "twitter.com"],
}


def run_op(args: list[str]) -> tuple[bool, str]:
    """Execute op CLI command."""
    try:
        result = subprocess.run(
            ["op", *args], capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return False, result.stderr.strip() or "Unknown error"
        return True, result.stdout
    except FileNotFoundError:
        return False, "op CLI not installed"
    except subprocess.TimeoutExpired:
        return False, "Timed out - run 'op signin'"


def normalize_domain(url: str) -> str:
    return url.lower().replace("https://", "").replace("http://", "").split("/")[0]


def extract_creds(item: dict) -> dict:
    username, password = None, None
    for f in item.get("fields", []):
        fid, purpose, val = f.get("id", ""), f.get("purpose", ""), f.get("value")
        if purpose == "USERNAME" or fid == "username":
            username = val
        elif purpose == "PASSWORD" or fid == "password":
            password = val
    return {"username": username, "password": password}


def find_items_by_url(url: str) -> list[dict]:
    success, output = run_op(["item", "list", "--format", "json"])
    if not success:
        return []

    try:
        items = json.loads(output)
    except json.JSONDecodeError:
        return []

    domain = normalize_domain(url)
    search_domains = DOMAIN_ALIASES.get(domain, [domain])

    matching = []
    for item in items:
        for url_entry in item.get("urls", []):
            href = url_entry.get("href", "").lower()
            if any(sd in href for sd in search_domains):
                matching.append(item)
                break
    return matching


def get_item_details(item_id: str) -> dict | None:
    success, output = run_op(["item", "get", item_id, "--format", "json"])
    if not success:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: find_credential.py <url> [username]", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    username_filter = sys.argv[2].lower() if len(sys.argv) > 2 else None

    items = find_items_by_url(url)
    if not items:
        print(json.dumps({"error": f"No items found for URL: {url}"}))
        sys.exit(1)

    candidates = []
    for item in items:
        details = get_item_details(item["id"])
        if not details:
            continue
        creds = extract_creds(details)
        item_username = (creds.get("username") or "").lower()

        if username_filter and username_filter == item_username:
            print(
                json.dumps(
                    {"item_name": item.get("title"), "item_id": item["id"], **creds}
                )
            )
            sys.exit(0)

        candidates.append(
            {"item_name": item.get("title"), "item_id": item["id"], **creds}
        )

    if not candidates:
        print(json.dumps({"error": "No matching credentials found"}))
        sys.exit(1)

    if len(candidates) == 1:
        print(json.dumps(candidates[0]))
    else:
        print(
            json.dumps(
                {
                    "message": f"Multiple items found for {url}. Specify username to filter.",
                    "items": [
                        {"item_name": c["item_name"], "username": c["username"]}
                        for c in candidates
                    ],
                }
            )
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
