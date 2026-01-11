---
name: post-impl-docs
description: "Update repository documentation after code implementation. Maintains README, CHANGELOG, docs/ folder, and inline docstrings based on changes made. Triggered by lane-executor after task completion."
---

# Post-Implementation Documentation Skill

Automatically update repository documentation to reflect code changes. This skill ensures that when code is implemented, the documentation stays in sync with the actual codebase.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| UPDATE_README | true | Update README.md for new features/APIs |
| UPDATE_CHANGELOG | true | Add entries to CHANGELOG.md |
| UPDATE_DOCS_FOLDER | true | Update files in docs/ that reference changed code |
| UPDATE_DOCSTRINGS | true | Update inline docstrings for changed functions/classes |
| CHANGELOG_FORMAT | conventional | `conventional`, `keep-a-changelog`, `simple` |
| COMMIT_DOCS | true | Commit documentation changes with code |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order. Do not skip steps.

1. Analyze what code changes were made (git diff)
2. Determine documentation impact
3. Update README if new features/APIs added
4. Update CHANGELOG with change summary
5. Scan docs/ folder for references to changed symbols
6. Update inline docstrings for modified functions/classes

## Red Flags - STOP and Reconsider

If you're about to:
- Update documentation without understanding the code changes
- Add CHANGELOG entries for trivial changes (typos, formatting)
- Update README for internal implementation details
- Modify docstrings without verifying the behavior changed

**STOP** -> Review the diff -> Understand the impact -> Then document

## Workflow

### 1. Gather Change Context

Analyze what was changed in the current implementation:

```bash
# Get changed files
git diff --name-only HEAD~1 HEAD

# Get change summary
git diff --stat HEAD~1 HEAD

# Get detailed changes for documentation
git diff HEAD~1 HEAD -- "*.py" "*.ts" "*.js" "*.go" "*.rs"
```

### 2. Classify Changes

Determine the type and scope of changes:

| Change Type | README Impact | CHANGELOG Entry | Docs Update |
|-------------|---------------|-----------------|-------------|
| New feature | Add to Features section | `feat:` entry | If documented |
| Bug fix | No change | `fix:` entry | If affects behavior |
| Breaking change | Update usage examples | `BREAKING:` entry | Update all refs |
| API addition | Add to API section | `feat:` entry | Add API docs |
| Deprecation | Add deprecation note | `deprecate:` entry | Update examples |
| Performance | No change | `perf:` entry | No |
| Refactor | No change | `refactor:` entry | No |
| Docs only | N/A | No entry | N/A |
| Tests only | No change | `test:` entry | No |

### 3. Update README.md

Only update README for significant changes:

**Add new feature to Features section:**
```markdown
## Features

- **New Feature Name** - Brief description of what it does
```

**Add new API to API/Usage section:**
```markdown
## API

### `newFunction(param: Type): ReturnType`

Description of the function and its purpose.
```

**Update usage examples if API changed:**
```markdown
## Usage

```python
# Updated example reflecting new API
result = module.new_function(param="value")
```

### 4. Update CHANGELOG.md

Add entry following the project's format:

**Conventional Changelog:**
```markdown
## [Unreleased]

### Added
- Add user authentication endpoint (#123)

### Changed
- Update database connection pool size for better performance

### Fixed
- Fix race condition in async queue processor (#124)

### Deprecated
- Deprecate `old_function()` in favor of `new_function()`

### Removed
- Remove support for Python 3.8

### Security
- Fix XSS vulnerability in user input handling
```

**Keep a Changelog format:**
```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Change description
```

### 5. Update docs/ Folder

Scan documentation files for references to changed symbols:

```bash
# Find docs that reference changed functions/classes
grep -r "changed_function\|ChangedClass" docs/
```

For each match:
1. Verify if the documentation is still accurate
2. Update parameter descriptions if signature changed
3. Update examples if behavior changed
4. Update cross-references if file moved

### 6. Update Inline Docstrings

For each modified function/class with docstrings:

**Python:**
```python
def function(param: str) -> bool:
    """Updated description reflecting new behavior.

    Args:
        param: Updated parameter description.

    Returns:
        Updated return value description.

    Raises:
        ValueError: If param is invalid (new error case).
    """
```

**TypeScript/JavaScript:**
```typescript
/**
 * Updated description reflecting new behavior.
 *
 * @param param - Updated parameter description
 * @returns Updated return value description
 * @throws {Error} If param is invalid (new error case)
 */
function func(param: string): boolean {
```

## Cookbook

### README Updates
- IF: Adding new public feature
- THEN: Read `cookbook/readme-updates.md`
- RESULT: Updated feature list and examples

### CHANGELOG Entries
- IF: Writing CHANGELOG entries
- THEN: Read `cookbook/changelog-formats.md`
- RESULT: Properly formatted entries

### Docstring Standards
- IF: Updating inline documentation
- THEN: Read `cookbook/docstring-standards.md`
- RESULT: Consistent docstring format

## Quick Reference

### What to Document

| Change | README | CHANGELOG | docs/ | Docstrings |
|--------|--------|-----------|-------|------------|
| New public API | Yes | Yes | Yes | Yes |
| New internal function | No | Maybe | No | Yes |
| Bug fix | No | Yes | If behavior docs exist | If signature changed |
| Performance improvement | No | Yes | No | No |
| Breaking change | Yes | Yes | Yes | Yes |
| Deprecation | Yes | Yes | Yes | Yes |

### Conventional Commit to CHANGELOG Mapping

| Commit Type | CHANGELOG Section |
|-------------|-------------------|
| `feat:` | Added |
| `fix:` | Fixed |
| `perf:` | Changed |
| `refactor:` | Changed |
| `deprecate:` | Deprecated |
| `BREAKING CHANGE:` | Changed (with breaking note) |
| `security:` | Security |
| `docs:` | (skip) |
| `test:` | (skip) |
| `chore:` | (skip) |

## Integration Points

This skill is invoked:
1. **By lane-executor**: After completing implementation tasks
2. **By test-engineer**: After significant test additions
3. **Before PR creation**: Ensure docs are current

### Example Integration in Lane Executor

```markdown
## Post-Implementation Steps

After completing implementation:
1. Run `dependency-sync` skill to update manifests
2. Run `post-impl-docs` skill to update documentation
3. Verify build/tests still pass
4. Commit all changes together
```

## Output

### Documentation Update Report

```json
{
  "status": "success",
  "updates": {
    "readme": {
      "updated": true,
      "sections_modified": ["Features", "API"]
    },
    "changelog": {
      "updated": true,
      "entries_added": [
        {"type": "feat", "description": "Add user authentication endpoint"}
      ]
    },
    "docs_folder": {
      "files_updated": ["docs/api.md", "docs/getting-started.md"],
      "references_fixed": 3
    },
    "docstrings": {
      "functions_updated": 5,
      "classes_updated": 2
    }
  },
  "commit_sha": "abc123"
}
```

### No Changes Report

```json
{
  "status": "no_changes",
  "reason": "Changes are internal implementation only",
  "analysis": {
    "change_type": "refactor",
    "public_api_affected": false,
    "documentation_impact": "none"
  }
}
```
