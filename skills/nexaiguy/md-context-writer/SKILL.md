---
name: md-context-writer
description: 'Write, audit and fix CLAUDE.md, AGENTS.md and .claude/rules from facts in your repository, with a linter that checks them against the code. Use when: Create a CLAUDE.md or AGENTS.md built on the real build, test and lint commands; Audit an existing instruction file for stale commands, moved paths and secrets; Split a long CLAUDE.md into path-scoped .claude/rules that load only when needed.'
license: MIT
metadata:
  author: Nex AI
  version: '1.1'
  agensi-slug: claude-md-writer
compatibility: Works with any agent that can run Python 3.8+. Writes instruction files for Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI and Windsurf.
---

# CLAUDE.md Writer

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/claude-md-writer). Scripts, extension source, and templates from the original package are not in this folder.

### What it does

The instruction file is read at the start of every agent session. Most are generated once and never checked, or grow into generic advice the agent stops following. This skill writes one from **verified facts** and keeps it honest.

### Two scripts, standard library only

**`repo_facts.py`** reports what the repo actually contains: every defined command (package.json per workspace, Makefile, justfile, Taskfile, pyproject, tox, nox, composer), **what CI really runs**, toolchain and versions, lint/test/type tools, layout, existing agent files for Claude, Codex, Cursor, Copilot, Gemini and Windsurf, commit style, and env var names (never values).

**`lint_claude_md.py`** checks the instruction file against the repo:

- commands that do not exist (`pnpm run e2e`, `make deploy`), with dependency binaries like `pnpm vitest` understood
- paths that moved, broken or too-deep `@imports`
- secrets, vague rules nobody can verify, contradictions, too much shouting
- oversized files, rules frontmatter that silently fails, an AGENTS.md Claude Code ignores, a CLAUDE.local.md about to be committed
- non-zero exit on errors, so it runs in CI and pre-commit

### The workflow

Collect facts, verify the commands, ask only what files cannot answer (at most five questions), write under 200 lines, put area-specific rules in path-scoped `.claude/rules/`, lint until clean. Includes a writing guide with before/after examples, a template, and a complete example file.

Tested on real repositories (a Python library and a large pnpm monorepo) and with 19 automated tests.

Built by Nex AI, nex-ai.be

## When to use

- Create a CLAUDE.md or AGENTS.md built on the real build, test and lint commands
- Audit an existing instruction file for stale commands, moved paths and secrets
- Split a long CLAUDE.md into path-scoped .claude/rules that load only when needed
- Set up one shared AGENTS.md for Claude Code, Codex, Cursor and Copilot
- Fail CI when the instruction file no longer matches the repository

## Known limitations

The linter verifies npm, pnpm, yarn and bun scripts, make and just targets; other command runners are not checked. Path checks cover paths written in backticks. It checks facts, it cannot judge whether a rule is wise.

## Example

**Request**

Our CLAUDE.md is a year old and Claude keeps running commands that don't exist. Fix it.

**Result**

## CLAUDE.md audited and rewritten

I ran the linter against the repo first:

```
$ python lint_claude_md.py
WARN  CLAUDE.md:1   [shouting] 6 uses of IMPORTANT/MUST/NEVER/ALWAYS in caps
ERROR CLAUDE.md:6   [commands] `pnpm run e2e`: no package.json script named 'e2e'
ERROR CLAUDE.md:7   [commands] `make deploy`: there is no Makefile
WARN  CLAUDE.md:10  [paths] `src/checkout/` does not exist in the repo
WARN  CLAUDE.md:13  [vague] "write clean code" cannot be verified
WARN  CLAUDE.md:14  [conflicts] says both use and do not use 'moment'
ERROR CLAUDE.md:16  [secrets] looks like a connection string with password

3 error, 4 warning, 0 info
```

### What I changed

| Problem | Fix |
|---------|-----|
| `pnpm run e2e` and `make deploy` do not exist | Replaced with the commands CI runs: `pnpm test`, `pnpm lint`, `pnpm typecheck` |
| `src/checkout/` was removed in a refactor | Removed; the file now names `src/orders/` and `src/payments/` |
| "Never use moment" and "use moment for timezones" | Kept one rule: dates are ISO 8601 in UTC at the API |
| A staging database URL with password | Removed; it now names `DATABASE_URL`. **Rotate that password**, it has been in git |
| Six rules in capitals | Plain, specific instructions |

Added what was missing: how to run one test (`pnpm vitest run src/orders/service.test.ts`) and a "before saying a task is done" line.

```
$ python lint_claude_md.py
Checked CLAUDE.md (16 lines)
0 error, 0 warning, 0 info
```

### Next step

Add `python lint_claude_md.py` to CI so the file fails the build when it drifts from the code again.

## Questions

### How is this different from /init?

/init drafts a file once. This skill grounds every command in the repo or CI, asks only what files cannot answer, places area-specific rules where they load on demand, and the linter keeps the file true as the code changes.

### Does it work for AGENTS.md?

Yes. The linter checks AGENTS.md and rules files, and warns when Claude Code would silently ignore an AGENTS.md next to a CLAUDE.md.

### Will it rewrite my file without asking?

No. It shows a diff with a reason for every removed section and never drops your content silently.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
