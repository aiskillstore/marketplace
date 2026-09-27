---
name: bootstrap
description: Interactive agent-flow setup for a repository. Scans the repo read-only, proposes AGENTS.md (root + per module), DOCS_INDEX.md and CONTEXT_MANIFEST.json with a confidence marker on every claim, calibrates protected paths and risk boundaries with the user, and writes each file only after the human approves it. Use when setting up agent-flow, when context files are missing, or when migrating from Root_AGENT.md. Also use whenever the user wants an AGENTS.md (or CLAUDE.md/GEMINI.md) written for a repo that doesn't have one, says their coding agents keep getting confused about the codebase, asks to "onboard" or "document" a repo for AI agents, or wants to set protected paths / risk boundaries — even if they don't say "agent-flow" or "bootstrap" by name.
compatibility: Requires git. Pi gets the bootstrap_scan/bootstrap_write tools; other harnesses use `npx agent-flow scan` plus normal file edits with the user's approval.
---

# Bootstrap

You propose. The human decides. Every claim you write carries a confidence marker, and every risk boundary is a question to the human, never an assumption.

Why this matters: a context file with confident wrong claims makes agents *worse* than having no context at all (FM-01). Fewer true claims beat many plausible ones.

## Phase 1: Reconnaissance (read-only)

1. Call `bootstrap_scan` (outside Pi: `npx agent-flow scan --json`). Every field it returns was read from a file, so those are `[HIGH CONFIDENCE]`. That covers: languages, package managers, test frameworks, commands from `package.json` scripts and the `Makefile`, CI files, existing context files, docs, default branch, and recent commits.
2. **Secrets gate.** If `secretSuspects` is not empty, stop and show the paths and kinds (never the values). A tracked `.env` or key file must be removed from git and **rotated** before bootstrap continues. Context files are sent to model providers.
3. **Existing context.** If `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules` or `.github/copilot-instructions.md` exist, read them first. They are the user's own rules. You merge into them; you never replace them. If you find `Root_AGENT.md` or `Per-app_AGENT.md` (agent-flow ≤1.0.x), offer to move them to `AGENTS.md`. No harness loads the old names automatically.
4. Read the entry points and 2–3 representative modules so you can describe them from the code itself. Anything you describe without reading gets `[INFERRED]`.

## Phase 2: Proposal (interactive, nothing written)

Why `AGENTS.md`: Pi, Codex, Cursor, Copilot, Windsurf and most agents load `AGENTS.md` automatically — it's a [shared, Linux-Foundation-stewarded convention](https://agents.md), not something specific to this project. Claude Code loads `CLAUDE.md`, which can import it with one line (`@AGENTS.md`). Gemini CLI loads it when `context.fileName` includes `AGENTS.md`. One source of truth, every harness.

Show the root `AGENTS.md` (template: `templates/AGENTS.md.template`) as a proposal, one section at a time:

```
Repository map
  src/api/      HTTP handlers (Express)          [HIGH CONFIDENCE — read src/api/index.ts]
  src/billing/  Stripe integration               [HIGH CONFIDENCE — read src/billing/charge.ts]
  scripts/      deploy helpers                   [INFERRED — names only]

Commands
  npm test          [HIGH CONFIDENCE — package.json#scripts.test]
  npm run typecheck [HIGH CONFIDENCE — package.json#scripts.typecheck]
```

Rules for the proposal:
- **Keep it short.** Aim for under 150 lines at the root. Agents pay for every line on every task.
- **No directory-tree dumps.** They go stale on the first rename. Describe what each module is *for*.
- **Paths go in `backticks`.** `/doctor` checks every backticked path against the filesystem, so a wrong path gets caught. For a path you mention on purpose even though it no longer exists (history, a warning), add `<!-- agent-flow:ignore-refs -->` on that line.
- **Only real commands.** Only commands that exist in `package.json`, the `Makefile`, or CI.

