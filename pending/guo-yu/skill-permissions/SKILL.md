---
name: skill-permissions
description: Skill permission analysis, one-time authorization, analyze skill permissions, batch authorization
---

# Skill Permissions

Automatically analyze permissions required by all skills in Claude Code and generate one-time authorization commands.

## Dangerous Operations Warning

**This skill can modify other skill files.** The following commands may cause widespread file changes:

| Command | Risk Level | Description |
|---------|------------|-------------|
| `/skill-permissions inject` | High | Batch modify all skill SKILL.md files |
| `/skill-permissions allow-all` | Medium | Batch modify settings.json |
| `/skill-permissions allow <name>` | Low | Only modify settings.json |
| `/skill-permissions <name>` | Safe | Read-only analysis, no file modifications |

**Recommendations:**
- Prefer **explicit commands** (e.g., `/skill-permissions allow port-allocator`)
- Avoid `inject` or `allow-all` unless you understand the impact
- Run `/skill-permissions` first to see analysis results before batch operations

## Usage

| Command | Description |
|---------|-------------|
| `/skill-permissions` | Analyze all skills and show permission summary |
| `/skill-permissions <skill-name>` | Analyze specific skill's permission requirements |
| `/skill-permissions allow <skill-name>` | Execute one-time authorization for specific skill |
| `/skill-permissions allow-all` | Execute one-time authorization for all skills |
| `/skill-permissions inject` | Inject allow command into all skills |
| `/skill-permissions allow` | Execute one-time authorization for this skill |

## How It Works

### 1. Permission Analysis

Scan skill's SKILL.md file, identifying patterns like:

**Bash Command Patterns:**
```
find * → Bash(find *)
ls * → Bash(ls *)
cat ~/.claude/* → Bash(cat ~/.claude/*)
lsof -i:3* → Bash(lsof -i:3*)
git * → Bash(git *)
npm * → Bash(npm *)
```

**Recognition Rules:**
- Bash commands in code blocks (```bash ... ```)
- Inline commands (`command`)
- Explicitly mentioned system commands

### 2. Permission Rule Generation

Convert identified commands to `permissions.allow` rules:

```json
{
  "permissions": {
    "allow": [
      "Bash(find * -name package.json *)",
      "Bash(ls -d *)",
      "Bash(cat ~/.claude/*)",
      "Bash(lsof -i:3*)"
    ]
  }
}
```

## Execution Steps

### Command: `/skill-permissions`

Analyze all skills and show permission summary:

1. **Scan all skills**
   ```bash
   find ~/.claude/skills -name "SKILL.md" -type f 2>/dev/null
   ```

2. **Analyze permissions for each skill**
   - Read SKILL.md content
   - Extract bash code blocks
   - Identify command patterns
   - Generate permission rules

3. **Output analysis results**

### Command: `/skill-permissions <skill-name>`

Analyze specific skill's permission requirements:

1. **Locate skill**
   ```bash
   SKILL_PATH=$(find ~/.claude/skills -type d -name "<skill-name>" 2>/dev/null | head -1)
   ```

2. **Read and analyze SKILL.md**

3. **Output detailed permission list**

### Command: `/skill-permissions allow <skill-name>`

Execute one-time authorization for specific skill:

1. **Analyze skill permission requirements**
2. **Read existing config**
3. **Merge permission rules** (deduplicate, preserve existing rules)
4. **Write config file**
5. **Output authorization result**

## Blocked Commands

The following command patterns are **automatically blocked** and won't be added to the allowlist:

### Dangerous File Operations
| Command | Reason |
|---------|--------|
| `rm *` | File deletion, may cause data loss |
| `rm -rf *` | Recursive force delete, extremely dangerous |
| `sudo *` | Super user privileges |
| `chmod 777 *` | Opens all permissions |

### Dangerous Process Operations
| Command | Reason |
|---------|--------|
| `kill -9 *` | Force kill process |
| `pkill *` | Kill processes by name |
| `curl * \| bash` | Remote code execution |
| `eval *` | Dynamic code execution |

### Dangerous Git Operations
| Command | Reason |
|---------|--------|
| `git push --force *` | Force push, may overwrite remote |
| `git reset --hard *` | Hard reset, loses uncommitted changes |

## Output Format

### Analysis Result (Single Skill)
```
Skill: port-allocator
Location: ~/.claude/skills/port-allocator

Detected commands:
  - find ~/Codes -maxdepth 3 -name "package.json"
  - ls -d */
  - cat ~/.claude/port-registry.json
  - lsof -i:3000

Generated permission rules:
  - Bash(find * -maxdepth * -name package.json *)
  - Bash(ls -d *)
  - Bash(cat ~/.claude/*)
  - Bash(lsof -i:3*)

Run `/skill-permissions allow port-allocator` to authorize
```

### Authorization Success
```
Permission authorization successful

Skill: port-allocator

Added permission rules:
  - Bash(find * -maxdepth * -name package.json *)
  - Bash(ls -d *)
  - Bash(cat ~/.claude/*)
  - Bash(lsof -i:3*)

Config file: ~/.claude/settings.json

New permissions take effect in next session, or run /clear to apply immediately
```

## Configuration Files

- **Permission config**: `~/.claude/settings.json`
- **Skill directory**: `~/.claude/skills/`

## First Use

If you encounter permission prompts, first run:
```
/skill-permissions allow
```

### Command: `/skill-permissions allow`

Execute one-time authorization for this skill:

1. Read `~/.claude/settings.json`
2. Merge the following permissions to `permissions.allow`:

```json
{
  "permissions": {
    "allow": [
      "Bash(find ~/.claude/skills *)",
      "Bash(cat ~/.claude/*)"
    ]
  }
}
```

3. Write config file (preserve existing permissions)
4. Output authorization result

## Notes

1. **Conservative analysis** - Only identify explicitly appearing commands, avoid over-authorization
2. **Deduplicated merge** - New permissions merge with existing, no duplicates
3. **No deletion** - Only adds permissions, won't delete user's existing permission config
4. **Wildcards** - Use `*` to match varying parameter parts
5. **Session effect** - Permission updates require new session or /clear to take effect
6. **Explicit preferred** - Recommend explicit commands over batch operations to reduce risks
