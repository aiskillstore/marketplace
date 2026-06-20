#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint a skill package for basic structure issues.")
    parser.add_argument("skill_dir")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    failures = []
    warnings = []

    if root.name.lower() != root.name:
        warnings.append("Skill directory is not lowercase.")
    if " " in root.name:
        failures.append("Skill directory contains spaces.")

    skill_md = root / "SKILL.md"
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        lines = text.splitlines()
        if len(lines) > 300:
            warnings.append("SKILL.md is getting long; consider moving detail into references/.")
        for dirname in ("references", "scripts", "evals", "assets"):
            path = root / dirname
            if path.exists() and not any(child.is_file() for child in path.rglob("*")):
                warnings.append(f"{dirname}/ exists but is empty.")
            if path.exists() and any(child.is_file() for child in path.rglob("*")) and dirname not in text and dirname.capitalize() not in text:
                warnings.append(f"{dirname}/ contains files but is not referenced in SKILL.md.")

    print(json.dumps({"ok": not failures, "failures": failures, "warnings": warnings}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
