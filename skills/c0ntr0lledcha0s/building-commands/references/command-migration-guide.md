# Command Migration Guide

Guide for migrating Claude Code slash commands across schema versions and best practices updates.

---

## Table of Contents

1. [When to Migrate](#when-to-migrate)
2. [Migration Types](#migration-types)
3. [Automated Migration Tool](#automated-migration-tool)
4. [Manual Migration Steps](#manual-migration-steps)
5. [Version-Specific Migrations](#version-specific-migrations)
6. [Validation After Migration](#validation-after-migration)
7. [Troubleshooting](#troubleshooting)

---

## When to Migrate

### Required Migrations (Breaking Changes)

Migrate immediately if:
- ❌ Commands fail with "model not found" errors
- ❌ Validation reports critical errors
- ❌ Pre-commit hooks block commits
- ❌ Commands won't load or execute

### Recommended Migrations (Best Practices)

Consider migrating when:
- ⚠️ Using deprecated fields or formats
- ⚠️ Audit reports warnings
- ⚠️ Upgrading Claude Code version
- ⚠️ Standardizing across team/repository

### Optional Migrations (Improvements)

Migrate opportunistically:
- 💡 Enhancing existing commands
- 💡 Cleaning up technical debt
- 💡 Improving consistency

---

## Migration Types

### 1. Model Field Migration (CRITICAL)

**From**: Short aliases (haiku/sonnet/opus)
**To**: Version aliases (claude-haiku-4-5) or full IDs

**Why**: Commands require version aliases. Short aliases cause API 404 errors.

**Automated**: ✅ Yes
**Risk**: 🟢 Low (safe, reversible)
**Impact**: 🔴 High (fixes broken commands)

```yaml
# Before (BROKEN)
model: haiku

# After (FIXED)
model: claude-haiku-4-5
```

---

### 2. Argument Hint Format

**From**: Various formats (strings, lists, no brackets)
**To**: Standardized bracket notation

**Why**: Consistency, better UX

**Automated**: ✅ Yes
**Risk**: 🟢 Low
**Impact**: 🟡 Medium (improves clarity)

```yaml
# Before
argument-hint: filename options

# After
argument-hint: [filename] [options]
```

---

### 3. Field Renames

**From**: `tools`
**To**: `allowed-tools`

**Why**: Clarity (distinguishes from other tool-related fields)

**Automated**: ✅ Yes (if needed in future)
**Risk**: 🟢 Low
**Impact**: 🟢 Low (mostly cosmetic)

```yaml
# Before (deprecated)
tools: Read, Write

# After (current)
allowed-tools: Read, Write
```

---

### 4. Description Length Normalization

**From**: Too short (< 10 chars) or too long (> 200 chars)
**To**: Optimal length (20-120 chars)

**Automated**: ⚠️ Requires human review
**Risk**: 🟡 Medium (may need rewording)
**Impact**: 🟡 Medium (improves discoverability)

---

## Automated Migration Tool

### Usage

```bash
# Preview all migrations (recommended first step)
/agent-builder:commands:migrate --dry-run

# Migrate single command (preview)
/agent-builder:commands:migrate my-command

# Migrate single command (apply)
/agent-builder:commands:migrate my-command --apply

# Migrate all commands (interactive, with confirmation)
/agent-builder:commands:migrate --apply
```

### What It Does

1. **Scans** all commands in repository
2. **Detects** outdated patterns
3. **Applies** migrations automatically
4. **Shows** diff before applying
5. **Creates** backup (.md.bak)
6. **Confirms** each change interactively

### Safety Features

- ✅ Preview mode by default
- ✅ Backup before modification
- ✅ Interactive confirmation
- ✅ Validates YAML syntax
- ✅ Reports errors without modifying

---

## Manual Migration Steps

For migrations not handled by automation:

### Step 1: Backup

```bash
cp .claude/commands/my-command.md .claude/commands/my-command.md.bak
```

### Step 2: Edit Frontmatter

Open command file and update YAML:

```yaml
---
# Update fields as needed
description: [new description]
allowed-tools: [updated tools]
model: [version alias]
argument-hint: [bracketed hint]
---
```

### Step 3: Update Body

Review and update command body:
- Add missing sections (## Arguments, ## Workflow, ## Examples)
- Improve documentation
- Add security notes for Bash commands

### Step 4: Validate

```bash
python3 agent-builder/skills/building-commands/scripts/validate-command.py my-command.md
```

### Step 5: Test

Invoke the command to ensure it works:

```bash
/my-command [test-args]
```

---

## Version-Specific Migrations

### Current Schema (v1.1.0)

**Fields**:
- `description` (required)
- `allowed-tools` (optional)
- `model` (optional, version alias or full ID)
- `argument-hint` (optional, bracketed format)
- `disable-model-invocation` (optional, boolean)

**Naming**: lowercase-hyphens, max 64 chars

**Model Format**:
- ✅ `claude-haiku-4-5` (version alias)
- ✅ `claude-haiku-4-5-20251001` (full ID)
- ❌ `haiku` (short alias - doesn't work)

---

### Migrating from Pre-1.0 Commands

If you have very old commands, you may need additional migrations:

#### Add Description Field

```yaml
# Before (invalid)
---
# No description field
---

# After (valid)
---
description: Brief explanation of what command does
---
```

#### Standardize Naming

```bash
# Before (invalid filenames)
My_Command.md
my.command.md

# After (valid)
my-command.md
```

**Action**: Rename files to lowercase-hyphens

#### Remove Deprecated Fields

Check for and remove any deprecated fields that may have existed in older versions.

---

## Validation After Migration

### Run Validation

```bash
# Single command
python3 agent-builder/skills/building-commands/scripts/validate-command.py my-command.md

# All commands
/agent-builder:commands:audit
```

### Expected Results

- ✅ No critical errors
- ⚠️ Warnings are acceptable (recommendations)
- 💡 Follow recommendations to improve quality

### Quality Check

```bash
/agent-builder:commands:enhance my-command
```

Aim for score ≥ 6 (good), ideally ≥ 8 (excellent)

---

## Migration Checklist

Use this checklist when migrating commands:

- [ ] Backup original file (.md.bak)
- [ ] Run `/agent-builder:commands:migrate --dry-run` to see what needs updating
- [ ] Fix critical issues first (model field, required fields)
- [ ] Run `/agent-builder:commands:migrate my-command --apply` or update manually
- [ ] Validate with `/agent-builder:commands:audit`
- [ ] Test command execution
- [ ] Check enhancement score `/agent-builder:commands:enhance my-command`
- [ ] Address warnings and recommendations
- [ ] Re-validate
- [ ] Commit changes

---

## Troubleshooting

### Migration Script Errors

#### "Command not found"

**Problem**: Script can't locate command file

**Solution**:
- Verify filename is correct (without .md if using command name)
- Check you're in correct directory
- Try with full path: `/agent-builder:commands:migrate ./path/to/command.md`

#### "Invalid YAML syntax"

**Problem**: Existing command has malformed YAML

**Solution**:
1. Run `python3 -m yaml my-command.md` to see YAML error
2. Fix YAML syntax manually
3. Re-run migration

#### "Permission denied"

**Problem**: Can't write to command file

**Solution**:
```bash
chmod 644 my-command.md
```

---

### Post-Migration Issues

#### Command Still Fails After Migration

**Check**:
1. Model field uses version alias (not short alias)
2. YAML frontmatter is valid
3. File has correct permissions
4. Command body doesn't have syntax errors

**Debug**:
```bash
# Validate syntax
python3 agent-builder/skills/building-commands/scripts/validate-command.py my-command.md

# Check enhancement score
python3 agent-builder/skills/building-commands/scripts/enhance-command.py my-command

# Compare with backup to see what changed
/agent-builder:commands:compare my-command my-command.md.bak
```

#### Model Field Still Causes Errors

**Verify format**:
```yaml
# ✅ Correct formats
model: claude-haiku-4-5         # Version alias
model: claude-haiku-4-5-20251001 # Full ID

# ❌ Wrong formats
model: haiku           # Short alias - doesn't work in commands
model: inherit         # Use field omission instead
model: claude-haiku    # Incomplete, missing version
```

**Fix**:
```bash
/agent-builder:commands:update my-command
> Select: 3 (model)
> Choose: 1 (claude-haiku-4-5)
```

---

## Bulk Migration Strategy

For repositories with many commands:

### Phase 1: Discovery

```bash
/agent-builder:commands:audit --verbose
```

Identify all commands needing migration.

### Phase 2: Automated Migration

```bash
/agent-builder:commands:migrate --dry-run
```

Preview all changes, note any that need manual intervention.

### Phase 3: Apply Migrations

```bash
/agent-builder:commands:migrate --apply
```

Apply migrations interactively, confirming each change.

### Phase 4: Manual Fixes

For any commands that couldn't be auto-migrated:
```bash
/agent-builder:commands:update <command-name>
```

### Phase 5: Validation

```bash
/agent-builder:commands:audit
```

Verify all commands pass validation.

### Phase 6: Quality Check

For critical commands:
```bash
/agent-builder:commands:enhance <command-name>
```

Ensure quality scores are acceptable.

---

## Best Practices

### Before Migration

1. **Commit current state** to version control
2. **Run audit** to understand scope
3. **Backup commands** (script does this automatically)
4. **Test critical commands** to know baseline behavior

### During Migration

1. **Use --dry-run first** to preview changes
2. **Migrate incrementally** (one at a time for critical commands)
3. **Review diffs carefully** before confirming
4. **Test after each migration** (for critical commands)

### After Migration

1. **Run full audit** to verify success
2. **Test command execution** (at least critical ones)
3. **Review quality scores** for important commands
4. **Update documentation** if command behavior changed
5. **Commit with clear message**: "chore: migrate commands to schema v1.1.0"

---

## Getting Help

If migration issues persist:

1. Check [Command Update Patterns](./command-update-patterns.md) for common issues
2. Review [Command Checklist](./command-checklist.md) for quality requirements
3. Compare with working commands: `/agent-builder:commands:compare my-command working-command`
4. Check validation output carefully for specific errors
5. Run enhancement analysis for detailed recommendations

---

## Related Resources

- [Command Update Patterns](./command-update-patterns.md) - Common update scenarios
- [Command Checklist](./command-checklist.md) - Quality review checklist
- [SKILL.md](../SKILL.md) - Command building guide
- [validate-command.py](../scripts/validate-command.py) - Validation script
