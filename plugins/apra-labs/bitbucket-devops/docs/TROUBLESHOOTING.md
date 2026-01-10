# Troubleshooting Guide

Common issues and their solutions when using the Bitbucket DevOps Skill.

## Common Errors

### Pipeline Not Found

**Error Message:**
```
Pipeline build #123 not found in the last 100 results
```

**Causes:**
- Build number too old (older than last 100 pipelines)
- Build number doesn't exist
- Wrong workspace/repository

**Solutions:**
```bash
# 1. List recent pipelines to verify build numbers
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  list-pipelines "workspace" "repo" 50

# 2. Use latest-failed helper instead
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-latest-failed "workspace" "repo"

# 3. Verify workspace and repository names
git config --get remote.origin.url
```

---

### Logs Unavailable

**Error Message:**
```
Error getting step logs: 404 Not Found
```

**Causes:**
- Pipeline still running (logs not finalized)
- Step was skipped
- Step UUID incorrect

**Solutions:**
```bash
# 1. Check pipeline status first
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-info "workspace" "repo" "{pipeline-uuid}"

# 2. Wait for pipeline to complete (state.name === "COMPLETED")

# 3. Use tail-step-log for running pipelines
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  tail-step-log "workspace" "repo" "{pipeline-uuid}" "{step-uuid}" 5000
```

---

### No Credential File Found

**Error Message:**
```
Error: Cannot find credentials file at ~/.claude/skills/bitbucket-devops/credentials.json
```

**Solution:**
```bash
# 1. Copy template
cd ~/.claude/skills/bitbucket-devops/
cp credentials.json.template credentials.json

# 2. Edit with your credentials
# Open credentials.json and fill in:
# - workspace: your-workspace-name
# - user_email: your-email@example.com (for API operations)
# - username: your-workspace-slug (for git operations)
# - password: your-bitbucket-app-password

# 3. Get app password from: https://bitbucket.org/account/settings/app-passwords/
# Required permissions: Repositories: Read, Pipelines: Read, Pull requests: Read
```

---

### API Authentication Failed (401)

**Error Message:**
```
401 Unauthorized - API authentication failed
```

**Causes:**
- Invalid app password
- Wrong email address in user_email field
- App password missing required permissions
- App password expired

**Solutions:**
```bash
# 1. Verify credentials format
cat ~/.claude/skills/bitbucket-devops/credentials.json
# Should have:
# - "user_email": "your-email@example.com" (NOT username)
# - "password": "your-app-password"

# 2. Test API authentication
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  list-repositories "workspace" 1

# 3. Generate new app password
# Visit: https://bitbucket.org/account/settings/app-passwords/
# Required scopes:
# - Repositories: Read
# - Pipelines: Read
# - Pull requests: Read (if using PR commands)

# 4. Check for email vs username confusion
# API requires EMAIL, not username
# If you see: "username": "kumaakh" → WRONG for API
# Should be: "user_email": "akhil@apra.in"
```

---

### Git Authentication Failed

**Error Message:**
```
fatal: Authentication failed for 'https://bitbucket.org/...'
```

**Causes:**
- Using email instead of username for git operations
- Invalid app password
- Missing git username in credentials

**Solutions:**
```bash
# 1. Verify git credentials format
cat ~/.claude/skills/bitbucket-devops/credentials.json
# Should have:
# - "username": "your-workspace-slug" (NOT email)
# - "password": "your-app-password"

# 2. Test git authentication
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  test-git-auth "workspace" "repo"

# 3. Check for email vs username confusion
# Git requires USERNAME (workspace slug), not email
# If you see: "username": "akhil@apra.in" → WRONG for git
# Should be: "username": "kumaakh"

# 4. Workspace slug is usually the first part of your repository URL
# From: https://bitbucket.org/kumaakh/my-repo
# Workspace: kumaakh (use this for git operations)
```

---

### Node.js Not Found

**Error Message:**
```
bash: node: command not found
```

**Solutions:**
```bash
# 1. Install Node.js v18 or later
# macOS:
brew install node

# Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows:
# Download from: https://nodejs.org/

# 2. Verify installation
node --version  # Should be v18.0.0 or higher
```

---

### Submodule Not Initialized

**Error Message:**
```
Error: Cannot find bitbucket-mcp at ~/.claude/skills/bitbucket-devops/bitbucket-mcp/
```

**Solutions:**
```bash
# 1. Navigate to skill directory
cd ~/.claude/skills/bitbucket-devops/

# 2. Initialize and update submodule
git submodule update --init --recursive

# 3. Install dependencies
cd bitbucket-mcp/
npm install
npm run build

# 4. Verify CLI exists
ls -la dist/index-cli.js

# 5. If still broken, run install script
cd ..
bash install.sh
```

---

### UUID Encoding Issues

**Error Message:**
```
400 Bad Request - Invalid pipeline UUID
```

**Note:** This should no longer occur with smart identifier detection, but if you're manually constructing UUIDs:

