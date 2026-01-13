# Hook Maintenance Guide

Quick reference for maintaining Claude Code hooks with security focus.

## Critical Security Principles

### 1. Never Trust Input
All hook parameters are potentially malicious:
```bash
# BAD - Command injection vulnerability
bash -c "echo $1"

# GOOD - Validate input first
if [[ "$1" =~ ^[a-zA-Z0-9_/-]+$ ]]; then
    echo "$1"
else
    echo '{"decision": "block", "reason": "Invalid input"}' >&2
    exit 2
fi
```

### 2. Use Safe Defaults
```bash
# Always use strict mode
set -euo pipefail

# Fail on undefined variables
set -u

# Fail on pipe errors
set -o pipefail
```

### 3. Validate Everything
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{
      "type": "command",
      "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/validate-bash.sh"
    }]
  }]
}
```

## Maintenance Tools Overview

### update-hook.py
**Purpose**: Interactive hook configuration updates
**Use When**: Changing event types, matchers, commands, or prompts
**Security**: Validates for dangerous patterns before saving

```bash
python3 update-hook.py hooks.json
```

### enhance-hook.py
**Purpose**: 7-category quality and security analysis
**Use When**: Security audits, quality gates, learning
**Exit Code**: 1 if critical security issues found

```bash
python3 enhance-hook.py hooks.json
```

**Categories Analyzed:**
1. Schema Compliance
2. **Security** ⚠️ CRITICAL
3. Matcher Validity
4. Script Existence
5. Hook Types
6. Documentation
7. Maintainability

### migrate-hook.py
**Purpose**: Automated schema migrations
**Use When**: Upgrading Claude Code, fixing validation errors
**Safety**: Creates backup, supports dry-run

```bash
# Preview changes
python3 migrate-hook.py hooks.json --dry-run

# Apply migrations
python3 migrate-hook.py hooks.json
```

**Migrations:**
- Remove invalid events
- Clean empty matchers from lifecycle events
- Add missing matchers to tool events
- Validate and fix hook types
- Recommend path normalization

### audit-hooks.py
**Purpose**: Bulk security audit of all hooks.json files
**Use When**: Repository-wide audits, CI/CD, pre-commit
**Output**: Summary with critical/warning counts

```bash
# Audit current directory
python3 audit-hooks.py .

# Verbose output
python3 audit-hooks.py . --verbose
```

### compare-hooks.py
**Purpose**: Side-by-side comparison of hooks files
**Use When**: Version comparison, migration validation, PR review
**Output**: Structural differences and similarity score

```bash
python3 compare-hooks.py hooks1.json hooks2.json

# Detailed diff
python3 compare-hooks.py hooks1.json hooks2.json --verbose
```

## Common Maintenance Scenarios

### Scenario 1: Adding Security Validation

**Goal**: Add validation to existing Bash hook

**Steps:**
1. Analyze current security:
   ```bash
   python3 enhance-hook.py hooks.json
   ```

2. Update hook to add validation:
   ```bash
   python3 update-hook.py hooks.json
   # Select the Bash hook
   # Update command to include validation script
   ```

3. Verify improvement:
   ```bash
   python3 enhance-hook.py hooks.json
   # Security score should increase
   ```

### Scenario 2: Migrating to New Event Type

**Goal**: Move hook from PostToolUse to PreToolUse

**Steps:**
1. Compare before:
   ```bash
   cp hooks.json hooks.json.before
   ```

2. Update event type:
   ```bash
   python3 update-hook.py hooks.json
   # Select hook
   # Change event to PreToolUse
   # Update matcher if needed
   ```

3. Validate migration:
   ```bash
   python3 compare-hooks.py hooks.json.before hooks.json
   python3 enhance-hook.py hooks.json
   ```

### Scenario 3: Repository-Wide Security Audit

**Goal**: Find all security issues across plugins

**Steps:**
1. Audit all hooks:
   ```bash
   python3 audit-hooks.py . --verbose > audit-report.txt
   ```

2. For each file with errors:
   ```bash
   python3 enhance-hook.py plugin/hooks/hooks.json
   ```

3. Fix critical issues:
   ```bash
   python3 update-hook.py plugin/hooks/hooks.json
   # Address each critical finding
   ```

4. Apply automated migrations:
   ```bash
   python3 migrate-hook.py plugin/hooks/hooks.json
   ```

5. Re-audit:
   ```bash
   python3 audit-hooks.py .
   ```

### Scenario 4: Preparing Hooks for Production

**Goal**: Ensure production-ready quality

**Steps:**
1. Run enhance to get baseline:
   ```bash
   python3 enhance-hook.py hooks.json
   # Target: Grade A (80%+)
   ```

2. Apply migrations:
   ```bash
   python3 migrate-hook.py hooks.json
   ```

3. Fix remaining issues:
   ```bash
   python3 update-hook.py hooks.json
   # Address each warning/error
   ```

4. Final validation:
   ```bash
   python3 enhance-hook.py hooks.json
   python3 validate-hooks.py hooks.json
   ```

5. Test by triggering events

## Security Checklist

Before committing hooks changes:

- [ ] Run `enhance-hook.py` - no critical errors
- [ ] Security score ≥ 8/10
- [ ] All scripts exist and are executable
- [ ] Input validation present for parameter usage
- [ ] No dangerous command patterns (eval, rm -rf, etc.)
- [ ] Matchers are valid regex
- [ ] Event types are correct
- [ ] Using `${CLAUDE_PLUGIN_ROOT}` for script paths
- [ ] Bash scripts use `set -euo pipefail`
- [ ] JSON structure validates
- [ ] Tested by triggering events

## Dangerous Patterns to Avoid

### Command Injection
```bash
# NEVER
eval "$1"
bash -c "$COMMAND"
sh -c "$INPUT"

