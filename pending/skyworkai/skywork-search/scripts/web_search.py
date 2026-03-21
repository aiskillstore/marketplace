#!/usr/bin/env python3
"""
web_search.py - Call Skywork web search API and print results.

Usage:
    python web_search.py "query1" ["query2" ...]

Accepts 1-3 search queries. Results are saved to individual text files
in a temporary directory and paths are printed to stdout.
"""

import argparse
import json
import os
import sys
import tempfile
import urllib.request

# Add scripts directory to path for skywork_auth import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skywork_auth import get_skywork_token

SKYWORK_GATEWAY_URL = os.environ.get("SKYWORK_GATEWAY_URL", "https://api-tools.skywork.ai/theme-gateway").rstrip("/")


def search(query: str) -> str:
    """Call web_search API and return formatted text of results."""
    url = f"{SKYWORK_GATEWAY_URL}/web_search"
    token = get_skywork_token()
    payload = {"query": query, "source_platform": "skyclaw" if os.environ.get("POD_TYPE", "") == "skyclaw" else ""}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "token": token,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"[ERROR] web_search failed for query '{query}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw

    results = data.get("search_res", [])
    if not results:
        return "(no results)"

    lines = []
    for i, item in enumerate(results, 1):
        content = (item.get("content") or "").strip()
        source_url = item.get("url", "")
        lines.append(f"[result-{i}] {source_url}\n{content}")
    return "\n\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search the web via Skywork API")
    parser.add_argument("queries", nargs="+", help="One or more search queries (max 3)")
    args = parser.parse_args()

    queries = args.queries[:3]
    out_dir = tempfile.mkdtemp(prefix="web_search_")

    for q in queries:
        print(f"[query] {q} ...", file=sys.stderr, flush=True)
        raw = search(q)
        out_path = os.path.join(out_dir, f"{q}_result.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"query: {q}\n\n{raw}")
        print(f"Saved: {out_path}", flush=True)


if __name__ == "__main__":
    main()
