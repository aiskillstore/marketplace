---
name: blocklet-updater
description: Creates a new release for a blocklet project by bumping version, building, and bundling. Use when asked to "create a new release", "bump and bundle", or "update blocklet version".
---

# Blocklet Updater

Bumps a blocklet project version and creates a release bundle.

## Workflow

### 1. Version Bump (Smart Detection)

Check for project-specific version update scripts before falling back to `blocklet version patch`.

#### 1.1 Detect Version Update Method

Check the following in priority order and use the **first match**:

| Priority | Detection | Command |
|----------|-----------|---------|
| 1 | Makefile has `bump-version` target | `make bump-version` |
| 2 | package.json has `bump-version` script | `pnpm run bump-version` |
| 3 | package.json has `version` script | `pnpm run version` |
| 4 | lerna.json exists | `lerna version patch --yes` |
| 5 | None of the above | `blocklet version patch` (fallback) |

**Detection commands**:

```bash
# Priority 1: Check Makefile for bump-version target
if [ -f "Makefile" ] && grep -q "^bump-version:" Makefile 2>/dev/null; then
    VERSION_CMD="make bump-version"
fi

# Priority 2: Check package.json for bump-version script
if [ -z "$VERSION_CMD" ] && [ -f "package.json" ]; then
    if cat package.json | jq -e '.scripts["bump-version"]' > /dev/null 2>&1; then
        VERSION_CMD="pnpm run bump-version"
    fi
fi

# Priority 3: Check package.json for version script
if [ -z "$VERSION_CMD" ] && [ -f "package.json" ]; then
    if cat package.json | jq -e '.scripts["version"]' > /dev/null 2>&1; then
        VERSION_CMD="pnpm run version"
    fi
fi

# Priority 4: Check for lerna.json
if [ -z "$VERSION_CMD" ] && [ -f "lerna.json" ]; then
    VERSION_CMD="lerna version patch --yes"
fi

# Priority 5: Fallback to blocklet version
if [ -z "$VERSION_CMD" ]; then
    VERSION_CMD="blocklet version patch"
fi
```

#### 1.2 Execute Version Bump

Run the detected command:

```bash
$VERSION_CMD
```

**Important**: Project-specific scripts (like `make bump-version`) often:
- Update `version` file
- Auto-generate `CHANGELOG.md` entries
- Update multiple package versions in monorepos
- Call additional tooling scripts

**If fails → EXIT** with error output.

#### 1.3 Update CHANGELOG (If Exists)

After version bump, verify and fix CHANGELOG.md if needed.

##### 1.3.1 Get Actual Version

First, get the actual version that was set (from blocklet.yml or package.json):

```bash
# Get version from blocklet.yml
ACTUAL_VERSION=$(grep -E "^version:" blocklet.yml | sed 's/version: *//' | tr -d '"'"'" 2>/dev/null)

# Fallback to package.json if no blocklet.yml
if [ -z "$ACTUAL_VERSION" ]; then
    ACTUAL_VERSION=$(cat package.json | jq -r '.version' 2>/dev/null)
fi
```

##### 1.3.2 Find CHANGELOG Location

```bash
# Common CHANGELOG locations in monorepos
CHANGELOG_PATHS=(
    "CHANGELOG.md"
    "blocklets/*/CHANGELOG.md"
    "packages/*/CHANGELOG.md"
)

for pattern in "${CHANGELOG_PATHS[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            echo "Found: $file"
        fi
    done
done
```

##### 1.3.3 Validate CHANGELOG Entry

For each CHANGELOG.md found, check if the latest entry matches the actual version:

```bash
# Extract first version number from CHANGELOG.md
CHANGELOG_VERSION=$(grep -E "^## \[?[0-9]+\.[0-9]+\.[0-9]+\]?" CHANGELOG.md | head -1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")

if [ "$CHANGELOG_VERSION" != "$ACTUAL_VERSION" ]; then
    echo "⚠️ Version mismatch!"
    echo "   CHANGELOG shows: $CHANGELOG_VERSION"
    echo "   Actual version:  $ACTUAL_VERSION"
fi
```

##### 1.3.4 Fix Version Mismatch

**If CHANGELOG version doesn't match actual version**, fix it:

1. If CHANGELOG has a newer entry with wrong version (e.g., script partially ran):
   - Replace the wrong version number with the correct one

2. If CHANGELOG has no entry for the new version:
   - Add a new entry at the top

```bash
# Example fix: Replace wrong version in first heading
sed -i "0,/^## \[*$WRONG_VERSION\]*/s//## $ACTUAL_VERSION/" CHANGELOG.md
```

##### 1.3.5 Check Entry Content

After fixing version, check if the entry has content:

```bash
# Get content between first ## and second ##
ENTRY_CONTENT=$(sed -n '/^## /,/^## /p' CHANGELOG.md | sed '1d;$d' | grep -v "^$")

if [ -z "$ENTRY_CONTENT" ]; then
    echo "⚠️ CHANGELOG entry is empty, needs content"
fi
```

##### 1.3.6 Generate Content for Empty Entry

**If entry is empty**, generate content based on:

1. **Git commits since last version tag**:
```bash
# Get commits since last tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
    git log $LAST_TAG..HEAD --oneline --no-merges
fi
```

2. **Categorize by commit type** (feat, fix, chore, etc.):
```markdown
## X.Y.Z (YYYY-MM-DD)

- feat: description of new feature
- fix: description of bug fix
- chore: description of maintenance task
```

3. **If no meaningful commits found**, use `AskUserQuestion` to ask user for changelog content.

##### 1.3.7 Common CHANGELOG Formats

Detect and follow the existing format:

| Format | Example |
|--------|---------|
| Keep a Changelog | `## [1.2.3] - 2024-01-20` |
| Simple with date | `## 1.2.3 (2024-1-20)` |
| Simple no date | `## 1.2.3` |

**Date format**: Match the existing format in the file (e.g., `2024-01-20` vs `2024-1-20`).

### 2. Build System Detection

Check if `package.json` exists and contains a `build` script.

#### If Build Script Exists

Install dependencies and build:

```bash
pnpm install && pnpm run build
```

**If either fails → EXIT** with error output.

#### If No Build Script

Skip build step - project is likely pre-built or static.

### 3. Entry Point Verification

#### Locate Output Directory & Entry Point

Find `index.html` in common locations: `dist/` → `build/` → `out/` → `public/` → `./`

**If not found → EXIT** with error message: "No index.html entry point found."

#### Verify blocklet.yml Main Field

Read `blocklet.yml` and check the `main` field:

- If `main` points to directory containing `index.html` → valid
- If `main` is misaligned → update it to the correct output directory
- After any update, inform user of the change

### 4. Metadata Verification

```bash
blocklet meta
```

**If fails → EXIT** with error output and suggestions.

### 5. Bundle Creation

```bash
blocklet bundle --create-release
```

**If fails → EXIT** with error output.

### 6. Finalization

**Do NOT output any summary or recap after completion.** Simply end silently after successful bundle creation. The tool outputs already provide sufficient feedback to the user.

## Error Reference

See `{baseDir}/errors.md` for all error conditions and suggestions.

## Supporting Files

- `errors.md` - Error reference
- `examples.md` - Workflow examples

`{baseDir}` resolves to the skill's installation directory.
