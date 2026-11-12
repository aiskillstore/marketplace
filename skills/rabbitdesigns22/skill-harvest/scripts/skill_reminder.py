"""UserPromptSubmit hook: name the installed skills that apply to THIS message.

Fixes the most common fleet gap: the skill is installed, the session never
loads it. Reads the hook JSON on stdin, matches the prompt against a rules
file, prints at most 3 short hints. Prints nothing when nothing matches, so
it costs no tokens on ordinary messages.

Rules file (JSON list), default ~/.claude/skill-reminder.json:
  [{"skill": "report-now", "why": "status checked live, with the time",
    "any": ["reporte", "como va", "que paso"]}]
Matching is case- and accent-insensitive, on whole words/phrases.
Skills not installed under ~/.claude/skills are skipped.

Test without a hook:  echo {"prompt":"dame el reporte"} | python skill_reminder.py
"""
import json, re, sys, unicodedata
from pathlib import Path

HOME = Path.home() / ".claude"


def plain(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        raw = sys.stdin.buffer.read()  # bytes: on Windows sys.stdin decodes as cp1252 and breaks accents ("cómo" -> "cÃ³mo")
        try:
            data = raw.decode("utf-8")
        except UnicodeDecodeError:
            data = raw.decode("cp1252", "replace")
        prompt = json.loads(data.lstrip("﻿") or "{}").get("prompt", "")
    except ValueError:
        return
    rules_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HOME / "skill-reminder.json"
    if not prompt or not rules_path.exists():
        return
    # Only the human's own words count. Pasted pages, other sessions' messages,
    # subagent reports and task notifications also arrive as prompts and
    # trigger false hints (seen live: a report saying "ERROR" fired diagnosing-bugs).
    prompt = re.sub(r"<(pasted_content|agent-message|cross-session-message|task-notification|system-reminder)\b[\s\S]*?</\1>", " ", prompt)
    if re.search(r"<(agent-message|cross-session-message|task-notification)\b", prompt):
        return  # unterminated machine block: say nothing rather than guess
    prompt = re.sub(r"(?<!\w)/[\w:-]+", " ", prompt)  # /slash-commands typed inline
    text = plain(prompt)
    if text.lstrip().startswith("/"):
        return  # the user is already invoking a skill/command
    installed = {p.parent.name for p in (HOME / "skills").glob("*/SKILL.md")}
    hits = []
    for rule in json.loads(rules_path.read_text(encoding="utf-8")):
        if rule["skill"] not in installed:
            continue
        n = sum(1 for k in rule["any"] if re.search(r"(?<!\w)" + re.escape(plain(k)) + r"(?!\w)", text))
        if n:
            hits.append((n, rule))
    if not hits:
        return
    hits.sort(key=lambda h: -h[0])
    lines = [f"- `{r['skill']}`: {r['why']}" for _, r in hits[:3]]
    print("SKILLS THAT APPLY TO THIS MESSAGE (load them with the Skill tool before working, unless already loaded in this session):\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
