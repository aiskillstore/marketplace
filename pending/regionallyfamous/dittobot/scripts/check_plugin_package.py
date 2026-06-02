#!/usr/bin/env python3
"""Check a generated Dittobot plugin package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from package_files import PACKAGE_FILES


SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin_dir", help="Generated plugin root.")
    parser.add_argument("--version", help="Expected plugin manifest version.")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    plugin = Path(args.plugin_dir).expanduser().resolve()
    manifest_path = plugin / ".codex-plugin" / "plugin.json"
    errors: list[str] = []

    if not manifest_path.exists():
        errors.append("missing .codex-plugin/plugin.json")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("name") != "dittobot":
            errors.append("plugin name must be dittobot")
        version = manifest.get("version")
        if not isinstance(version, str) or SEMVER_RE.fullmatch(version) is None:
            errors.append("plugin version must be strict semver")
        if args.version and version != args.version:
            errors.append(f"plugin version must be {args.version}")
        if manifest.get("skills") != "./skills/":
            errors.append("plugin skills path must be ./skills/")
        if manifest.get("license") != "GPL-2.0-or-later":
            errors.append("plugin license must be GPL-2.0-or-later")
        interface = manifest.get("interface", {})
        if interface.get("displayName") != "Dittobot":
            errors.append("plugin interface.displayName must be Dittobot")
        if "$dittobot" not in interface.get("defaultPrompt", ""):
            errors.append("plugin defaultPrompt must mention $dittobot")
        if interface.get("brandColor") != "#4F46E5":
            errors.append("plugin interface.brandColor must be #4F46E5")
        for field, expected in (
            ("composerIcon", "skills/dittobot/assets/icon-small.svg"),
            ("logo", "skills/dittobot/assets/icon-large.svg"),
        ):
            if interface.get(field) != expected:
                errors.append(f"plugin interface.{field} must be {expected}")
            elif not (plugin / expected).exists():
                errors.append(f"plugin interface.{field} points to a missing file")

    skill_root = plugin / "skills" / "dittobot"
    for rel in PACKAGE_FILES:
        source = repo / rel
        packaged = skill_root / rel
        if not packaged.exists():
            errors.append(f"missing packaged file: {rel}")
        elif digest(source) != digest(packaged):
            errors.append(f"packaged file differs: {rel}")

    if errors:
        print("Plugin package check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Plugin package check passed: {plugin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
