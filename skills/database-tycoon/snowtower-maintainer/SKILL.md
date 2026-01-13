---
name: snowtower-maintainer
description: Maintains SnowTower project documentation, README, and Claude configuration. Use when updating documentation, auditing .claude folder contents, syncing README with actual project state, or reviewing agent/pattern definitions. Triggers on mentions of documentation, README, maintenance, or .claude folder updates.
---

# SnowTower Project Maintainer

A specialized skill for maintaining the SnowTower project's documentation, README, and Claude Code configuration.

## Core Responsibilities

### 1. README Maintenance

Keep `README.md` accurate and current:

- **Version badges**: Ensure CI/CD badges point to correct workflows
- **Command references**: Verify all `uv run` commands are valid
- **Architecture diagrams**: Keep mermaid diagrams in sync with actual structure
- **Statistics**: Update user counts, database counts, warehouse counts
- **Links**: Verify all internal links resolve correctly

**Audit checklist:**
```bash
# Verify commands mentioned in README actually exist
uv run --help | grep -E "snowddl-plan|deploy-safe|manage-users"

# Check workflow badge URLs match actual workflow files
ls .github/workflows/

# Verify documentation links
find docs/ -name "*.md" | head -20
```

### 2. Claude Folder Maintenance

Maintain `.claude/` organization:

```
.claude/
├── skills/           # Claude Code skills (like this one)
├── agents/           # Agent definitions for task delegation
├── patterns/         # Reusable patterns and templates
└── settings.local.json
```

**Agent audit tasks:**
- Remove duplicate or redundant agents
- Consolidate agents with overlapping purposes
- Update agent descriptions to match current capabilities
- Ensure agents reference correct file paths

**Pattern audit tasks:**
- Verify patterns match current project conventions
- Update code examples in patterns
- Remove outdated patterns

### 3. Documentation Sync

Ensure docs reflect actual project state:

| Doc File | Should Match |
|----------|--------------|
| `docs/guide/MANAGEMENT_COMMANDS.md` | `pyproject.toml` scripts |
| `docs/guide/QUICKSTART.md` | Current setup process |
| `docs/guide/SCHEMA_GRANTS.md` | Current grant handling |
| Agent files in `.claude/agents/` | Available functionality |

## Maintenance Procedures

### Quick Health Check

```bash
# 1. Verify project structure
ls -la snowddl/ src/ scripts/ docs/

# 2. Check available commands
uv run --help

# 3. Verify tests pass
uv run pytest --co -q | tail -5

# 4. Check pre-commit status
uv run pre-commit run --all-files
```

### README Update Workflow

1. **Gather current state:**
   ```bash
   # Count configured users
   grep -c "^  [A-Z]" snowddl/user.yaml

   # Count databases
   ls -d snowddl/*/ | grep -v __pycache__ | wc -l

   # List warehouses
   grep "^  [A-Z]" snowddl/warehouse.yaml
   ```

2. **Verify commands:**
   ```bash
   # Extract commands from pyproject.toml
   grep -A1 "\[project.scripts\]" pyproject.toml
   ```

3. **Update statistics section** in README with current counts

4. **Verify all links** resolve to existing files

### Agent Consolidation

When auditing `.claude/agents/`:

1. **List all agents:**
   ```bash
   ls .claude/agents/*.md
   ```

2. **Identify overlaps:** Look for agents with similar purposes

3. **Consolidation criteria:**
   - Merge agents that serve the same domain
   - Keep agents with distinct, valuable roles
   - Remove agents that duplicate built-in capabilities

4. **Update references:** After consolidation, update any docs referencing removed agents

### Self-Maintenance

This skill should maintain itself by:

1. Keeping this SKILL.md up to date with project changes
2. Adding new maintenance procedures as project evolves
3. Updating file paths when project structure changes
4. Documenting new patterns discovered during maintenance

## Common Maintenance Tasks

### Task: Update README Statistics

```markdown
### Status & Metrics

- **Active Users**: [COUNT] configured users with MFA
- **Databases**: [COUNT] production databases managed
- **Warehouses**: [COUNT] warehouses with auto-suspend
```

Update these by running:
```bash
echo "Users: $(grep -c '^  [A-Z]' snowddl/user.yaml)"
echo "Databases: $(ls -d snowddl/*/ 2>/dev/null | grep -v __pycache__ | wc -l)"
echo "Warehouses: $(grep -c '^  [A-Z]' snowddl/warehouse.yaml)"
```

### Task: Verify Workflow Badges

Check that README badges match actual workflows:
```bash
# List workflows
ls .github/workflows/

# Verify badge URLs in README reference these files
grep "actions/workflows" README.md
```

### Task: Audit Agent Definitions

```bash
# List agents and their purposes
for f in .claude/agents/*.md; do
  echo "=== $f ==="
  head -5 "$f"
  echo
done
```

### Task: Clean Up Obsolete Content

Remove references to:
- Deleted files or directories
- Deprecated commands
- Old workflow names
- Removed features

## Integration with Project

This skill works with:

- **CI/CD workflows**: `.github/workflows/`
- **SnowDDL configs**: `snowddl/*.yaml`
- **Python tooling**: `src/`, `scripts/`
- **Documentation**: `docs/`
- **Claude config**: `.claude/`

## When to Trigger

Invoke this skill when:
- User asks to "update the README"
- User mentions "documentation maintenance"
- User wants to "audit the .claude folder"
- User asks about "project documentation"
- After significant feature additions
- Before releases to ensure docs are current
- When onboarding new contributors
