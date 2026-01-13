# Testing Guide

Before publishing this skill publicly, follow this testing checklist.

## Smoke Test (Quick Validation)

After making any changes to the skill, run the smoke test to ensure basic functionality:

```bash
# Run smoke test on deployed skill
bash smoke-test.sh

# Or test a specific directory
bash smoke-test.sh ~/.claude/skills/bitbucket-devops
```

The smoke test validates:
- ✅ File structure is correct
- ✅ Dependencies are installed (node_modules, axios, etc.)
- ✅ package.json files are present and configured
- ✅ ES modules can be imported
- ✅ CLI tool is executable
- ✅ Credentials template exists

**Run smoke test after:**
- Installing or updating the skill
- Making changes to install.sh
- Modifying lib/helpers.js or CLI tools
- Before committing major changes
- Before creating a release

Expected output: All tests should pass (green checkmarks).

## Pre-Test Setup

### 1. Verify No Credentials in Repository

Run this check to ensure no sensitive information:

```bash
cd /c/ak/claude-bitbucket-devops-skill

# Search for potential credentials
grep -r "ATATT" .
grep -r "password" . | grep -v "your-app-password"
grep -r "kumaakh" .
grep -r "akhil@apra.in" . | grep -v "@apralabs.com"

# All should return no results or only template/example references
```

### 2. Review All Files

- [ ] No hardcoded workspace names (except in examples)
- [ ] No hardcoded paths (except in examples clearly marked)
- [ ] All examples use placeholder values
- [ ] Author is Akhil Kumar (akhil@apralabs.com)

## Installation Test

### Test 1: Fresh Install

Simulate a new user installing the skill:

1. **Backup current skill** (if you have one):
   ```bash
   mv ~/.claude/skills/bitbucket-devops ~/.claude/skills/bitbucket-devops.backup
   ```

2. **Install from this repo**:
   ```bash
   cp /c/ak/claude-bitbucket-devops-skill/SKILL.md ~/.claude/skills/bitbucket-devops/
   ```

3. **Restart VSCode**:
   - Close all VSCode windows
   - Reopen VSCode
   - Wait 10 seconds

4. **Verify installation**:
   ```
   Ask Claude: "Can you help with Bitbucket pipelines?"
   Expected: Skill should activate
   ```

## Functional Tests

### Test 2: Find Latest Pipeline

```
Test: "What's the latest pipeline in apranvr?"

Expected behavior:
- Skill activates
- Asks for MCP approval
- Returns pipeline details
- No errors
```

### Test 3: Get Specific Pipeline

```
Test: "Show me pipeline #72 details"

Expected behavior:
- Lists pipeline information
- Shows all steps
- Indicates which failed (if any)
```

### Test 4: Download Logs

```
Test: "Get logs for the failed steps in pipeline #72"

Expected behavior:
- Identifies failed steps
- Downloads logs
- Saves to .pipeline-logs/ in current project
- Creates readable log files
```

### Test 5: Large Log Handling

```
Test: "Get logs from pipeline #72" (where logs > 10KB)

Expected behavior:
- Detects large logs
- Splits into chunks automatically
- Presents chunk index
- Each chunk is manageable size
```

### Test 6: Cross-Project

```
Test: "Show latest failure in workspace/different-repo"

Expected behavior:
- Works with different workspace
- Works with different repo
- Doesn't mix up with default settings
```

### Test 7: Trigger Pipeline

```
Test: "What pipelines can I run on the main branch?"

Expected behavior:
- Lists available pipeline types
- Shows custom pipelines
- No errors

Then: "Trigger the <pipeline-name>"
Expected:
- Confirms parameters
- Triggers pipeline
- Returns pipeline URL and number
```

## Edge Cases

### Test 8: No Failures

```
Test: "What's the latest failed pipeline?" (when no recent failures)

Expected behavior:
- Gracefully handles no results
- Suggests checking successful pipelines
- Doesn't error out
```

### Test 9: Running Pipeline

```
Test: "Get logs from a currently running pipeline"

Expected behavior:
- Detects pipeline is running
- Informs user to wait
- Doesn't crash
```

### Test 10: Very Old Pipeline

```
Test: "Show me pipeline #1"

Expected behavior:
- Attempts to find it
- If not found, explains may be too old
- Suggests using recent pipeline numbers
```

## Documentation Tests

### Test 11: README Accuracy

