# Common Issues Reference

Issue → Cause → Solution lookup for Claude Code debugging.

## Skills

### Skill Never Activates

| Cause | Solution |
|-------|----------|
| Description too vague | Add specific trigger keywords: "Triggers on: keyword1, keyword2" |
| YAML syntax error | Check frontmatter opens/closes with `---` |
| Wrong location | Must be `.claude/skills/name/SKILL.md` or `~/.claude/skills/name/SKILL.md` |
| Name mismatch | Directory name must match `name:` field |
| Missing SKILL.md | File must be named exactly `SKILL.md` (uppercase) |

**Diagnosis:**
```bash
# Check structure
ls -la .claude/skills/my-skill/

# Verify frontmatter
head -5 .claude/skills/my-skill/SKILL.md

# Check name matches
dirname=$(basename "$(pwd)")
grep "^name: $dirname" SKILL.md
```

### Skill Loads But Doesn't Help

| Cause | Solution |
|-------|----------|
| Content too generic | Add specific commands, examples, patterns |
| Missing tool examples | Include `bash` blocks with real commands |
| No "When to Use" | Add scenarios for activation |

## Hooks

### Hook Doesn't Execute

| Cause | Solution |
|-------|----------|
| Not executable | `chmod +x hook-script.sh` |
| Invalid JSON in settings | Validate with `jq '.' settings.json` |
| Wrong matcher | Matchers are case-sensitive: `"Bash"` not `"bash"` |
| Relative path fails | Use `$CLAUDE_PROJECT_DIR/path/to/script.sh` |
| Script not found | Check path exists, use absolute paths |

**Diagnosis:**
```bash
# Check executable
ls -la .claude/hooks/

# Test script manually
echo '{"tool_name":"Test"}' | ./hook.sh
echo "Exit code: $?"

# Verify JSON
jq '.' ~/.claude/settings.json

# List registered hooks
/hooks
```

### Hook Runs But Doesn't Block

| Cause | Solution |
|-------|----------|
| Exit code not 2 | Use `exit 2` to block (not 1) |
| Error on stdout | Put error messages on stderr: `echo "error" >&2` |
| Blocking for wrong tool | Check matcher pattern matches tool name |

### Hook Blocks Everything

| Cause | Solution |
|-------|----------|
| Matcher too broad | Use specific matcher instead of `"*"` |
| Logic error | Add debugging: `echo "DEBUG: $TOOL" >&2` |
| Always exits 2 | Check conditional logic in script |

## Agents

### Custom Agent Not Used

| Cause | Solution |
|-------|----------|
| Description doesn't match | Include "Use for: scenario1, scenario2" |
| Wrong location | Must be `.claude/agents/name.md` or `~/.claude/agents/name.md` |
| YAML invalid | Check frontmatter has `name:` and `description:` |
| Name conflicts | Check for duplicate agent names |

**Diagnosis:**
```bash
# List available agents
/agents

# Check file location
ls ~/.claude/agents/
ls .claude/agents/

# Verify frontmatter
head -10 .claude/agents/my-agent.md

# Force usage
# "Use the my-agent agent to help with this"
```

### Agent Doesn't Have Expected Tools

| Cause | Solution |
|-------|----------|
| `tools` field restricts | Remove `tools` field to inherit all tools |
| Permission denied | Check settings.json allow rules |
| Tool not installed | Verify tool exists (e.g., `which jq`) |

## MCP

### MCP Server Won't Connect

| Cause | Solution |
|-------|----------|
| Package not installed | `npm install -g @modelcontextprotocol/server-X` |
| Missing env vars | Check `.mcp.json` for `${VAR}` references |
| Server crashes | Test manually: `npx @modelcontextprotocol/server-X` |
| Wrong transport | HTTP servers need `--transport http` |

**Diagnosis:**
```bash
# Test server manually
npx @modelcontextprotocol/server-filesystem

# Check .mcp.json
cat .mcp.json | jq '.'

# Verify env vars exist
echo $GITHUB_TOKEN
```

### MCP Tools Not Available

| Cause | Solution |
|-------|----------|
| Server not in config | Add to `.mcp.json` or use `claude mcp add` |
| Permission denied | Add `mcp__server__*` to allow rules |
| Token limit | Reduce output size, check MAX_MCP_OUTPUT_TOKENS |

## Memory & Rules

### CLAUDE.md Not Loading

| Cause | Solution |
|-------|----------|
| Wrong location | Must be `./CLAUDE.md` or `./.claude/CLAUDE.md` |
| Import cycle | Max 5 hops for `@path` imports |
| Syntax error | Check markdown syntax, especially code blocks |

**Diagnosis:**
```bash
# Check what's loaded
/memory

# Verify file exists
ls -la CLAUDE.md .claude/CLAUDE.md 2>/dev/null

# Check imports
grep "^@" CLAUDE.md
```

### Rules Not Applying

| Cause | Solution |
|-------|----------|
| Wrong glob pattern | Test pattern: `ls .claude/rules/**/*.md` |
| Path not matching | Check `paths:` field matches current file |
| Lower priority | User rules load before project rules |

## Permissions

### Tool Blocked Unexpectedly

| Cause | Solution |
|-------|----------|
| Not in allow list | Add to `permissions.allow` in settings.json |
| In deny list | Remove from `permissions.deny` |
| Hook blocking | Check PreToolUse hooks |

**Diagnosis:**
```bash
# Check settings
cat ~/.claude/settings.json | jq '.permissions'

# Check project settings
cat .claude/settings.local.json | jq '.permissions' 2>/dev/null

# Debug mode shows permission decisions
claude --debug
```

## General Debugging Steps

1. **Enable debug mode**: `claude --debug`
2. **Check file locations**: `ls -la .claude/` and `ls -la ~/.claude/`
3. **Validate JSON**: `jq '.' settings.json`
4. **Verify YAML**: Check frontmatter opens/closes with `---`
5. **Test manually**: Run scripts directly, test MCP servers
6. **Check permissions**: Review allow/deny rules
7. **Use inspection commands**: `/hooks`, `/agents`, `/memory`, `/config`
