# Debugging Assistant - Quick Start Guide

## What is This?

The Debugging Assistant is an intelligent, systematic approach to finding and fixing bugs in your code. It uses specialized AI agents to analyze symptoms, identify root causes, generate fixes, validate solutions, and prevent recurrence.

## When to Use

Use this skill whenever you encounter:
- Runtime errors or exceptions
- Unexpected behavior or wrong output
- Performance issues or memory leaks
- Intermittent failures or race conditions
- Test failures that need investigation

## Quick Start

### 1. Activate the Skill

**Via Slash Command:**
```bash
/debug-assist "[description of issue]"
```

**Via Direct Invocation:**
```bash
npx claude-flow@alpha sparc run debugging-assistant "NullPointerException in user processing"
```

**Via Subagent:**
```
@debugging-assistant analyze error: TypeError at line 45 in users.js
```

### 2. Provide Context

The assistant will ask for:
- Error messages and stack traces
- Steps to reproduce
- Expected vs actual behavior
- Recent code changes
- Environment details

### 3. Follow the 5-Phase Process

The assistant will guide you through:
1. **Symptom Identification** - Gathering all relevant information
2. **Root Cause Analysis** - Finding why the bug occurs
3. **Fix Generation** - Creating a solution with explanation
4. **Validation Testing** - Confirming the fix works
5. **Regression Prevention** - Adding permanent safeguards

### 4. Review and Apply

Review the:
- Root cause explanation
- Proposed fix with alternatives considered
- Test cases validating the fix
- Documentation updates

## Simple Example

**Issue:** "Users can't log in, getting 'undefined' error"

**Assistant Process:**
```
1. Symptom Identification
   - Error: TypeError: Cannot read property 'password' of undefined
   - Location: auth.js line 23
   - Reproduction: Any login attempt fails

2. Root Cause Analysis
   - User object not retrieved before password check
   - Missing await on async database query

3. Fix Generation
   - Add await to getUserByEmail call
   - Add null check for user object

4. Validation Testing
   - Test passes after fix
   - No regressions in auth test suite

5. Regression Prevention
   - Added test for missing user case
   - Added ESLint rule for async/await
```

## Command Options

### Basic Usage
```bash
/debug-assist "describe your issue here"
```

### With Specific File
```bash
/debug-assist --file src/auth.js "login failing"
```

### With Error Log
```bash
/debug-assist --log error.log "analyze crash"
```

### Interactive Mode
```bash
/debug-assist --interactive
```

## Common Patterns

### Null/Undefined Errors
```
Symptom: "Cannot read property 'x' of undefined"
Common Causes: Missing validation, async timing, optional fields
Fix Pattern: Add null checks, optional chaining, default values
```

### Race Conditions
```
Symptom: Intermittent failures, data corruption
Common Causes: Concurrent access, missing await, shared state
Fix Pattern: Synchronization, locks, immutable updates
```

### Memory Leaks
```
Symptom: Growing memory usage, performance degradation
Common Causes: Unremoved listeners, circular refs, global state
Fix Pattern: Cleanup functions, weak references, proper disposal
```

### Async Issues
```
Symptom: Promises not resolving, timing errors
Common Causes: Missing await, unhandled rejection, callback hell
Fix Pattern: Async/await, proper error handling, Promise.all
```

## Configuration

Create `.debug-config.json` in your project:
```json
{
  "testCommand": "npm test",
  "lintCommand": "npm run lint",
  "logLevel": "verbose",
  "autoTest": true,
  "maxFixes": 3,
  "requireTests": true
}
```

## Integration

### With Git
Automatically creates fix branches:
```
debug/issue-[id]-[description]
```

### With CI/CD
Validates fixes don't break builds:
```bash
# Runs full test suite before committing
```

### With Issue Tracking
Links to bug tracking system:
```bash
/debug-assist --issue JIRA-1234
```

## Tips for Success

1. **Be Specific:** Provide exact error messages and reproduction steps
2. **Share Context:** Include recent changes and environment details
3. **Trust the Process:** Follow all 5 phases, don't skip ahead
4. **Test Thoroughly:** Validate fixes in realistic conditions
5. **Document Learnings:** Help future debugging efforts

## Troubleshooting

**Can't Reproduce Issue:**
- Try different environments (dev, staging)
- Check for timing-dependent behavior
- Look for environmental differences

**Fix Doesn't Work:**
- Verify root cause analysis was correct
- Check for multiple contributing factors
- Consider alternative approaches

**Tests Keep Failing:**
- Ensure tests are valid and up-to-date
- Check for flaky tests unrelated to fix
- Verify test environment matches production

## Advanced Features

### Multi-Service Debugging
```bash
/debug-assist --distributed --services api,database,cache
```

### Performance Analysis
```bash
/debug-assist --profile --benchmark
```

### Security Review
```bash
/debug-assist --security-scan
```

## Examples

### Example 1: Simple Fix
```bash
/debug-assist "Getting undefined when accessing user.email"
# Result: Added null check, test added, fix validated
```

### Example 2: Complex Issue
```bash
/debug-assist "Intermittent database deadlocks in checkout process"
# Result: Transaction ordering fixed, retry logic added, monitoring improved
```

### Example 3: Performance
```bash
/debug-assist "API response time degraded from 100ms to 2s"
# Result: N+1 query identified, eager loading added, indexes created
```

## Getting Help

- Full Documentation: See SKILL.md
- Process Details: See PROCESS.md
- Architecture: See process-diagram.gv
- Issues: Report bugs to your project issue tracker

## Agent Responsibilities

- **code-analyzer:** Symptom identification, root cause analysis
- **coder:** Fix generation, implementation
- **tester:** Validation testing, regression prevention

All agents coordinate via Claude Flow hooks and memory system.

## Success Metrics

- 95%+ first-attempt fix success rate
- < 30 minutes to root cause for typical bugs
- < 2% regression rate from fixes
- 100% of fixes include tests

---

**Quick Command Reference:**

```bash
/debug-assist "[issue]"              # Start debugging
/debug-assist --help                 # Show options
/debug-assist --status               # Check progress
/debug-assist --report               # Generate report
```

Start debugging smarter today!
