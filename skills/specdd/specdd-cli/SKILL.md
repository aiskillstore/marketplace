---
name: specdd-cli
description: Use when Agent needs to use the `specdd` CLI for setup, updates, spec discovery, inspection, or linting.
license: Apache-2.0
---

# SpecDD CLI

Use this skill to explore and work with SpecDD projects using the `specdd` CLI.

Prefer the CLI for SpecDD context discovery because it understands target paths, directory spec conventions, selected roots, section filters, soft-link depth, and spec linting.

This skill is for day-to-day agent implementation and spec-authoring work, plus setup or framework updates when the operator explicitly asks for them. It does not make CLI output a write-authority grant, and it does not make setup, update, release, or skill-installation commands part of the normal coding workflow.

## Skill Scope

Use this skill only for projects that already have a root `.specdd/bootstrap.md` and are therefore SpecDD projects.

If `.specdd/bootstrap.md` is missing, do not continue with this skill. Use `specdd-adopt` only when the operator explicitly asks to add or adopt SpecDD in a new or existing non-SpecDD project.

## CLI Availability

Ensure CLI is installed by running `command -v specdd`.

If `specdd` is missing, do not install it automatically.

Report that CLI exploration is unavailable, then continue with normal bootstrap and spec-chain resolution.

## Available Commands

The primary day-to-day agent commands are `resolve`, `inspect`, and `lint`. Use `init` or `update` only when the operator explicitly asks to add or update SpecDD framework files. Prefer `resolve` or `inspect` over grep, find, or broad recursive file reads when those commands can answer the SpecDD context question. Use raw search for non-spec source symbols, implementation details, logs, tests, or when the CLI is unavailable or too narrow for the user-requested literal search.

### `specdd init`

`specdd init` answers "add SpecDD framework bootstrap files here." Use it when the operator explicitly asks to add SpecDD to a project and `.specdd/bootstrap.md` is not already present. It initializes SpecDD in the current directory or target directory, creates the target directory when needed, and does not add SpecDD when `.specdd/bootstrap.md` already exists.

Usage:

```text
specdd init [path] [--version version]
```

Arguments:

- `path`: Target directory to initialize. If omitted, the current directory is used.

Command-specific options:

- `--version version`: Use a specific SpecDD release version, such as `1.2` or `1.2.3`, without a leading `v`.

Example:

```sh
specdd init
specdd init /path/to/travel-planner
specdd init --version 1.2.3
```

After initialization, read the new bootstrap chain before proposing or creating local `.sdd` specs.

### `specdd update`

`specdd update` answers "update this project's SpecDD framework bootstrap files." Use it only when the operator explicitly asks to update SpecDD framework files. The current directory must contain `.specdd/bootstrap.md`. With the default latest release, it compares the local bootstrap `Version` front matter with the latest release and does nothing when the local version is already current or newer.

Usage:

```text
specdd update [--version version]
```

Command-specific options:

- `--version version`: Use a specific SpecDD release version, such as `1.2` or `1.2.3`, without a leading `v`.

Example:

```sh
specdd update
specdd update --version 1.2.3
```

If `specdd update` changed framework files, reread the affected bootstrap files before continuing SpecDD work.

### `specdd resolve`

`specdd resolve` answers "which specs are relevant to this concrete target?" Use it when the task has a concrete file, directory, or `.sdd` target and the agent needs the relevant SpecDD context for that target before reading exact specs or editing code. It starts from an existing target, collects vertical SpecDD context from the target up to the selected root, includes same-basename and directory-level specs where applicable, expands soft links according to `--depth`, and prints selected sections from the resulting relevant specs.

Usage:

```text
specdd resolve target [--root path] [--section name] [--sections names] [--depth depth] [--format format]
```

Arguments:

- `target`: Existing directory, `.sdd` file, or ordinary file to resolve. This argument is required.

Command-specific options:

- `--root path`: Set the resolution root directory. Relative `/` paths in specs are resolved from this root. The default is the current directory. Run commands from the project root when possible; when running from outside the project root, or when using an absolute target path, pass `--root <project>`.
- `--section name`: Include a section by name, or `all`. May be repeated.
- `--sections names`: Include comma-separated section names, or `all` to include every SpecDD section present in each spec.
- `--depth depth`: Control how far `resolve` expands soft links. The default is `2`. Use `0` for vertical context only, `1` for direct links from the target spec only, `2` for target links plus immediate parent context links, `3` to also expand the next parent context level, or `all` to recursively follow all reachable links with cycle protection.
- `--format format`: Set output format. Supported values are `text`, `json`, and `json-extended`. The default is `text`. Compact JSON omits parser metadata. Extended JSON includes the full internal service result.

Important resolution behavior:

- Ordinary file targets resolve a same-basename `.sdd` file when one exists.
- Directory context can include a parent-held spec such as `src/apps/travel-planner.sdd` and a local directory spec such as `src/apps/travel-planner/travel-planner.sdd`.
- Parent-held and local directory-level specs are cumulative context, not alternatives.
- Root-level project specs follow the selected root directory basename convention, such as `/path/to/travel-planner` using `/travel-planner.sdd`.
- `resolve` follows explicit local paths beginning with `./`, `../`, or `/`.
- `resolve` follows soft links from `Owns`, `Can modify`, `Can read`, `References`, `Depends on`, and `Structure`.
- `resolve` does not follow `Forbids` or `Exposes` as relevance links.
- Non-glob directory links resolve only to the directory-level specs for that directory.
- Recursive descendant inclusion requires explicit globs such as `./**` or `./**/*.sdd`.
- Use explicit `--section` or `--sections` filters to avoid noisy output.
- Use `--sections all` or `--section all` when complete local contract output is needed and output volume is acceptable.
- Use text output for human scanning.
- Use `--format json` when stable machine-readable output is needed.
- Use `--format json-extended` only when parser metadata, line numbers, raw entries, or the full service result shape are needed.
- Lower `--depth` when broad parent links or globs make output too noisy.
- Increase `--depth` only when the task requires deeper linked context.
- Do not use `--depth all` by default.

