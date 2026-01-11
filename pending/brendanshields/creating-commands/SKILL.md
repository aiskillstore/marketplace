---
name: creating-commands
description: |
  Creates new Claude Code slash commands following best practices. Guides through command
  structure, naming, arguments, and frontmatter. Use when user wants to create a command,
  build a slash command, or asks about command best practices.
---

# Creating Commands

Guides creation of Claude Code slash commands using documented best practices.

## Quick Start

For a new command:
1. Ask user for command purpose and arguments needed
2. Generate using appropriate template
3. Validate against checklist

For reviewing existing command:
1. Read command file
2. Check against anti-patterns in [reference.md](reference.md)
3. Report issues with fixes

## Workflow: Create New Command

```
Progress:
- [ ] Gather requirements (purpose, arguments, scope)
- [ ] Choose template (basic, with-args, workflow)
- [ ] Generate command file
- [ ] Validate against checklist
```

### Step 1: Gather Requirements

Ask user with AskUserQuestion:
- What should this command do? (purpose)
- Does it need arguments? (none, single, multiple)
- Project or personal? (scope)

### Step 2: Choose Template

| Type | Template | When to Use |
|------|----------|-------------|
| Basic | [templates/basic.md](templates/basic.md) | No arguments, simple prompt |
| With Args | [templates/with-args.md](templates/with-args.md) | Single or multiple arguments |
| Workflow | [templates/workflow.md](templates/workflow.md) | Integrates with skills/agents |

### Step 3: Generate Command

Create in appropriate location:
- `.claude/commands/` - Project commands (git-tracked)
- `~/.claude/commands/` - Personal commands (your machine only)

### Step 4: Validate

Run through checklist before finishing:

```
Validation Checklist:
- [ ] Name: lowercase with hyphens only
- [ ] Name: descriptive, verb-noun format preferred
- [ ] Description: explains what command does
- [ ] Arguments: documented with argument-hint if used
- [ ] Prompt: clear, actionable instructions
- [ ] Tools: allowed-tools declared if needed
```

## Naming Rules

**Format**: `verb-noun` or `action` (lowercase, hyphens)
- `fix-issue`
- `review-pr`
- `run-tests`
- `optimize`

**Constraints**:
- Lowercase letters, numbers, hyphens only
- No spaces or underscores
- Keep concise (1-3 words)

## Command File Format

```markdown
---
description: Brief explanation shown in help
allowed-tools:
  - Bash(bash:*)
  - WebSearch
argument-hint: "param_name"
---

Your command prompt here.
Use $ARGUMENTS for all args or $1, $2 for positional.
```

## Argument Syntax

| Syntax | Usage | Example |
|--------|-------|---------|
| `$ARGUMENTS` | All arguments as one string | `/cmd foo bar` → `foo bar` |
| `$1`, `$2` | Positional arguments | `/cmd foo bar` → `$1=foo`, `$2=bar` |
| `@file` | Include file contents | `Review @src/main.ts` |

## Frontmatter Options

| Field | Purpose | Required |
|-------|---------|----------|
| `description` | Shown in help, enables auto-invoke | Recommended |
| `allowed-tools` | Tools the command can use | If using tools |
| `argument-hint` | Documents expected args | If has args |
| `model` | Specific model to use | Optional |

## Example: Basic Command

```markdown
---
description: Run all tests and report failures
allowed-tools:
  - Bash(npm:*)
---

Run the test suite and summarize results:

1. Execute `npm test`
2. If failures, show failing tests with context
3. Suggest fixes for common issues
```

See [reference.md](reference.md) for detailed best practices and anti-patterns.
