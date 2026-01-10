---
name: claude-code-debug
description: "Troubleshoot Claude Code extensions and behavior. Triggers on: debug, troubleshoot, not working, skill not loading, hook not running, agent not found."
compatibility: "Claude Code CLI"
allowed-tools: "Bash Read"
depends-on: []
related-skills: [claude-code-hooks, claude-code-headless, claude-code-templates]
---

# Claude Code Debug

Troubleshoot extensions, hooks, and unexpected behavior.

## Quick Diagnostics

```bash
# Enable debug mode
claude --debug

# Check loaded extensions
/hooks        # View registered hooks
/agents       # View available agents
/memory       # View loaded memory files
/config       # View current configuration
```

## Common Issues

| Symptom | Quick Check |
|---------|-------------|
| Skill not activating | Verify description has trigger keywords |
| Hook not running | Check `chmod +x`, run `/hooks` |
| Agent not delegating | Add "Use proactively" to description |
| MCP connection fails | Test server manually with `npx` |
| Permission denied | Check settings.json allow rules |

## Debug Mode Output

```bash
claude --debug
# Shows:
# - Hook execution and errors
# - Skill loading status
# - Subagent invocations
# - Tool permission decisions
# - MCP server connections
```

## Quick Fixes

### Skill Not Loading

```bash
# Check structure
ls -la .claude/skills/my-skill/
# Must have: SKILL.md

# Verify YAML frontmatter
head -10 .claude/skills/my-skill/SKILL.md
# Must start/end with ---

# Check name matches directory
grep "^name:" .claude/skills/my-skill/SKILL.md
```

### Hook Not Executing

```bash
# Make executable
chmod +x .claude/hooks/my-hook.sh

# Test manually
echo '{"tool_name":"Bash"}' | .claude/hooks/my-hook.sh
echo $?  # Check exit code

# Verify JSON syntax
jq '.' ~/.claude/settings.json
```

### Agent Not Being Used

```bash
# Check file location
ls ~/.claude/agents/
ls .claude/agents/

# Verify description includes "Use for:" or "Use proactively"
grep -i "use" agents/my-agent.md | head -5

# Explicitly request
# "Use the my-agent agent to analyze this"
```

## Validation

```bash
# Run all validations
just test

# YAML validation only
just validate-yaml

# Name matching only
just validate-names
```

## Official Documentation

- https://code.claude.com/docs/en/hooks - Hooks reference
- https://code.claude.com/docs/en/skills - Skills reference
- https://code.claude.com/docs/en/sub-agents - Custom subagents
- https://code.claude.com/docs/en/settings - Settings configuration

## Additional Resources

- `./references/common-issues.md` - Issue → Solution lookup table
- `./references/debug-commands.md` - All inspection commands
- `./references/troubleshooting-flow.md` - Decision tree

---

**See Also:** `claude-code-hooks` for hook debugging, `claude-code-templates` for correct structure
