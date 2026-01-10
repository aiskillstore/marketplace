---
name: bitbucket-devops
description: Comprehensive Bitbucket pipeline automation using direct Node.js API calls. Monitor pipeline status, analyze failures, download logs, and trigger builds. Use this skill when the user asks to check pipeline status, find failing pipelines, download logs, trigger builds, or debug pipeline failures. No MCP approval prompts required - uses Bash tool with node commands.
allowed-tools: Bash, Read, Write, Grep, Glob
---

# Bitbucket DevOps Skill

This skill provides comprehensive Bitbucket DevOps automation using direct Node.js API calls via the Bash tool. Built on the [bitbucket-mcp](https://github.com/Apra-Labs/bitbucket-mcp) client library.

**Key Advantage:** Uses direct Node.js calls (auto-approved) instead of MCP tools, eliminating the approval prompts issue from [GitHub Issue #10801](https://github.com/anthropics/claude-code/issues/10801).

## ⚠️ MANDATORY: How to Approach User Requests

**You MUST follow this three-tier fallback strategy for ALL Bitbucket operations. This is REQUIRED, not optional.**

**CRITICAL RULES:**
- **DO NOT create new .js files for Bitbucket API calls**
- **DO NOT use `node -e` for inline Bitbucket API operations**
- **ONLY use the pre-built CLI tools listed below**
- **ALWAYS start with Tier 1, fall back to Tier 2 if needed, use Tier 3 only as last resort**

### Tier 1: High-Level Helper Functions (REQUIRED FIRST STEP)

**You MUST check these helpers FIRST before attempting any other approach.**

These solve common workflows in a single command. If the user's request matches any of these patterns, you MUST use the corresponding helper.

**Location:** `~/.claude/skills/bitbucket-devops/lib/helpers.js`

**Available Commands:**
- `get-latest-failed <workspace> <repo>` - Get most recent failed pipeline
- `get-latest <workspace> <repo>` - Get most recent pipeline (any status)
- `get-by-number <workspace> <repo> <build-number>` - Find pipeline by build number
- `get-failed-steps <workspace> <repo> <pipeline-uuid>` - Get all failed steps
- `download-failed-logs <workspace> <repo> <pipeline-uuid> <build-number>` - Download all failed step logs
- `get-info <workspace> <repo> <pipeline-uuid>` - Get formatted pipeline + steps info

**MUST use for:** "latest failed build", "download logs for pipeline #123", "what failed in this build", "get pipeline by number"

**Usage:**
```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js <command> <args>
```

**Example:**
```bash
# User: "What's the latest failing pipeline?"
# You MUST use:
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-latest-failed "workspace" "repo"

# DO NOT create a new script
# DO NOT use node -e
# DO NOT write custom API calls
```

### Tier 2: Low-Level CLI Commands (IF TIER 1 CANNOT SOLVE)

**ONLY use Tier 2 if NO Tier 1 helper matches the user's request.**

Direct API wrappers for specific operations. You MUST use these for operations not covered by Tier 1 helpers.

**Location:** `~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js`

**Key Commands** (see [docs/REFERENCE.md](docs/REFERENCE.md) for complete list):

**Pipeline Operations:**
- `list-pipelines <workspace> <repo> [limit]`
- `get-pipeline <workspace> <repo> <pipeline-uuid>`
- `get-pipeline-steps <workspace> <repo> <pipeline-uuid>`
- `get-step-logs <workspace> <repo> <pipeline-uuid> <step-uuid>`
- `run-pipeline <workspace> <repo> <branch> [pipeline-name] [variables-json]`
- `stop-pipeline <workspace> <repo> <pipeline-uuid>`

**Pull Request Operations:**
- `list-prs <workspace> <repo> [state] [limit]`
- `get-pr <workspace> <repo> <pr_id>`
- `approve-pr <workspace> <repo> <pr_id>`
- `merge-pr <workspace> <repo> <pr_id> [message] [strategy]`
- `decline-pr <workspace> <repo> <pr_id> [message]`

**Repository Operations:**
- `get-branching-model <workspace> <repo>`
- `list-repositories <workspace>`

**Usage:**
```bash
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js <command> <args>
```

**You MAY chain multiple Tier 2 commands** - see [docs/PATTERNS.md](docs/PATTERNS.md) for examples.

### Tier 3: Direct Bitbucket API Calls (ONLY IF TIER 1 AND 2 FAIL)

**ONLY use Tier 3 if BOTH Tier 1 AND Tier 2 cannot solve the request. This should be RARE.**

Before using Tier 3, you MUST:
1. Verify no Tier 1 helper exists
2. Verify no Tier 2 CLI command exists
3. Verify no combination of Tier 1 + Tier 2 can solve it

**Documentation:** `~/.claude/skills/bitbucket-devops/bitbucket-mcp/docs/`
- `api-overview.md` - Authentication, base URLs, rate limits
- `pipelines-api.md` - Complete pipeline API reference
- `repositories-api.md` - Repository operations
- `pull-requests-api.md` - PR operations (future)

---

## REQUIRED Decision Process

**Before performing ANY Bitbucket operation, you MUST:**

1. **Check Tier 1 helpers** - Review the 6 helpers above. Does one solve this?
   - **YES** → Use it immediately with `node ~/.claude/skills/bitbucket-devops/lib/helpers.js <command>`
   - **NO** → Continue to step 2

2. **Check Tier 2 CLI** - Review the CLI commands above. Can one or more solve this?
   - **YES** → Use them with `node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js <command>`
   - **NO** → Continue to step 3

3. **Check Tier 3 docs** - Read API docs. Is there a direct API call needed?
   - **YES** → Read docs, use curl with credentials
   - **NO** → Ask user for clarification

**NEVER skip this process. NEVER create new .js files. ALWAYS use pre-built tools.**

---

## Known Limitations

### Pipeline Artifacts Cannot Be Downloaded via API

**IMPORTANT:** Bitbucket Cloud does NOT provide an API to download pipeline artifacts.

**If a user asks to download build artifacts:**
1. Inform them that artifact download via API is not possible
2. Direct them to the Bitbucket web UI:
   - Repository → Pipelines → Build # → Step → Artifacts section → Download button
3. Note: Artifacts expire automatically after 14 days

**Tip:** For programmatic artifact access, consider uploading to S3/Azure Blob Storage during your pipeline.

**DO NOT:** Search for undocumented endpoints - this has been thoroughly researched and no API exists.

---

## The DevOps REPL Advantage

Traditional pipeline debugging is slow: push code → wait → fail → investigate logs → fix → repeat (hours per cycle).

This skill enables a **REPL-like experience for DevOps**: Claude observes pipelines in real-time, analyzes failures instantly, suggests precise fixes, and iterates with you until builds pass - reducing debugging cycles from hours to minutes.

**The Loop:**
1. **Read**: Monitor pipeline execution and capture failures
2. **Eval**: AI analyzes logs and identifies root cause
3. **Print**: Claude presents findings and suggests fixes
4. **Loop**: Apply fix, trigger build, repeat until green ✅

This transforms DevOps from slow batch processing into interactive, conversational development.

---

## Prerequisites

This skill uses the Bash tool (auto-approved in Claude Code) to run Node.js commands. Required:
- Node.js (v18+)
- Git (for submodule management)

**Note:** No MCP server required - bitbucket-mcp is used as a library via git submodule.

---

## Configuration

The skill directory is located at: `~/.claude/skills/bitbucket-devops/`

Credentials are loaded with priority (first found wins):
1. **Project level**: `./credentials.json` or `./.bitbucket-credentials` (current working directory)
2. **User level**: `~/.bitbucket-credentials` (home directory)
3. **Skill level**: `~/.claude/skills/bitbucket-devops/credentials.json`

### Credential Format

**IMPORTANT: Different credentials for different operations**

```json
{
  "url": "https://api.bitbucket.org/2.0",
  "workspace": "your-workspace-name",
  "user_email": "your-email@example.com",
  "username": "your-workspace-name",
  "password": "your-bitbucket-app-password"
}
```

**Field explanations:**
- `user_email`: Your Bitbucket account email (for API authentication) - MUST contain `@`
- `username`: Your Bitbucket workspace slug (for git operations) - MUST NOT contain `@`
- `password`: App password from https://bitbucket.org/account/settings/app-passwords/
  - Required permissions: Repositories: Read, Pipelines: Read

See [docs/GIT_OPERATIONS.md](docs/GIT_OPERATIONS.md) for details on credential requirements.

---

## Quick Start: Essential Patterns

### Pattern 0: Always Detect Workspace and Repository First

**Before any pipeline operation**, determine the workspace and repository.

**Auto-detect from git remote:**
```bash
git_url=$(git config --get remote.origin.url 2>/dev/null)
if [[ "$git_url" =~ bitbucket.org[:/]([^/]+)/([^/.]+) ]]; then
  WORKSPACE="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]}"
  echo "Detected: $WORKSPACE/$REPO"
fi
```

**Or ask user:** "What's your Bitbucket workspace and repository name?"

**IMPORTANT:** Use actual values in commands. Never use literal strings `"workspace"` or `"repo"`.

### Pattern 1: Find Latest Failing Pipeline

```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-latest-failed "workspace" "repo"
```

**Present to user:**
```
Latest failed pipeline:
- Pipeline #123
- Branch: main
- Commit: abc123d - "Fix bug in deployment"
- Status: FAILED
```

### Pattern 2: Download Logs for Failed Pipeline

```bash
# Step 1: Get pipeline by build number
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-by-number "workspace" "repo" 123

# Step 2: Download all failed step logs
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  download-failed-logs "workspace" "repo" "{pipeline-uuid}" 123
```

**Present to user:**
```
Downloaded logs for 2 failed steps:

1. Deploy
   - Saved to: .pipeline-logs/pipeline-123-Deploy.log
   - Size: 12.4 KB

2. Integration_Tests
   - Saved to: .pipeline-logs/pipeline-123-Integration_Tests.log
   - Size: 45.2 KB
```

**Important:** Check log file size before displaying. If > 50KB, show summary only:
```bash
tail -n 100 .pipeline-logs/pipeline-123-Deploy.log
grep -i "error\|failed\|exception" .pipeline-logs/pipeline-123-Deploy.log
```

### Pattern 3: The DevOps REPL Loop (Full Debugging Workflow)

**User: "Fix the failing build"**

**1. READ - Find and Analyze Failure:**
```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-latest-failed "workspace" "repo"
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-failed-steps "workspace" "repo" "{uuid}"
node ~/.claude/skills/bitbucket-devops/lib/helpers.js download-failed-logs "workspace" "repo" "{uuid}" 123
```

**2. EVAL - Analyze the Logs:**
```bash
grep -i "error\|failed\|exception\|fatal" .pipeline-logs/*.log
grep -i -A 5 -B 5 "error" .pipeline-logs/pipeline-*.log
```

**3. PRINT - Suggest Fix:**
```
Found the issue in Pipeline #123:

Error Type: TypeScript compilation error
Location: src/auth/service.ts:42
Error: Property 'userId' does not exist on type 'User'

Root Cause: The User interface was updated but this file wasn't

Suggested Fix:
Change line 42 from:
  return user.userId
To:
  return user.id

Should I apply this fix?
```

**4. LOOP - Apply Fix and Re-Test:**
```bash
# Apply fix using Edit tool
# Commit changes
git add src/auth/service.ts
git commit -m "Fix: Update User property reference from userId to id"

# Trigger new pipeline run
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  run-pipeline "workspace" "repo" "branch-name"

# Monitor the new build
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-by-number "workspace" "repo" <new-build-number>
```

**5. REPEAT or CELEBRATE:**
- If new build FAILS: Go back to step 1 with new logs
- If new build SUCCEEDS: ✅ Success! Build is green
- If new build IN_PROGRESS: Monitor with Pattern 9

**This transforms hours of manual debugging into minutes of AI-assisted iteration.**

---

## Complete Documentation

For comprehensive coverage, refer to these detailed guides:

- **[docs/REFERENCE.md](docs/REFERENCE.md)** - Complete command reference for all Tier 1, 2, and 3 operations
- **[docs/PATTERNS.md](docs/PATTERNS.md)** - All 11 usage patterns with detailed examples and bash scripts
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common errors, diagnostic commands, and solutions
- **[docs/GIT_OPERATIONS.md](docs/GIT_OPERATIONS.md)** - Credential requirements for API vs git operations

---

## Log Storage

Logs are downloaded to `.pipeline-logs/` in the directory where VSCode is opened (your working directory).

**Structure:**
```
/path/to/open-project/
├── .pipeline-logs/           ← Created automatically here
│   ├── pipeline-123-Deploy.log
│   ├── pipeline-123-Test.log
│   └── errors-only.txt
├── src/
└── ...
```

**Important:**
- Logs are stored in the current working directory
- Always use relative path: `.pipeline-logs/filename.log`
- Tell user to add `.pipeline-logs/` to their project's `.gitignore`
- Logs persist across sessions for easy reference

---

## Common Errors (Quick Reference)

| Error | Cause | Solution |
|-------|-------|----------|
| "Pipeline not found" | Build number too old | Use `get-latest-failed` instead |
| "Logs unavailable" | Pipeline still running | Wait for completion |
| "No credential file found" | Missing credentials.json | Copy from credentials.json.template |
| "Node.js not found" | Node not installed | Install Node.js v18+ |
| "Submodule not initialized" | Git submodule missing | Run `bash install.sh` |
| "401 Unauthorized" | Wrong credentials | Check user_email (not username) in credentials.json |
| "Git auth failed" | Wrong username | Check username (not email) for git operations |

**For detailed troubleshooting:** See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Best Practices

1. **Always confirm workspace/repo** - Auto-detect from git or ask user
2. **Check pipeline status before logs** - Don't request logs for running pipelines
3. **Limit initial results** - Start with 10 recent pipelines, increase if needed
4. **Smart log filtering** - Use grep to find errors first
5. **Cache results** - Store JSON responses in variables to avoid redundant calls
6. **Use helper functions** - Prefer Tier 1 helpers for common operations

---

## Performance Notes

- **No approval prompts**: Bash tool with node commands is auto-approved
- **Direct API calls**: No MCP protocol overhead
- **Credential caching**: Loaded once per invocation
- **Bitbucket rate limits**: 60 requests/hour per user (standard tier)

---

## Credits

This skill is built on [bitbucket-mcp](https://github.com/Apra-Labs/bitbucket-mcp) by Apra Labs, forked from [@MatanYemini's original work](https://github.com/MatanYemini/bitbucket-mcp).

**Architecture:** Uses bitbucket-mcp as a library (git submodule), NOT as an MCP server. This approach eliminates approval prompts while maintaining full API functionality.

**License**: CC BY 4.0
**Maintained by**: [Apra Labs](https://github.com/Apra-Labs)
