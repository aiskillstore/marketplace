---
name: write-agents-md
description: Draft a short, accurate AGENTS.md (and a CLAUDE.md bridge) for a repository from evidence in the repo. Use when a project has no agent instructions, or when asked to create or rewrite AGENTS.md.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Write an AGENTS.md from evidence

Goal: a file under about 100 lines that tells a coding agent how to run, test and change this repo, using only facts you verified. Unknown beats invented.

## Gather evidence first (read, do not guess)

1. `README*`, `CONTRIBUTING*`, any `docs/` index.
2. Manifests and task runners: `package.json` scripts, `Makefile`, `justfile`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `*.csproj`, `project.godot`.
3. CI config (`.github/workflows/*`, `.gitlab-ci.yml`): the commands CI runs are the commands that must pass.
4. Lint, format and type-check config (`.eslintrc*`, `ruff.toml`, `.editorconfig`, `tsconfig.json`).
5. Directory layout, two levels deep, ignoring `node_modules`, `.git`, build output.
6. Existing instruction files (`CLAUDE.md`, `.cursor/rules`, `.github/copilot-instructions.md`). Merge, do not duplicate.

## Write the file

Use [references/template.md](references/template.md) as the skeleton. Rules:

- **Commands first.** Exact commands to install, run, test one file, run the full suite, lint, build. Copy them from the manifests; run the safe ones to confirm.
- **Only what the agent cannot infer.** Skip "this is a Next.js app" if `package.json` says so. Keep: unusual conventions, forbidden areas, generated files, required env setup.
- **Make each rule testable.** "Run `npm run lint` before finishing" not "keep code clean".
- **Boundaries section.** Files and directories never to edit by hand (generated code, lockfiles, vendored code), and actions that need approval (migrations, deploys, deleting data, force-push).
- **Unknowns.** Where evidence is missing, write `TODO(owner): <question>` instead of guessing, and list the TODOs in your final message.
- **No secrets, no personal paths, no links you did not open.**

## Bridge for other tools

- Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If no `CLAUDE.md` exists, create one containing only `@AGENTS.md` so both stay in sync (Claude Code supports `@path` imports). If one exists, add that import line at the top and remove duplicated content.
- Cursor, GitHub Copilot, Codex and others read `AGENTS.md` directly or via their own files; do not copy the content into several places.

## Verify before finishing

1. Run each command you documented (skip destructive ones, say so).
2. Check every path exists.
3. Count lines. If over about 100, move scoped rules to nested `AGENTS.md` files or tool-specific rule files.
4. Show the user the file and the TODO list. Do not commit unless asked.
