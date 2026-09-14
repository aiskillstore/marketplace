#!/usr/bin/env python3
"""Agent World — platform status check.

Usage:
  python3 check_status.py <url>          # check one URL (HTTP status)
  python3 check_status.py --all          # check all platforms in the registry
  python3 check_status.py --timeout 10   # override timeout seconds (default 15)

Exits 0 if all checked URLs returned HTTP < 400; exits 1 otherwise.
Network failures are reported distinctly (NET) and do NOT count as asset 404s —
per M4 ops rule: distinguish network faults from real outages.
"""

import argparse
import re
import sys
import urllib.request
import urllib.error

# Platform base URLs from references/platform-registry.md (kept in sync manually)
PLATFORMS = {
    "XiaLiao/ClawdChat": "https://clawdchat.cn",
    "InStreet": "https://instreet.coze.site",
    "agentid.sh": "https://agentid.sh",
    "SkillsMD": "https://skillsmd.dev",
    "theskills.directory": "https://theskills.directory",
    "KodaClaw Community": "https://community.ai-koda.com",
    "Coze Agent World": "https://world.coze.site",
    "Agentica": "https://agentica.wiki",
    "Moltbook": "https://moltbook.com",
    "PromptFrenzy": "https://promptfrenzy.com",
}


def check(url, timeout):
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "agent-world-status-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # network faults (timeout, DNS, SSL)
        return f"NET ({type(e).__name__})"


def main():
    ap = argparse.ArgumentParser(description="Check agent-platform HTTP health")
    ap.add_argument("url", nargs="?", help="single URL to check")
    ap.add_argument("--all", action="store_true", help="check all registry platforms")
    ap.add_argument("--timeout", type=int, default=15)
    args = ap.parse_args()

    targets = []
    if args.url:
        targets = [("custom", args.url)]
    elif args.all:
        targets = list(PLATFORMS.items())
    else:
        ap.print_help()
        return 2

    failures = 0
    for name, url in targets:
        code = check(url, args.timeout)
        if isinstance(code, str) or code >= 400:
            failures += 1
            print(f"  [FAIL] {name} — {url} → {code}")
        else:
            print(f"  [OK  ] {name} — {url} → HTTP {code}")

    print(f"RESULT: {len(targets) - failures}/{len(targets)} ok")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
