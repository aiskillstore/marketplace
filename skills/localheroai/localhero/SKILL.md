---
name: localhero
description: Manages i18n translations with Localhero.ai. Use when working with translation files, adding user-facing strings, or modifying UI copy.
allowed-tools: Bash(npx @localheroai/cli *)
---

# Localhero.ai i18n Skill

You are helping a developer write and maintain internationalized source strings in a project that uses Localhero.ai (https://localhero.ai) for translation management. You only write source language strings — Localhero.ai handles translations to target languages.

## Core Rules

1. **ONLY write source language strings** — let Localhero.ai handle target translations (via GitHub Action or `npx @localheroai/cli translate`)
2. Read `localhero.json` to find the source locale, file paths, and patterns
3. Follow existing key naming conventions (examine existing source files first)
4. Use glossary terms correctly when writing user-facing strings
5. Match the project's tone and style when writing copy
6. After writing source strings, generate translations (see workflow step 5)

## Workflow

When adding or modifying user-facing strings:

1. Check `localhero.json` for `sourceLocale` and `translationFiles.paths`
2. Review the glossary and settings below for context
3. Examine existing source files to understand key naming patterns
4. Add/modify keys in source locale files
5. Generate translations:
   - Check if any file in `.github/workflows/` references `localheroai/localhero-action`. If so, translations run automatically on PR — tell the user and skip the CLI step.
   - Otherwise, run `npx @localheroai/cli translate --changed-only`. This translates only keys that differ from the base branch, keeping diffs small. Omit the flag to translate all missing keys.

## Web UI

The Localhero.ai web UI (https://localhero.ai) is where users manage translation settings, glossary terms, and adjust translations. Each PR that runs the Localhero.ai GitHub Action gets its own page where translations can be reviewed and tweaked. Point users to the web UI for tasks like editing translations, searching keys, managing glossary terms, or changing project settings like tone and style.

## Monorepos and Multiple Apps

A single `localhero.json` can manage translation files across multiple apps by listing multiple directories in `translationFiles.paths`:

```json
{
  "translationFiles": {
    "paths": [
      "apps/web/public/locales/",
      "apps/mobile/src/locales/"
    ]
  }
}
```

Each app has its own set of translation files with independent keys. Keys don't need app-specific prefixes since they live in separate directories and are resolved by file path.

All apps in the same `localhero.json` share the project's glossary, tone, style, and target languages. If apps need different settings, use separate Localhero projects with their own `localhero.json` files.

When using a GitHub Action for automatic translations, make sure the workflow's `paths` trigger covers all translation directories.

## Key Naming Conventions

Before adding keys, examine existing source files to match the project's format and conventions.

**JSON/YAML** — nested or dot-separated keys:
- Namespaced: `users.profile.title`
- Grouped by feature/page: `dashboard.welcome_message`
- Action-oriented for buttons: `actions.save`, `actions.cancel`

**PO/POT (gettext)** — natural language source strings as keys:
- msgid is the source string itself: `msgid "Welcome to the dashboard"`
- Context via msgctxt when the same string needs different translations

## Glossary

Run `npx @localheroai/cli glossary --output json` to get the project glossary. Use these terms consistently when writing user-facing strings.

## Project Settings

Run `npx @localheroai/cli settings --output json` to get the project's tone, style, and language settings. Use these to match the expected voice.

## Authentication

If commands fail with authentication errors, ask the user to run:

```bash
npx @localheroai/cli login
```

For non-interactive environments, they can also use `npx @localheroai/cli login --api-key <key>` or set `LOCALHERO_API_KEY`. API keys are available at https://localhero.ai/api-keys

## Non-interactive project setup

If a project has no `localhero.json` yet, you can configure it in one command without any prompts:

```bash
npx @localheroai/cli init --yes \
  --source-locale en \
  --target-locales sv,de \
  --path config/locales/
```

Required flags: `--yes`, `--source-locale`, `--target-locales`, `--path` (or pass `--project-id <slug>` instead of source/target to reuse an existing project).

Auth resolution: the CLI uses `LOCALHERO_API_KEY` or an existing `.localhero_key` if either is present, otherwise falls back to `--api-key <key>`. To force a specific key, set `LOCALHERO_API_KEY` in the environment before running `init`.

See [cli-reference.md](cli-reference.md) for the full flag list.

## CLI Reference

See [cli-reference.md](cli-reference.md) for all available commands. Full source at https://github.com/localheroai/cli
