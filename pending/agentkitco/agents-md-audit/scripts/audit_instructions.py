#!/usr/bin/env python3
"""Mechanical checks for agent instruction files (AGENTS.md, CLAUDE.md, .mdc, copilot instructions).

Usage: python3 audit_instructions.py FILE [FILE ...] [--root DIR] [--json]

Heuristics only. It finds things worth a human look; it does not prove a file is good.
Standard library only (Python 3.8+).
"""
import argparse, json, os, re, sys

LONG_WARN = 150
VAGUE = [
    "clean code", "best practices", "be careful", "high quality", "write good",
    "as needed", "when appropriate", "make sure it works", "follow conventions",
    "industry standard", "production-ready", "production ready", "robust",
]
SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"ghp_[A-Za-z0-9]{30,}", "GitHub token"),
    (r"sk-[A-Za-z0-9_-]{20,}", "API key (sk-...)"),
    (r"xox[abp]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key block"),
    (r"(?i)\b(api[_-]?key|secret|password|token)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-/+=]{12,}", "secret-looking assignment"),
]
PATH_EXT = r"(?:md|mdc|json|ya?ml|toml|py|js|jsx|ts|tsx|go|rs|rb|java|kt|cs|sh|sql|txt|cfg|ini|lock|html|css)"
PATH_RE = re.compile(r"`([A-Za-z0-9_./@-]+(?:/[A-Za-z0-9_.@*-]+)+|[A-Za-z0-9_.-]+\.%s)`" % PATH_EXT)
CMD_RE = re.compile(r"`((?:npm|pnpm|yarn|bun)\s+(?:run\s+)?([A-Za-z0-9:_-]+)[^`]*|make\s+([A-Za-z0-9_.-]+)[^`]*|just\s+([A-Za-z0-9_-]+)[^`]*)`")
NPM_BUILTIN = {"install", "i", "ci", "add", "remove", "update", "init", "audit", "publish", "link", "exec", "dlx", "x", "create", "outdated", "pack", "version", "help", "config", "cache", "rebuild", "uninstall"}
# `npm test`, `npm start`, `npm stop`, `npm restart` run package.json scripts without "run".
NPM_SCRIPT_ALIASES = {"test", "start", "stop", "restart"}


def read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def makefile_targets(root):
    out = set()
    path = os.path.join(root, "Makefile")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8", errors="replace"):
            m = re.match(r"^([A-Za-z0-9_.-]+)\s*:(?!=)", line)
            if m:
                out.add(m.group(1))
    return out


def justfile_recipes(root):
    out = set()
    for name in ("justfile", "Justfile"):
        path = os.path.join(root, name)
        if os.path.exists(path):
            for line in open(path, encoding="utf-8", errors="replace"):
                m = re.match(r"^([A-Za-z0-9_-]+)[^:=\n]*:(?!=)", line)
                if m:
                    out.add(m.group(1))
    return out


SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".next", "target"}


def basename_index(root):
    names = set()
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        names.update(fns)
        if len(names) > 200000:
            break
    return names


