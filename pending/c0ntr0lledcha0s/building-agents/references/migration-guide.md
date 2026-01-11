# Agent Migration Guide

Guide for migrating agents across schema versions and updating to current best practices.

---

## Table of Contents

1. [Schema Versions](#schema-versions)
2. [Migration Path](#migration-path)
3. [Version-Specific Migrations](#version-specific-migrations)
4. [Breaking Changes](#breaking-changes)
5. [Automated Migration](#automated-migration)
6. [Manual Migration](#manual-migration)

---

## Schema Versions

### Current Version: 1.0 (Stable)

**Required fields**:
- `name` (string, lowercase-hyphens, max 64 chars)
- `description` (string, max 1024 chars)

**Optional fields**:
- `tools` (string, comma-separated list)
- `model` (string: "haiku", "sonnet", "opus", or version alias)

**File format**:
```yaml
---
name: agent-name
description: Agent description
tools: Read, Grep, Glob
model: sonnet
---

# Agent body content (markdown)
```

---

## Migration Path

### Check Current Version

Agents don't explicitly declare schema version. Infer from structure:

**Indicators of old agents**:
- ❌ No YAML frontmatter (pre-1.0)
- ❌ Different frontmatter format
- ❌ Missing required fields
- ❌ Use deprecated patterns

**Check with enhancement**:
```bash
python3 enhance-agent.py my-agent
# Reviews schema compliance
```

---

### Migration Decision Tree

```
Is agent valid?
├─ YES → Check for improvements
│   └─ Run: /agent-builder:agents:enhance my-agent
│       ├─ Score < 7/10 → Consider updates
│       └─ Score >= 7/10 → Agent is good
│
└─ NO → Migrate to current schema
    └─ Fix critical issues first
        └─ Then enhance for quality
```

---

## Version-Specific Migrations

### Pre-1.0 to 1.0

**Changes**:
- Added YAML frontmatter requirement
- Standardized required fields
- Introduced optional fields

**Migration steps**:

1. **Add YAML frontmatter** if missing:

```markdown
<!-- Before (no frontmatter) -->
# My Agent

You are an agent that...

<!-- After (with frontmatter) -->
---
name: my-agent
description: Brief description of what the agent does
---

# My Agent

You are an agent that...
```

2. **Extract name from heading**:
   - Use heading text to create name
   - Convert to lowercase-hyphens
   - Add to frontmatter

3. **Create description**:
   - Extract from first paragraph or role statement
   - Keep under 1024 chars
   - Focus on when to invoke

4. **Add tools if needed**:
   - Review what agent does
   - Select minimal necessary tools
   - Default: `Read, Grep, Glob`

5. **Validate**:
```bash
python3 validate-agent.py my-agent.md
```

---

### 1.0 Refinements (Ongoing)

These aren't version changes but best practice updates:

#### Model Field Evolution

**Old style** (deprecated):
```yaml
model: claude-sonnet-4-5  # Specific version
```

**New style** (recommended):
```yaml
model: sonnet  # Version alias (preferred)
# or
model: haiku   # Fast model
# or
model: opus    # Capable model
```

**Migration**:
```bash
/agent-builder:agents:update my-agent
> 3 (model)
> Select alias instead of specific version
```

**Why**: Version aliases are more maintainable

---

#### Tool Permission Minimization

**Old pattern** (over-permissioned):
```yaml
tools: Read, Write, Edit, Grep, Glob, Bash, WebFetch, WebSearch
```

**New pattern** (minimal):
```yaml
tools: Read, Grep, Glob  # Only what's needed
```

**Migration**:
```bash
/agent-builder:agents:enhance my-agent
# Identifies: "⚠️ Many tools granted"

/agent-builder:agents:update my-agent
> 2 (tools)
> Select minimal preset
```

---

#### Description Improvements

**Old pattern** (vague):
```yaml
description: Helps with code
```

**New pattern** (specific):
```yaml
description: Code reviewer for identifying bugs, security issues, and quality concerns. Use when reviewing PRs or auditing code quality.
```

**Template**:
```
[What it does] [What it specializes in]. Use when [scenario 1], [scenario 2], or [scenario 3].
```

**Migration**:
```bash
/agent-builder:agents:update my-agent
> 1 (description)
> Enter new description following template
```

---

## Breaking Changes

### Known Breaking Changes

**None currently** - Schema 1.0 is stable and backward compatible.

### Future Breaking Changes

If breaking changes are introduced, they will be documented here with:
- **Version number** (e.g., 2.0)
- **What changed** (fields added/removed/renamed)
- **Migration path** (step-by-step)
- **Automated tools** (scripts to auto-migrate)

---

## Automated Migration

### Using enhance-agent.py

Identify issues automatically:

```bash
python3 enhance-agent.py my-agent

# Output shows:
# - Schema compliance issues
# - Security concerns
# - Missing best practices
# - Actionable recommendations
```

### Using update-agent.py

Apply fixes interactively:

```bash
python3 update-agent.py my-agent

# Interactive menu guides you through:
# - Updating description
# - Changing tools
# - Selecting model
# - Validating changes
```

### Using Commands

Workflow for comprehensive update:

```bash
# 1. Analyze
/agent-builder:agents:enhance my-agent

# 2. Update based on recommendations
/agent-builder:agents:update my-agent

# 3. Verify improvement
/agent-builder:agents:enhance my-agent
# Check score improved
```

---

## Manual Migration

### Step-by-Step Manual Process

#### Step 1: Backup

```bash
cp .claude/agents/my-agent.md .claude/agents/my-agent.md.bak
```

#### Step 2: Validate Current State

```bash
python3 validate-agent.py .claude/agents/my-agent.md
```

Note all errors and warnings.

#### Step 3: Fix Schema Issues

Open agent file and address issues:

```yaml
---
# Ensure name is valid
name: my-agent  # lowercase-hyphens only

# Ensure description exists and is clear
description: Clear description under 1024 chars

# Optional: minimize tools
tools: Read, Grep, Glob

# Optional: use version alias
model: sonnet
---
```

#### Step 4: Improve Content

Add missing sections:

```markdown
---
name: my-agent
description: Updated description
tools: Read, Grep, Glob
model: sonnet
---

# Agent Name

You are [role definition].

## Your Capabilities

1. Capability 1
2. Capability 2

## Your Workflow

1. Step 1
2. Step 2

## Examples

### Example 1: Scenario
Expected behavior

### Example 2: Scenario
Expected behavior

## Best Practices

- Guideline 1
- Guideline 2

## Error Handling

- How you handle errors
```

#### Step 5: Re-Validate

```bash
python3 validate-agent.py .claude/agents/my-agent.md
```

Should pass with no errors.

#### Step 6: Enhance Check

```bash
python3 enhance-agent.py my-agent
```

Review score and recommendations.

#### Step 7: Test

Invoke the agent and verify behavior:

```bash
# Use Task tool to test
Task: [test scenario]
Agent: my-agent
```

#### Step 8: Commit

```bash
git add .claude/agents/my-agent.md
git commit -m "refactor(agent): migrate my-agent to current schema

- Added missing YAML frontmatter
- Minimized tool permissions
- Improved description clarity
- Added examples and error handling
- Enhanced score: 5.5/10 → 8.0/10"
```

---

## Common Migration Scenarios

### Scenario 1: No Frontmatter

**Before**:
```markdown
# Code Reviewer

You are a code reviewer...
```

**After**:
```markdown
---
name: code-reviewer
description: Reviews code for bugs and security issues. Use when analyzing PRs.
tools: Read, Grep, Glob
model: sonnet
---

# Code Reviewer

You are a code reviewer...
```

---

### Scenario 2: Invalid Name

**Before**:
```yaml
---
name: Code_Reviewer_v2
---
```

**After**:
```yaml
---
name: code-reviewer-v2
---
```

---

### Scenario 3: Over-Permissioned

**Before**:
```yaml
---
name: reader-agent
description: Reads files
tools: Read, Write, Edit, Grep, Glob, Bash
---
```

**After**:
```yaml
---
name: reader-agent
description: Reads and analyzes files. Use when extracting information.
tools: Read, Grep, Glob
---
```

---

### Scenario 4: Vague Description

**Before**:
```yaml
---
name: helper
description: Helps with stuff
---
```

**After**:
```yaml
---
name: code-helper
description: Assists with code refactoring, optimization, and cleanup. Use when improving existing code quality.
tools: Read, Write, Edit, Grep, Glob
model: sonnet
---
```

---

### Scenario 5: Missing Examples

**Before**:
Agent has no examples section.

**After**:
Add examples section:

```markdown
## Examples

### Example 1: Reviewing Security

**Invocation**: "Review auth.py for security issues"

**Process**:
1. Read auth.py
2. Analyze authentication logic
3. Identify vulnerabilities

**Output**: Security report with findings

### Example 2: Quick Scan

**Invocation**: "Check this function for bugs"

**Process**:
1. Analyze function logic
2. Identify potential bugs
3. Suggest fixes

**Output**: List of issues with solutions
```

---

## Validation Checklist

After migration, verify:

- [ ] ✅ YAML frontmatter present
- [ ] ✅ Name is lowercase-hyphens, max 64 chars
- [ ] ✅ Description is clear and under 1024 chars
- [ ] ✅ Tools are minimal and necessary
- [ ] ✅ Model is appropriate (if specified)
- [ ] ✅ Role definition is clear
- [ ] ✅ Capabilities are documented
- [ ] ✅ Workflow is step-by-step
- [ ] ✅ Examples are present (2-3)
- [ ] ✅ Best practices are listed
- [ ] ✅ Error handling is documented
- [ ] ✅ Validation passes: `python3 validate-agent.py`
- [ ] ✅ Enhancement score >= 7/10: `python3 enhance-agent.py`
- [ ] ✅ Agent works when invoked

---

## Migration Tools

### validate-agent.py

```bash
python3 agent-builder/skills/building-agents/scripts/validate-agent.py my-agent.md
```

**Checks**:
- Schema compliance
- Required fields
- Naming conventions
- YAML syntax

**Output**: Pass/fail with specific errors

---

### enhance-agent.py

```bash
python3 agent-builder/skills/building-agents/scripts/enhance-agent.py my-agent
```

**Analyzes**:
- Schema (0-10)
- Security (0-10)
- Quality (0-10)
- Maintainability (0-10)

**Output**: Overall score and prioritized recommendations

---

### update-agent.py

```bash
python3 agent-builder/skills/building-agents/scripts/update-agent.py my-agent
```

**Provides**:
- Interactive update menu
- Diff preview
- Automatic backup
- Post-update validation

---

## Best Practices for Migration

### 1. Migrate in Batches

Don't try to update all agents at once:

```bash
# Audit to prioritize
/agent-builder:agents:audit

# Fix critical issues first
# Then warnings
# Then enhancements
```

### 2. Test After Each Migration

Verify agent works before committing:

```bash
# Migrate
python3 update-agent.py my-agent

# Test
# (invoke agent with test scenario)

# Verify
python3 enhance-agent.py my-agent

# Commit only if working
git add .claude/agents/my-agent.md
git commit -m "refactor(agent): migrate my-agent"
```

### 3. Track Improvements

Measure before/after:

```bash
# Before
python3 enhance-agent.py my-agent > before.txt

# Migrate
# ...

# After
python3 enhance-agent.py my-agent > after.txt

# Compare
diff before.txt after.txt
```

### 4. Document Breaking Behavior

If migration changes agent behavior:

```yaml
description: Updated description (NOTE: Now uses different workflow - see CHANGELOG)
```

Create CHANGELOG in agent comments:

```markdown
<!-- CHANGELOG
v2 (2025-01-13):
- Migrated to current schema
- Changed from opus to sonnet (faster)
- Removed Bash access (security)
- Added examples section

v1 (2024-12-01):
- Initial creation
-->
```

---

## Rollback

If migration breaks an agent:

### Quick Rollback

```bash
# Restore from backup
mv .claude/agents/my-agent.md.bak .claude/agents/my-agent.md
```

### Git Rollback

```bash
# Restore from git
git checkout HEAD -- .claude/agents/my-agent.md
```

### Selective Rollback

```bash
# Keep some changes, revert others
git diff .claude/agents/my-agent.md
# Manually edit to keep good changes
```

---

## Migration Support

### Getting Help

1. **Run enhancement analysis**:
   ```bash
   python3 enhance-agent.py my-agent
   ```

2. **Check update patterns**:
   See [agent-update-patterns.md](./agent-update-patterns.md)

3. **Use quality checklist**:
   See [agent-checklist.md](../templates/agent-checklist.md)

4. **Review examples**:
   Check `agent-builder/skills/building-agents/references/agent-examples.md`

---

## Related Resources

- [Update Patterns](./agent-update-patterns.md) - Common update scenarios
- [Agent Checklist](../templates/agent-checklist.md) - Quality review checklist
- [SKILL.md](../SKILL.md) - Complete building guide
- [Agent Template](../templates/agent-template.md) - Standard template
