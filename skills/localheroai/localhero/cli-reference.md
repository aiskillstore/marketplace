# Localhero CLI Reference

## Primary Commands

### `npx @localheroai/cli translate`

Translate missing keys in your i18n files using AI.

```bash
npx @localheroai/cli translate                # Translate all missing keys
npx @localheroai/cli translate --verbose      # Show detailed progress
npx @localheroai/cli translate --changed-only # Only translate keys changed in current branch
npx @localheroai/cli translate --commit       # Auto-commit changes (for CI/CD)
```

### `npx @localheroai/cli push`

Push source files to Localhero.ai for translation management.

```bash
npx @localheroai/cli push            # Push changed files
npx @localheroai/cli push --force    # Push all files regardless of git changes
npx @localheroai/cli push --prune    # Delete keys from API that no longer exist locally
npx @localheroai/cli push --yes      # Skip confirmation prompt
```

### `npx @localheroai/cli pull`

Pull translated files from Localhero.ai to your local project.

```bash
npx @localheroai/cli pull                # Pull all translations
npx @localheroai/cli pull --changed-only # Only pull translations for changed keys
npx @localheroai/cli pull --verbose      # Show detailed progress
```

### `npx @localheroai/cli glossary`

View project glossary terms for consistent terminology.

```bash
npx @localheroai/cli glossary                 # Show all glossary terms
npx @localheroai/cli glossary --output json   # Output as JSON
npx @localheroai/cli glossary --search <term> # Search for specific terms
```

### `npx @localheroai/cli settings`

View project translation settings (tone, style, languages).

```bash
npx @localheroai/cli settings               # Show project settings
npx @localheroai/cli settings --output json # Output as JSON
```

## Setup Commands

### `npx @localheroai/cli login`

Authenticate with Localhero.ai.

```bash
npx @localheroai/cli login                  # Interactive login
npx @localheroai/cli login --api-key tk_xxx # Non-interactive (for CI/scripts)
```

Environment variable alternative: `export LOCALHERO_API_KEY=tk_xxx`

### `npx @localheroai/cli init`

Initialize a new project with `localhero.json` configuration.

```bash
npx @localheroai/cli init  # Interactive project setup
```

**Non-interactive mode (for agents and CI):** Pass `--yes` together with the required flags to create a project without any prompts.

```bash
# New project (requires --source-locale, --target-locales, --path)
npx @localheroai/cli init --yes \
  --source-locale en \
  --target-locales sv,de \
  --path config/locales/

# Reuse an existing project (requires --project-id and --path)
# Project IDs are slugs like "my-app", visible in the web UI URL
npx @localheroai/cli init --yes \
  --project-id my-app \
  --path config/locales/
```

Flags:

| Flag | Description |
|---|---|
| `-y, --yes` | Activate non-interactive mode (required) |
| `--project-id <id>` | Use an existing project (a slug, e.g. `my-app`); locales are read from the project |
| `--project-name <name>` | Name for a new project (defaults to the current directory name) |
| `--source-locale <code>` | Source locale, e.g. `en`. Required without `--project-id` |
| `--target-locales <codes>` | Comma-separated targets, e.g. `sv,de,fr`. Required without `--project-id` |
| `--path <dir>` | Translation files directory. Always required |
| `--pattern <glob>` | Override the detected file pattern |
| `--ignore <paths>` | Comma-separated ignore paths |
| `--api-key <key>` | API key used only when no existing auth is found (see below) |
| `--skip-import` | Do not import existing translation files |
| `--github-action` | Opt in to creating a GitHub Actions workflow (only applies in `--yes` mode; off by default) |

**Auth resolution order:** the CLI first checks `LOCALHERO_API_KEY` env var, then the `.localhero_key` file in the working directory. If either contains a valid key, that key is used and `--api-key` is ignored. Only if neither is present does `--api-key` kick in as a fallback. If none of the three are available, `init --yes` fails with an actionable error.

To force a specific key in an agent workflow, either set `LOCALHERO_API_KEY` in the environment or remove any stale `.localhero_key` before running `init`.

**Re-running `init --yes`:** if `localhero.json` already exists, the command verifies the config against the server and exits 0 without changing it. It runs an initial import only if the project hasn't been synced yet (`lastSyncedAt` is null in the config). Safe to re-run idempotently.

### `npx @localheroai/cli clone`

Download all translation files from Localhero.ai, useful for initial setup or CI/CD builds.

```bash
npx @localheroai/cli clone          # Clone translations
npx @localheroai/cli clone --force  # Override existing files
```

## CI/CD

### `npx @localheroai/cli ci`

Run translations in CI/CD. Auto-detects PR vs main branch context.

```bash
npx @localheroai/cli ci           # Auto-detect mode and translate
npx @localheroai/cli ci --verbose # Show detailed progress
```

## Configuration

### `localhero.json`

Project configuration file created by `npx @localheroai/cli init`:

```json
{
  "schemaVersion": "1.0",
  "projectId": "your-project-slug",
  "sourceLocale": "en",
  "outputLocales": ["sv", "de", "fr"],
  "translationFiles": {
    "paths": ["src/locales/"],
    "ignore": []
  }
}
```

Multiple translation directories (e.g. monorepos with multiple apps):

```json
{
  "translationFiles": {
    "paths": [
      "apps/web/public/locales/",
      "apps/admin/src/locales/"
    ]
  }
}
```

All paths share the same project settings, glossary, and target languages. The CLI processes all paths when running `translate`, `push`, or `pull`.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `LOCALHERO_API_KEY` | API key (alternative to `.localhero_key` file) |
| `LOCALHERO_API_HOST` | Override API host (for development) |

## Global Options

All commands support:
- `--debug` — Show detailed error information and stack traces