**Solutions:**
```bash
# The CLI handles UUID encoding automatically
# UUIDs look like: {abc-123-def-456}

# If calling API directly, URL-encode the braces:
# {uuid} → %7Buuid%7D

# Better: Use build numbers instead
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-by-number "workspace" "repo" 60
# This returns the UUID, which you can then use safely
```

---

### JSON Parsing Errors in Bash

**Error Message:**
```
parse error: Invalid numeric literal at line 1, column 10
```

**Solutions:**
```bash
# Option 1: Use jq for JSON parsing
result=$(node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-latest "workspace" "repo")
build_number=$(echo "$result" | jq -r '.build_number')
uuid=$(echo "$result" | jq -r '.uuid')

# Option 2: Use node for JSON parsing
build_number=$(node -e "const data = $result; console.log(data.build_number)")

# Option 3: Save to file first
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-latest "workspace" "repo" > /tmp/pipeline.json
cat /tmp/pipeline.json | jq -r '.build_number'
```

---

### Large Log Files

**Issue:**
Log files are too large to process or display.

**Solutions:**
```bash
# 1. Check file size
ls -lh .pipeline-logs/pipeline-123-Deploy.log

# 2. Extract errors only
grep -i "error\|failed\|exception\|fatal" .pipeline-logs/pipeline-123-Deploy.log \
  > .pipeline-logs/errors-only.txt

# 3. Show last 200 lines (where failures typically occur)
tail -n 200 .pipeline-logs/pipeline-123-Deploy.log

# 4. Show first occurrence of error with context
grep -i -m 1 -A 10 -B 5 "error" .pipeline-logs/pipeline-123-Deploy.log

# 5. Count error types
grep -i "error" .pipeline-logs/pipeline-123-Deploy.log | \
  cut -d: -f2- | sort | uniq -c | sort -nr | head -20
```

---

### Rate Limiting

**Error Message:**
```
429 Too Many Requests - Rate limit exceeded
```

**Causes:**
- Too many API calls in short time
- Bitbucket Cloud: 60 requests/hour per user (standard tier)
- Bitbucket Server: Varies by configuration

**Solutions:**
```bash
# 1. Wait 1 hour for rate limit to reset

# 2. Use caching - store results in variables
pipeline=$(node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-latest "workspace" "repo")
# Reuse $pipeline instead of making new calls

# 3. Combine operations
# Instead of:
#   - Call 1: get pipeline
#   - Call 2: get steps
#   - Call 3: get logs
# Use helper that does multiple operations:
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  download-failed-logs "workspace" "repo" "{pipeline-uuid}" 123

# 4. Increase API limits (paid Bitbucket plans)
```

---

### Permission Errors

**Error Message:**
```
403 Forbidden - Insufficient permissions
```

**Solutions:**
```bash
# 1. Check app password scopes
# Visit: https://bitbucket.org/account/settings/app-passwords/
# Verify permissions:
# ✓ Repositories: Read
# ✓ Pipelines: Read
# ✓ Pull requests: Read (if using PR commands)
# ✓ Pull requests: Write (if approving/merging PRs)

# 2. Check repository access
# Ensure your Bitbucket user has access to the repository

# 3. Regenerate app password with correct scopes

# 4. Update credentials.json with new password
```

---

## Diagnostic Commands

### Verify Skill Installation

```bash
# Check skill directory
ls -la ~/.claude/skills/bitbucket-devops/

# Check submodule
ls -la ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/

# Check credentials
cat ~/.claude/skills/bitbucket-devops/credentials.json

# Test CLI tool
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js --help
```

### Test API Connectivity

```bash
# List repositories (simplest API test)
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  list-repositories "workspace" 1

# List recent pipelines
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  list-pipelines "workspace" "repo" 5

# Get workspace info
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  get-repo "workspace" "repo"
```

### Test Git Connectivity

```bash
# Test git authentication
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  test-git-auth "workspace" "repo"

# Expected output:
# {
#   "success": true,
#   "commit": "abc123def456..."
# }
```

### Verify Node.js and Dependencies

```bash
# Check Node.js version
node --version  # Should be v18.0.0+

# Check npm version
npm --version

# Rebuild skill dependencies if needed
cd ~/.claude/skills/bitbucket-devops/bitbucket-mcp/
npm install
npm run build

# Verify helpers
cd ~/.claude/skills/bitbucket-devops/
node lib/helpers.js --help
```

---

## Getting Help

If issues persist:

1. **Check credentials format**: See [REFERENCE.md](REFERENCE.md) for correct format
2. **Review git operations**: See [GIT_OPERATIONS.md](GIT_OPERATIONS.md) for auth details
3. **Check patterns**: See [PATTERNS.md](PATTERNS.md) for usage examples
4. **Verify installation**: Run `bash install.sh` in skill directory
5. **Test with minimal example**: Use `list-repositories` command first

---

## Performance Tips

1. **Cache API responses**: Store JSON in variables, don't re-fetch
2. **Use helpers over CLI**: Helpers combine multiple API calls efficiently
3. **Limit result sets**: Use `limit` parameter (default: 10)
4. **Filter logs early**: Use grep before displaying large logs
5. **Auto-approve enabled**: No approval prompts for node commands
