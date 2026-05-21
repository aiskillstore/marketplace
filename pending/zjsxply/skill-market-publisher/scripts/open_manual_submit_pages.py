#!/usr/bin/env python3
"""Open manual-web submission pages and print a short operator checklist."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from skill_market_publish import MARKETS, clean_repo_url, github_skill_urls, github_tree_url, load_skill  # type: ignore


MANUAL_MARKETS = [
    "skillnet-openkg",
    "skillsdirectory-com",
    "skillsdir-dev",
    "skillscatalog-ai",
    "mdskills-ai",
    "skillery-dev",
    "skillszoo",
    "skillhub-club",
    "skillhq-dev",
    "agentskillsrepo",
]

CHECKLISTS = {
    "skillnet-openkg": [
        "Open Contribute or the current submit entry on the site.",
        "Choose Submit via URL if it is available.",
        "Paste the skill folder URL or the repository URL the form accepts.",
        "Submit and keep the resulting queue, search, or detail URL if shown.",
    ],
    "skillsdirectory-com": [
        "Sign in with GitHub.",
        "Open the submit form.",
        "Paste the public GitHub repository URL.",
        "Submit and keep the resulting detail or registry URL if shown.",
    ],
    "skillsdir-dev": [
        "Open the add page.",
        "Check whether the GitHub issue path or page flow currently works.",
        "Paste the repo URL or follow the current site instructions.",
        "Capture the resulting issue URL or listing URL if the site creates one.",
    ],
    "skillscatalog-ai": [
        "Open the submit page.",
        "Try the anonymous GitHub submission flow the page currently exposes.",
        "Paste the public repository URL or folder URL if the form accepts it.",
        "Keep the resulting detail or search URL if the site returns one.",
    ],
    "mdskills-ai": [
        "Sign in.",
        "Open the submit page.",
        "Paste the GitHub-backed skill repository details the site asks for.",
        "Submit and capture the resulting listing or queue URL if shown.",
    ],
    "skillery-dev": [
        "Sign in.",
        "Open the submit page.",
        "Choose the GitHub-hosted skill flow if offered.",
        "Submit and capture the resulting listing URL if the site creates one.",
    ],
    "skillszoo": [
        "Sign in.",
        "Open the submit page.",
        "Paste the GitHub repository URL and complete the review metadata.",
        "Submit and keep the My Submissions or listing URL.",
    ],
    "skillhub-club": [
        "Sign in.",
        "Open the app skills page.",
        "Choose SKILL.md or GitHub-backed publish if the UI offers both.",
        "Submit and keep the public skill URL if one appears.",
    ],
    "skillhq-dev": [
        "Open the seller onboarding page.",
        "Complete seller setup, payout, and compliance steps.",
        "Stop here if the site does not yet grant publish access.",
        "Tell me when seller onboarding is complete.",
    ],
    "agentskillsrepo": [
        "Open the submit page.",
        "Paste the public GitHub repository URL that contains SKILL.md.",
        "Submit the form.",
        "Keep the resulting detail page or search URL if the site exposes one.",
    ],
}


def open_url(url: str) -> None:
    subprocess.run(["open", url], check=False)


def print_skill_links(skill_paths: list[str], repo_url: str | None, git_ref: str | None) -> None:
    if not skill_paths:
        return

    normalized_repo_url = clean_repo_url(repo_url)
    print("## Submission Assets")
    if normalized_repo_url:
        print(f"- Repository URL: {normalized_repo_url}")
    if git_ref:
        print(f"- Git Ref: {git_ref}")
    for skill_target in skill_paths:
        skill = load_skill(skill_target)
        urls = github_skill_urls(normalized_repo_url, git_ref, skill.relative_skill_dir)
        skill_dir_url = github_tree_url(normalized_repo_url, git_ref, skill.relative_skill_dir) or normalized_repo_url
        print(f"### {skill.title} ({skill.name})")
        print(f"- Local path: {skill.path}")
        print(f"- Suggested folder URL: {skill_dir_url or '(set --repo-url and --git-ref first)'}")
        print(f"- SKILL.md URL: {urls['skill_url'] or '(set --repo-url and --git-ref first)'}")
        print(f"- Raw SKILL.md URL: {urls['raw_skill_url'] or '(set --repo-url and --git-ref first)'}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Open manual submission pages and print a short checklist.")
    parser.add_argument(
        "markets",
        nargs="*",
        help="Specific market keys to open. Default: all supported manual-web targets that currently need user action.",
    )
    parser.add_argument(
        "--skill-path",
        action="append",
        default=[],
        help="Skill directory or SKILL.md path to print exact GitHub submission URLs for. Repeat for multiple skills.",
    )
    parser.add_argument("--repo-url", help="Public GitHub repository URL used for submission.")
    parser.add_argument("--git-ref", help="Git ref used to build folder and SKILL.md URLs.")
    args = parser.parse_args()

    markets = args.markets or MANUAL_MARKETS
    print_skill_links(args.skill_path, args.repo_url, args.git_ref)
    for market in markets:
        if market not in MARKETS:
            print(f"[SKIP] Unknown market: {market}")
            continue
        submit_url = MARKETS[market].get("submit_url") or MARKETS[market].get("source_url")
        if not submit_url:
            print(f"[SKIP] No URL recorded for {market}")
            continue
        open_url(submit_url)
        print(f"## {MARKETS[market]['title']} ({market})")
        print(f"- URL: {submit_url}")
        for item in CHECKLISTS.get(market, []):
            print(f"- {item}")
        print()


if __name__ == "__main__":
    main()
