---
name: momentic-explore-prompt
description: Generate an explore-prompt.md file that gives Momentic's explore agent (`momentic ai explore diff` / `momentic ai explore latest`) repo-specific context — which applications to test, the URLs tests must target, how to authenticate, where to save generated tests, and repo quirks. Use when setting up or improving the prompt file passed via `--prompt-file`.
---

# Generating an explore-prompt.md

## What this file is

The explore agent (`momentic ai explore diff` over a git range, or
`momentic ai explore latest` over the whole app) identifies changed user
journeys and builds Momentic tests for them. Both accept extra instructions
appended to the explorer's system prompt via two repeatable options:

- `--prompt <text>` — inline text. Repeatable.
- `--prompt-file <path>` — a file whose contents are appended. Repeatable.

Passing any `--prompt` or `--prompt-file` replaces the project's cloud custom
prompt. The combined instructions are all `--prompt-file` contents followed by
all `--prompt` values, each in the order passed — so multiple flags stack rather
than one overriding the other.

`explore-prompt.md` is the conventional file passed to `--prompt-file`. It is
**repo-specific**: it tells the explorer which apps exist in this repo, the URLs
its tests must target, how to sign in, exactly where to save generated tests,
and any quirks it must respect. It is NOT a place to restate general Momentic
behavior — that already lives in the `momentic-test` skill.

Usage:

```sh
momentic ai explore diff --prompt-file ./explore-prompt.md
```

## Gather the repo facts first

Do not write the prompt from memory. Inspect the repo and confirm each fact:

1. **Applications under test.** Enumerate every frontend/app the generated
   tests will drive. For each, determine the URL the **tests** must hit. This is
   the served/deployed URL used at run time, which is often NOT the Vite/dev URL
   used while authoring locally. Cross-check `momentic.config.yaml`
   `environments[].baseUrl` and how each app is started in CI (the workflow that
   runs `momentic ai explore diff`).
2. **Authentication.** How should the explorer sign in? Prefer a reusable login
   module — record its exact `name` and `id`. Note access assumptions (e.g. "this
   user can reach all parts of the app").
3. **Test placement.** The folder each app's tests belong in, expressed relative
   to the workspace, including any mandatory path prefix. Make the constraints
   unambiguous.
4. **Throwaway / nested tests.** Where tests created as a side effect of an
   explore run must be saved (usually the single gitignored `momentic/junk/`
   folder). Confirm which path is gitignored.
5. **Quirks.** Externally-persisted data that survives runs (must be randomized
   per run to avoid collisions), auth peculiarities, flaky areas, base-URL
   caching flags, etc.

## Structure to produce

Write concise, imperative markdown. Recommended sections:

- **Applications and target URLs** — one bullet per app: name — the URL tests
  must target — purpose — how it is served/run — the login module (name + id) if
  auth is required.
- **Journey → application mapping** — how to map an in-scope diff to the app(s)
  it affects so the right editor/port is driven.
- **Test placement rules** — the destination folder per app, with explicit
  `HARD RULE` callouts for any mandatory prefix. The explorer will otherwise
  save tests in the wrong place.
- **Throwaway / nested test rule** — the gitignored junk folder that every
  nested test must land in, and that naming a file `junk-*` does NOT count.
- **Quirks to watch out for** — the repo-specific gotchas gathered above.

## Rules for a good prompt

- Target URLs must be the URLs tests actually run against, never the authoring
  dev-server URLs.
- Be explicit about path constraints and use `HARD RULE:` callouts — path
  mistakes are the most common and most costly explorer failure.
- Keep it repo-specific and short. Omit anything already covered by general
  Momentic docs/skills.
- Reference login modules by both `name` and `id` so the explorer can pin the
  exact module.

## Reference template

Below is a placeholder-only skeleton with the sections a good prompt has. Fill
in the bracketed values with your repo's real apps, URLs, modules, and folders —
do not ship the placeholders.

```md
This repo has <N> frontend application(s). When tests run, each app is served at
the URL below — target these, not the dev-server URLs used while authoring.

- <app-name> — <one-line purpose> at <https://url-tests-must-target>. Sign in
  first using the module named `<login-module-name>` (id: <login-module-id>).
  <access assumptions, e.g. this user can reach all parts of the app>.
- <app-name-2> — <purpose> at <https://url-2>. Tests MUST use <https://url-2>
  as their base URL.

When identifying changed user journeys, map each in-scope diff to the
application(s) above so the right app/port is driven.

Place new tests in the folder matching the app they drive. Every target path is
relative to your workspace and the `<mandatory-prefix>/` segment is MANDATORY —
never drop it:

- <app-name> journeys → <mandatory-prefix>/<app-folder>/.
- <app-name-2> journeys → <mandatory-prefix>/<app-2-folder>/.

HARD RULE — keep the `<mandatory-prefix>/` prefix on the authored test. Saving
to any path that omits it is a hard failure.

HARD RULE: any test created as a side effect of building another test is
throwaway and MUST be saved into the gitignored `<junk-folder>/` directory.
Naming a file `junk-*` does NOT count — only that directory is gitignored.

Some quirks to watch out for:

- <quirk, e.g. externally-synced data persists across runs — randomize any data
  you write each run so runs don't conflict>.
```