Ask: *"What here is wrong or missing? What do new people always get wrong in this repo?"* Their answer to the second question gives you the **Local traps**, the most valuable part of the file.

For monorepos: propose `<package>/AGENTS.md` for each package that has its own rules (template: `templates/module-AGENTS.md.template`). Skip packages that have nothing specific to say.

## Phase 3: Risk calibration (interactive)

Ask these one at a time. Never pre-fill the answers.

1. **Protected paths.** "Which paths must agents never modify?" These are usually migrations, lockfiles, CI, security modules, and vendored code. They go into `protected_paths`, and the guard and pre-commit hook enforce them.
2. **Critical paths.** "Where are money, auth, contracts or PII?" These become `risk_boundaries` with `risk_level: critical`. Changes there get high-reasoning review, a draft PR, and human approval.
3. **Low-risk paths.** "What is safe for mechanical edits?" (docs, tests, generated code). These become `risk_level: low`.
4. **Auto-merge.** "Should low-risk changes that pass QA auto-merge?" Recommend **no** until the pipeline has shipped about 10 clean PRs in this repo. This sets `pipeline.auto_merge_low_risk`.

Show the resulting `risk_boundaries` and `protected_paths` back to the human and get a yes.

## Phase 4: Write (one confirmation per file)

Call `bootstrap_write` once per file. It shows the human a confirmation dialog, refuses paths outside the repo, refuses an invalid manifest, and refuses secret-shaped content. It will not overwrite an existing file unless you pass `overwrite: true`, and it asks again when you do.

1. `AGENTS.md`, plus one `AGENTS.md` per module.
2. `CLAUDE.md` containing `@AGENTS.md`, if the user uses Claude Code (template: `templates/CLAUDE.md.template`). If a `CLAUDE.md` already exists, propose adding the import line to it.
3. `DOCS_INDEX.md` (`templates/DOCS_INDEX.md.template`).
4. `CONTEXT_MANIFEST.json`. Follow `templates/CONTEXT_MANIFEST.json.template` and `schemas/context-manifest.schema.json` **exactly**: `context_files[].references[]` with `path`, `type`, a real ISO `last_verified`, and `exists`. List every path the prose names. Set `default_branch` from the scan. Don't leave any `{{PLACEHOLDER}}` in any file. `/doctor` fails on them.

Outside Pi, show each file's full content and write it only after the human says yes.

## Phase 5: Harness wiring

Suggest these; the human runs them:

- Pi: nothing more. The guard and tools are active once the package is installed.
- Claude Code / Codex / Gemini / Cursor / Copilot / Windsurf: `npx agent-flow install --harness <name>`. It copies the skills and the reviewer subagent and never overwrites your edits.
- Everyone: `npx agent-flow hook install` for the pre-commit gate (protected paths, secrets, broken context references).
- CI: add `npx agent-flow doctor` and `npx agent-flow audit-risk --fail-on-new` as steps (see `README.md`).
- First baseline: after the human reviews `npx agent-flow audit-risk`, `npx agent-flow baseline accept --all --yes`.

## Phase 6: Verify

Run `/doctor` (`stale_detect`). It has to be healthy before you say you're done. If it isn't, fix what it reports; don't explain it away.

## Edge cases

| Situation | Action |
|---|---|
| Empty repo | Write a minimal `AGENTS.md` with `[NEEDS VERIFICATION]` on everything. No manifest refs yet. |
| No tests | Say so plainly in `AGENTS.md`. The pipeline's QA step will report `no_commands_defined` until tests exist. |
| No CI | Propose the CI steps above. Don't write CI files yourself (bootstrap only writes context files). |
| Huge repo (`truncated: true`) | Bootstrap the top-level modules the user names, not everything. |
| Existing agent-flow ≤1.0 files | Offer the migration in Phase 1.3. |
| The user won't answer the risk questions | Write nothing to `protected_paths` or `risk_boundaries`. The classifier falls back to path heuristics and says so. |
