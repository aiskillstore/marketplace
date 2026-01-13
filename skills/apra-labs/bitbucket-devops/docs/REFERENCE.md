# Command Reference

Complete reference for all Bitbucket DevOps Skill commands.

## Tier 1: High-Level Helper Functions

**Purpose:** Solve common workflows in a single command.
**Location:** `~/.claude/skills/bitbucket-devops/lib/helpers.js`
**Usage:** `node ~/.claude/skills/bitbucket-devops/lib/helpers.js <command> <args>`

### Pipeline Helpers

#### get-latest-failed
Get the most recent failed pipeline for a repository.

```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-latest-failed <workspace> <repo>
```

**Returns:** Full pipeline object with UUID, build number, state, target branch, creator, etc.

**Use when:** User asks "what's the latest failed pipeline", "show me the last build that failed"

---

#### get-latest
Get the most recent pipeline (any status) for a repository.

```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-latest <workspace> <repo>
```

**Returns:** Full pipeline object with UUID, build number, state, etc.

**Use when:** User asks "what's the latest pipeline", "show me the last build"

---

#### get-by-number
Find a specific pipeline by its build number.

```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-by-number <workspace> <repo> <build-number>
```

**Parameters:**
- `build-number`: Sequential build number (e.g., 60, 123)

**Returns:** Full pipeline object including UUID.

**Use when:** User references a specific build number like "pipeline #60", "build 123"

---

#### get-failed-steps
Get all failed steps from a pipeline.

```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-failed-steps <workspace> <repo> <pipeline-uuid>
```

**Parameters:**
- `pipeline-uuid`: Pipeline UUID in format `{abc-123...}`

**Returns:** Array of failed step objects with names, UUIDs, and status.

**Use when:** User asks "what steps failed", "which parts of the build failed"

---

#### download-failed-logs
Download logs from all failed steps and save to `.pipeline-logs/` directory.

```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js download-failed-logs <workspace> <repo> <pipeline-uuid> <build-number>
```

**Parameters:**
- `pipeline-uuid`: Pipeline UUID
- `build-number`: Build number for log file naming

**Returns:** Array of objects with step info and log file paths.

**Creates files:** `.pipeline-logs/pipeline-<build>-<step-name>.log`

**Use when:** User asks "download the logs", "save the failed step logs"

---

#### get-info
Get formatted pipeline information including all steps.

```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-info <workspace> <repo> <pipeline-uuid>
```

**Returns:** Structured object with pipeline details and all steps (failed, successful, pending).

**Use when:** User asks for comprehensive pipeline overview.

---

### Git Operation Helpers

#### test-git-auth
Test git authentication to a repository.

```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js test-git-auth <workspace> <repo>
```

**Returns:** Success status and HEAD commit hash if successful.

---

#### clone-repo
Clone a repository to local directory.

```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js clone-repo <workspace> <repo> [target-dir]
```

**Parameters:**
- `target-dir`: Optional target directory (defaults to repo name)

**Returns:** Success status and directory path.

---

## Tier 2: Low-Level CLI Commands

**Purpose:** Direct API wrappers for specific operations.
**Location:** `~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js`
**Usage:** `node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js <command> <args>`

### Pipeline Operations

#### list-pipelines
List recent pipelines for a repository (raw API response).

```bash
list-pipelines <workspace> <repo> [limit] [status]
```

**Parameters:**
- `limit`: Number of pipelines to return (default: 10)
- `status`: Filter by status (SUCCESSFUL, FAILED, IN_PROGRESS, etc.)

**Returns:** Paginated list of pipeline objects.

---

#### get-pipeline
Get a specific pipeline by UUID or build number.

```bash
get-pipeline <workspace> <repo> <build_number_or_uuid>
```

**Smart Identifier:** Accepts either build number (60) or UUID ({abc...})

**Returns:** Complete pipeline object.

---

#### get-pipeline-steps
Get all steps for a pipeline.

```bash
get-pipeline-steps <workspace> <repo> <build_number_or_uuid>
```

**Smart Identifier:** Accepts either build number (60) or UUID ({abc...})

**Returns:** Paginated list of step objects with setup/script commands.

---

#### get-step-logs
Get complete logs for a specific step.

```bash
get-step-logs <workspace> <repo> <build_number_or_uuid> <step_uuid>
```

**Parameters:**
- `step_uuid`: Step UUID from get-pipeline-steps

**Returns:** Plain text log output.

---

#### tail-step-log
Get the tail (last N bytes) of a step's log.

```bash
tail-step-log <workspace> <repo> <build_number_or_uuid> <step_uuid> [bytes]
```

**Parameters:**
- `bytes`: Number of bytes to fetch (default: 2000)

**Returns:** Plain text log output (tail only).

**Use when:** Checking status of running step without downloading entire log.

---

#### run-pipeline
Trigger a new pipeline run.

```bash
run-pipeline <workspace> <repo> <branch> [custom_pipeline_name] [variables_json]
```

**Parameters:**
- `branch`: Branch to run pipeline on
- `custom_pipeline_name`: Optional pipeline name from bitbucket-pipelines.yml
- `variables_json`: Optional JSON string of variables

