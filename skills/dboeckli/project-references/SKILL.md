---
name: project-references
description: "Look up conventions, patterns, and concrete implementations from your own GitHub repositories checked out locally under ~/projects/referenzen/. Use this skill whenever there is uncertainty about how something is done in your codebase family — e.g. Helm chart structure, Kubernetes manifests, framework configuration patterns, Docker Compose conventions, CI/CD pipeline setup, or any other recurring architectural decision. Invoke it proactively before guessing at a convention; always cite the source project and path when a pattern is adopted. Also use when the user asks to check out, update, or search reference repositories, or to generate an overview/report of GitHub Actions triggers (push, pull_request, schedule/cron) across repositories."
---

---

# Project References

This skill manages a local mirror of your own GitHub repositories under
`~/projects/referenzen/` and lets you look up conventions and implementation
patterns without guessing or reading all repos blindly.

All operations are **read-only** on the reference projects themselves. Only
`git clone` and `git pull` write into that directory — never edits.

---

## Instructions

### Step 1: Check whether the relevant repo is already cloned

```bash
ls ~/projects/referenzen/
```

If the needed repo is missing, run `scripts/clone-or-update.sh owner/repo` to clone it first.

### Step 2: Ask the user which reference project is most relevant

Do not scan all repos blindly — that fills context. Ask: "Which of your sibling projects uses this pattern?" or list the available repos and let the user pick.

### Step 3: Search targeted — file first, then grep

Use `find` to locate a file by name, then `cat` or `grep` to read only the relevant section. For search commands and patterns, consult `references/search-patterns.md`.

### Step 4: Cite the source when adopting a pattern

Always state which project and file path a pattern came from before applying it:

> Pattern adopted from `your-service` → `helm-charts/Chart.yaml` line 4

### Step 5: Sync only when explicitly requested

Run `scripts/sync-all.sh` only when the user says "sync all" or "update all references". For a single repo, prefer `scripts/clone-or-update.sh`.

---

## Examples

### Example 1: Looking up a Helm chart convention

User says: "How should I structure the Helm chart for this project?"

Actions:

1. Run `ls ~/projects/referenzen/` to see available repos
2. Ask: "Which sibling project should I use as reference?" — user says `your-service`
3. Run `find ~/projects/referenzen/your-service -name "Chart.yaml"` to locate it
4. Read the file, note the structure (apiVersion, dependencies, version pattern)
5. Apply the same structure; cite: "adopted from `your-service/helm-charts/Chart.yaml`"

Result: Helm chart consistent with sibling projects, traceable source cited.

### Example 2: Checking out a new reference repo

User says: "Clone my other-service project as a reference"

Actions:

1. Run `bash scripts/clone-or-update.sh owner/other-service`
2. Stream output so user sees CLONE/PULL/SKIP progress
3. Confirm with `ls ~/projects/referenzen/other-service/`

Result: Repo available locally for pattern lookups; no edits made.

### Example 3: Finding a configuration pattern

User says: "How do I configure the database pool like in the other projects?"

Actions:

1. `ls ~/projects/referenzen/` — pick a relevant sibling project
2. `grep -rn "database.pool" ~/projects/referenzen/your-service/src/main/resources/`
3. Read the relevant config section
4. Cite: "pattern from `your-service/src/main/resources/application.yaml` line 42"

Result: Exact config from a proven sibling project, not guessed.

### Example 4: Overview of GitHub Actions triggers

User says: "When do my projects run their GitHub Actions — push, PR, or schedule?"

Actions:

1. Run `bash scripts/list-workflow-triggers.sh` (add `--glob` to narrow to one
   pipeline, `--root` for a different checkout directory)
2. Present the sorted overview (weekday/time, human-readable plus original
   cron) and the event-only workflows
3. Point the user to the generated report at `target/workflow-triggers.md`

Result: Consolidated, time-sorted trigger overview across all reference repos
plus a Markdown report, without opening each workflow file.

---

## Repository source

Two sources are supported — prefer the manual list when it exists:

1. **Manual list** (`~/claude-shared/projekte.txt`): one GitHub repo URL or
   `owner/name` slug per line, blank lines and `#` comments ignored.
2. **Automatic discovery**: `gh repo list --limit 200 --json nameWithOwner`
   when the file is absent or the user explicitly asks for a full sync.

---

## Scripts

