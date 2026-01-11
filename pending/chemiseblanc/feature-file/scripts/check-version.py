#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
Check git history to see if feature versions need bumping.

Compares when each feature's section was last modified vs when version was last set.

Usage:
    ./check-version.py [--format plain|markdown|json]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml


FEATURES_FILE = "features.yml"


def load_features(path: Path) -> list[dict]:
    """Load all feature documents from features.yml."""
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        docs = list(yaml.safe_load_all(f))

    return [doc for doc in docs if doc is not None]


def is_git_repo() -> bool:
    """Check if we're in a git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"], capture_output=True, text=True
    )
    return result.returncode == 0


def get_file_in_git() -> bool:
    """Check if features.yml is tracked by git."""
    result = subprocess.run(
        ["git", "ls-files", FEATURES_FILE], capture_output=True, text=True
    )
    return bool(result.stdout.strip())


def get_feature_line_ranges(path: Path) -> list[tuple[str, int, int]]:
    """
    Parse features.yml and return (feature_name, start_line, end_line) for each feature.
    Lines are 1-indexed to match git blame output.
    """
    with open(path) as f:
        content = f.read()

    lines = content.split("\n")
    features = []
    current_feature = None
    start_line = 1

    for i, line in enumerate(lines, start=1):
        # Check for document separator or feature field
        if line.strip() == "---" or (
            line.startswith("feature:") and current_feature is not None
        ):
            if current_feature is not None:
                features.append((current_feature, start_line, i - 1))
            if line.strip() == "---":
                start_line = i + 1
                current_feature = None
            else:
                start_line = i
                # Extract feature name
                match = re.match(r'feature:\s*["\']?(.+?)["\']?\s*$', line)
                if match:
                    current_feature = match.group(1).strip()
                else:
                    current_feature = line.split(":", 1)[1].strip().strip("\"'")
        elif line.startswith("feature:") and current_feature is None:
            # Extract feature name
            match = re.match(r'feature:\s*["\']?(.+?)["\']?\s*$', line)
            if match:
                current_feature = match.group(1).strip()
            else:
                # Handle multiline feature names
                current_feature = line.split(":", 1)[1].strip().strip("\"'|")
                if not current_feature:
                    # Multiline - look at next non-empty line
                    for j in range(i, min(i + 3, len(lines) + 1)):
                        if (
                            j < len(lines)
                            and lines[j - 1].strip()
                            and not lines[j - 1].startswith(" ")
                        ):
                            break
                        if j < len(lines) and lines[j - 1].strip():
                            current_feature = lines[j - 1].strip()
                            break

    # Don't forget the last feature
    if current_feature is not None:
        features.append((current_feature, start_line, len(lines)))

    return features


def get_last_modification(start_line: int, end_line: int) -> tuple[str, str] | None:
    """
    Get the most recent commit that modified lines in the given range.
    Returns (commit_hash, date) or None.
    """
    result = subprocess.run(
        [
            "git",
            "blame",
            "-l",
            f"-L{start_line},{end_line}",
            "--date=short",
            FEATURES_FILE,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return None

    # Parse blame output to collect unique commits
    commits = set()
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        # Format: ^?hash (author date line_no) content
        # Note: ^ prefix appears on boundary commits
        match = re.match(r"^\^?([a-f0-9]+)", line)
        if match:
            commits.add(match.group(1))

    if not commits:
        return None

    # Use git log to find most recent commit among those that touched these lines
    # This properly handles commit ordering when dates are the same
    commit_list = list(commits)
    result = subprocess.run(
        ["git", "log", "--format=%H %cs", "-1", "--"] + commit_list,
        capture_output=True,
        text=True,
    )

    # Fallback: use git rev-list to find most recent among our commits
    result = subprocess.run(
        ["git", "rev-list", "--no-walk", "--date-order"] + commit_list,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 or not result.stdout.strip():
        return None

    # First line is most recent commit
    most_recent_hash = result.stdout.strip().split("\n")[0][:8]

    # Get its date
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", most_recent_hash],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return None

    date = result.stdout.strip()
    return (most_recent_hash, date)


def get_version_last_set(start_line: int, end_line: int) -> tuple[str, str, int] | None:
    """
    Find when the version field was last changed for this feature.
    Returns (commit_hash, date, version) or None.
    """
    # First, find the version line within this range
    with open(FEATURES_FILE) as f:
        lines = f.readlines()

    version_line = None
    version_value = None
    for i in range(start_line - 1, min(end_line, len(lines))):
        if lines[i].startswith("version:"):
            version_line = i + 1  # 1-indexed
            match = re.match(r"version:\s*(\d+)", lines[i])
            if match:
                version_value = int(match.group(1))
            break

    if version_line is None:
        return None

    # Get blame for just the version line
    result = subprocess.run(
        [
            "git",
            "blame",
            "-l",
            f"-L{version_line},{version_line}",
            "--date=short",
            FEATURES_FILE,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return None

    line = result.stdout.strip()
    # Note: ^ prefix appears on boundary commits
    match = re.match(r"^\^?([a-f0-9]+)\s+.*?(\d{4}-\d{2}-\d{2})", line)
    if match:
        return (match.group(1)[:8], match.group(2), version_value or 1)

    return None


def format_plain(results: list[dict]) -> str:
    """Format output as plain text."""
    lines = []

    for r in results:
        lines.append(f"{r['name']} (v{r['version']})")
        if r.get("error"):
            lines.append(f"  {r['error']}")
        else:
            lines.append(
                f"  Last modified: {r['last_modified_date']} (commit {r['last_modified_commit']})"
            )
            lines.append(
                f"  Version set:   {r['version_set_date']} (commit {r['version_set_commit']})"
            )
            lines.append(f"  Recommendation: {r['recommendation']}")
        lines.append("")

    return "\n".join(lines).rstrip()


def format_markdown(results: list[dict]) -> str:
    """Format output as markdown."""
    lines = []
    lines.append("# Version Check")

    for r in results:
        lines.append("")
        lines.append(f"## {r['name']} (v{r['version']})")
        lines.append("")
        if r.get("error"):
            lines.append(f"- {r['error']}")
        else:
            lines.append(
                f"- **Last modified**: {r['last_modified_date']} (commit `{r['last_modified_commit']}`)"
            )
            lines.append(
                f"- **Version set**: {r['version_set_date']} (commit `{r['version_set_commit']}`)"
            )
            rec = r["recommendation"]
            if "BUMP" in rec:
                lines.append(f"- **Recommendation**: {rec}")
            else:
                lines.append(f"- Recommendation: {rec}")

    return "\n".join(lines)


def format_json(results: list[dict]) -> str:
    """Format output as JSON."""
    return json.dumps({"features": results}, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Check if feature versions need bumping"
    )
    parser.add_argument(
        "--format",
        choices=["plain", "markdown", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    args = parser.parse_args()

    path = Path(FEATURES_FILE)
    features = load_features(path)

    if not features:
        print("No features found in features.yml", file=sys.stderr)
        sys.exit(1)

    if not is_git_repo():
        print("Error: Not a git repository", file=sys.stderr)
        sys.exit(1)

    if not get_file_in_git():
        print(f"Error: {FEATURES_FILE} is not tracked by git", file=sys.stderr)
        sys.exit(1)

    # Get line ranges for each feature
    line_ranges = get_feature_line_ranges(path)

    results = []
    for feature_name, start_line, end_line in line_ranges:
        version = 1
        # Find matching feature to get version
        for f in features:
            fname = f.get("feature", "")
            if fname.strip().startswith(feature_name[:20]) or feature_name.startswith(
                fname[:20]
            ):
                version = f.get("version", 1)
                break

        result = {
            "name": feature_name[:50] + ("..." if len(feature_name) > 50 else ""),
            "version": version,
        }

        last_mod = get_last_modification(start_line, end_line)
        version_info = get_version_last_set(start_line, end_line)

        if last_mod is None:
            result["error"] = (
                "Could not determine last modification (uncommitted changes?)"
            )
        elif version_info is None:
            result["error"] = "Could not determine when version was set"
        else:
            result["last_modified_commit"] = last_mod[0]
            result["last_modified_date"] = last_mod[1]
            result["version_set_commit"] = version_info[0]
            result["version_set_date"] = version_info[1]

            if last_mod[1] > version_info[1]:
                result["recommendation"] = (
                    "BUMP VERSION - feature modified since version was set"
                )
                result["needs_bump"] = True
            elif last_mod[0] != version_info[0] and last_mod[1] == version_info[1]:
                result["recommendation"] = (
                    "BUMP VERSION - feature modified since version was set"
                )
                result["needs_bump"] = True
            else:
                result["recommendation"] = "Up to date"
                result["needs_bump"] = False

        results.append(result)

    if args.format == "plain":
        print(format_plain(results))
    elif args.format == "markdown":
        print(format_markdown(results))
    else:
        print(format_json(results))


if __name__ == "__main__":
    main()
