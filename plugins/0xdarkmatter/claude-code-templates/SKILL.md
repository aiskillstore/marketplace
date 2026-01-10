---
name: claude-code-templates
description: "Boilerplate templates for Claude Code extensions. Triggers on: create agent, new skill, command template, hook script, extension scaffold."
compatibility: "Claude Code CLI"
allowed-tools: "Read Write"
depends-on: []
related-skills: [claude-code-hooks, claude-code-debug]
---

# Claude Code Templates

Starter templates for building Claude Code extensions.

## Template Selection

| Building | Template | Key Features |
|----------|----------|--------------|
| Expert persona | `agent-template.md` | Focus areas, quality checklist, references |
| Tool capability | `skill-template.md` | Commands, examples, triggers |
| User workflow | `command-template.md` | Execution flow, options |
| Automation | `hook-script.sh` | Input parsing, exit codes |

## Quick Start

### Create an Agent

```bash
# Copy template
cp ~/.claude/skills/claude-code-templates/assets/agent-template.md \
   ~/.claude/agents/my-expert.md

# Edit: name, description, focus areas, references
```

### Create a Skill

```bash
# Create skill directory
mkdir -p ~/.claude/skills/my-skill

# Copy template
cp ~/.claude/skills/claude-code-templates/assets/skill-template.md \
   ~/.claude/skills/my-skill/SKILL.md

# Edit: name, description, commands, examples
```

### Create a Command

```bash
# Copy template
cp ~/.claude/skills/claude-code-templates/assets/command-template.md \
   ~/.claude/commands/my-command.md

# Edit: name, description, execution flow
```

### Create a Hook Script

```bash
# Copy template
cp ~/.claude/skills/claude-code-templates/assets/hook-script.sh \
   .claude/hooks/my-hook.sh

# Make executable
chmod +x .claude/hooks/my-hook.sh
```

## Template Locations

Templates are in `./assets/`:

| File | Purpose |
|------|---------|
| `agent-template.md` | Expert agent boilerplate |
| `skill-template.md` | Skill with YAML frontmatter |
| `command-template.md` | Slash command scaffold |
| `hook-script.sh` | Secure hook script template |

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Agent | `{technology}-expert.md` | `react-expert.md` |
| Skill | `{tool-or-pattern}/SKILL.md` | `git-workflow/SKILL.md` |
| Command | `{action}.md` | `review.md` |
| Hook | `{event}-{action}.sh` | `pre-write-validate.sh` |

## Validation

```bash
# Validate YAML frontmatter
head -20 my-extension.md

# Check name matches filename
grep "^name:" my-extension.md

# Run project tests
just test
```

## Official Documentation

- https://code.claude.com/docs/en/skills - Skills reference
- https://code.claude.com/docs/en/sub-agents - Custom subagents
- https://code.claude.com/docs/en/hooks - Hooks reference
- https://agentskills.io/specification - Agent Skills open standard

## Assets

- `./assets/agent-template.md` - Expert agent scaffold
- `./assets/skill-template.md` - Skill with references pattern
- `./assets/command-template.md` - Slash command scaffold
- `./assets/hook-script.sh` - Secure bash hook template

---

**See Also:** `claude-code-debug` for troubleshooting extensions