**Example with variables:**
```bash
run-pipeline workspace repo main deploy '{"ENV":"production","VERSION":"1.2.3"}'
```

**Returns:** New pipeline object with UUID and build number.

---

#### stop-pipeline
Stop a running pipeline.

```bash
stop-pipeline <workspace> <repo> <build_number_or_uuid>
```

**Smart Identifier:** Accepts either build number (60) or UUID ({abc...})

**Returns:** Updated pipeline object with STOPPED state.

---

### Pull Request Operations

#### list-prs
List pull requests for a repository.

```bash
list-prs <workspace> <repo> [state] [limit]
```

**Parameters:**
- `state`: OPEN, MERGED, DECLINED, SUPERSEDED (default: OPEN)
- `limit`: Number of PRs to return

**Returns:** Paginated list of PR objects.

---

#### get-pr
Get details for a specific pull request.

```bash
get-pr <workspace> <repo> <pr_id>
```

**Returns:** Complete PR object with comments, reviewers, etc.

---

#### approve-pr
Approve a pull request.

```bash
approve-pr <workspace> <repo> <pr_id>
```

**Returns:** Approval object.

---

#### merge-pr
Merge a pull request.

```bash
merge-pr <workspace> <repo> <pr_id> [message] [strategy]
```

**Parameters:**
- `message`: Optional commit message
- `strategy`: merge-commit (default), squash, or fast-forward

**Returns:** Merged PR object.

---

#### decline-pr
Decline/close a pull request.

```bash
decline-pr <workspace> <repo> <pr_id> [message]
```

**Parameters:**
- `message`: Optional reason for declining

**Returns:** Declined PR object.

---

### Repository Operations

#### list-repositories
List all repositories in a workspace.

```bash
list-repositories <workspace> [limit]
```

**Returns:** Paginated list of repository objects.

---

#### get-repo
Get details for a specific repository.

```bash
get-repo <workspace> <repo>
```

**Returns:** Complete repository object.

---

#### get-branching-model
Get the branching model/strategy for a repository.

```bash
get-branching-model <workspace> <repo>
```

**Returns:** Branching model configuration with branch types and prefixes.

**Use when:** Need to know available pipeline types, branch naming conventions.

---

## Tier 3: Direct API Calls

**Purpose:** Access Bitbucket API directly when no helper or CLI command exists.
**Usage:** Only as last resort after verifying Tier 1 & 2 cannot solve the request.

### Prerequisites

1. Read API documentation from `~/.claude/skills/bitbucket-devops/docs/bitbucket-api/`
2. Load credentials from skill configuration
3. Construct proper API endpoint URL

### Available Documentation

- `bitbucket-cloud-api-v2.0-swagger.json` - Complete OpenAPI spec
- `bitbucket-cloud-api-openapi3.yml` - OpenAPI 3.0 format

### Authentication

Use credentials from skill configuration:
```bash
curl -u "user_email:password" https://api.bitbucket.org/2.0/...
```

**Note:** `user_email` is your Bitbucket account email, not username.

---

## Smart Pipeline Identifiers

All pipeline commands (Tier 2) accept either:
- **Build Number:** `60` (auto-converts to UUID)
- **UUID:** `{63bac81c-165b-41bd-bc58-26445567a332}`

When you provide a build number, the CLI:
1. Detects it's a number
2. Searches recent 100 pipelines
3. Finds the matching UUID
4. Shows: `🔍 Detected build number 60, looking up UUID...`
5. Uses the UUID for the API call

This eliminates the common "400 Bad Request" error from passing build numbers where UUIDs are expected.

---

## Command Chaining Examples

### Example 1: Download Specific Step Logs
```bash
# Get pipeline UUID
pipeline=$(node ~/.claude/skills/bitbucket-devops/lib/helpers.js get-by-number "workspace" "repo" 123)
uuid=$(echo "$pipeline" | jq -r '.uuid')

# Get steps
steps=$(node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js get-pipeline-steps "workspace" "repo" "$uuid")
step_uuid=$(echo "$steps" | jq -r '.values[] | select(.name=="Deploy") | .uuid')

# Download logs
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js get-step-logs "workspace" "repo" "$uuid" "$step_uuid" > .pipeline-logs/deploy.log
```

### Example 2: Monitor Running Pipeline
```bash
# Trigger pipeline
result=$(node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js run-pipeline "workspace" "repo" "main")
uuid=$(echo "$result" | jq -r '.uuid')

# Check status periodically
while true; do
  status=$(node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js get-pipeline "workspace" "repo" "$uuid" | jq -r '.state.name')
  echo "Status: $status"
  [[ "$status" == "COMPLETED" ]] && break
  sleep 30
done
```

---

## Notes

- All commands output JSON (except log commands which output plain text)
- Use `jq` for parsing JSON responses in bash
- Pipeline UUIDs contain curly braces: `{abc-123...}` (CLI handles encoding)
- Build numbers are sequential integers: 1, 2, 3, ... 60, ...
- Workspace is typically same as username for personal repos