def audit(path, root):
    findings = []
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError as e:
        return [dict(level="error", line=0, msg="cannot read file: %s" % e)], 0
    lines = text.splitlines()
    n = len(lines)
    if n > LONG_WARN:
        findings.append(dict(level="trim", line=0, msg="file is %d lines (over %d). Long files dilute the rules that matter; consider splitting scoped rules out." % (n, LONG_WARN)))

    names = None
    pkg = read_json(os.path.join(root, "package.json"))
    scripts = set((pkg or {}).get("scripts", {}).keys()) if pkg else None
    targets = makefile_targets(root)
    recipes = justfile_recipes(root)

    seen = {}
    in_fence = False
    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if line.startswith("```"):
            in_fence = not in_fence
        if line and not line.startswith("#") and len(line) > 25:
            key = re.sub(r"\s+", " ", line.lower())
            if key in seen:
                findings.append(dict(level="trim", line=i, msg="duplicate of line %d" % seen[key]))
            else:
                seen[key] = i
        low = raw.lower()
        for phrase in VAGUE:
            if phrase in low:
                findings.append(dict(level="trim", line=i, msg="vague wording '%s': say what to do or run instead" % phrase))
                break
        if re.search(r"\[[A-Z][A-Z0-9 _/-]{2,}\]", raw):
            findings.append(dict(level="fix", line=i, msg="unfilled placeholder: %s" % re.search(r"\[[A-Z][A-Z0-9 _/-]{2,}\]", raw).group(0)))
        for pat, label in SECRET_PATTERNS:
            if re.search(pat, raw):
                findings.append(dict(level="fix", line=i, msg="possible secret (%s): remove it and rotate it if it was real" % label))
                break
        for m in PATH_RE.finditer(raw):
            tok = m.group(1)
            if any(c in tok for c in "*<>") or tok.startswith(("http", "~", "/")) or "://" in tok:
                continue
            if tok.startswith("@"):
                continue
            cand = os.path.join(root, tok)
            base_dir = os.path.dirname(os.path.abspath(path))
            if os.path.exists(cand) or os.path.exists(os.path.join(base_dir, tok)):
                continue
            if "/" not in tok:
                # bare file name: only flag it if no file with that name exists anywhere in the repo
                if names is None:
                    names = basename_index(root)
                if tok in names:
                    continue
                findings.append(dict(level="check", line=i, msg="file name not found anywhere in the repo: %s" % tok))
            else:
                findings.append(dict(level="fix", line=i, msg="path does not exist from repo root: %s" % tok))
        for m in CMD_RE.finditer(raw):
            full = m.group(1)
            if full.startswith(("npm", "pnpm", "yarn", "bun")):
                word = m.group(2)
                explicit_run = re.match(r"(?:npm|pnpm|yarn|bun)\s+run\s", full) is not None
                if scripts is None:
                    findings.append(dict(level="check", line=i, msg="cannot confirm script '%s': no package.json at repo root" % word))
                elif word in NPM_BUILTIN and not explicit_run:
                    continue
                elif word not in scripts:
                    if word in NPM_SCRIPT_ALIASES and not explicit_run:
                        findings.append(dict(level="check", line=i, msg="no package.json script named '%s'; `npm %s` only works here if the default fallback applies (npm start runs server.js if it exists)" % (word, word)))
                    else:
                        findings.append(dict(level="fix", line=i, msg="package.json has no script named '%s'" % word))
            elif full.startswith("make"):
                t = m.group(3)
                if not targets:
                    findings.append(dict(level="check", line=i, msg="`make %s` but no Makefile targets found at repo root" % t))
                elif t not in targets:
                    findings.append(dict(level="fix", line=i, msg="Makefile has no target '%s'" % t))
            elif full.startswith("just"):
                t = m.group(4)
                if recipes and t not in recipes:
                    findings.append(dict(level="fix", line=i, msg="justfile has no recipe '%s'" % t))
    return findings, n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--root", default=".", help="repository root used to resolve paths and scripts (default: current directory)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    result = {}
    worst = 0
    for f in args.files:
        findings, n = audit(f, root)
        result[f] = dict(lines=n, findings=findings)
        if any(x["level"] in ("fix", "error") for x in findings):
            worst = 1
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        order = {"error": 0, "fix": 1, "check": 2, "trim": 3}
        for f, r in result.items():
            print("== %s (%d lines)" % (f, r["lines"]))
            if not r["findings"]:
                print("   no mechanical findings (this does not mean the file is good)")
            for x in sorted(r["findings"], key=lambda x: (order.get(x["level"], 9), x["line"])):
                where = "line %d" % x["line"] if x["line"] else "file"
                print("   [%s] %s: %s" % (x["level"].upper(), where, x["msg"]))
    sys.exit(worst)


if __name__ == "__main__":
    main()
