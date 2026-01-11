# Hook Quality & Security Checklist

Quick checklist for reviewing and validating Claude Code hooks before commit/deploy.

## Pre-Commit Checklist

Run before committing hooks.json changes:

### Automated Validation
```bash
# 1. Run security analysis
python3 enhance-hook.py hooks.json
# Target: Grade A (≥80%), Security ≥8/10

# 2. Run schema validation
python3 validate-hooks.py hooks.json
# Must pass with 0 critical errors

# 3. Check for migrations needed
python3 migrate-hook.py hooks.json --dry-run
# Review any recommended changes
```

### Manual Review

#### Schema & Structure
- [ ] Valid JSON syntax (no parse errors)
- [ ] Top-level `hooks` object exists
- [ ] All event names are valid
- [ ] Tool events (PreToolUse, PostToolUse) have matchers
- [ ] Lifecycle events (UserPromptSubmit, Stop, etc.) have NO matchers
- [ ] All hooks have valid `type` field ('command' or 'prompt')
- [ ] Command hooks have `command` field
- [ ] Prompt hooks have `prompt` field

#### Security - CRITICAL
- [ ] NO `eval` commands
- [ ] NO `rm -rf /` or similar destructive commands
- [ ] NO command substitution without validation (`$(...)`, `` `...` ``)
- [ ] NO piping wget/curl to bash
- [ ] NO chmod 777 or overly permissive permissions
- [ ] NO dd, mkfs, or data destruction commands
- [ ] Input parameters ($1, $2, etc.) are validated before use
- [ ] Scripts use `set -euo pipefail` for error handling
- [ ] Scripts exist at specified paths
- [ ] Scripts are executable (chmod +x)
- [ ] Using absolute paths or `${CLAUDE_PLUGIN_ROOT}`

#### Matcher Patterns
- [ ] Valid regex patterns (test with `python3 -c "import re; re.compile('pattern')"`)
- [ ] Using `|` for OR (not `\\|`)
- [ ] Appropriate specificity (avoid overly broad `*` unless intended)
- [ ] No empty matchers on tool events
- [ ] Matchers match intended tools

#### Hook Logic
- [ ] Clear purpose for each hook
- [ ] Appropriate event type for use case
- [ ] Return proper JSON format:
  ```json
  {"decision": "approve|block|warn", "reason": "..."}
  ```
- [ ] Correct exit codes:
  - `0` for success/approve
  - `2` for block
  - Other for warnings
- [ ] No infinite loops or circular dependencies

#### Testing
- [ ] Tested by triggering the event manually
- [ ] Verified hook executes correctly
- [ ] Checked stdout/stderr output
- [ ] Confirmed blocking works (if PreToolUse)
- [ ] Verified logging (if applicable)

## Pull Request Checklist

For reviewing hooks in PRs:

### Reviewer Checks
- [ ] Run `audit-hooks.py` on repository
- [ ] Run `enhance-hook.py` on changed hooks.json files
- [ ] Compare with previous version:
  ```bash
  git show main:path/to/hooks.json > hooks-main.json
  python3 compare-hooks.py hooks-main.json path/to/hooks.json
  ```
- [ ] Review security score - must be ≥7/10
- [ ] No new critical security issues introduced
- [ ] All scripts referenced exist in the PR
- [ ] Scripts have proper shebang and error handling

### Security-Specific PR Review
- [ ] New hooks don't introduce privilege escalation
- [ ] Input validation is present and thorough
- [ ] No secrets or credentials in hooks
- [ ] Logging doesn't expose sensitive data
- [ ] Error messages don't leak system information

## Production Deployment Checklist

Before deploying hooks to production:

### Quality Gates
- [ ] `enhance-hook.py` score ≥80% (Grade A)
- [ ] Security category score ≥8/10
- [ ] Zero critical errors from `audit-hooks.py`
- [ ] All migrations applied (`migrate-hook.py`)
- [ ] Validated with `validate-hooks.py`

### Security Hardening
- [ ] All bash scripts use strict mode (`set -euo pipefail`)
- [ ] Input validation on all parameters
- [ ] Whitelist approach for file paths
- [ ] No dynamic command construction
- [ ] Logging configured appropriately
- [ ] Error handling covers edge cases

### Testing
- [ ] Unit tested individual hook scripts
- [ ] Integration tested with Claude Code
- [ ] Verified in staging environment
- [ ] Load tested (if high-frequency hooks)
- [ ] Rollback plan documented

### Documentation
- [ ] Purpose of each hook documented
- [ ] Security considerations noted
- [ ] Maintenance procedures documented
- [ ] Known limitations listed
- [ ] Update CHANGELOG if applicable

## Quick Security Scan

Run this one-liner before commit:

```bash
python3 enhance-hook.py hooks.json && \
python3 validate-hooks.py hooks.json && \
echo "✅ Hooks validation passed"
```

Or add to git pre-commit hook:

