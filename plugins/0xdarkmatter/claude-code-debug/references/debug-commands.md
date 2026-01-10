# Debug Commands Reference

All inspection and debugging commands for Claude Code.

## CLI Debug Mode

```bash
# Full debug output
claude --debug

# Verbose logging
claude --verbose
claude -v
```

### Debug Mode Shows

| Category | Information |
|----------|-------------|
| Hooks | Loading, execution, errors, exit codes |
| Skills | Discovery, activation, loading errors |
| Agents | Invocation, tool access, context inheritance |
| Permissions | Allow/deny decisions, rule matching |
| MCP | Server connections, tool registration |
| Context | Memory loading, rule application |

## Slash Commands

### /hooks

List all registered hooks and their configuration.

```
/hooks

Output:
PreToolUse:
  - Bash: ./hooks/validate-bash.sh (timeout: 5000ms)
  - *: ./hooks/audit-log.sh (timeout: 3000ms)

PostToolUse:
  - Write: ./hooks/notify-write.sh
```

### /agents

Manage and inspect subagents.

```
/agents

Output:
Available Agents:
  Built-in:
    - Explore (read-only codebase search)
    - Plan (implementation planning)
    - general-purpose (default)

  Custom (user):
    - python-expert
    - react-expert

  Custom (project):
    - my-project-agent
```

Actions:
- View agent details
- Create new agent
- Edit existing agent
- Delete agent

### /memory

View and edit memory files (CLAUDE.md).

```
/memory

Output:
Loaded Memory Files:
  1. ~/.claude/CLAUDE.md (user)
  2. ./CLAUDE.md (project)
  3. ./.claude/CLAUDE.md (project)

Imports:
  - @README.md
  - @docs/api.md
```

Opens system editor for editing when invoked.

### /config

View current configuration state.

```
/config

Output:
Permission Mode: default
Model: claude-sonnet-4-20250514

Permissions:
  Allow: Bash(git:*), Bash(npm:*), Read, Write
  Deny: Bash(rm -rf:*)

Active MCP Servers:
  - filesystem: /Users/me/.npm/_npx/...
  - github: /Users/me/.npm/_npx/...
```

### /plugin

Browse and manage installed plugins.

```
/plugin

Output:
Installed Plugins:
  - my-plugin (v1.0.0)
    Commands: /my-command
    Skills: my-skill

Marketplaces:
  - awesome-plugins (github:user/repo)
```

## File System Inspection

### Check Extension Structure

```bash
# Skills
ls -la .claude/skills/
ls -la ~/.claude/skills/

# Agents
ls -la .claude/agents/
ls -la ~/.claude/agents/

# Commands
ls -la .claude/commands/
ls -la ~/.claude/commands/

# Rules
ls -la .claude/rules/
ls -la ~/.claude/rules/

# Hooks
ls -la .claude/hooks/
```

### Verify Configuration Files

```bash
# Global settings
cat ~/.claude/settings.json | jq '.'

# Project settings
cat .claude/settings.local.json | jq '.'

# MCP configuration
cat .mcp.json | jq '.'
```

### Check YAML Frontmatter

```bash
# View frontmatter
head -20 path/to/extension.md

# Extract name field
grep "^name:" path/to/extension.md

# Validate YAML structure
head -20 path/to/extension.md | grep -E "^---|^name:|^description:"
```

## Process Debugging

### Test Hook Scripts

```bash
# Test with sample input
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | ./hook.sh

# Check exit code
echo $?

# View stderr output
echo '{"tool_name":"Bash"}' | ./hook.sh 2>&1
```

### Test MCP Servers

```bash
# Run server directly
npx @modelcontextprotocol/server-filesystem

# Check if package exists
npm view @modelcontextprotocol/server-github

# Verify env vars
printenv | grep -i token
```

## Log Analysis

### Hook Audit Logs

```bash
# View recent hook activity
tail -50 .claude/audit.log

# Search for errors
grep -i error .claude/audit.log

# Count by tool
awk -F'|' '{print $2}' .claude/audit.log | sort | uniq -c | sort -rn
```

### Session Logs

```bash
# Find session files
ls -la ~/.claude/sessions/

# View recent session
cat ~/.claude/sessions/$(ls -t ~/.claude/sessions/ | head -1)
```

## Environment Verification

```bash
# Claude Code version
claude --version

# Check API key is set
echo ${ANTHROPIC_API_KEY:0:10}...

# Project directory
echo $CLAUDE_PROJECT_DIR

# Current working directory
pwd
```

## Validation Commands

```bash
# Run full validation suite (claude-mods)
just test

# YAML validation only
just validate-yaml

# Name matching validation
just validate-names

# Windows validation
just test-win
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `claude --debug` | Enable debug output |
| `/hooks` | List registered hooks |
| `/agents` | Manage subagents |
| `/memory` | View/edit memory files |
| `/config` | View configuration |
| `/plugin` | Manage plugins |
| `just test` | Run validations |
