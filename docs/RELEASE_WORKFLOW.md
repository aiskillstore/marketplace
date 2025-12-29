# Release Workflow

> Version: 1.0.0 | Last Updated: 2025-12-29

This document describes the release workflow system for the AI Skillstore marketplace, including versioning strategy, changelog generation, and Supabase synchronization.

## Overview

The release system automates:
- Semantic version bumping
- Changelog generation from commit history
- AI-powered release summaries
- GitHub Release creation
- Supabase database synchronization for skillstore.io

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Manual Trigger: Actions → "Create Release" → Run workflow  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  release.yml                                                │
│  ├── Calculate new version (major/minor/patch)              │
│  ├── Analyze commits → find new/updated plugins             │
│  ├── Generate AI summary (GPT-5.2)                          │
│  ├── Update marketplace.json version + released_at          │
│  ├── Update CHANGELOG.md with new entry                     │
│  ├── Create git tag (vX.Y.Z)                                │
│  ├── Create GitHub Release with notes                       │
│  └── Sync to Supabase (skillstore.releases table)           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Supabase skillstore.releases                               │
│  ├── Creates records for all 11 languages                   │
│  ├── Sets is_latest = true (previous = false)               │
│  └── Stores: tag, version, summary, changelog, counts       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  skillstore.io/releases                                     │
│  ├── /releases → List all releases                          │
│  └── /releases/vX.Y.Z → Release detail page                 │
└─────────────────────────────────────────────────────────────┘
```

## Workflow Files

| File | Trigger | Purpose |
|------|---------|---------|
| `release.yml` | Manual (workflow_dispatch) | Primary release workflow |
| `on-release-published.yml` | GitHub release event | Backup sync for manual releases |

## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):

| Bump Type | When to Use | Example |
|-----------|-------------|---------|
| `major` | Breaking schema changes, CLI incompatibility | 1.0.0 → 2.0.0 |
| `minor` | New plugins added | 1.0.0 → 1.1.0 |
| `patch` | Plugin updates, bug fixes, documentation | 1.0.0 → 1.0.1 |

### Version Storage

- **marketplace.json**: `metadata.version` and `metadata.released_at`
- **Git tags**: `vX.Y.Z` format
- **Supabase**: `skillstore.releases.version` column

## How to Create a Release

### Step 1: Navigate to GitHub Actions

1. Go to [aiskillstore/marketplace](https://github.com/aiskillstore/marketplace)
2. Click **Actions** tab
3. Select **"Create Release"** workflow
4. Click **"Run workflow"**

### Step 2: Configure Release

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `bump_type` | Yes | `minor` | Version bump: major, minor, or patch |
| `release_summary` | No | AI-generated | Custom release summary (optional) |

### Step 3: Monitor Workflow

The workflow will:

1. ✅ Calculate new version number
2. ✅ Analyze commits since last tag
3. ✅ Generate AI summary (if not provided)
4. ✅ Update `marketplace.json`
5. ✅ Update `CHANGELOG.md`
6. ✅ Commit and push changes
7. ✅ Create git tag
8. ✅ Create GitHub Release
9. ✅ Sync to Supabase (all languages)

### Step 4: Verify

- Check [Releases page](https://github.com/aiskillstore/marketplace/releases)
- Verify [skillstore.io/releases](https://skillstore.io/releases) shows the new release

## Changelog Format

The `CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [1.1.0] - 2025-12-30

### Summary

Marketplace update with 2 new plugins for document processing.

### Statistics

- Total plugins: 18
- New plugins: 2
- Updated plugins: 0

### New Plugins

- `new-plugin-1`
- `new-plugin-2`

### Infrastructure Changes

- feat: improved security scanning
- fix: resolved sync issue
```

## Supabase Integration

### Table: `skillstore.releases`

| Column | Type | Description |
|--------|------|-------------|
| `tag` | TEXT | Version tag (e.g., "v1.1.0") |
| `version` | TEXT | Version number (e.g., "1.1.0") |
| `release_date` | DATE | Release date |
| `skill_count` | INTEGER | Total plugins in marketplace |
| `summary` | TEXT | Release summary |
| `changelog` | JSONB | Structured changelog data |
| `added_count` | INTEGER | New plugins added |
| `updated_count` | INTEGER | Plugins updated |
| `removed_count` | INTEGER | Plugins removed |
| `is_latest` | BOOLEAN | Whether this is the latest release |
| `language` | VARCHAR(10) | Language code (en, zh-hans, etc.) |

### Supported Languages

Releases are synced for all 11 supported languages:

- `en` - English
- `zh-hans` - Simplified Chinese
- `zh-hant` - Traditional Chinese
- `ja` - Japanese
- `ko` - Korean
- `de` - German
- `fr` - French
- `es` - Spanish
- `pt` - Portuguese
- `ru` - Russian
- `ar` - Arabic

## API Endpoints

### List Releases

```
GET /api/releases?lang=en
```

Response:
```json
{
  "data": [
    {
      "tag": "v1.1.0",
      "date": "2025-12-30",
      "skillCount": 18,
      "added": 2,
      "updated": 0
    }
  ],
  "total": 5
}
```

### Get Release Detail

```
GET /api/releases/v1.1.0?lang=en
```

Response:
```json
{
  "data": {
    "tag": "v1.1.0",
    "version": "1.1.0",
    "date": "2025-12-30",
    "skillCount": 18,
    "summary": "...",
    "changelog": {...},
    "added": 2,
    "updated": 0,
    "removed": 0,
    "isLatest": true
  }
}
```

## Troubleshooting

### Release Not Showing on Website

1. Check workflow run completed successfully
2. Verify Supabase sync step passed
3. Check `skillstore.releases` table directly:
   ```sql
   SELECT * FROM skillstore.releases WHERE tag = 'vX.Y.Z';
   ```

### AI Summary Generation Failed

The workflow falls back to a generic summary:
```
"Marketplace update with N new plugins. Total M plugins available."
```

To use custom summary, provide it in the `release_summary` input.

### Duplicate Release Error

If a tag already exists:
1. Delete the existing tag: `git push --delete origin vX.Y.Z`
2. Delete the GitHub Release
3. Re-run the workflow

## Environment Variables

Required secrets in GitHub Actions:

| Secret | Description |
|--------|-------------|
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |

AI API (hardcoded in workflow):

| Variable | Value |
|----------|-------|
| `AI_API_URL` | `http://192.168.199.7:3001/v1` |
| `AI_MODEL` | `gpt-5.2:high` |

## Best Practices

1. **Release after plugin approvals**: Wait until PRs are merged before releasing
2. **Use minor for new plugins**: Default bump type for adding plugins
3. **Use patch for fixes**: Infrastructure changes, bug fixes
4. **Review changelog**: Verify the auto-generated changelog is accurate
5. **Monitor sync**: Ensure Supabase sync completes successfully

## Related Documentation

- [MARKETPLACE_ARCHITECTURE.md](./MARKETPLACE_ARCHITECTURE.md) - Overall system architecture
- [CHANGELOG.md](../CHANGELOG.md) - Release history
- [README.md](../README.md) - Quick start guide
