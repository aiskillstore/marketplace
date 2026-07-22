---
name: git-commit-writer-free
description: Generate conventional commit messages from staged git changes. Use when the user asks to write commit message, generate commit, what should my commit say, or after the user runs git add and wants a commit message for staged files.
metadata:
  version: 1.0.0
  author: JustHandled Labs
  triggers:
  - write commit message
  - generate commit
  - what should my commit say
  - git add
---
# Git Commit Writer

Generate a conventional commit message from staged changes only.

## Workflow

1. Run `git status --short`.
2. Determine whether any files are staged by checking the first status column for anything other than a space or `?`.
3. If no files are staged, do not suggest a commit message. Tell the user to stage changes first with `git add <files>` or `git add .`.
4. Run `git diff --cached --stat` to summarize staged file impact.
5. Run `git diff --cached` to inspect the staged patch.
6. Analyze the staged changes and return one primary commit recommendation in conventional commit format, plus optional alternatives if useful.

Use only staged changes. Do not base the commit message on unstaged, untracked, or working-tree-only changes.

## Required Commands

```bash
git status --short
git diff --cached --stat
git diff --cached
```

If `git diff --cached` is empty, the correct response is:

```text
No staged changes found. Run `git add <files>` first, then ask me to write the commit message.
```

## Commit Format

Use this format:

```text
type(scope): imperative summary

- Optional bullet describing notable staged change
- Optional bullet describing another notable staged change
```

Use `type(scope)!: summary` when the staged changes introduce a breaking change.

Keep the summary under 72 characters when practical. Use imperative mood: `add`, `fix`, `update`, `remove`, `refactor`, not `added`, `fixed`, or `updates`.

## Type Reference

- `feat`: Adds or exposes user-facing functionality.
- `fix`: Fixes a bug, regression, crash, bad output, broken state, or incorrect behavior.
- `docs`: Changes documentation only.
- `style`: Changes formatting, whitespace, lint-only style, or visual styling without behavior changes.
- `refactor`: Restructures code without intended behavior change.
- `test`: Adds or changes tests, fixtures, mocks, or test infrastructure.
- `chore`: Changes maintenance files, build config, dependencies, scripts, metadata, or repository housekeeping.

When multiple types apply, choose the type that best represents the user-visible reason for the commit. Prefer `feat` or `fix` over `chore` when product behavior changes. Prefer `test` only when the commit is primarily test work.

## Scope Detection Rules

Choose a concise lowercase scope from the most specific shared path or domain:

- `src/auth/`, `app/auth/`, `lib/auth/`, login, session, password, OAuth, token: `auth`
- `src/api/`, `app/api/`, routes, controllers, endpoints, request/response contracts: `api`
- `src/ui/`, `components/`, `pages/`, `views/`, templates, CSS tied to interface changes: `ui`
- `tests/`, `test/`, `__tests__/`, specs, fixtures, mocks: `test`
- `.github/`, workflow files, CI config: `ci`
- `package.json`, lockfiles, dependency manifests: `deps`
- docs, README, markdown guides: `docs`
- build tools, bundlers, release scripts: `build`
- database migrations, schema files, SQL models: `db`

If staged files share a clear parent directory, use that parent directory name as the scope, such as `auth` for `src/auth/reset.ts`. If no useful scope exists, omit the scope: `chore: update repository metadata`.

For multi-area changes, choose the scope that matches the main intent. If the commit genuinely spans unrelated areas, omit scope or use a broad existing project term such as `core`.

## Breaking Change Detection

Add `!` after the type or scope when staged changes appear to break downstream callers or users. Treat these as breaking indicators:

- Public function, method, class, CLI command, endpoint, event, config, schema, or exported type is removed or renamed.
- Required parameters are added to public APIs.
- Parameter order or return shape changes for exported functions or documented endpoints.
- Database schema changes remove columns, rename columns, or add non-null required fields without defaults.
- CLI flags, environment variables, config keys, or response fields are removed or renamed.
- The diff or docs explicitly mention `BREAKING CHANGE`, `breaking`, `migration required`, or an incompatible version bump.

Do not mark `!` for internal-only refactors unless there is clear evidence of public contract impact.

## Output Rules

- Start with the recommended commit message in a fenced `text` block.
- Include 2-4 short bullets explaining why that message fits when the diff is non-trivial.
- If the type or scope is uncertain, briefly name the uncertainty and provide one alternate message.
- Never invent files or behavior not present in the staged diff.
- Never suggest a commit message when no files are staged.

## Quality Checks

Before answering, verify:

- `git status --short` shows at least one staged file.
- The message reflects staged changes from `git diff --cached`, not unstaged changes.
- Multiple file types are handled by intent, not by extension alone.
- The selected type is one of `feat`, `fix`, `docs`, `style`, `refactor`, `test`, or `chore`.
- The scope is lowercase, concise, and derived from paths or domain terms.
