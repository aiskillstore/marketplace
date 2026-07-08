---
name: bitbucket-devops
description: Comprehensive Bitbucket pipeline automation using direct Node.js API calls. Monitor pipeline status, analyze failures, download logs, and trigger builds. Use this skill when the user asks to check pipeline status, find failing pipelines, download logs, trigger builds, or debug pipeline failures. No MCP approval prompts required - uses Bash tool with node commands.
allowed-tools: Bash, Read, Write, Grep, Glob
---

# Bitbucket DevOps Skill

This skill provides comprehensive Bitbucket DevOps automation using direct Node.js API calls via a Bash-equivalent tool. Built on the [bitbucket-mcp](https://github.com/Apra-Labs/bitbucket-mcp) client library. It's plain Node.js CLI invocation with no Claude-specific dependency, so it runs unchanged under Claude Code, AGY, OpenCode, or any other agent runtime that can shell out to `node`.

**Note on paths:** Paths below (`~/.claude/skills/bitbucket-devops/...`) reflect Claude Code's skill-install convention, since `install.sh`/`install.ps1` default to `--llm claude`. If this skill was installed with `--llm agy` or `--llm opencode`, substitute `~/.gemini/antigravity-cli/skills/bitbucket-devops/` or `~/.config/opencode/skills/bitbucket-devops/` respectively (or whatever `TARGET_DIR` was used) - the commands themselves are identical.

**Key Advantage:** Uses direct Node.js calls via a Bash-equivalent tool instead of MCP tools. This works the same way in any agent runtime that can invoke shell commands (Claude Code, AGY, OpenCode, etc.) - there's no Claude-specific API or tool assumption anywhere in this skill's code. In Claude Code specifically, Bash is auto-approved by default, which also eliminates the MCP approval-prompt friction described in [GitHub Issue #10801](https://github.com/anthropics/claude-code/issues/10801); other runtimes may have their own approval model for shell commands, but the underlying calls are identical either way.

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
- `list-environments <workspace> <repo>` - List deployment environments (sandbox/production/etc)
- `create-environment <workspace> <repo> <name> [environment_type] [rank]` - Create a deployment environment
- `list-deploy-variables <workspace> <repo> <environment>` - List secured deployment variables for an environment
- `create-deploy-variable <workspace> <repo> <environment> <key> <value> [secured]` - Add a deployment variable
- `update-deploy-variable <workspace> <repo> <environment> <variable> [key] [value] [secured]` - Update a deployment variable
- `delete-deploy-variable <workspace> <repo> <environment> <variable>` - Delete a deployment variable
- `check-credentials` - Reports which credential file is active and whether it's shaped correctly (field names, format validity), WITHOUT ever printing a secret value. Run this instead of opening/catting a credentials file directly to debug an auth problem.
- `check-for-updates` - Reports whether this repo's `main` branch has moved forward since this skill was installed. Report-only, never applies anything.
- `self-update [confirm]` - Without `confirm`, same report as `check-for-updates`. With `confirm`, pulls/rebuilds the update in place (git checkout installs) or redeploys from a fresh clone (file-copy installs) - never overwrites `credentials.json`.

**MUST use for:** "latest failed build", "download logs for pipeline #123", "what failed in this build", "get pipeline by number", "create a sandbox/production deployment environment", "add a deployment secret/variable", "list deployment environments", "check for skill updates", "update this skill"

**Requires a different app-password scope than the rest of this skill** - see [Deployment Environments & Variables](#deployment-environments--variables-new) below before using these six commands.

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
- `create-pr <workspace> <repo> <title> <source_branch> <target_branch> [description] [reviewers_csv]`
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

## Deployment Environments & Variables (NEW)

Bitbucket Cloud's REST API v2.0 **does** support creating and managing repository "Deployment environments" (Repository settings → Pipelines → Deployments, e.g. "sandbox", "production") and their secured deployment variables. This was previously undocumented in this skill - it's now available via six new Tier 1 helpers.

**Available Commands** (`node ~/.claude/skills/bitbucket-devops/lib/helpers.js <command> <args>`):
- `list-environments <workspace> <repo>`
- `create-environment <workspace> <repo> <name> [environment_type=Test] [rank]`
- `list-deploy-variables <workspace> <repo> <environment_name_or_uuid>`
- `create-deploy-variable <workspace> <repo> <environment_name_or_uuid> <key> <value> [secured=true]`
- `update-deploy-variable <workspace> <repo> <environment_name_or_uuid> <variable_key_or_uuid> [key] [value] [secured]`
- `delete-deploy-variable <workspace> <repo> <environment_name_or_uuid> <variable_key_or_uuid>`

Full details, endpoints, and JSON shapes: [docs/REFERENCE.md](docs/REFERENCE.md#deployment-environments--variables).

### ⚠️ Scope Requirements (CONFIRMED empirically, 2026-07)

This skill's originally documented scope (`Repositories: Read, Pipelines: Read` under the classic app-password model) is **NOT enough** for the write operations below. Confirmed against a real repo using Atlassian's newer **"API token with scopes"** credential type (a separate creation flow from the plain/classic API token at https://id.atlassian.com/manage-profile/security/api-tokens -- a classic unscoped token carries **zero** Bitbucket scopes regardless of account privileges, and fails with `"API Token provided has no Bitbucket scopes"` if used against Bitbucket's API at all):

| Operation | Required scope (Atlassian scoped-token name) | Classic app-password equivalent |
|---|---|---|
| `list-environments`, `list-deploy-variables` (read) | `read:repository:bitbucket` | `Repositories: Read` |
| pipeline read commands (list-pipelines, get-pipeline*, etc.) | `read:pipeline:bitbucket` | `Pipelines: Read` |
| `create-deploy-variable`, `update-deploy-variable`, `delete-deploy-variable` | `write:pipeline:bitbucket` -- confirmed sufficient in practice, no separate "edit variables" scope exists in the scoped-token model | `Pipelines: Edit variables` |
| `create-environment` | **`admin:pipeline:bitbucket`** -- CONFIRMED via a live 403 response (see below); `write:pipeline:bitbucket` alone is NOT sufficient | Unclear under the classic model; likely needs `Repositories: Admin` |
| `create-pr`/`approve-pr`/`merge-pr`/`decline-pr` | `write:pullrequest:bitbucket` | `Pull requests: Write` |

**Debugging tip, generalizable to any scope-mismatch**: Bitbucket's 403 response for a scope failure is self-diagnosing -- it returns a JSON body with both `required` and `granted` scope arrays, e.g.:
```json
{"error":{"message":"Your credentials lack one or more required privilege scopes.","detail":{"required":["admin:pipeline:bitbucket"],"granted":["read:repository:bitbucket","write:pipeline:bitbucket", ...]}}}
```
Read this directly rather than guessing which scope to add next -- it names the exact missing scope.

**Before the write commands above will work**, generate an Atlassian **API token with scopes** (not the plain "Create API token" button, which produces a Bitbucket-incompatible classic token) with the scopes needed for the operations you intend to use, then update your credentials file's `password` field. Run `check-credentials` (see below) first to confirm the file shape is valid before testing scope.

### ⚠️ App Passwords Are Being Retired

Atlassian has an active brownout/deprecation schedule for Bitbucket app passwords, ending in **full removal**. Before investing in a new app-password scope, check the current status at https://bitbucket.org/account/settings/app-passwords/ and Atlassian's Bitbucket Cloud deprecation announcements - **API tokens with scopes** (Atlassian account email + scoped API token, still Basic auth) are the forward-compatible replacement and should be used for any credential created or rotated from now on. The credential-loading code in this skill is auth-mechanism agnostic (Basic auth over `email:secret`), so switching from an app password to an API token is a drop-in credentials-file update, not a code change.

### `environment_type` casing: CONFIRMED

Bitbucket's create-environment endpoint is not in the official API reference, but empirically, **title case works**: `environment_type.name` of `"Test"`, `"Staging"`, or `"Production"` is accepted and echoed back correctly by a real `create-environment` call and subsequent `list-environments` reads. Upper-case (`"TEST"`, etc.) has not been tested and title case should be used.

### Secured variable values are write-only

Once a variable is created with `secured: true` (the default for `create-deploy-variable`), its `value` is never returned by any subsequent `GET`/`list-deploy-variables` call - this matches the Bitbucket web UI's behavior for secrets. `update-deploy-variable` can replace the value; there is no way to read it back via the API.

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

This skill enables a **REPL-like experience for DevOps**: your agent observes pipelines in real-time, analyzes failures instantly, suggests precise fixes, and iterates with you until builds pass - reducing debugging cycles from hours to minutes. This works the same in Claude Code, AGY, OpenCode, or any other runtime driving this skill.

**The Loop:**
1. **Read**: Monitor pipeline execution and capture failures
2. **Eval**: AI analyzes logs and identifies root cause
3. **Print**: The agent presents findings and suggests fixes
4. **Loop**: Apply fix, trigger build, repeat until green ✅

This transforms DevOps from slow batch processing into interactive, conversational development.

---

## Prerequisites

This skill uses a Bash-equivalent tool (auto-approved in Claude Code; check your runtime's docs for AGY/OpenCode/others) to run Node.js commands. Required:
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
  - Required permissions for existing (pipeline/PR/repo) commands: Repositories: Read, Pipelines: Read
  - Required permissions for the new deployment environment/variable commands: **Pipelines: Edit variables** at minimum, likely also **Repositories: Admin** for `create-environment` - see [Deployment Environments & Variables](#deployment-environments--variables-new). Not covered by the scope above - regenerate the app password to add write scopes before using those six commands.
  - Note: app passwords are being deprecated by Atlassian in favor of API tokens - check https://bitbucket.org/account/settings/app-passwords/ for current status before regenerating.

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
