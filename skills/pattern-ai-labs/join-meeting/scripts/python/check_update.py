#!/usr/bin/env python3
"""Check if a newer version of the AgentCall skill is available on GitHub.

Optional. Not required for normal skill operation. Primarily useful for users
who installed the skill directly from GitHub (marketplace users get updates
via /plugin update).

Reads current version from ../../.claude-plugin/plugin.json, fetches the latest
version from GitHub's main branch, compares, and prints JSON to stdout.
Caches results for 7 days at ~/.agentcall/update-check.json.

Always exits 0 (never breaks the caller).
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_URL = "https://github.com/pattern-ai-labs/agentcall"
GITHUB_PLUGIN_URL = "https://raw.githubusercontent.com/pattern-ai-labs/agentcall/main/.claude-plugin/plugin.json"
CACHE_TTL_DAYS = 7
CACHE_VERSION = 1
FETCH_TIMEOUT = 5  # seconds

UPDATE_COMMANDS = {
    "marketplace": "/plugin marketplace update pattern-ai-labs-agentcall && /plugin update join-meeting",
    "git": "git pull",
    "zip": f"Download the latest release from {REPO_URL}",
}


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def plugin_json_path() -> Path:
    # scripts/python/ -> skill root -> .claude-plugin/plugin.json
    return script_dir().parent.parent / ".claude-plugin" / "plugin.json"


def cache_path() -> Path:
    return Path.home() / ".agentcall" / "update-check.json"


def read_current_version() -> str:
    try:
        with open(plugin_json_path(), "r") as f:
            data = json.load(f)
        return str(data.get("version", "unknown"))
    except Exception:
        return "unknown"


def parse_version(v: str):
    """Return tuple of ints for X.Y.Z, or None if unparseable."""
    try:
        parts = v.split(".")
        return tuple(int(p) for p in parts[:3])
    except Exception:
        return None


def compare_versions(current: str, latest: str) -> bool:
    """True if latest > current."""
    c = parse_version(current)
    l = parse_version(latest)
    if c is None or l is None:
        return False
    return l > c


def load_cache() -> dict:
    try:
        with open(cache_path(), "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(data: dict) -> None:
    try:
        cache_path().parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path(), "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def cache_is_fresh(cache: dict) -> bool:
    last = cache.get("last_checked")
    if not last:
        return False
    try:
        last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
        return datetime.now(timezone.utc) - last_dt < timedelta(days=CACHE_TTL_DAYS)
    except Exception:
        return False


def fetch_latest_version() -> str:
    req = urllib.request.Request(
        GITHUB_PLUGIN_URL,
        headers={"Accept": "application/json", "User-Agent": "agentcall-skill-update-check"},
    )
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
        data = json.load(resp)
    return str(data.get("version", "unknown"))


def build_result(current: str, latest: str) -> dict:
    return {
        "current_version": current,
        "latest_version": latest,
        "update_available": compare_versions(current, latest),
        "repo_url": REPO_URL,
        "update_commands": UPDATE_COMMANDS,
        "last_checked": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "cached": False,
    }


def main() -> int:
    current = read_current_version()
    cache = load_cache()

    # Serve cached result if fresh.
    if cache_is_fresh(cache):
        result = cache.get("cached_result", {})
        if result:
            result["cached"] = True
            print(json.dumps(result))
            return 0

    # Fetch latest from GitHub.
    try:
        latest = fetch_latest_version()
        result = build_result(current, latest)
        save_cache({
            "cache_version": CACHE_VERSION,
            "last_checked": result["last_checked"],
            "latest_version": latest,
            "cached_result": result,
        })
        print(json.dumps(result))
        return 0
    except Exception as e:
        # Fetch failed. Return stale cache if present, else error response.
        stale = cache.get("cached_result")
        if stale:
            stale["stale"] = True
            stale["cached"] = True
            print(json.dumps(stale))
            return 0
        print(json.dumps({
            "current_version": current,
            "latest_version": "unknown",
            "update_available": False,
            "repo_url": REPO_URL,
            "error": "network_failure",
            "error_detail": str(e),
        }))
        return 0


if __name__ == "__main__":
    sys.exit(main())