```bash
#!/bin/bash
# .git/hooks/pre-commit

for file in $(git diff --cached --name-only | grep 'hooks.json'); do
  echo "Validating $file..."

  python3 agent-builder/skills/building-hooks/scripts/enhance-hook.py "$file"

  if [ $? -ne 0 ]; then
    echo "❌ Critical security issues found in $file"
    echo "   Fix issues before committing"
    exit 1
  fi

  security_score=$(python3 agent-builder/skills/building-hooks/scripts/enhance-hook.py "$file" 2>&1 | grep "Security:" | awk '{print $2}' | cut -d'/' -f1)

  if [ "$security_score" -lt 8 ]; then
    echo "❌ Security score too low: $security_score/10 (minimum: 8/10)"
    exit 1
  fi
done

echo "✅ All hooks validated successfully"
```

## Common Issues Checklist

### Issue: Hooks Not Triggering
- [ ] Event name spelled correctly
- [ ] Matcher pattern matches the tool
- [ ] Hook enabled in settings
- [ ] Script path is correct
- [ ] Script is executable

### Issue: Hook Blocking Unexpectedly
- [ ] Check exit code (should be 2 for block)
- [ ] Review stderr output
- [ ] Verify validation logic
- [ ] Check for unintended matches in matcher

### Issue: Security Warnings
- [ ] Review `enhance-hook.py` output
- [ ] Fix critical issues first
- [ ] Add input validation
- [ ] Update script error handling
- [ ] Re-validate after fixes

### Issue: JSON Parse Errors
- [ ] Validate JSON syntax: `python3 -m json.tool hooks.json`
- [ ] Check for trailing commas
- [ ] Verify quote escaping
- [ ] Ensure proper array/object structure

## Scoring Thresholds

### Enhance Hook Scores

| Category | Minimum | Target | Notes |
|----------|---------|--------|-------|
| Schema Compliance | 8/10 | 10/10 | Fix all schema errors |
| Security | 8/10 | 10/10 | **CRITICAL - No exceptions** |
| Matcher Validity | 7/10 | 10/10 | Fix invalid regex |
| Script Existence | 7/10 | 10/10 | Ensure scripts exist |
| Hook Types | 9/10 | 10/10 | Must have valid types |
| Documentation | 5/10 | 8/10 | Recommended |
| Maintainability | 6/10 | 8/10 | Recommended |
| **Overall** | **70%** | **85%+** | **Production ready** |

### Grade Scale
- **A (80%+)**: Production ready
- **B (60-79%)**: Acceptable with review
- **C (<60%)**: Requires work before merge

## Emergency Rollback Checklist

If hooks cause issues in production:

1. [ ] Disable hooks in settings immediately
2. [ ] Identify problematic hook (`audit-hooks.py --verbose`)
3. [ ] Rollback to previous version: `git revert <commit>`
4. [ ] Test rollback in staging
5. [ ] Deploy rollback to production
6. [ ] Post-mortem: analyze what went wrong
7. [ ] Fix issues in new PR with thorough testing
8. [ ] Document incident and prevention measures

## Regular Maintenance Schedule

### Weekly
- [ ] Run `audit-hooks.py` on all repositories
- [ ] Review any new warnings

### Monthly
- [ ] Security audit with `enhance-hook.py` on all hooks
- [ ] Update scripts to latest best practices
- [ ] Review and update documentation

### Quarterly
- [ ] Comprehensive security review
- [ ] Test all hooks end-to-end
- [ ] Update to latest Claude Code features
- [ ] Review and optimize performance

## Resources

- **Validation Script**: `agent-builder/skills/building-hooks/scripts/validate-hooks.py`
- **Enhancement Analyzer**: `agent-builder/skills/building-hooks/scripts/enhance-hook.py`
- **Migration Tool**: `agent-builder/skills/building-hooks/scripts/migrate-hook.py`
- **Audit Tool**: `agent-builder/skills/building-hooks/scripts/audit-hooks.py`
- **Comparison Tool**: `agent-builder/skills/building-hooks/scripts/compare-hooks.py`
- **Documentation**: `agent-builder/skills/building-hooks/SKILL.md`
- **Examples**: `self-improvement/hooks/hooks.json`, `github-workflows/hooks/hooks.json`

## Summary

**Minimum Requirements for Commit:**
1. ✅ `enhance-hook.py` passes (no critical errors)
2. ✅ Security score ≥8/10
3. ✅ `validate-hooks.py` passes
4. ✅ Manual testing completed

**Red Flags (Never Commit):**
- ❌ Critical security issues
- ❌ Invalid JSON
- ❌ Missing scripts
- ❌ eval, rm -rf, or similar dangerous commands
- ❌ Command injection vulnerabilities

**When in Doubt:**
1. Run `enhance-hook.py` for detailed analysis
2. Ask for security review
3. Test extensively in safe environment
4. Document assumptions and edge cases

**Remember**: Hooks execute with privileges. Security first, always.