Two ready-made scripts live in `scripts/` — use them instead of writing
inline Bash. Both accept `REFERENZEN_DIR` as an env override (default:
`~/projects/referenzen`).

### `scripts/clone-or-update.sh <owner/repo>`

Clones a single repository or pulls if it already exists locally. Refuses
to pull when local changes are present (exit code 2) — never stashes or
resets.

```bash
bash scripts/clone-or-update.sh owner/your-repo
```

Exit codes: `0` = ok, `2` = skipped (local changes), `3` = clone/pull failed.

### `scripts/sync-all.sh [--list <file>] [--limit <n>]`

Iterates over all repositories and calls the clone-or-update logic for each.
Prefers `~/claude-shared/projekte.txt` as source; falls back to `gh repo list`
when the file is absent. Prints a summary line at the end.

```bash
# Sync everything (auto-detect source)
bash scripts/sync-all.sh

# Use a specific list file
bash scripts/sync-all.sh --list ~/claude-shared/projekte.txt

# Limit gh repo list to 50 repos
bash scripts/sync-all.sh --limit 50
```

**Do not** run sync-all blindly — use it only when the user explicitly says
"sync all" or "update all references". For a single repo prefer
`clone-or-update.sh`.

### `scripts/list-workflow-triggers.sh [--root <dir>] [--glob <pattern>] [--out <file>] [--no-report]`

Scans every repo checkout for `.github/workflows/*.yml` and `*.yaml`, extracts
the triggers from the `on:` block (`push`, `pull_request`, `schedule`,
`workflow_dispatch`, `release`, …) plus any `cron:` expressions, prints the
overview and writes a Markdown report. Scheduled workflows are **sorted by
weekday/time** and shown with a **human-readable run time** (e.g. `Monday
02:05`) next to the **original cron expression**; workflows without a schedule
are listed in a separate event-only section. Read-only, no network access.

- `--root <dir>` — directory containing repo checkouts. Default:
  `$REFERENZEN_DIR` or `~/projects/referenzen`.
- `--glob <pattern>` — optional filename filter, e.g. `maven-build.yml`.
  Default: all workflows.
- `--out <file>` — Markdown report path. Default: `target/workflow-triggers.md`
  (relative to the current project directory, created if missing).
- `--no-report` — print to stdout only, skip the report file.

```bash
# Overview + report for all reference repos
bash scripts/list-workflow-triggers.sh

# Only maven-build.yml, custom report location
bash scripts/list-workflow-triggers.sh --glob 'maven-build.yml' --out target/maven-triggers.md

# A different checkout root (e.g. Windows mount)
bash scripts/list-workflow-triggers.sh --root /mnt/c/Development/projects/all-git-repos
```

---

## Workflows

### 1. Check out or update repositories

Run the appropriate script and stream output so the user sees every
CLONE / PULL / SKIP action as it happens.

### 2. Search within reference projects

Scope the search to what the user actually needs. Prefer targeted lookups
over broad recursive greps. For ready-made search commands and citing patterns,
consult `references/search-patterns.md`.

### 3. Discover available reference projects

```bash
ls ~/projects/referenzen/
```

If `~/claude-shared/projekte.txt` exists, show its contents alongside to
explain which repos are tracked vs. which are locally present.

### 4. Overview of GitHub Actions triggers

Run `scripts/list-workflow-triggers.sh` to get a cross-repo overview of every
workflow's `on:` triggers and `cron:` entries. It also writes the report to
`target/workflow-triggers.md`. Use `--glob` to focus on a single pipeline
(e.g. `maven-build.yml`) and `--root` for a different checkout directory.

---

## When to suggest this skill proactively

Suggest looking up a reference project when:

- The user asks how something is structured and the answer may vary by
  project convention (Helm chart layout, Flyway migration naming, Dockerfile
  patterns, Maven plugin ordering, etc.)
- There is more than one reasonable approach and consistency with sibling
  projects matters
- The user says "like the other projects" or "same as before" without
  specifying which project

Ask the user which reference project is most relevant rather than scanning
all of them — scanning is expensive in context.

---

## Safety rules

- Never edit, stage, commit, or delete files inside `~/projects/referenzen/`.
- If `git pull` would fail due to local changes, report the conflict clearly
  and stop — do not stash, reset, or force.
- Do not expose repository contents that contain secrets (`.env`, credential
  files) in the response — read and cite structure only.
