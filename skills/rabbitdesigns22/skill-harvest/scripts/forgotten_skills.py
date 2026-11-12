"""Find skills that were INSTALLED, matched what the human asked, and were NEVER loaded.

This is a prefilter, not a verdict: it matches the human's words against each
installed skill's trigger phrases (quoted phrases in its description, plus its
name). An agent must read the hits and drop the false ones before telling anyone.

Usage:
  python forgotten_skills.py DIGEST_DIR [--skills ~/.claude/skills] [--min-hits 2]
DIGEST_DIR is the output of read_sessions.py. Prints a Markdown table per session.
"""
import re, sys
from pathlib import Path

STOP = {"use", "when", "the", "and", "for", "with", "this", "that", "user", "skill", "asks", "wants", "also"}


def arg(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def triggers(skill_md):
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    front = m.group(1) if m else text[:1500]
    name = skill_md.parent.name
    phrases = {p.strip().lower() for p in re.findall(r"[\"'“‘]([^\"'”’]{4,60})[\"'”’]", front)}
    # Single words ("video", "ads") match everything and prove nothing: keep 2-7 word phrases.
    phrases = {p for p in phrases if p not in STOP and 2 <= len(p.split()) <= 7}
    if "-" in name:
        phrases.add(name.replace("-", " ").lower())
    return name, phrases


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    digests = Path(sys.argv[1])
    root = Path(arg("--skills", str(Path.home() / ".claude" / "skills"))).expanduser()
    min_hits = arg("--min-hits", 2)
    catalog = [triggers(p) for p in root.glob("*/SKILL.md")]
    for md in sorted(digests.glob("*.md")):
        body = md.read_text(encoding="utf-8", errors="replace")
        loaded = re.search(r"^skills loaded: (.*)$", body, re.M)
        loaded = {s.split("(")[0].split(":")[-1].strip() for s in (loaded.group(1).split(",") if loaded else [])}
        asks = body.split("## What the human asked", 1)[-1].lower()
        rows = []
        for name, phrases in catalog:
            if name in loaded:
                continue
            hits = [p for p in phrases if re.search(r"\b" + re.escape(p) + r"\b", asks)]
            count = sum(len(re.findall(r"\b" + re.escape(p) + r"\b", asks)) for p in hits)
            if count >= min_hits:
                rows.append((count, name, ", ".join(sorted(hits)[:4])))
        if rows:
            print(f"\n### {md.stem}\n\n| hits | skill not loaded | matched phrases |\n|---|---|---|")
            for count, name, hits in sorted(rows, reverse=True)[:10]:
                print(f"| {count} | {name} | {hits} |")


if __name__ == "__main__":
    main()
