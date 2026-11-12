"""Digest every Claude Code session on this machine into one short Markdown file each.

Per session: title, folder, dates, what the HUMAN asked (real text, system
reminders and command wrappers stripped), skills loaded, top tools.
Raw .jsonl files are never modified.

Usage:
  python read_sessions.py OUT_DIR [--days 30] [--max-chars 600] [--root PATH]
Writes OUT_DIR/<title>__<id8>.md and OUT_DIR/_index.csv (newest first).
"""
import csv, json, re, sys, time, collections
from pathlib import Path

NOISE = re.compile(r"<(system-reminder|command-message|command-name|command-args|local-command-stdout|local-command-caveat)[\s\S]*?</\1>", re.I)


def arg(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def human_text(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return c
    return "\n".join(b.get("text", "") for b in c or [] if isinstance(b, dict) and b.get("type") == "text")


def digest(path, max_chars):
    title, cwd, first, last = None, "", "", ""
    asks, skills, tools = [], collections.Counter(), collections.Counter()
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            kind = d.get("type")
            if kind == "custom-title":
                title = d.get("customTitle") or title
            ts = d.get("timestamp") or ""
            if ts:
                first = first or ts
                last = ts
            cwd = d.get("cwd") or cwd
            # Real human turns only: tool results also arrive as role=user.
            if kind == "user" and (d.get("origin") or {}).get("kind") == "human" and not d.get("isSidechain"):
                text = NOISE.sub("", human_text(d.get("message", {}))).strip()
                if text:
                    asks.append(ts[:16] + " " + text[:max_chars].replace("\n", " "))
            if kind == "assistant":
                for b in d.get("message", {}).get("content", []) or []:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        tools[b.get("name", "")] += 1
                        if b.get("name") == "Skill":
                            skills[(b.get("input") or {}).get("skill", "?")] += 1
    return dict(title=title or "(untitled)", cwd=cwd, first=first, last=last, asks=asks, skills=skills, tools=tools)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    days, max_chars = arg("--days", 30), arg("--max-chars", 600)
    root = Path(arg("--root", str(Path.home() / ".claude" / "projects")))
    cutoff = time.time() - days * 86400
    rows = []
    for f in root.rglob("*.jsonl"):
        if "subagents" in f.parts or f.stat().st_mtime < cutoff:
            continue
        r = digest(f, max_chars)
        if not r["asks"]:
            continue  # scheduled/automatic runs with no human turn
        safe = re.sub(r"[^\w\- ]", "", r["title"])[:50].strip().replace(" ", "_") or "session"
        md = out / f"{safe}__{f.stem[:8]}.md"
        with open(md, "w", encoding="utf-8") as w:
            w.write(f"# {r['title']}\n\nid: {f.stem}\nfolder: {r['cwd']}\nfrom {r['first'][:16]} to {r['last'][:16]}\n")
            w.write("skills loaded: " + (", ".join(f"{k}({v})" for k, v in r["skills"].most_common()) or "NONE") + "\n")
            w.write("top tools: " + ", ".join(f"{k}({v})" for k, v in r["tools"].most_common(12)) + "\n\n")
            w.write(f"## What the human asked ({len(r['asks'])} messages)\n\n")
            w.writelines(f"- {a}\n" for a in r["asks"])
        rows.append([r["title"], f.stem, r["cwd"], r["first"][:16], r["last"][:16], len(r["asks"]),
                     ";".join(r["skills"]), md.name, md.stat().st_size])
    rows.sort(key=lambda x: x[4], reverse=True)
    with open(out / "_index.csv", "w", newline="", encoding="utf-8") as w:
        cw = csv.writer(w)
        cw.writerow(["title", "id", "folder", "first", "last", "human_msgs", "skills", "file", "bytes"])
        cw.writerows(rows)
    print(f"{len(rows)} sessions with human messages -> {out} ({sum(r[8] for r in rows)//1024} KB of digests)")


if __name__ == "__main__":
    main()
