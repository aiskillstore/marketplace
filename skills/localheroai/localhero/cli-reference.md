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

### Environment Variables

| Variable | Description |
|----------|-------------|
| `LOCALHERO_API_KEY` | API key (alternative to `.localhero_key` file) |
| `LOCALHERO_API_HOST` | Override API host (for development) |

## Global Options

All commands support:
- `--debug` — Show detailed error information and stack traces
