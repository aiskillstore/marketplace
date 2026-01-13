---
name: dependency-sync
description: "Detect new imports in modified files and auto-install missing dependencies. Works with npm, uv, pip, cargo, go mod, and other package managers. Triggers after code implementation to keep manifests in sync."
---

# Dependency Sync Skill

Automatically detect new imports in modified code files and update package manifests. This skill ensures that when code is written that uses new dependencies, the appropriate manifest files (package.json, pyproject.toml, requirements.txt, etc.) are updated automatically.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| AUTO_INSTALL | true | Automatically install detected dependencies |
| PROMPT_BEFORE_INSTALL | false | Ask user before installing (overrides AUTO_INSTALL) |
| INCLUDE_DEV_DEPS | true | Detect dev dependencies (test frameworks, linters) |
| COMMIT_CHANGES | true | Commit manifest changes as part of the task |
| TRIGGER_DOCS_AUDIT | true | Run docs-audit --new-only after adding deps |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order. Do not skip steps.

1. Detect modified files from git diff or implementation context
2. Parse imports/requires from modified files
3. Compare against current manifest dependencies
4. Identify package manager for the project
5. Install missing dependencies
6. Optionally trigger docs-audit for new libraries

## Red Flags - STOP and Reconsider

If you're about to:
- Install a package without verifying the import is actually used
- Skip manifest detection (assuming package manager)
- Install to wrong manifest (e.g., devDependencies vs dependencies)
- Install without checking if package exists in registry

**STOP** -> Verify the import is real -> Check manifest -> Then install

## Workflow

### 1. Gather Modified Files

Identify files that were modified in the current implementation:

```bash
# If in git context
git diff --name-only HEAD~1 HEAD -- "*.py" "*.ts" "*.js" "*.tsx" "*.jsx" "*.go" "*.rs"

# Or from task context - files that were written/edited
```

### 2. Extract Imports

Parse imports from each modified file based on language:

| Language | Import Pattern |
|----------|----------------|
| Python | `import X`, `from X import Y` |
| TypeScript/JavaScript | `import X from 'Y'`, `require('Y')` |
| Go | `import "X"` |
| Rust | `use X::Y`, `extern crate X` |

### 3. Detect Package Manager

Check for manifest files to determine the package manager:

| Manifest | Package Manager | Install Command |
|----------|-----------------|-----------------|
| `pyproject.toml` (with uv) | uv | `uv add <package>` |
| `pyproject.toml` (poetry) | poetry | `poetry add <package>` |
| `requirements.txt` | pip | `pip install <package>` |
| `package.json` | npm/yarn/pnpm | `npm install <package>` |
| `Cargo.toml` | cargo | `cargo add <package>` |
| `go.mod` | go | `go get <package>` |
| `pubspec.yaml` | pub | `flutter pub add <package>` |

### 4. Compare Dependencies

For each extracted import:
1. Normalize import name to package name (e.g., `from PIL import Image` -> `pillow`)
2. Check if package exists in manifest
3. If missing, add to installation list

### 5. Install Dependencies

Execute installation commands for missing dependencies:

```bash
# Python with uv
uv add <package1> <package2>

# Node.js
npm install <package1> <package2>

# Rust
cargo add <package1> <package2>

# Go
go get <package1> <package2>
```

### 6. Post-Install Actions

If TRIGGER_DOCS_AUDIT is true and new dependencies were added:
1. Run `/ai-dev-kit:docs-audit --new-only`
2. Suggest `/ai-dev-kit:docs-add-stack` if documentation is missing

## Cookbook

### Python Import Mapping
- IF: Parsing Python imports
- THEN: Read `cookbook/python-imports.md`
- RESULT: Normalized package names

### Node Import Mapping
- IF: Parsing JavaScript/TypeScript imports
- THEN: Read `cookbook/node-imports.md`
- RESULT: Normalized package names

### Classification Rules
- IF: Determining if dependency is dev or prod
- THEN: Read `cookbook/dependency-classification.md`
- RESULT: Correct target in manifest

## Quick Reference

### Import-to-Package Mappings

| Import | Package Name | Notes |
|--------|--------------|-------|
| `PIL` | `pillow` | Python imaging |
| `cv2` | `opencv-python` | OpenCV |
| `yaml` | `pyyaml` | YAML parser |
| `sklearn` | `scikit-learn` | ML library |
| `bs4` | `beautifulsoup4` | HTML parsing |
| `pg` | `pg` (npm) / `asyncpg` (py) | PostgreSQL |
| `@tanstack/react-query` | `@tanstack/react-query` | Direct match |

### Dev Dependency Indicators

| Pattern | Classification |
|---------|----------------|
| `pytest`, `vitest`, `jest` | Test framework (dev) |
| `eslint`, `ruff`, `black` | Linter (dev) |
| `@types/*` | Type definitions (dev) |
| `*-dev`, `*-debug` | Development tools (dev) |

## Integration Points

This skill is invoked:
1. **By lane-executor**: After implementing code in a task
2. **By test-engineer**: After writing tests that need new test dependencies
3. **Manually**: Via `/ai-dev-kit:dependency-sync` command

### Example Integration in Lane Executor

```markdown
## Post-Implementation Steps

After completing implementation:
1. Run `dependency-sync` skill to update manifests
2. Run `post-impl-docs` skill to update documentation
3. Verify build/tests still pass
```

## Output

### Success Report

```json
{
  "status": "success",
  "dependencies_added": [
    {"name": "asyncpg", "version": "^0.29.0", "manifest": "pyproject.toml", "type": "production"},
    {"name": "pytest-asyncio", "version": "^0.23.0", "manifest": "pyproject.toml", "type": "development"}
  ],
  "manifest_updated": "pyproject.toml",
  "commit_sha": "abc123",
  "docs_audit_triggered": true
}
```

### No Changes Report

```json
{
  "status": "no_changes",
  "message": "All imports already present in manifest",
  "files_scanned": 5,
  "imports_found": 12,
  "imports_matched": 12
}
```
