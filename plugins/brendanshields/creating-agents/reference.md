# Agent Configuration Reference

Complete reference for Claude Code subagent configuration.

## File Format

Agent files are Markdown with YAML frontmatter:

```markdown
---
name: agent-name
description: When to use this agent
tools: Tool1, Tool2
model: sonnet
permissionMode: default
skills: skill1, skill2
---

System prompt content here.
Can be multiple paragraphs.
```

## Frontmatter Fields

### name (required)

Unique identifier for the agent.

**Format**: lowercase letters, numbers, hyphens only
**Max length**: 64 characters

```yaml
name: code-reviewer      # Good
name: CodeReviewer       # Bad - uppercase
name: code_reviewer      # Bad - underscore
```

### description (required)

Explains when Claude should use this agent. Critical for automatic selection.

**Best practices**:
- Include trigger words users might say
- Be specific about the task
- Use action-oriented language

```yaml
# Good - specific with triggers
description: |
  Reviews code for quality, security, and maintainability issues.
  Use when user asks for code review, PR feedback, or quality check.

# Bad - vague
description: Helps with code stuff
```

### tools (optional)

Comma-separated list of tools the agent can use.

**If omitted**: Agent inherits all tools from parent
**Recommendation**: Grant minimum needed (principle of least privilege)

```yaml
tools: Read, Grep, Glob           # Read-only
tools: Read, Write, Edit, Bash    # Full access
```

**Available tools**:
| Tool | Purpose |
|------|---------|
| Read | Read file contents |
| Write | Create new files |
| Edit | Modify existing files |
| Glob | Find files by pattern |
| Grep | Search file contents |
| Bash | Execute shell commands |
| Task | Spawn subagents |
| WebFetch | Fetch web content |
| WebSearch | Search the web |
| AskUserQuestion | Ask user for input |
| TodoWrite | Manage task list |

### model (optional)

Which model powers the agent.

| Value | Description |
|-------|-------------|
| `opus` | Most capable, complex reasoning |
| `sonnet` | Balanced performance (default) |
| `haiku` | Fast, cost-effective |
| `inherit` | Use parent's model |

```yaml
model: haiku    # For quick lookups
model: opus     # For complex analysis
model: inherit  # Match parent context
```

### permissionMode (optional)

Controls how agent handles permissions.

| Mode | Behavior |
|------|----------|
| `default` | Normal permission prompts |
| `plan` | Plan mode only |
| `acceptEdits` | Auto-accept file edits |
| `bypassPermissions` | Skip all prompts (use carefully) |

### skills (optional)

Auto-load specific skills when agent runs.

```yaml
skills: creating-skills, reviewing-dotnet-code
```

## System Prompt Guidelines

The content after frontmatter is the agent's system prompt.

### Structure

```markdown
---
(frontmatter)
---

# Role Statement
You are a {role} that {primary function}.

## Responsibilities
- {responsibility 1}
- {responsibility 2}

## Constraints
- {constraint 1}
- {constraint 2}

## Output Format
{how to structure responses}
```

### Best Practices

1. **Be specific**: State exact behaviors, not general goals
2. **Set boundaries**: What the agent should NOT do
3. **Provide examples**: Show expected output format
4. **Keep focused**: One clear purpose per agent

### Example Prompts

**Code Reviewer**:
```markdown
You are a code reviewer focused on quality and security.

Review code for:
- Security vulnerabilities (injection, XSS, etc.)
- Performance issues
- Code style consistency
- Error handling gaps

Format findings as:
- **Critical**: Must fix before merge
- **Warning**: Should address
- **Suggestion**: Nice to have
```

**Research Agent**:
```markdown
You are a codebase researcher. You do NOT modify files.

When asked about the codebase:
1. Search for relevant files using Glob
2. Read key files to understand patterns
3. Summarize findings with file references

Always cite specific files and line numbers.
```

## Storage Locations

| Type | Path | Priority |
|------|------|----------|
| CLI | `--agents` flag | Highest |
| Project | `.claude/agents/` | High |
| User | `~/.claude/agents/` | Low |
| Plugin | Plugin's `agents/` | Varies |

Project agents override user agents with same name.

## Invoking Agents

### Automatic

Claude selects based on task and description match.

### Explicit

```
> Use the code-reviewer agent to check this PR
> Have the security-agent analyze auth.ts
```

### Resume Previous

```
> Resume agent abc123 and continue
```

## Common Patterns

### Read-Only Agent

```yaml
tools: Read, Glob, Grep
```

No Write, Edit, or Bash - cannot modify anything.

### Analysis Agent

```yaml
tools: Read, Glob, Grep, Bash
model: opus
```

Full read access plus command execution for analysis tools.

### Modification Agent

```yaml
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
```

Full access for making changes.

## Debugging Agents

1. Check file location: `.claude/agents/` or `~/.claude/agents/`
2. Validate frontmatter YAML syntax
3. Ensure name is lowercase with hyphens
4. Verify description includes trigger words
5. Test with explicit invocation first
