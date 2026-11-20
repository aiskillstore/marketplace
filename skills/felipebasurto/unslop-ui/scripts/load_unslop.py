#!/usr/bin/env python3
"""Print the /pstack:unslop rules that apply to interface copy.

Called through dynamic context injection when /unslop-ui is invoked, so it
must always exit 0: a non-zero exit would abort the whole skill.
"""
import glob
import os
import re

# Where Claude Code, Cursor, Codex and `npx skills` put plugin and skill
# folders. Earlier patterns win.
SEARCH = [
    "~/.claude/plugins/cache/*/pstack/*/skills/unslop/SKILL.md",
    "~/.cursor/plugins/**/pstack/**/skills/unslop/SKILL.md",
    "~/.claude/skills/unslop/SKILL.md",
    "~/.cursor/skills/unslop/SKILL.md",
    "~/.agents/skills/unslop/SKILL.md",
    "~/.codex/skills/unslop/SKILL.md",
    ".claude/skills/unslop/SKILL.md",
    ".cursor/skills/unslop/SKILL.md",
    ".agents/skills/unslop/SKILL.md",
]

# Rules written for documents and chat replies. They either cannot occur in
# interface strings or contradict them: 33 asks for full sentences where a
# label is a fragment by design, 19 undoes correct typographic quotes, and
# 18 is U11. Rules added upstream later pass through.
SKIP_RULES = {5, 14, 15, 16, 18, 19, 20, 22, 24, 26, 33}

RULES_HEADING = "## Patterns to detect and fix"
FALLBACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "unslop-fallback.md")
NOT_INSTALLED = (
    "/pstack:unslop is not installed (https://github.com/cursor/plugins/tree/main/pstack). "
    "These are the bundled rules, with the same numbers."
)


def newest(paths):
    # A version folder (0.15.20) beats a commit-hash folder; between hash
    # folders, whose names say nothing about age, the last one written wins.
    def key(path):
        version = re.search(r"/(\d+(?:\.\d+)+)/", path)
        return ([int(p) for p in version.group(1).split(".")] if version else [], os.path.getmtime(path))

    return max(paths, key=key)


def find_unslop():
    for pattern in SEARCH:
        paths = glob.glob(os.path.expanduser(pattern), recursive=True)
        if paths:
            return newest(paths)
    return None


def ui_rules(text):
    """The numbered rules minus SKIP_RULES, or None when the file has no rule list."""
    start = text.find(RULES_HEADING)
    if start == -1:
        return None
    body = text[start + len(RULES_HEADING):]
    next_section = re.search(r"^## ", body, re.M)
    if next_section:
        body = body[:next_section.start()]

    kept, heading, skipping, found = [], None, False, False
    for line in body.splitlines():
        rule = re.match(r"(\d+)\. ", line)
        if line.startswith("### "):
            heading, skipping = line, False
        elif rule:
            found = True
            skipping = int(rule.group(1)) in SKIP_RULES
            if not skipping:
                # A group heading prints only once one of its rules is kept.
                if heading:
                    kept += ["", heading, ""]
                    heading = None
                kept.append(line)
        elif not skipping and line.strip() and kept:
            kept.append(line)
    return "\n".join(kept).strip() if found else None


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def main():
    text = read(find_unslop() or "")
    if text:
        # An unslop whose layout changed is still better whole than replaced.
        print(ui_rules(text) or re.sub(r"\A---.*?---\s*", "", text, flags=re.S).strip())
        return
    print(NOT_INSTALLED)
    print()
    print((read(FALLBACK) or "No AI vocabulary, no em dashes, sentence-case text, plain words.").strip())


if __name__ == "__main__":
    main()