- [ ] All installation steps work as written
- [ ] All example commands work
- [ ] Links to external resources are valid
- [ ] GitHub issue link works

### Test 12: INSTALL.md Walkthrough

- [ ] Follow INSTALL.md step-by-step as a new user
- [ ] Note any unclear instructions
- [ ] Verify all commands work on Windows
- [ ] Verify all paths are correct

## Clean-up Tests

### Test 13: Log Files

1. **Generate logs**:
   - Download several pipeline logs
   - Check `.pipeline-logs/` directory exists
   - Verify files are created with correct names

2. **Verify .gitignore**:
   ```bash
   git status
   # Should NOT show .pipeline-logs/ files
   ```

3. **Clean-up**:
   ```bash
   rm -rf .pipeline-logs/
   ```

## Multi-Project Test

### Test 14: Different Projects

1. **Project A**:
   ```
   cd /c/project-a
   Ask: "Get pipeline #10 logs"
   Verify: Logs go to /c/project-a/.pipeline-logs/
   ```

2. **Project B**:
   ```
   cd /c/project-b
   Ask: "Get pipeline #20 logs"
   Verify: Logs go to /c/project-b/.pipeline-logs/
   Verify: No mix-up with Project A logs
   ```

## Performance Tests

### Test 15: Multiple Requests

```
1. "What's the latest failure?"
2. "Show me the steps"
3. "Get the logs"
4. "Analyze the errors"

Expected:
- Each request is handled correctly
- No slowdowns
- Cached data is reused when appropriate
```

## Error Handling Tests

### Test 16: Invalid Workspace

```
Test: "Show pipelines in nonexistent-workspace/fake-repo"

Expected behavior:
- Returns clear error message
- Suggests checking workspace name
- Doesn't crash
```

### Test 17: No MCP Server

```
Test: Remove MCP server config temporarily

Expected behavior:
- Skill attempts to activate
- Clear error about MCP server not configured
- Points to installation docs
```

## Final Checks

### Before Publishing

- [ ] All tests pass
- [ ] No credentials in any file
- [ ] Documentation is accurate
- [ ] Examples work on fresh install
- [ ] .gitignore properly configured
- [ ] LICENSE file is correct (CC BY 4.0)
- [ ] Author attribution is correct
- [ ] README credits bitbucket-mcp properly
- [ ] GitHub issue links are valid

### Create GitHub Repository

Once all tests pass:

1. **Create repo on GitHub**:
   - Organization: Apra-Labs
   - Name: claude-bitbucket-devops-skill
   - Description: "A Claude Code skill for comprehensive Bitbucket DevOps automation"
   - Public
   - Don't initialize with README (we have our own)

2. **Push to GitHub**:
   ```bash
   cd /c/ak/claude-bitbucket-devops-skill
   git remote add origin git@github.com:Apra-Labs/claude-bitbucket-devops-skill.git
   git push -u origin master
   ```

3. **Create initial release**:
   - Tag: v1.0.0
   - Title: "Initial Release - Claude Bitbucket DevOps Skill"
   - Copy CHANGELOG.md content to release notes

## Test Results Log

Document your test results:

| Test | Status | Notes |
|------|--------|-------|
| 1. Fresh Install | ⏸️ Pending | |
| 2. Find Latest | ⏸️ Pending | |
| 3. Get Specific | ⏸️ Pending | |
| 4. Download Logs | ⏸️ Pending | |
| 5. Large Logs | ⏸️ Pending | |
| 6. Cross-Project | ⏸️ Pending | |
| 7. Trigger Pipeline | ⏸️ Pending | |
| 8. No Failures | ⏸️ Pending | |
| 9. Running Pipeline | ⏸️ Pending | |
| 10. Old Pipeline | ⏸️ Pending | |
| 11. README Accuracy | ⏸️ Pending | |
| 12. INSTALL.md | ⏸️ Pending | |
| 13. Log Files | ⏸️ Pending | |
| 14. Multi-Project | ⏸️ Pending | |
| 15. Performance | ⏸️ Pending | |
| 16. Invalid Workspace | ⏸️ Pending | |
| 17. No MCP Server | ⏸️ Pending | |

**Legend:**
- ⏸️ Pending
- ✅ Passed
- ❌ Failed (with notes)
- ⚠️ Passed with issues

---

**Testing Coordinator**: Akhil Kumar (akhil@apralabs.com)
**Repository**: /c/ak/claude-bitbucket-devops-skill
