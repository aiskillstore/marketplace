---
name: creating-agents
description: |
  Creates Claude Code subagents for task delegation. Guides through agent configuration,
  tool selection, and system prompts. Use this skill when the user wants to create a new agent,
  delegate tasks to specialists, or asks about subagents.
---

# Creating Agents

Guides creation of Claude Code subagents for task delegation.

## Quick Start

1. Define agent purpose (what task does it handle?)
2. Choose location (project or user level)
3. Select tools (minimal set needed)
4. Write system prompt
5. Save to `.claude/agents/`

## Workflow: Create New Agent

```
Progress:
- [ ] Define purpose and triggers
- [ ] Choose storage location
- [ ] Select tools and model
- [ ] Write system prompt
- [ ] Create agent file
```

### Step 1: Define Purpose

Ask user:
- What specific task should this agent handle?
- When should it be invoked? (trigger phrases)
- Should it run proactively or on-demand?

### Step 2: Choose Location

| Location | Path | Use For |
|----------|------|---------|
| Project | `.claude/agents/` | Team-shared, project-specific |
| User | `~/.claude/agents/` | Personal, cross-project |

Project agents take priority over user agents.

### Step 3: Select Tools and Model

**Tools** - Grant minimum needed:

| Tool | Purpose |
|------|---------|
| Read | Read files |
| Write | Create files |
| Edit | Modify files |
| Glob | Find files |
| Grep | Search content |
| Bash | Run commands |
| Task | Spawn subagents |

**Model** - Choose based on task:

| Model | Best For |
|-------|----------|
| `opus` | Complex reasoning, nuanced decisions |
| `sonnet` | General tasks (default) |
| `haiku` | Quick lookups, simple analysis |
| `inherit` | Use parent's model |

### Step 4: Write System Prompt

Keep prompts focused:
- State the agent's role clearly
- Define scope and constraints
- Provide examples if helpful
- Avoid unnecessary detail

### Step 5: Create Agent File

```markdown
---
name: {agent-name}
description: {when to use - include trigger words}
tools: Read, Grep, Glob
model: sonnet
---

{System prompt here}
```

Save to `.claude/agents/{name}.md`

## Agent File Format

```yaml
---
name: agent-name          # Required: lowercase, hyphens
description: |            # Required: when to invoke
  Reviews code for quality issues.
  Use when user asks for code review.
tools: Read, Grep, Glob   # Optional: omit to inherit all
model: sonnet             # Optional: opus, sonnet, haiku, inherit
permissionMode: default   # Optional: permission handling
skills: skill1, skill2    # Optional: auto-load skills
---

System prompt defining the agent's behavior.
```

## Built-in Agents

Before creating custom agents, know what's built-in:

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| general-purpose | sonnet | All | Complex multi-step tasks |
| plan | haiku | Read, Glob, Grep, Bash | Research and strategy |
| explore | haiku | Read, Glob, Grep | Fast codebase exploration |

**When to create custom agents:**
- Need different tool restrictions
- Want domain-specific prompts
- Need proactive invocation

## When to Use Each Type

| Need | Use |
|------|-----|
| Quick file search | Built-in `explore` |
| Research before planning | Built-in `plan` |
| Multi-step code changes | Built-in `general-purpose` |
| Code review with specific rules | Custom reviewer agent |
| Security analysis | Custom security agent |
| Domain expertise (DB, API, etc.) | Custom specialist agent |

## Proactive Invocation

To make Claude automatically use your agent, include in description:
- "PROACTIVELY" or "MUST BE USED"
- Clear trigger conditions

```yaml
description: |
  PROACTIVELY reviews all code changes before commit.
  MUST BE USED when user mentions "review" or "check code".
```

## Templates

Use templates from `templates/` directory:
- [templates/reviewer.md](templates/reviewer.md) - Code review agent
- [templates/researcher.md](templates/researcher.md) - Read-only research
- [templates/specialist.md](templates/specialist.md) - Domain expert

See [reference.md](reference.md) for complete configuration details.
