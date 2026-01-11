# Skill Maintenance Guide

Quick reference for maintaining Claude Code skills.

---

## Critical Differences: Skills vs Commands

| Aspect | Skills | Commands |
|--------|--------|----------|
| **Model Field** | ❌ NOT supported | ✅ Supported (version aliases) |
| **Structure** | Directory with SKILL.md | Single .md file |
| **Naming** | Gerund form (building-x) | Action verb (create-x) |
| **Focus** | WHEN to auto-invoke | WHAT action to perform |
| **Invocation** | Automatic by Claude | Manual by user |

---

## Maintenance Tools

### Update Skill
```bash
/agent-builder:skills:update <skill-name>
```
Interactive updater for description, allowed-tools, version.
**Critical**: Blocks if model field present.

### Enhance Skill
```bash
/agent-builder:skills:enhance <skill-name>
```
7-category quality analysis (0-10 score each):
1. Schema compliance
2. Model field check (CRITICAL)
3. Auto-invocation clarity
4. Directory structure
5. Security
6. Content quality
7. Maintainability

### Migrate Skill
```bash
/agent-builder:skills:migrate <skill-name> --apply
```
**CRITICAL**: Removes model field (skills don't support it).
Also checks gerund form and auto-invocation triggers.

---

## Common Issues

### 1. Model Field Present (CRITICAL ERROR)

**Problem**: Skill has `model:` field in SKILL.md frontmatter

**Symptoms**:
- Skill may fail to load
- Update script blocks with error
- Validation fails

**Solution**:
```bash
/agent-builder:skills:migrate my-skill --apply
```

**Why**: Skills are "always-on" and use conversation context. Only agents (with isolated invocations) support model specification.

### 2. Unclear Auto-Invocation

**Problem**: Description doesn't state WHEN Claude should use skill

**Symptoms**:
- Enhancement score low on "Auto-Invocation" category
- Claude doesn't invoke skill when appropriate
- Users unsure when skill activates

**Solution**: Update description to include triggers:
```yaml
# Bad (vague)
description: Helps with building commands

# Good (specific)
description: Expert at building commands. Auto-invokes when user wants to create, update, or validate a command.
```

### 3. Missing {baseDir} Variable

**Problem**: Skill has scripts/references/assets but doesn't use {baseDir}

**Symptoms**:
- Scripts can't be found
- References aren't accessible
- Enhancement flags missing {baseDir}

**Solution**: Reference resources with {baseDir}:
```markdown
Run script:
\`\`\`bash
python3 {baseDir}/scripts/helper.py
\`\`\`

See: [{baseDir}/references/guide.md]
```

### 4. Non-Executable Scripts

**Problem**: Scripts in scripts/ directory aren't executable

**Symptoms**:
- Permission denied errors
- Enhancement reports non-executable scripts

**Solution**:
```bash
chmod +x agent-builder/skills/my-skill/scripts/*.py
chmod +x agent-builder/skills/my-skill/scripts/*.sh
```

### 5. Non-Gerund Naming

**Problem**: Skill name doesn't use gerund form

**Symptoms**:
- Enhancement recommendation about naming
- Inconsistent with other skills

**Solution**: Consider renaming directory:
```bash
# Current
my-commands/

# Better (gerund form)
building-commands/
```

Note: This is a recommendation, not a requirement.

---

## Quick Checklist

### Schema
- [ ] Name is lowercase-hyphens (max 64 chars)
- [ ] Name uses gerund form (recommended)
- [ ] Description clearly states WHEN to auto-invoke
- [ ] ❌ NO model field (CRITICAL)
- [ ] Has version field (semantic versioning)
- [ ] Directory name matches frontmatter name

### Content
- [ ] Has "When to Use" section
- [ ] Has "Capabilities" section
- [ ] Has examples showing auto-invocation
- [ ] Documents all resources (scripts, references)
- [ ] Uses {baseDir} for resource paths
- [ ] Well-organized with headings

### Directory Structure
- [ ] SKILL.md is present and valid
- [ ] scripts/ subdirectory (if needed)
- [ ] references/ subdirectory (if needed)
- [ ] assets/ or templates/ (if needed)
- [ ] No unexpected subdirectories
- [ ] All scripts are executable (chmod +x)

### Security
- [ ] Minimal allowed-tools
- [ ] Bash access documented with validation
- [ ] No hardcoded secrets
- [ ] Input validation documented

---

## Workflow

### Creating a New Skill
1. Use skill creation tools or templates
2. Validate: `python3 validate-skill.py my-skill/`
3. Enhance: `/agent-builder:skills:enhance my-skill`
4. Address recommendations
5. Re-validate and test

### Updating an Existing Skill
1. Analyze: `/agent-builder:skills:enhance my-skill`
2. Update: `/agent-builder:skills:update my-skill`
3. Validate changes
4. Test auto-invocation

### Migrating Skills
1. Preview: `/agent-builder:skills:migrate --dry-run`
2. Apply: `/agent-builder:skills:migrate --apply`
3. Validate all skills
4. Test critical skills

---

## Model Field: Why Skills Don't Support It

**Skills** are "always-on" expertise modules:
- Auto-invoked by Claude based on context
- Use the conversation's model
- No isolated context
- Progressive resource disclosure

**Agents** are explicitly invoked tasks:
- Called manually or by Claude's Task tool
- Have isolated context
- Can specify their own model
- Full context on invocation

**Result**: Only agents support the `model` field. Skills use the conversation's model context.

---

## Resources

### Scripts
- `validate-skill.py` - Schema validation
- `update-skill.py` - Interactive updater
- `enhance-skill.py` - Quality analysis
- `migrate-skill.py` - Schema migration

### Commands
- `/agent-builder:skills:update` - Update configuration
- `/agent-builder:skills:enhance` - Get quality score
- `/agent-builder:skills:migrate` - Migrate schema

### Related Guides
- Phase 1 (Commands Maintenance) provides parallel examples
- Building Skills SKILL.md for creation guidance
- Validate script source for validation rules

---

## Quick Reference

```bash
# Analyze quality
/agent-builder:skills:enhance my-skill

# Update interactively
/agent-builder:skills:update my-skill

# Remove model field (critical)
/agent-builder:skills:migrate my-skill --apply

# Validate schema
python3 agent-builder/skills/building-skills/scripts/validate-skill.py my-skill/

# Make scripts executable
chmod +x my-skill/scripts/*.py

# Preview migrations
/agent-builder:skills:migrate --dry-run
```

---

**Remember**: The most critical difference between skills and commands is that **skills cannot have a model field**. Always check for and remove this field first.
