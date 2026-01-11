---
name: releasing-versions
description: Manages release preparation including validation, version bumping, documentation verification, and security checks.
---

# Releasing Versions

## When to Use

- Preparing a new release
- Version bumping
- Pre-release validation
- Documentation verification before release

## Release Workflow Overview

| Phase | Purpose | Blocking? |
|-------|---------|-----------|
| 1. Pre-Release Validation | Tests, security | Yes |
| 2. Version Bump | Update version strings | Yes |
| 3. Documentation | Verify/update docs | Warning |
| 4. Template Sync | Cookiecutter alignment | Warning |
| 5. Build Verification | Package builds | Yes |
| 6. Git Operations | Commit and tag | Yes |

## Phase 1: Pre-Release Validation

### 1.1 Verify Sprint Tasks Complete

```bash
# Check for incomplete tasks
bpsai-pair task list --status in_progress
bpsai-pair task list --status blocked

# Check current state
bpsai-pair status
```

**BLOCKER**: All tasks must be complete or moved to next sprint.

### 1.2 Run Full Test Suite

```bash
# All tests must pass
pytest tests/ -v --tb=short

# Check coverage meets target (80%)
pytest tests/ --cov=bpsai_pair --cov-report=term-missing --cov-fail-under=80
```

**BLOCKER**: Release cannot proceed if tests fail.

### 1.3 Security Scans

```bash
# Scan for accidentally committed secrets
bpsai-pair security scan-secrets

# Scan dependencies for known vulnerabilities
bpsai-pair security scan-deps
```

**BLOCKER**: Secrets detected = cannot release.
**WARNING**: Dependency vulnerabilities should be reviewed but may not block.

## Phase 2: Version Bump

### Locate Version Files

```bash
grep -E "^version|__version__" tools/cli/pyproject.toml tools/cli/bpsai_pair/__init__.py
```

### Update Both Files

| File | Format |
|------|--------|
| `pyproject.toml` | `version = "X.Y.Z"` |
| `__init__.py` | `__version__ = "X.Y.Z"` |

**Note**: Version in files has NO 'v' prefix. Git tags use 'v' prefix.

### Related Files to Update

| File | Update |
|------|--------|
| `capabilities.yaml` | `version: "X.Y.Z"` |
| `config.yaml` | `version: "X.Y.Z"` |

## Phase 3: Documentation Verification

### 3.1 Required Documentation

```bash
# Check CHANGELOG has entry for this version
grep -A 20 "## \[X.Y.Z\]" CHANGELOG.md

# Check README mentions current features
head -100 README.md

# Check FEATURE_MATRIX is current
head -50 .paircoder/docs/FEATURE_MATRIX.md
```

### 3.2 Documentation Freshness

```bash
# Check modification dates
git log -1 --format="%ci" -- README.md
git log -1 --format="%ci" -- CHANGELOG.md
git log -1 --format="%ci" -- .paircoder/docs/FEATURE_MATRIX.md
```

**WARNING** if any required doc older than 7 days - may need update.

### 3.3 CHANGELOG Entry Format

If missing, create entry following Keep a Changelog format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Feature 1
- Feature 2

### Changed
- Change 1

### Fixed
- Fix 1

### Removed
- (if applicable)
```

Generate content from archived tasks:
```bash
bpsai-pair task changelog-preview --since <last-version>
```

## Phase 4: Template Sync (PairCoder Only)

Verify cookiecutter template matches current version:

```bash
# Check template exists
ls -la tools/cli/bpsai_pair/data/cookiecutter-paircoder/

# Compare key files
diff .paircoder/config.yaml \
  tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/.paircoder/config.yaml

diff CLAUDE.md \
  tools/cli/bpsai_pair/data/cookiecutter-paircoder/{{cookiecutter.project_slug}}/CLAUDE.md
```

**Key files that should stay in sync:**
- `config.yaml` structure (not values)
- `CLAUDE.md` instructions
- `capabilities.yaml` format
- Skill files

## Phase 5: Build Verification

```bash
# Clean old builds
rm -rf tools/cli/dist/ tools/cli/build/ tools/cli/*.egg-info

# Build the package
cd tools/cli && pip install build && python -m build

# Verify clean install
pip install dist/*.whl --force-reinstall

# Verify version is correct
bpsai-pair --version
```

## Phase 6: Release Checklist

- [ ] All sprint tasks complete
- [ ] Tests passing (100%)
- [ ] Coverage ≥ 80%
- [ ] No secrets in codebase
- [ ] Version bumped in pyproject.toml
- [ ] Version bumped in __init__.py
- [ ] Version bumped in capabilities.yaml
- [ ] Version bumped in config.yaml
- [ ] CHANGELOG updated
- [ ] README current
- [ ] FEATURE_MATRIX updated
- [ ] Cookiecutter template synced (if applicable)
- [ ] Package builds successfully
- [ ] Package installs cleanly

## Phase 7: Git Operations

```bash
# Stage all changes
git add -A

# Commit with release message
git commit -m "Release vX.Y.Z"

# Create annotated tag
git tag -a "vX.Y.Z" -m "Release vX.Y.Z"

# Show what will be pushed
git log --oneline -5
git tag -l | tail -5
```

**DO NOT push yet** - let user review and confirm.

## Phase 8: Report Summary

```
📦 **Release Prepared**: vX.Y.Z

**Pre-Release Checks**:
- ✅ All tasks complete
- ✅ Tests: XXX passed
- ✅ Coverage: XX%
- ✅ Security: Clean

**Documentation**:
- ✅ CHANGELOG: Updated
- ✅ README: Current
- ✅ FEATURE_MATRIX: Updated
- ⚠️ User guide: Last updated X days ago (review recommended)

**Cookiecutter**: 
- ✅ Template synced

**Build**:
- ✅ Package built: bpsai_pair-X.Y.Z-py3-none-any.whl
- ✅ Installs cleanly
- ✅ Version verified

**Ready to Release**:
```bash
git push origin main
git push origin vX.Y.Z
```

Then publish to PyPI:
```bash
cd tools/cli && twine upload dist/*
```
```

## Error Recovery

### Tests Fail
1. Do not proceed with release
2. Fix failing tests
3. Re-run from Phase 1

### Secrets Detected
1. Do not proceed with release
2. Remove secrets from history (git filter-branch or BFG)
3. Rotate any exposed credentials
4. Re-run security scan

### Documentation Stale
1. WARNING, not blocker
2. User can choose to update or proceed
3. Log the decision

### Cookiecutter Differs
1. Determine if difference is intentional
2. If template should be updated, do so
3. If difference is project-specific, document why

## Configuration Reference

Release configuration in `config.yaml`:

```yaml
release:
  version_source: tools/cli/pyproject.toml
  documentation:
    - CHANGELOG.md
    - README.md
    - .paircoder/docs/FEATURE_MATRIX.md
  cookie_cutter:
    template_path: tools/cli/bpsai_pair/data/cookiecutter-paircoder
    sync_required: true
  freshness_days: 7
```

## Version Format Reference

| Location | Format | Example |
|----------|--------|---------|
| pyproject.toml | X.Y.Z | 2.9.0 |
| __init__.py | X.Y.Z | 2.9.0 |
| Git tags | vX.Y.Z | v2.9.0 |
| CHANGELOG | [X.Y.Z] | [2.9.0] |
