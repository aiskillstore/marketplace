#!/usr/bin/env python3
"""Wire CODEDNA.md into common coding-agent instruction files."""

import argparse
import json
import re
from pathlib import Path

START = "<!-- codedna:start -->"
END = "<!-- codedna:end -->"

PLAIN_BLOCK = """<!-- codedna:start -->
## Code and prose style

When writing or editing code or repository prose, match the conventions in [CODEDNA.md](CODEDNA.md): naming, formatting, comment and message voice, structure, and idioms, so new contributions match the existing work. Before finishing, self-check against the "AI tells" section of that file.
<!-- codedna:end -->
"""

CURSOR_FRONTMATTER = """---
description: Apply the codedna style profile for this repository.
alwaysApply: true
---

"""

CASCADE_FRONTMATTER = """---
trigger: always_on
---

"""

PLAIN_TARGETS = {
    "agents": Path("AGENTS.md"),
    "claude": Path("CLAUDE.md"),
    "gemini": Path("GEMINI.md"),
    "copilot": Path(".github/copilot-instructions.md"),
}

ALL_TARGETS = ["agents", "claude", "gemini", "copilot", "cursor", "cascade"]


def block_pattern(start_marker, end_marker):
    inner = "(?:(?!" + re.escape(start_marker) + ").)*?"
    return re.compile(re.escape(start_marker) + inner + re.escape(end_marker), re.S)


def replace_block(text, block=PLAIN_BLOCK, start_marker=START, end_marker=END):
    match = block_pattern(start_marker, end_marker).search(text)
    if match:
        head = text[: match.start()].rstrip()
        tail = text[match.end():].lstrip("\n")
        updated = (head + "\n\n" if head else "") + block.rstrip() + "\n"
        if tail:
            updated += "\n" + tail
        return updated.rstrip() + "\n"
    if text.strip():
        return text.rstrip() + "\n\n" + block
    return block


def write_target(path, body, prefix="", start_marker=START, end_marker=END):
    existed = path.exists()
    text = path.read_text(encoding="utf-8") if existed else ""
    if text.strip():
        updated = replace_block(text, body, start_marker, end_marker)
    else:
        updated = prefix + body
    if updated == text:
        return "unchanged"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated, encoding="utf-8")
    return "updated" if existed else "created"


def cascade_path(root):
    devin = root / ".devin/rules"
    windsurf = root / ".windsurf/rules"
    if windsurf.exists() and not devin.exists():
        return windsurf / "codedna.md"
    return devin / "codedna.md"


def target_path(root, target):
    if target in PLAIN_TARGETS:
        return root / PLAIN_TARGETS[target], ""
    if target == "cursor":
        return root / ".cursor/rules/codedna.mdc", CURSOR_FRONTMATTER
    if target == "cascade":
        return cascade_path(root), CASCADE_FRONTMATTER
    raise ValueError("unknown target: %s" % target)


def existing_targets(root):
    targets = ["agents"]
    for name, rel in PLAIN_TARGETS.items():
        if name != "agents" and (root / rel).exists():
            targets.append(name)
    if (root / ".cursor/rules").exists():
        targets.append("cursor")
    if (root / ".devin/rules").exists() or (root / ".windsurf/rules").exists():
        targets.append("cascade")
    return targets


def wire(root, targets=None, all_targets=False):
    root = Path(root)
    selected = ALL_TARGETS if all_targets else (targets or existing_targets(root))
    results = []
    for target in dict.fromkeys(selected):
        path, prefix = target_path(root, target)
        action = write_target(path, PLAIN_BLOCK, prefix, START, END)
        results.append({"target": target, "path": str(path), "action": action})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="Wire CODEDNA.md into agent instruction files.")
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--agent", action="append", choices=ALL_TARGETS, help="agent target to create or update")
    parser.add_argument("--all", action="store_true", help="create or update every supported target")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    results = wire(args.repo, targets=args.agent, all_targets=args.all)
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        for item in results:
            print("%s %s: %s" % (item["action"], item["target"], item["path"]))


if __name__ == "__main__":
    main()
