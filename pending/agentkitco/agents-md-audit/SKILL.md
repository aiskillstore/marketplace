---
name: agents-md-audit
description: Audit an AGENTS.md, CLAUDE.md, Cursor rule or Copilot instructions file for stale commands, broken paths, vague rules, secrets and contradictions. Use when asked to review, trim or check agent instructions.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Audit an agent instruction file

Goal: find lines in an instruction file that are wrong, stale, vague or risky, and propose a shorter, accurate version. Never "fix" a command you have not run or a path you have not checked.

## Steps

1. **Find the files.** Look for `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/*.md`, `.cursor/rules/*.mdc`, `.cursorrules`, `.github/copilot-instructions.md` and `.github/instructions/*.md`. List what you found and who reads each file.
2. **Run the checker** from the repository root to get mechanical findings first:
   `python3 scripts/audit_instructions.py <file> [<file> ...]`
   (The path is relative to this skill's folder; use the full path to the installed skill.) It reports length, broken file paths, commands that name a script or make target that does not exist, vague phrases, left-over `[BRACKET]` placeholders, duplicate lines and secret-looking strings. If Python is not available, do the same checks by hand.
3. **Check each command yourself.** For every command in the file, confirm it exists (script in `package.json`, target in `Makefile`, entry in `pyproject.toml`). Run the cheap, safe ones (lint, unit tests, type check). Do not run deploy, migrate or delete commands; list them as "not verified".
4. **Check the judgment calls** the script cannot make:
   - Rules a linter or formatter already enforces (candidates to delete).
   - Rules that contradict each other, or contradict another instruction file.
   - Facts the agent can read from the repo in seconds (framework name, folder listing).
   - Rules with no testable meaning ("write clean code").
   - Anything that belongs in a path-scoped rule instead of the root file.
5. **Report**, then wait for approval before editing.

## Report format

```
## Instruction file audit: <file>
Length: <n> lines (<verdict>)

### Must fix (wrong or unsafe)
- line <n>: <what is wrong>, <evidence: command output or missing path>

### Should trim (low value)
- line <n>: <why it can go>

### Contradictions
- <file A line n> vs <file B line m>: <the conflict>

### Not verified
- <command>: <why you did not run it>

### Proposed version
<the shorter file, or a diff>
```

## Rules

- Evidence over opinion: every "must fix" cites output or a missing file.
- Keep the owner's voice and any rule that encodes a real incident or a hard constraint.
- Do not add new rules during an audit. Suggest them separately at the end, at most three.
- Treat a secret-looking string as real: tell the user to rotate it, and do not repeat the value in your report.
