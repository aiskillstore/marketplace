#!/usr/bin/env python3
"""Build a local Codex plugin package for Dittobot."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from package_files import PACKAGE_FILES


PLUGIN_NAME = "dittobot"
DEFAULT_VERSION = "0.2.0"
PLUGIN_DESCRIPTION = (
    "Voice-faithful rewrites for people who want AI to sound like them."
)
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def manifest(version: str) -> dict:
    return {
        "name": PLUGIN_NAME,
        "version": version,
        "description": PLUGIN_DESCRIPTION,
        "skills": "./skills/",
        "author": {
            "name": "Regionally Famous",
            "url": "https://github.com/RegionallyFamous",
        },
        "homepage": "https://github.com/RegionallyFamous/dittobot",
        "repository": "https://github.com/RegionallyFamous/dittobot",
        "license": "GPL-2.0-or-later",
        "keywords": ["writing", "editing", "voice", "rewrites", "skills"],
        "interface": {
            "displayName": "Dittobot",
            "shortDescription": "Voice-faithful rewrites without factual drift.",
            "longDescription": (
                "Dittobot rewrites messy drafts, notes, emails, and posts while "
                "preserving the user's voice, facts, stance, rhythm, humor, and "
                "constraints."
            ),
            "developerName": "Regionally Famous",
            "category": "Productivity",
            "capabilities": [
                "Voice-preserving rewrites",
                "Messy-note cleanup",
                "Fact and claim protection",
                "Local regression tooling",
            ],
            "websiteURL": "https://github.com/RegionallyFamous/dittobot",
            "privacyPolicyURL": "https://github.com/RegionallyFamous/dittobot/blob/main/SECURITY.md",
            "termsOfServiceURL": "https://github.com/RegionallyFamous/dittobot/blob/main/LICENSE",
            "brandColor": "#4F46E5",
            "composerIcon": "skills/dittobot/assets/icon-small.svg",
            "logo": "skills/dittobot/assets/icon-large.svg",
            "defaultPrompt": "Use $dittobot on this. Paste the messy draft, notes, or thought dump below.",
        },
    }


def copy_skill_package(repo: Path, plugin_root: Path) -> None:
    skill_root = plugin_root / "skills" / PLUGIN_NAME
    for rel in PACKAGE_FILES:
        source = repo / rel
        destination = skill_root / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def validate_plugin(plugin_root: Path, validator: str | None) -> int:
    if not validator:
        return 0
    validator_path = Path(validator).expanduser()
    if not validator_path.exists():
        print(f"Plugin validator not found, skipping: {validator_path}")
        return 0
    return subprocess.run(
        [sys.executable, str(validator_path), str(plugin_root)],
        check=False,
    ).returncode


def is_dittobot_plugin_dir(path: Path) -> bool:
    manifest_path = path / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        return False
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return payload.get("name") == PLUGIN_NAME


def assert_safe_output(repo: Path, output: Path, dist_root: Path) -> None:
    if output == dist_root:
        raise SystemExit("Refusing to replace the whole dist directory.")
    if output == repo or (
        repo in output.parents and output != dist_root and dist_root not in output.parents
    ):
        raise SystemExit("Refusing unsafe output directory inside the repo.")
    if output.exists() and dist_root not in output.parents and not is_dittobot_plugin_dir(output):
        raise SystemExit(
            "Refusing to replace an existing directory that is not a Dittobot plugin package."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="dist/dittobot-plugin",
        help="Directory to create or replace.",
    )
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Strict semver plugin version.")
    parser.add_argument(
        "--validator",
        default=str(
            Path.home()
            / ".codex"
            / "skills"
            / ".system"
            / "plugin-creator"
            / "scripts"
            / "validate_plugin.py"
        ),
        help="Optional plugin validator path. Pass an empty string to skip.",
    )
    parser.add_argument(
        "--require-validator",
        action="store_true",
        help="Fail if the plugin validator path is empty or missing.",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    output = (repo / args.output_dir).resolve()
    dist_root = (repo / "dist").resolve()
    if SEMVER_RE.fullmatch(args.version) is None:
        raise SystemExit(f"Plugin version must be strict semver: {args.version}")
    assert_safe_output(repo, output, dist_root)
    if args.require_validator:
        validator = Path(args.validator).expanduser() if args.validator else None
        if validator is None or not validator.exists():
            raise SystemExit("Plugin validator is required but was not found.")
    if output.exists():
        shutil.rmtree(output)
    (output / ".codex-plugin").mkdir(parents=True, exist_ok=True)
    (output / ".codex-plugin" / "plugin.json").write_text(
        json.dumps(manifest(args.version), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    copy_skill_package(repo, output)
    code = validate_plugin(output, args.validator or None)
    if code != 0:
        return code
    print(f"Built plugin package: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
