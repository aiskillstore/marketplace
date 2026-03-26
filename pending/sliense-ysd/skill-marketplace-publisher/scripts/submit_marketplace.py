#!/usr/bin/env python3
"""Submit a public skill repo URL to supported marketplace intake endpoints."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


USER_AGENT = "skill-marketplace-publisher/1.0"


def post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="ignore")
        return json.loads(body) if body else {}


def handle_skillstore(args: argparse.Namespace) -> int:
    payload = {"github_url": args.repo_url.rstrip("/")}
    if args.notes:
        payload["notes"] = args.notes

    try:
        response = post_json("https://skillstore.io/api/submit", payload)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        print(body or f"Skillstore submission failed with HTTP {exc.code}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Skillstore submission failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(response, indent=2, ensure_ascii=False))
    data = response.get("data", {})
    submission_id = data.get("submission_id")
    if submission_id:
        print(f"\nStatus URL: https://skillstore.io/submissions/{submission_id}")
    return 0 if response.get("success") else 1


def build_skillmap_message(args: argparse.Namespace) -> str:
    if args.message:
        return args.message

    skill_name = args.skill_name or "this skill"
    return (
        f"Hello SkillMap team, I would like to request marketplace consideration for "
        f"{skill_name}. Public repo: {args.repo_url.rstrip('/')}. "
        "It is a public-safe skill with no embedded API keys or private runtime secrets. "
        "Please let me know if you prefer a different listing intake path."
    )


def handle_skillmap_feedback(args: argparse.Namespace) -> int:
    payload = {"content": build_skillmap_message(args)}
    if args.email:
        payload["email"] = args.email

    try:
        response = post_json("https://skillmaps.net/v1/feedback", payload)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        print(body or f"SkillMap feedback submission failed with HTTP {exc.code}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"SkillMap feedback submission failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(response, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit a skill to marketplace intake endpoints.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    skillstore = subparsers.add_parser("skillstore", help="Submit a repo URL to Skillstore")
    skillstore.add_argument("--repo-url", required=True, help="Public GitHub repo or tree URL")
    skillstore.add_argument("--notes", help="Optional notes for the submission")
    skillstore.set_defaults(func=handle_skillstore)

    skillmap = subparsers.add_parser(
        "skillmap-feedback", help="Send a SkillMap listing request through feedback intake"
    )
    skillmap.add_argument("--repo-url", required=True, help="Public GitHub repo or tree URL")
    skillmap.add_argument("--skill-name", help="Human-readable skill name")
    skillmap.add_argument("--email", help="Optional reply email")
    skillmap.add_argument("--message", help="Explicit feedback body override")
    skillmap.set_defaults(func=handle_skillmap_feedback)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
