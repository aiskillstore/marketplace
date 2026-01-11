# Skill Developer Quick Reference

One-page cheat sheet for common commands, patterns, and configuration.

---

## Commands

### Test Skill Triggers

```bash
# Test UserPromptSubmit hook
echo '{"prompt":"create backend route"}' | npx tsx .claude/hooks/skill-activation-prompt.ts

# Test with specific file context
echo '{"prompt":"fix this","files":[{"path":"src/api/user.ts"}]}' | \
  npx tsx .claude/hooks/skill-activation-prompt.ts
```

### Validate Configuration

```bash
# Validate skill-rules.json syntax
cat .claude/skills/skill-rules.json | jq .

# Pretty-print with colors
cat .claude/skills/skill-rules.json | jq . -C | less -R

# Check specific skill config
cat .claude/skills/skill-rules.json | jq '.skills["my-skill"]'
```

### Test Hook Execution

```bash
# Make hooks executable
chmod +x .claude/hooks/*.sh

# Test a hook directly
./.claude/hooks/skill-activation-prompt.sh

# Check exit code
echo $?  # Should be 0 for success
```

---

## File Structure

```
.claude/
├── settings.json                     # Hook registration & config
├── skills/
│   ├── skill-rules.json             # Master trigger configuration
│   └── {skill-name}/
│       ├── SKILL.md                 # Main content (< 500 lines)
│       └── resources/               # Optional detailed references
│           ├── {TOPIC}.md           # Topic-specific deep dives
│           └── ...
├── hooks/
│   ├── *.sh                         # Bash wrappers (executable)
│   ├── *.ts                         # TypeScript logic
│   └── package.json                 # Node dependencies
├── commands/
│   └── {command-name}.md           # Slash commands
└── agents/
    └── {agent-name}.md             # Specialized agents
```

---

## Trigger Pattern Syntax

### Keywords (Case-Insensitive)

```json
"keywords": ["layout", "grid", "component"]
```

- Substring match: `"layout"` matches `"grid layout system"`
- Space-separated: Matches any word
- No regex: Literal text only

### Intent Patterns (Regex)

```json
"intentPatterns": [
  "(create|add|implement).*?(feature|endpoint|component)",
  "(how|what|why).*?(work|pattern|best practice)"
]
```

- Use `.*?` for non-greedy matching
- Capture user intent, not exact words
- Case-insensitive by default

### File Path Patterns (Glob)

```json
"pathPatterns": [
  "**/*.tsx",                    // All .tsx files
  "src/**/*.ts",                 // All .ts in src/
  "backend/api/**/*.{ts,js}",    // Multiple extensions
  "!**/*.test.ts"                // Exclusion (requires pathExclusions)
]
```

- `**` = any directory depth
- `*` = any characters in filename
- `{a,b}` = match a OR b
- Use `pathExclusions` for negation

### Content Patterns (Regex)

```json
"contentPatterns": [
  "import.*Prisma",              // Import statements
  "router\\.get\\(",             // Escape special chars
  "@Controller\\('",             // Decorators
  "interface\\s+\\w+\\s*\\{"     // Interface definitions
]
```

- Escape special regex characters: `\\.` `\\(` `\\{`
- Use `\\s` for whitespace, `\\w` for word characters
- Remember: JSON strings need double backslash

---

## Exit Codes

| Code | Effect | Claude Sees | Use Case |
|------|--------|-------------|----------|
| **0** (UserPromptSubmit) | Allow | stdout content | Skill suggestions |
| **0** (PreToolUse) | Allow | Nothing | Normal operation |
| **2** (PreToolUse) | **BLOCK** | **stderr content** | **Enforce guardrails** |
| 1 or Other | Block silently | Nothing | Errors |

### Why Exit Code 2 is Critical

```bash
# In PreToolUse hook
if (violatesGuardrail) {
  console.error("⚠️ GUARDRAIL: Table 'xyz' not in schema");
  process.exit(2);  # ← THE MAGIC NUMBER
}
```

Exit code 2 is the **ONLY** way to:
- Block tool execution
- Send message to Claude (via stderr)
- Enforce guardrails

---

## Enforcement Levels

```json
{
  "enforcement": "suggest" | "block" | "warn"
}
```

| Level | Effect | Use Case | Frequency |
|-------|--------|----------|-----------|
| `suggest` | Advisory, non-blocking | Most skills | 90% |
| `block` | Can prevent execution | Critical guardrails | 5% |
| `warn` | Low-priority hint | Rarely used | 5% |

**Rule of Thumb**: Use `suggest` unless preventing catastrophic mistakes.

---

## Skill Types

```json
{
  "type": "domain" | "guardrail"
}
```

| Type | Purpose | Enforcement | Example |
|------|---------|-------------|---------|
| `domain` | Provide guidance & patterns | Usually `suggest` | backend-dev-guidelines |
| `guardrail` | Prevent mistakes | Usually `block` | database-verification |

---

## YAML Frontmatter Template

```yaml
---
name: my-skill-name
description: Brief description including all trigger keywords. Mention file types, frameworks, and use cases explicitly. Keywords: react, component, tsx, frontend, mui, typescript, hooks. Use when creating components, building UIs, or working with React patterns.
---
```

**Requirements**:
- `name`: lowercase-with-hyphens
- `description`: < 1024 chars, include ALL keywords
- Keywords improve relevance matching

---

## skill-rules.json Template