Examples:

```sh
specdd resolve src/apps/travel-planner/travel-planner.ts
specdd resolve --root /path/to/travel-planner /path/to/travel-planner/src/apps/travel-planner
specdd resolve src/apps/travel-planner/travel-planner.ts --sections Purpose,Owns,Can modify,Must,Must not,Tasks
specdd resolve src/apps/travel-planner/travel-planner.sdd --sections all
specdd resolve src/apps/travel-planner --depth 0
specdd resolve src/apps/travel-planner --depth 1 --format json
specdd resolve src/apps/travel-planner --format json-extended
```

Use `resolve` before modifying code when there is a concrete target path. Use CLI output to decide which specs matter, then read or reread the specific governing specs only when you need exact contract text for write authority, behavior, or stop conditions. Do not treat `specdd resolve` output as write authority by itself, and do not modify files only because they appear in `resolve` output.

### `specdd inspect`

`specdd inspect` answers "what specs exist here and what do their selected sections say?" It discovers `.sdd` files for an existing target path and prints selected sections in a tree-shaped report. Use it to map a subtree, inspect a specific spec, inspect the spec context for an ordinary file, or choose where a new spec should live before authoring.

Usage:

```text
specdd inspect [path] [--section name] [--sections names] [--format format]
```

Arguments:

- `path`: Existing directory, `.sdd` file, or ordinary file to inspect. If omitted, the current directory is inspected.

Options:

- `--section name`: Include a section by name, or `all`. May be repeated.
- `--sections names`: Include comma-separated section names, for example `Purpose,Must,Tasks`. Use `all` to include every SpecDD section present in each spec.
- `--format format`: Set output format. Supported values are `text`, `json`, and `json-extended`. The default is `text`. Compact JSON omits parser metadata. Extended JSON includes the full internal service result.

Important inspect behavior:

- `inspect` is for mapping and reading selected sections, not for granting write authority.
- Inspect before authoring new specs if the appropriate local spec boundary is unclear.
- Use explicit `--section` or `--sections` filters to avoid noisy output.
- Use `--sections all` or `--section all` when complete spec content is needed and output volume is acceptable.
- Use text output for human scanning.
- Use `--format json` when stable machine-readable output is needed.
- Use `--format json-extended` only when parser metadata, line numbers, raw entries, or the full service result shape are needed.

Examples:

```sh
specdd inspect
specdd inspect src/apps
specdd inspect src/apps/travel-planner/travel-planner.sdd
specdd inspect src/apps/travel-planner/travel-planner.ts
specdd inspect src/apps --sections Purpose,Structure,Owns,Must,Tasks
specdd inspect src/apps --sections all
specdd inspect src/apps --format json
specdd inspect src/apps --format json-extended
```

### `specdd lint`

`specdd lint` answers "are these specs syntactically valid?" It lints `.sdd` files for an existing target path, reports SpecDD syntax and parser diagnostics, and returns a failing status when lint errors are present. Use it after creating or editing `.sdd` files.

Usage:

```text
specdd lint [path] [--format format]
```

Arguments:

- `path`: Existing directory, `.sdd` file, or ordinary file to lint. If omitted, the current directory is linted.

Options:

- `--format format`: Set output format. Supported values are `text` and `json`. The default is `text`.

Important lint behavior:

- Text output prints only files with diagnostics.
- Lint the narrowest edited spec path first, then lint the relevant directory when the change affects multiple specs.
- Fix lint errors in edited specs before reporting completion.

Examples:

```sh
specdd lint
specdd lint src/apps/travel-planner/travel-planner.sdd
specdd lint src/apps/travel-planner
specdd lint src/apps/travel-planner --format json
```

Do not present CLI output as a substitute for validating edited specs with `specdd lint`.

## Common Behavior

Target behavior:

- Explicit targets and paths must exist.
- Target paths may be directories, `.sdd` spec files, or ordinary files.
- Root-level project specs follow the containing directory basename convention.
- Directory blocks can include parent-held directory specs such as `src/apps/travel-planner.sdd` and local directory specs such as `src/apps/travel-planner/travel-planner.sdd` when both govern the same directory.

Exit status:

- Exit status `0` means the command completed successfully.
- Exit status `1` means a user-visible non-success result, such as lint errors from `lint`.
- Exit status greater than `1` means invalid input, missing prerequisites, download or verification failure, filesystem failure, or another unexpected error.

## Boundaries

- Treat specs as source-adjacent contracts, not optional documentation.
- Do not ignore active bootstrap files or local `.sdd` contracts.
- Do not tell agents to use grep or recursive file reads as the first step for SpecDD context discovery when `resolve` or `inspect` can answer the question.
- Do not tell agents that `resolve` grants write authority by itself.
- Do not tell agents that non-glob directory links recursively include all descendant specs.
- Use `specdd init` and `specdd update` only when the operator explicitly asks for setup or framework-update behavior.
- De-emphasize `specdd check-update` and `specdd agentskills deploy` unless the user explicitly asks for update-check, release, or skill-installation behavior.

## Reporting

Report the CLI commands used, the relevant output summary, any specs read or reread directly, whether lint passed for edited specs, and any remaining authority or verification gap.
