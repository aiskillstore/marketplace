---
name: release-skills
description: Release workflow for baoyu-skills plugin. Use when user says "release", "发布", "push", "推送", "new version", "新版本", "bump version", "更新版本", or wants to publish changes to remote. Analyzes changes since last tag, updates CHANGELOG (EN/CN), bumps marketplace.json version, commits, and creates version tag. MUST be used before any git push with uncommitted skill changes.
---

# Release Skills

Automate the release process for baoyu-skills plugin: analyze changes, update changelogs, bump version, commit, and tag.

## CRITICAL: Mandatory Release Checklist

**NEVER skip these steps when releasing:**

1. ✅ Update `CHANGELOG.md` (English)
2. ✅ Update `CHANGELOG.zh.md` (Chinese)
3. ✅ Update `marketplace.json` version
4. ✅ Update `README.md` / `README.zh.md` if needed
5. ✅ Commit all changes together
6. ✅ Create version tag

**If user says "直接 push" or "just push" - STILL follow all steps above first!**

## When to Use

Trigger this skill when user requests:
- "release", "发布", "create release", "new version"
- "bump version", "update version"
- "prepare release"
- "push to remote" (with uncommitted changes)

## Workflow

### Step 1: Analyze Changes Since Last Tag

```bash
# Get the latest version tag
LAST_TAG=$(git tag --sort=-v:refname | head -1)

# Show changes since last tag
git log ${LAST_TAG}..HEAD --oneline
git diff ${LAST_TAG}..HEAD --stat
```

Categorize changes by type based on commit messages and file changes:

| Type | Prefix | Description |
|------|--------|-------------|
| feat | `feat:` | New features, new skills |
| fix | `fix:` | Bug fixes |
| docs | `docs:` | Documentation only |
| refactor | `refactor:` | Code refactoring |
| style | `style:` | Formatting, styling |
| chore | `chore:` | Build, tooling, maintenance |

**Breaking Change Detection**: If changes include:
- Removed skills or scripts
- Changed API/interfaces
- Renamed public functions/options

Warn user: "Breaking changes detected. Consider major version bump (--major flag)."

### Step 2: Determine Version Bump

Current version location: `.claude-plugin/marketplace.json` → `metadata.version`

Version rules:
- **Patch** (0.6.1 → 0.6.2): Bug fixes, docs updates, minor improvements
- **Minor** (0.6.x → 0.7.0): New features, new skills, significant enhancements
- **Major** (0.x → 1.0): Breaking changes, only when user explicitly requests with `--major`

Default behavior:
- If changes include `feat:` or new skills → Minor bump
- Otherwise → Patch bump

### Step 3: Check and Update README

Before updating changelogs, check if README files need updates based on changes:

**When to update README**:
- New skills added → Add to skill list
- Skills removed → Remove from skill list
- Skill renamed → Update references
- New features affecting usage → Update usage section
- Breaking changes → Update migration notes

**Files to sync**:
- `README.md` (English)
- `README.zh.md` (Chinese)

If changes include new skills or significant feature changes, update both README files to reflect the new capabilities. Keep both files in sync with the same structure and information.

### Step 4: Update Changelogs

Files to update:
- `CHANGELOG.md` (English)
- `CHANGELOG.zh.md` (Chinese)

Format (insert after header, before previous version):

```markdown
## {NEW_VERSION} - {YYYY-MM-DD}

### Features
- `skill-name`: description of new feature

### Fixes
- `skill-name`: description of fix

### Documentation
- description of docs changes

### Other
- description of other changes
```

Only include sections that have changes. Omit empty sections.

For Chinese changelog, translate the content maintaining the same structure.

### Step 5: Update marketplace.json

Update `.claude-plugin/marketplace.json`:
```json
{
  "metadata": {
    "version": "{NEW_VERSION}"
  }
}
```

### Step 6: Commit Changes

```bash
git add README.md README.zh.md CHANGELOG.md CHANGELOG.zh.md .claude-plugin/marketplace.json
git commit -m "chore: release v{NEW_VERSION}"
```

**Note**: Do NOT add Co-Authored-By line. This is a release commit, not a code contribution.

### Step 7: Create Version Tag

```bash
git tag v{NEW_VERSION}
```

**Important**: Do NOT push to remote. User will push manually when ready.

## Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview changes without executing. Show what would be updated. |
| `--major` | Force major version bump (0.x → 1.0 or 1.x → 2.0) |
| `--minor` | Force minor version bump |
| `--patch` | Force patch version bump |
| `--pre <tag>` | (Reserved) Create pre-release version, e.g., `--pre beta` → `0.7.0-beta.1` |

## Dry-Run Mode

When `--dry-run` is specified:
1. Show all changes since last tag
2. Show proposed version bump (current → new)
3. Show draft changelog entries (EN and CN)
4. Show files that would be modified
5. Do NOT make any actual changes

Output format:
```
=== DRY RUN MODE ===

Last tag: v0.6.1
Proposed version: v0.7.0

Changes detected:
- feat: new skill baoyu-foo added
- fix: baoyu-bar timeout issue
- docs: updated README

Changelog preview (EN):
## 0.7.0 - 2026-01-17
### Features
- `baoyu-foo`: new skill for ...
### Fixes
- `baoyu-bar`: fixed timeout issue

README updates needed: Yes/No
(If yes, show proposed changes)

Files to modify:
- README.md (if updates needed)
- README.zh.md (if updates needed)
- CHANGELOG.md
- CHANGELOG.zh.md
- .claude-plugin/marketplace.json

No changes made. Run without --dry-run to execute.
```

## Example Usage

```
/release-skills              # Auto-detect version bump
/release-skills --dry-run    # Preview only
/release-skills --minor      # Force minor bump
/release-skills --major      # Force major bump (with confirmation)
```

## Post-Release Reminder

After successful release, remind user:
```
Release v{NEW_VERSION} created locally.

To publish:
  git push origin main
  git push origin v{NEW_VERSION}
```
