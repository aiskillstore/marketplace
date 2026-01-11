# Command Reference

Detailed best practices for Claude Code slash commands.

## Command File Format

Commands are Markdown files with optional YAML frontmatter:

```markdown
---
description: "Brief explanation for help and auto-invoke"
allowed-tools:
  - Bash(bash:*)
  - WebSearch
  - WebFetch(domain:github.com)
argument-hint: "issue_number"
model: claude-sonnet-4-5-20250929
---

# Command prompt content

Instructions for Claude to follow...
```

## Frontmatter Reference

### description

Shown in help output and enables Claude to auto-invoke the command.

```yaml
description: "Find and fix a GitHub issue by number"
```

If omitted, first line of content is used as description.

### allowed-tools

Specifies which tools the command can use:

```yaml
allowed-tools:
  - Bash(bash:*)           # All bash commands
  - Bash(npm:*)            # npm commands only
  - Bash(mkdir:*)          # mkdir commands
  - WebSearch              # Web search
  - WebFetch(domain:X)     # Fetch from specific domain
  - Skill(skill-name)      # Invoke a skill
  - Task                   # Launch subagents
```

### argument-hint

Documents expected parameters for auto-completion:

```yaml
argument-hint: "issue_number"
argument-hint: "branch_name commit_message"
```

### model

Designates a specific AI model:

```yaml
model: claude-sonnet-4-5-20250929
```

### disable-model-invocation

Prevents Claude from auto-invoking this command:

```yaml
disable-model-invocation: true
```

## Argument Patterns

### All Arguments ($ARGUMENTS)

Best for single-value or freeform input:

```markdown
Find and fix issue #$ARGUMENTS. Analyze the problem and implement a solution.
```

Usage: `/fix-issue 123` → `$ARGUMENTS` = `123`

### Positional Arguments ($1, $2, etc.)

Best for multiple distinct parameters:

```markdown
Create a new component:
- Name: $1
- Type: $2

Generate the component following project conventions.
```

Usage: `/new-component Button functional` → `$1` = `Button`, `$2` = `functional`

### File References (@)

Include file contents in the prompt:

```markdown
Review this code for issues:

@$1

Focus on performance and security.
```

Usage: `/review @src/api/auth.ts`

## File Locations

| Location | Scope | Visibility |
|----------|-------|------------|
| `.claude/commands/` | Project | All team members |
| `~/.claude/commands/` | Personal | Only you |
| `.claude/commands/namespace/` | Namespaced | Team, grouped |

### Namespacing

Organize related commands:

```
.claude/commands/
├── review-pr.md           → /review-pr
├── frontend/
│   ├── component.md       → /component (project:frontend)
│   └── style.md           → /style (project:frontend)
└── backend/
    └── migrate.md         → /migrate (project:backend)
```

## Integration Patterns

### With Skills

```yaml
---
description: "Start workflow using orbit skill"
allowed-tools:
  - Skill(orbit-workflow)
---

Use the orbit-workflow skill to begin a new feature.
Feature name: $1
```

### With Agents

```yaml
---
description: "Analyze codebase architecture"
allowed-tools:
  - Task
---

Launch the analyzing-codebase agent to examine this project's structure.
Focus on: $ARGUMENTS
```

### With Bash

```yaml
---
description: "Run tests with coverage"
allowed-tools:
  - Bash(npm:*)
  - Bash(npx:*)
---

Run the test suite with coverage:

1. Execute `npm test -- --coverage`
2. Summarize coverage report
3. Flag files under 80% coverage
```

## Anti-Patterns

| Avoid | Do Instead |
|-------|------------|
| Vague descriptions | Specific action + context |
| Missing allowed-tools | Declare tools needed |
| No argument-hint | Document expected args |
| Overly complex prompts | Break into multiple commands |
| Hardcoded paths | Use arguments for flexibility |
| Windows paths | Unix paths only |

## Validation Checklist

Before saving a command:

```
- [ ] Name: lowercase with hyphens
- [ ] Name: verb-noun format, concise
- [ ] Description: clear, actionable
- [ ] Description: includes what and when
- [ ] Arguments: documented if used
- [ ] Arguments: hint provided
- [ ] Tools: allowed-tools declared
- [ ] Prompt: step-by-step instructions
- [ ] Prompt: no hardcoded values
```

## Command Examples

### Simple: Run Tests

```markdown
---
description: "Run tests and summarize results"
allowed-tools:
  - Bash(npm:*)
---

Run the test suite:

1. Execute `npm test`
2. Summarize pass/fail counts
3. Show details for any failures
```

### With Args: Fix Issue

```markdown
---
description: "Find and fix a GitHub issue"
allowed-tools:
  - WebFetch(domain:github.com)
argument-hint: "issue_number"
---

Fix issue #$1:

1. Fetch issue details from GitHub
2. Understand the requirements
3. Locate relevant code
4. Implement the fix
5. Add tests if applicable
```

### Workflow: Deploy

```markdown
---
description: "Deploy to specified environment"
allowed-tools:
  - Bash(npm:*)
  - Bash(git:*)
argument-hint: "environment"
---

Deploy to $1 environment:

1. Run tests to ensure passing
2. Build production bundle
3. Deploy using environment config
4. Verify deployment health
```