# ALWAYS validate first
if [[ "$1" =~ ^[a-zA-Z0-9_/-]+$ ]]; then
    # Safe to use
fi
```

### Destructive Commands
```bash
# Block these patterns
rm -rf /
dd if=/dev/zero of=/dev/sda
mkfs.*
chmod 777
wget .* | bash
curl .* | bash
```

### Parameter Substitution Without Validation
```bash
# BAD
FILE_PATH="$1"
cat "$FILE_PATH"  # No validation!

# GOOD
FILE_PATH="$1"
if [[ ! "$FILE_PATH" =~ \.\. ]] && [[ -f "$FILE_PATH" ]]; then
    cat "$FILE_PATH"
else
    echo '{"decision": "block"}' >&2
    exit 2
fi
```

## Hook.json Structure Reminder

### Tool Events (PreToolUse, PostToolUse)
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit",  // REQUIRED
      "hooks": [{
        "type": "command",
        "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/validate.sh"
      }]
    }]
  }
}
```

### Lifecycle Events (UserPromptSubmit, Stop, SessionStart, etc.)
```json
{
  "hooks": {
    "UserPromptSubmit": [{
      // NO matcher field
      "hooks": [{
        "type": "command",
        "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/log-prompt.sh"
      }]
    }]
  }
}
```

## Quick Reference: Hook Types

| Type | Field | Use Case | Example |
|------|-------|----------|---------|
| `command` | `command` | Execute bash script | Validation, formatting, logging |
| `prompt` | `prompt` | LLM evaluation | Complex policy, context-aware decisions |

## Quick Reference: Events

| Event | Matcher? | When Triggered | Common Use |
|-------|----------|----------------|------------|
| PreToolUse | ✅ | Before tool executes | Validation, security checks |
| PostToolUse | ✅ | After tool completes | Formatting, logging |
| UserPromptSubmit | ❌ | User submits prompt | Logging, context tracking |
| Stop | ❌ | Conversation ends | Cleanup, summaries |
| SessionStart | ❌ | Session begins | Initialization, setup |
| Notification | ❌ | Alert sent | Logging |
| SubagentStop | ❌ | Subagent completes | Cleanup |
| PreCompact | ❌ | Before compaction | State preservation |

## Exit Codes in Hook Scripts

| Code | Meaning | Effect |
|------|---------|--------|
| 0 | Success/Approve | Tool proceeds, stdout shown |
| 2 | Block | Tool blocked, stderr to Claude |
| Other | Warning | Tool proceeds, warning logged |

## Best Practices

1. **Always backup** before bulk operations
2. **Test locally** before committing
3. **Use dry-run** for migrations first
4. **Validate** after every change
5. **Review diffs** carefully
6. **Document** complex hooks
7. **Audit regularly** for security
8. **Version control** hooks.json
9. **Test by triggering** events
10. **Security first** - when in doubt, block

## Integration with Git

### Pre-Commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

if git diff --cached --name-only | grep -q 'hooks.json'; then
    echo "Validating hooks.json changes..."

    for file in $(git diff --cached --name-only | grep 'hooks.json'); do
        python3 agent-builder/skills/building-hooks/scripts/enhance-hook.py "$file"

        if [ $? -ne 0 ]; then
            echo "❌ Hook validation failed for $file"
            exit 1
        fi
    done
fi
```

### GitHub Actions
```yaml
name: Validate Hooks
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Audit Hooks
        run: |
          python3 agent-builder/skills/building-hooks/scripts/audit-hooks.py .
```

## Troubleshooting

### "Invalid JSON" Error
```bash
# Validate JSON syntax
python3 -m json.tool hooks.json

# Or use jq
jq . hooks.json
```

### "Script not found" Warning
```bash
# Check script path
ls -la path/to/script.sh

# Ensure using correct variable
# Use: ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/script.sh
```

### "Matcher regex invalid" Error
```bash
# Test regex in Python
python3 -c "import re; re.compile('your|pattern')"

# Common mistake: Don't escape | in JSON
# WRONG: "Write\\|Edit"
# RIGHT: "Write|Edit"
```

### Security Score Too Low
1. Run `enhance-hook.py` to see specific issues
2. Address critical errors first
3. Add input validation
4. Use `set -euo pipefail` in scripts
5. Fix dangerous command patterns
6. Re-run enhance to verify improvement

## Getting Help

- **Validation errors**: Check error message, run `validate-hooks.py`
- **Security issues**: Run `enhance-hook.py` for detailed findings
- **Schema questions**: See building-hooks/SKILL.md
- **Examples**: Check self-improvement/hooks/hooks.json, github-workflows/hooks/hooks.json

## Summary

**Core Workflow:**
1. `enhance-hook.py` → Identify issues
2. `update-hook.py` → Fix issues interactively
3. `migrate-hook.py` → Apply automated fixes
4. `validate-hooks.py` → Verify correctness
5. Test by triggering events
6. Commit

**Security Priority Order:**
1. Fix critical security vulnerabilities
2. Add input validation
3. Fix schema compliance errors
4. Address warnings
5. Improve documentation

**Remember**: Hooks execute with privileges - security is paramount!