```json
{
  "version": "1.0",
  "description": "Skill activation rules",
  "skills": {
    "my-skill": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "One-line summary",
      "promptTriggers": {
        "keywords": ["keyword1", "keyword2"],
        "intentPatterns": [
          "(create|add).*?pattern"
        ]
      },
      "fileTriggers": {
        "pathPatterns": ["src/**/*.ts"],
        "pathExclusions": ["**/*.test.ts"],
        "contentPatterns": ["import.*MyLib"]
      },
      "skipConditions": {
        "sessionSkillUsed": true,
        "fileMarkers": ["@skip-my-skill"],
        "envOverride": "SKIP_MY_SKILL"
      }
    }
  }
}
```

---

## Priority Levels

```json
{
  "priority": "critical" | "high" | "medium" | "low"
}
```

Affects suggestion order when multiple skills match:
1. `critical` - Shown first
2. `high` - Important
3. `medium` - Default
4. `low` - Shown last

---

## Skip Conditions

```json
{
  "skipConditions": {
    "sessionSkillUsed": true,           // Only suggest once per session
    "fileMarkers": ["@skip-validation"], // Skip files with comment
    "envOverride": "SKIP_SKILL_NAME"    // Disable via env var
  }
}
```

### Usage Examples

**File Marker**:
```typescript
// @skip-validation
// This file is intentionally non-standard
export const legacyCode = { ... };
```

**Environment Variable**:
```bash
SKIP_DATABASE_VERIFICATION=1 claude-code
```

---

## Common Patterns

### Backend Framework Detection

```json
"contentPatterns": [
  "from express import|require.*express",     // Express
  "@Controller\\(|@nestjs/common",            // NestJS
  "fastify\\.register|@fastify/",             // Fastify
  "from django|from rest_framework"           // Django
]
```

### Frontend Framework Detection

```json
"contentPatterns": [
  "from react import|import.*React",          // React
  "from vue import|import.*Vue",              // Vue
  "@Component\\(|@angular/core",              // Angular
  "from svelte import|<script>"               // Svelte
]
```

### Database/ORM Detection

```json
"contentPatterns": [
  "@prisma/client|prisma\\.",                 // Prisma
  "from typeorm import|@Entity\\(",           // TypeORM
  "from sequelize import|Sequelize",          // Sequelize
  "from drizzle-orm|drizzle\\("               // Drizzle
]
```

---

## Testing Checklist

Before deploying a skill:

- [ ] YAML frontmatter is valid
- [ ] Description includes all trigger keywords
- [ ] skill-rules.json is valid JSON (`jq` test)
- [ ] Keywords trigger on expected prompts
- [ ] Intent patterns catch target use cases
- [ ] File patterns match project structure
- [ ] No false positives on unrelated files
- [ ] Enforcement level is appropriate
- [ ] Skip conditions work as expected
- [ ] Main SKILL.md is < 500 lines
- [ ] Resource files are < 400 lines (recommended)
- [ ] Cross-references are valid

---

## Troubleshooting Quick Fixes

### Skill Not Triggering

```bash
# 1. Check keyword match
echo '{"prompt":"your test prompt"}' | \
  npx tsx .claude/hooks/skill-activation-prompt.ts

# 2. Validate JSON syntax
jq . .claude/skills/skill-rules.json

# 3. Check hook is registered
grep "skill-activation-prompt" .claude/settings.json

# 4. Verify hook is executable
ls -la .claude/hooks/*.sh | grep rwx
```

### False Positives

- Add `pathExclusions` to skip test files
- Use more specific keywords (not generic terms)
- Add `sessionSkillUsed: true` to reduce nag fatigue

### Hook Not Executing

```bash
# Check exit code
./.claude/hooks/my-hook.sh
echo $?  # Should be 0

# Check for TypeScript errors
npx tsx .claude/hooks/my-hook.ts

# Check dependencies installed
ls .claude/hooks/node_modules/
```

---

## Performance Tips

**Hooks should complete in < 200ms**:

✅ **DO**:
- Early exit when no triggers match
- Cache file reads
- Use efficient regex patterns
- Minimize file I/O

❌ **DON'T**:
- Read all skills on every prompt
- Parse large files unnecessarily
- Make network requests
- Use expensive operations in hot path

---

## Memory Patterns Quick Reference

See [MEMORY_PATTERNS.md](MEMORY_PATTERNS.md) for full details.

```typescript
// Load memory
const memory = await loadMemory('skill-name');

// Check staleness
if (isStale(memory, '7 days')) {
  memory = await refresh();
}

// Apply learned preferences
if (memory.preferences.pattern) {
  applyPattern(memory.preferences.pattern);
}

// Track corrections
memory.corrections.push({...});

// Save memory
await saveMemory('skill-name', memory);
```

**Storage**: `.claude/memory/{skill-name}/`

---

## Resources

- **Full Documentation**: [SKILL.md](SKILL.md)
- **Trigger Types**: [TRIGGER_TYPES.md](TRIGGER_TYPES.md)
- **Hook Mechanisms**: [HOOK_MECHANISMS.md](HOOK_MECHANISMS.md)
- **Configuration**: [SKILL_RULES_REFERENCE.md](SKILL_RULES_REFERENCE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Memory Patterns**: [MEMORY_PATTERNS.md](MEMORY_PATTERNS.md)
- **Advanced Topics**: [ADVANCED.md](ADVANCED.md)

---

**🚀 Pro Tip**: Bookmark this file for quick lookups during skill development!
