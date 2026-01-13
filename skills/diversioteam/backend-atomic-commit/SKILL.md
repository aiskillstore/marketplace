---
name: backend-atomic-commit
description: >
  Pedantic backend pre-commit and atomic commit Skill for Django/Optimo-style
  repos. Enforces local AGENTS.md / CLAUDE.md, pre-commit hooks, .security/*
  helpers, and Monty’s backend engineering taste – with no AI signatures in
  commit messages.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Glob
  - Grep
---

# Backend Atomic Commit Skill

## When to Use This Skill

Use this Skill in backend/Django repos (especially the Diversio monolith
backend) when you want:

- `/backend-atomic-commit:pre-commit` – to **actively fix** the current code
  (formatting, imports, type hints, logging, etc.) so that it matches:
  - Local `AGENTS.md` / `CLAUDE.md` rules.
  - `.pre-commit-config.yaml` expectations.
  - `.security/` diff helpers (ruff and local imports).
  - Monty’s backend taste.
- `/backend-atomic-commit:atomic-commit` – to run the same checks plus:
  - Enforce that the **staged changes are atomic** (one coherent change).
  - Ensure all quality gates are green (no shortcuts).
  - Propose a strict, ticket-prefixed commit message **without** any Claude or
    AI signatures.

## Example Prompts

- “Run `/backend-atomic-commit:pre-commit` on this repo and actively fix all
  files in `git status` so they obey backend `AGENTS.md`, `.pre-commit-config.yaml`,
  `.security/*` helpers, and Monty’s taste (no local imports, strong typing,
  structured logging). Then summarize what you changed and what’s still
  `[BLOCKING]`.”
- “Use `/backend-atomic-commit:atomic-commit` to prepare an atomic commit for
  the staged changes in `backend/`. Enforce all pre-commit hooks and
  `.security` scripts, run Ruff, ty, Django checks, and relevant pytest
  subsets, then propose a ticket-prefixed commit message with **no AI
  signature** and clearly mark any `[BLOCKING]` issues.”
- “Treat my current backend changes as one logical bugfix and run
  `/backend-atomic-commit:pre-commit` in a strict mode: eliminate local
  imports, fix type hints (no `Any`, no string-based annotations), clean up
  debug statements, and ensure Ruff, `.security/local_imports_pr_diff.sh`,
  ty, and Django checks are happy."
- “Before I commit these `optimo_*` changes, run
  `/backend-atomic-commit:atomic-commit --auto` to:
  - enforce structured logging with `TypedDict` payloads,
  - ensure no PII in logs,
  - verify tests and `.security/*` scripts,
  and then tell me whether the commit is ready and what the commit message
  should be.”

If you’re not in a backend repo (no `manage.py`, no backend-style `AGENTS.md`,
no `.pre-commit-config.yaml`), this Skill should say so explicitly and fall
back to a lighter “generic Python pre-commit” behavior.

## Modes

This Skill behaves differently based on how it is invoked:

- `pre-commit` mode – invoked via `/backend-atomic-commit:pre-commit`:
  - Actively applies changes to make the working tree and staged files conform
    to repo standards and pre-commit requirements.
  - Runs all relevant static checks and auto-fixers.
  - Does **not** propose or drive a commit.
- `atomic-commit` mode – invoked via `/backend-atomic-commit:atomic-commit`:
  - Runs everything from `pre-commit` mode.
  - Enforces atomicity of staged changes.
  - Requires all gates to be green.
  - Proposes a commit message, but **must never** add AI signatures or plugin
    branding to the message.

The command markdown sets the mode. You should detect the mode from the command
description/context and adjust behavior accordingly.

## Core Priorities

Emulate Monty’s backend engineering and review taste, tuned for pre-commit:

1. **Correctness & invariants** – multi-tenancy, time dimensions, and security
   constraints come first.
2. **Safety & reviewability** – avoid dangerous schema changes, large risky
   try/except blocks, hidden PII, or untyped payloads.
3. **Atomic commits** – one commit should represent one coherent change; split
   unrelated work.
4. **Local repo rules first** – treat `AGENTS.md` and `CLAUDE.md` as the source
   of truth when present; this Skill is a default baseline.
5. **Tooling alignment** – use uv wrappers, `.security/*` helpers, and
   `.pre-commit-config.yaml` hooks as documented, not ad-hoc commands.
6. **Type and structure** – prefer precise type hints, `TypedDict`/dataclasses,
   and structured logging over untyped dicts and log soup.
7. **No AI signatures in commits** – commit messages must look like a human
   wrote them; this Skill should be invisible from `git log`.

Always prioritize `[BLOCKING]` issues over style and nits.

## Environment & Context Gathering

When this Skill runs, you should first gather context using `Bash`, `Read`,
`Glob`, and `Grep`:

- Git context:
  - `git status --porcelain`
  - `git branch --show-current`
  - `git diff --cached --stat`
  - `git diff --cached --name-only`
  - `git log --oneline -10`
- Repo configuration:
  - Read `AGENTS.md` and `CLAUDE.md` (if present) for repo-specific rules.
  - Detect `.pre-commit-config.yaml`.
  - Detect `.security/` scripts, especially:
    - `./.security/ruff_pr_diff.sh`
    - `./.security/local_imports_pr_diff.sh`
  - Detect `manage.py` / Django project layout.
- Tool availability:
  - `uv` and `.bin/` wrappers:
    - `.bin/ruff`, `.bin/ty`, `.bin/django`, `.bin/pytest`.
  - Fallback to `uv run` or plain `python` / `pytest` / `ruff` where necessary.

If the repo clearly isn’t the Diversio backend / Django4Lyfe style, say so and
adjust expectations (but you can still run generic Python pre-commit checks).

## Checks in Both Modes

In **both** `pre-commit` and `atomic-commit` modes, follow this pipeline:

1. **Scope changed files**
   - Start from files reported by `git status` and `git diff --cached`:
     - Distinguish staged vs unstaged vs untracked.
   - Categorize by type:
     - Python (src vs tests; `optimo_*`, `dashboardapp`, `survey`, etc.).
     - Templates (Django HTML).
     - Config (YAML, JSON, `.pre-commit-config.yaml`, `pyproject.toml`,
       `requirements*.txt`).
     - Docs/markdown.

2. **Static formatting/linting**
   - Ruff:
     - Run `./.security/ruff_pr_diff.sh` if present.
     - Run `.bin/ruff check --fix` on changed Python files.
     - Run `.bin/ruff format` on those files.
   - **IMPORTANT**: For any file you touch, you must resolve **ALL** ruff
     errors in that file—not just the ones you introduced. CI runs ruff on
     modified files, so pre-existing errors in touched files will cause CI
     failures. Do **not** dismiss errors as "pre-existing" if the file is in
     your diff.
   - Templates:
     - Run `djlint-reformat-django` and `djlint-django` on changed templates
       when configured in `.pre-commit-config.yaml`.
   - Generic pre-commit hooks:
     - Respect hook definitions in `.pre-commit-config.yaml`; run
       `pre-commit run` on relevant files when possible.

3. **Backend-specific .security gates**
   - Run `.security` scripts where present:
     - `./.security/ruff_pr_diff.sh` – Ruff on changed files vs base branch.
     - `./.security/local_imports_pr_diff.sh` – check for local imports.
   - Treat failures as at least `[SHOULD_FIX]` and usually `[BLOCKING]` for
     `atomic-commit`.

4. **Type checking with ty**
   - Run `ty` on **modified Python files only** to catch type errors before CI:
     ```bash
     # For staged files (atomic-commit mode):
     .bin/ty check $(git diff --cached --name-only --diff-filter=ACMR | grep '\.py$')

     # For all modified files (pre-commit mode):
     .bin/ty check $(git diff --name-only --diff-filter=ACMR | grep '\.py$')
     ```
   - This scoped approach avoids triggering baseline errors in **unmodified**
     files while matching CircleCI's `ty` check behavior.
   - **IMPORTANT**: For any file you touch, you must resolve **ALL** `ty` errors
     in that file—not just the ones you introduced. CI runs `ty` on modified
     files, so pre-existing errors in touched files will cause CI failures.
     Do **not** dismiss errors as "pre-existing" if the file is in your diff.
   - Common pitfall: Fixing ruff ARG002 (unused argument) by prefixing with `_`
     may satisfy ruff but break `ty` if the method signature must match a parent
     class (e.g., Django admin methods). Always run both checks together.
   - Treat **any** `ty` errors in modified files as `[BLOCKING]` for
     `atomic-commit` mode or `[SHOULD_FIX]` for `pre-commit` mode.

5. **Django system checks**
   - Run `.bin/django check` or equivalent:
     - `uv run python manage.py check --fail-level WARNING`.
   - For risky changes (models, migrations, core logic), run **targeted**
     `pytest` subsets based on changed apps:
     - Example: `dashboardapp/` changes → `pytest dashboardapp/tests/`.
   - If tests cannot be run (e.g. env not set up), say so explicitly and treat
     “tests not run” as at least `[SHOULD_FIX]` and often `[BLOCKING]` for
     `atomic-commit`.

6. **Interaction with pre-commit hooks**
   - If `.pre-commit-config.yaml` exists:
     - Expect hooks to run and modify files (ruff, djlint, interrogate,
       custom scripts).
     - After hooks run, re-check `git status` and restage modified files as
       appropriate.
   - If a hook executable is missing (e.g. `check_prepare_commit_msg_hook.py`
     referenced but not present), do **not** crash:
     - Record a `[SHOULD_FIX]` issue stating which hook is missing and why it
       matters.

## Monty Backend Taste – Auto-Fix Rules

When running in `pre-commit` mode, you are allowed and expected to **actively
edit code** to align with Monty’s backend taste where it is clearly safe. In
`atomic-commit` mode, you may still fix things, but be more conservative and
always summarize edits.

### Imports & local imports

- Enforce **no local imports at any cost**:
  - Avoid `from myapp.models import MyModel` inside functions or methods just
    to dodge cyclic imports.
  - Use `.security/local_imports_pr_diff.sh` as the first line of defense.
  - Prefer:
    - Module-level imports.
    - Refactoring helpers to avoid cycles.
    - Type-only imports (e.g. `from __future__ import annotations`) when needed.
  - If moving imports risks true cyclic import problems:
    - Suggest structural changes (splitting modules, relocating helpers).
    - Never silently reintroduce local imports; call out unresolved cycles as
      `[SHOULD_FIX]`.

### Logging (especially in optimo_* apps)

- Enforce structured logging:
  - Prefer structured payloads over single log strings:
    - Good: `logger.info("optimo_event", extra={"company_uuid": str(company.uuid)})`.
    - Avoid: `logger.info("Company %s did %s", company.name, something)`.
  - In `optimo_*` apps, treat unstructured logging as at least `[SHOULD_FIX]`.
- PII in logs:
  - Never log PII such as `assignment.employee.email`; this is enforced by
    pre-commit hooks already, but you should also conceptually check.
  - Prefer logging UUIDs/IDs instead of emails or names.
- Log levels:
  - Avoid `logger.exception` for expected error paths; use `error` or `warning`
    with explicit messages.

### Try/except and error handling

- Avoid large, catch-all `try/except` blocks:
  - Shrink the `try` body to only the lines that can raise.
  - Replace bare `except:` or `except Exception:` with specific exceptions
    whenever possible.
- Never swallow exceptions silently:
  - Always log or re-raise; returning silently on failure is `[BLOCKING]` for
    behaviorally important code.
- Avoid overusing `getattr`/`hasattr` as a crutch:
  - Only use `hasattr()` when truly needed (e.g. cross-version adapters) and
    document why.

### Types, hints, and data structures

- Be pedantic about type hints:
  - Avoid `Any` as much as possible; prefer precise types and generics.
  - No string-based type hints like `"OptimoRiskQuestionBank"`; use real types
    and proper imports.
  - Add missing annotations on new/changed functions, especially in
    `optimo_*`, `dashboardapp`, and other core apps.
- Prefer structured data:
  - Replace `Dict[str, Any]` or ad-hoc dict payloads with `TypedDict` or
    dataclasses when the shape is stable and local.
  - Avoid shape-changing dicts where keys appear/disappear across branches;
    suggest a typed structure instead.

### Tests and fixtures

- Avoid repeating fixtures or introducing fixture collisions:
  - Prefer existing rich fixtures described in `AGENTS.md` (e.g. `responses`
    in survey tests, company/survey fixtures that respect multi-tenant
    relationships).
  - Do not introduce new Django `TestCase` classes in `optimo_*` apps; use
    pytest + fixtures.
  - Watch for multi-tenant fixture mismatches (e.g. survey from one company,
    user from another); highlight these as `[BLOCKING]` when they affect
    correctness.
- When touching tests:
  - Prefer pytest fixtures and helper factories.
  - Avoid local imports inside tests; use module-level imports.

### ORM and query patterns

- Use reverse relations where it reduces imports and improves clarity:
  - Prefer `company.surveys.all()` to `Survey.objects.filter(company=company)`
    when it avoids extra imports and is idiomatic.
- Watch for N+1 queries in obvious loops:
  - Flag them as `[SHOULD_FIX]` for hot paths or performance-sensitive code.

### Commented / dead code and debug artifacts

- Remove obvious debug leftovers:
  - `print(...)`, `pdb.set_trace()`, `ipdb.set_trace()`, `breakpoint()` in
    non-test code.
- Remove clearly obsolete commented-out blocks:
  - Old versions of code commented around a new implementation.
- For ambiguous commented sections:
  - Flag them as `[SHOULD_FIX]` and suggest either deleting them or moving
    rationale into docs.
- `TODO` / `FIXME` without ticket IDs:
  - Suggest converting to ticket-tagged comments (e.g. `TODO(GH-123): ...` or
    `TODO(27pfu0): ...`) or moving the note into ClickUp.

### String / formatting style

- Migrate to f-strings where it improves clarity:
  - Replace old `%` formatting or `.format()` with f-strings when not blocked
    by translation/i18n constraints.
- Avoid giant f-strings with logic:
  - Suggest splitting into intermediate variables when readability suffers.

### Security & secrets

- Detect obvious secrets checked into code or fixtures:
  - Hardcoded tokens, passwords, API keys.
  - Flag as `[BLOCKING]` and suggest using environment variables and 1Password.
- Avoid staging obvious secret-heavy files:
  - `.env`, `google_creds.json`, `google_drive_creds.json`, etc.
  - Recommend un-staging and `.gitignore` updates where appropriate.

### Migrations and schema changes

- Do **not** change migration behavior automatically; instead:
  - Detect destructive schema changes (dropping fields/tables) combined with
    code changes that still expect those fields:
    - Mark as `[BLOCKING]` and recommend a two-step rollout:
      - PR 1: remove usage in code, keep schema.
      - PR 2: drop the field/table once code is clean.
  - Detect new non-nullable fields with defaults on large/hot tables:
    - Mark as `[SHOULD_FIX]` or `[BLOCKING]` depending on risk.
    - Suggest the safer pattern:
      - Add nullable field with no default.
      - Backfill in batches.
      - Then add default for new rows only.
  - Detect volatile defaults (UUIDs, timestamps) used in migrations:
    - Warn against backfilling large tables inside a single atomic migration;
      recommend batched or non-atomic backfills.

### Critical backend patterns from AGENTS.md

- Watch for new instances of patterns explicitly banned in backend `AGENTS.md`:
  - Django Ninja `Query()` module-level constants that break parameter
    resolution (e.g. `Q_INCLUDE_INACTIVE = Query(False, ...)`).
  - Legacy survey models like `OptimoEmployeeSurvey` or `employee_survey`.
  - Any other CRITICAL warnings spelled out in that file.
- Treat any new usage of these patterns as `[BLOCKING]`.

## Atomic-Commit Mode – Extra Strictness

In `atomic-commit` mode (invoked via `/backend-atomic-commit:atomic-commit`),
you must be **very strict**:

1. **Atomicity of staged changes**
   - From `git diff --cached --name-only`, determine if staged changes belong
     to one coherent change:
     - Example of non-atomic:
       - Refactor in `survey/` plus an unrelated optimo bugfix and docs tweak.
   - Emit:
     - `[BLOCKING]` if the staged set is clearly multiple logical changes.
     - `[SHOULD_FIX]` for minor opportunistic cleanups that could be split.
   - You may suggest a split (e.g. “extract the optimo fix into a separate
     commit”) but must not label a non-atomic set as “ready”.

2. **All gates must be green**
   - The commit is **not** ready if any of these fail:
     - `./.security/ruff_pr_diff.sh`
     - `./.security/local_imports_pr_diff.sh`
     - `.bin/ruff check` / `ruff format`
     - `.bin/ty check <staged_python_files>` (scoped to modified files only)
     - `.bin/django check` / `manage.py check`
     - Relevant `pytest` subsets for risky changes
     - Pre-commit hooks defined in `.pre-commit-config.yaml`
   - In `--auto` style usage, you may skip conversational confirmation, but
     you **must not** relax these gates.
   - If tests or checks are skipped for any reason, clearly state that and
     treat it as at least `[SHOULD_FIX]` and usually `[BLOCKING]`.

3. **Commit message generation (no AI signature)**

- Extract ticket ID from branch name using repo conventions:
  - For the Diversio backend:
    - Branch name: `clickup_<ticket_id>_...`
    - Commit format per `AGENTS.md`: `<ticket_id>: Description`.
  - If commit message hooks like `commit_msg_hook.py` exist:
    - Avoid double-prefixing ticket IDs.
    - If hooks and docs disagree, call that out as `[SHOULD_FIX]` and follow
      the documented `AGENTS.md` convention for suggestions.
- Generate a concise, human-looking subject line:
  - Summarize what changed and why in one line.
  - Do **not** mention Claude, AI, this Skill, or plugin names.
- Do **not** add any footer or signature:
  - No “via Claude Code”.
  - No “Generated by backend-atomic-commit”.
  - Commit messages must look like a human wrote them.

4. **Final preview and verdict**

Your `atomic-commit` output should include:

- A short summary of what was checked.
- `Checks run` – listing each gate and its status.
- `What’s aligned` – strengths and good patterns in the staged changes.
- `Needs changes` – bullets with `[BLOCKING]`, `[SHOULD_FIX]`, `[NIT]`.
- `Proposed commit` – suggested commit message and list of files.
- An explicit verdict:
  - “✅ Commit ready” only if there are **no `[BLOCKING]` items**.
  - Otherwise:
    - “❌ Not ready to commit” with concrete next steps.

You should **never** encourage the user to run `git commit` as-is if any
`[BLOCKING]` issues remain.

## Pre-Commit Mode – Fixing Without Committing

In `pre-commit` mode (invoked via `/backend-atomic-commit:pre-commit`):

- You may aggressively auto-fix:
  - Formatting, linting, local imports, obvious type hints, logging patterns,
    removal of debug code, and consistent fixtures.
- You must:
  - Run the same gates described above (Ruff, `.security/*`, ty, Django
    checks, tests as appropriate).
  - Re-run or re-stage files modified by tools or hooks.
- You do **not** propose a commit or check atomicity.
- Your output should focus on:
  - `Fixes applied` – concrete edits you made.
  - `Remaining issues` – with severity tags.
  - `Checks run` – which gates passed/failed.

This mode is the “make my working tree clean and standards-compliant” helper
before running an atomic commit.

## Severity Tags & Output Shape

Always structure findings using severity tags and sections:

- `[BLOCKING]` – must be fixed before a commit is considered ready:
  - Failing `.security` scripts or pre-commit hooks.
  - New banned patterns from `AGENTS.md` (e.g., Ninja Query constants, legacy
    survey models).
  - Obvious multi-tenant or security regressions.
  - Non-atomic staged changes in `atomic-commit` mode.
- `[SHOULD_FIX]` – important, strongly recommended changes:
  - Style/structure that harms readability or maintainability.
  - Missing type hints where types are clear.
  - Ambiguous commented code or TODOs without tickets.
  - Missing tests for non-trivial new behavior.
- `[NIT]` – minor cleanups:
  - Docstring tone/punctuation.
  - Minor naming and formatting nits not covered by Ruff.

Output shape for both modes:

- 1–3 sentence summary of what was checked.
- Sections (when appropriate):
  - `What’s aligned`
  - `Needs changes`
  - `Checks run`
  - `Proposed commit` (only in atomic-commit mode)

Be direct, specific, and actionable in each bullet, pointing to file/area and
suggesting concrete corrections. Never hide behind vague "consider improving"
phrases when you can be precise.

## Compatibility Notes

This skill is designed to work with both **Claude Code** and **OpenAI Codex**.

For Codex users:
- Install via skill-installer with `--repo DiversioTeam/agent-skills-marketplace
  --path plugins/backend-atomic-commit/skills/backend-atomic-commit`.
- Use `$skill backend-atomic-commit` to invoke.

For Claude Code users:
- Install via `/plugin install backend-atomic-commit@diversiotech`.
- Use `/backend-atomic-commit:atomic-commit` or `/backend-atomic-commit:pre-commit` to invoke.
