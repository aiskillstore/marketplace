# Usage Patterns

Comprehensive guide to common DevOps workflows with the Bitbucket skill.

**Before starting:** Follow the three-tier fallback strategy (Tier 1 helpers → Tier 2 CLI → Tier 3 API). Start with Tier 1 helpers, fall back to Tier 2 CLI if needed, use Tier 3 API docs as last resort.

## Pattern 0: Detect Workspace and Repository (ALWAYS DO THIS FIRST)

**Before any pipeline operation**, determine the workspace and repository.

**Option 1: Auto-detect from git remote**
```bash
# Get git remote URL
git_url=$(git config --get remote.origin.url 2>/dev/null)

# Parse workspace and repo from: git@bitbucket.org:workspace/repo.git or https://bitbucket.org/workspace/repo.git
if [[ "$git_url" =~ bitbucket.org[:/]([^/]+)/([^/.]+) ]]; then
  WORKSPACE="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]}"
  echo "Detected: $WORKSPACE/$REPO"
fi
```

**Option 2: Check credentials file**
```bash
# Check configured workspace
cat ~/.claude/skills/bitbucket-devops/credentials.json | grep workspace
```

**Option 3: Ask user**
If auto-detection fails or user is asking about a different repo, ask:
- "What's your Bitbucket workspace?"
- "What's the repository name?"

**IMPORTANT:** Use the actual workspace/repo values in all subsequent commands. Never use literal strings `"workspace"` or `"repo"`.

---

## Pattern 1: Find Latest Failing Pipeline

**User Requests:**
- "What's the latest failing pipeline?"
- "Show me the most recent build failure"
- "Find the last failed pipeline"

**Steps:**
1. Use helper function to get latest failed pipeline
2. Extract and present key information

**Command:**
```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-latest-failed "workspace" "repo"
```

**Example Output:**
```json
{
  "build_number": 123,
  "state": { "name": "FAILED" },
  "target": {
    "ref_name": "main",
    "commit": {
      "hash": "abc123def",
      "message": "Fix bug in deployment"
    }
  },
  "created_on": "2025-11-02T10:30:00Z",
  "uuid": "{pipeline-uuid}"
}
```

**Present to User:**
```
Latest failed pipeline:
- Pipeline #123
- Branch: main
- Commit: abc123d - "Fix bug in deployment"
- Status: FAILED
- Started: 2025-11-02 10:30 UTC
```

---

## Pattern 2: Inspect Specific Pipeline by Number

**User Requests:**
- "Show me pipeline #34"
- "Get details for build 34"
- "What happened in pipeline 34?"

**Steps:**
1. Use helper to get pipeline by build number (auto-finds UUID)
2. Get detailed info including all steps
3. Present formatted output

**Commands:**
```bash
# Get pipeline by number
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-by-number "workspace" "repo" 34

# Get full info with steps
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-info "workspace" "repo" "{pipeline-uuid}"
```

**Example Output:**
```
Pipeline #34 Details:
- Status: FAILED
- Branch: main
- Commit: abc123d
- Duration: 5m 30s

Steps:
1. Build (step 1/5) - ✅ SUCCESSFUL (1m 20s)
2. Test (step 2/5) - ✅ SUCCESSFUL (2m 15s)
3. Deploy (step 3/5) - ❌ FAILED (30s)
4. Integration Tests (step 4/5) - ⏭️ SKIPPED
5. Cleanup (step 5/5) - ⏭️ SKIPPED
```

---

## Pattern 3: Identify Which Steps Failed

**User Requests:**
- "Which steps failed?"
- "What part of the build broke?"

**Steps:**
1. Get failed steps using helper function
2. Display step names, status, and duration

**Command:**
```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-failed-steps "workspace" "repo" "{pipeline-uuid}"
```

**Example Output:**
```
Failed Steps in Pipeline #34:

1. Deploy (step 3/5)
   - Status: FAILED
   - Duration: 30s

2. Integration Tests (step 4/5)
   - Status: ERROR
   - Duration: 2m 15s
```

---

## Pattern 4: Download Failing Steps Logs

**User Requests:**
- "Get logs for failed steps"
- "Download the logs"
- "Show me what went wrong"

**Steps:**
1. Use helper to download all failed step logs
2. Logs are saved to `.pipeline-logs/` in current directory
3. Present summary and file locations

**Command:**
```bash
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  download-failed-logs "workspace" "repo" "{pipeline-uuid}" 34
```

**Output:**
```json
[
  {
    "stepName": "Deploy",
    "stepUuid": "{step-uuid}",
    "logFilePath": "/path/to/project/.pipeline-logs/pipeline-34-Deploy.log",
    "size": 12450,
    "status": "FAILED"
  }
]
```

**Present to User:**
```
Downloaded logs for 2 failed steps:

1. Deploy
   - Saved to: .pipeline-logs/pipeline-34-Deploy.log
   - Size: 12.4 KB

2. Integration_Tests
   - Saved to: .pipeline-logs/pipeline-34-Integration_Tests.log
   - Size: 45.2 KB
```

**Important:** Check log file size before displaying. If > 50KB, show summary only:
```bash
# Check file size
ls -lh .pipeline-logs/pipeline-34-Deploy.log

# Show last 100 lines (most relevant errors)
tail -n 100 .pipeline-logs/pipeline-34-Deploy.log

# Or search for errors
grep -i "error\|failed\|exception" .pipeline-logs/pipeline-34-Deploy.log
```

---

## Pattern 5: Download Specific Step Logs

**User Requests:**
- "Get logs from the Deploy step"
- "Download logs from step 3"
- "Show me Deploy step logs"

**Steps:**
1. Get all pipeline steps
2. Find step by name or position
3. Download logs using CLI

**Commands:**
```bash
# Get all steps
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  get-pipeline-steps "workspace" "repo" "{pipeline-uuid}"

# Find step UUID (use jq or parse JSON in bash)
# Then download logs
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  get-step-logs "workspace" "repo" "{pipeline-uuid}" "{step-uuid}" \
  > .pipeline-logs/deploy-step.log
```

---

## Pattern 6: Analyze Large Logs

**User Requests:**
- "The log is too large"
- "Summarize the errors"
- Context window concerns

**Steps:**
1. Check log file size
2. Extract relevant portions (errors, warnings)
3. Present summary

**Commands:**
```bash
# Check size
size=$(wc -c < .pipeline-logs/pipeline-34-Deploy.log)
echo "Log size: $size bytes"

# Extract errors only
grep -i "error\|fatal\|exception" .pipeline-logs/pipeline-34-Deploy.log > .pipeline-logs/errors-only.txt

# Show last 200 lines (where failures typically occur)
tail -n 200 .pipeline-logs/pipeline-34-Deploy.log

# Count error types
grep -i "error" .pipeline-logs/pipeline-34-Deploy.log | sort | uniq -c | sort -nr
```

---

## Pattern 7: List Available Pipeline Types

**User Requests:**
- "What pipelines can I run?"
- "What can I trigger on this branch?"
- "What pipeline types exist?"

**Note:** Pipeline types are defined in `bitbucket-pipelines.yml` in the repository.

**Steps:**
1. Read bitbucket-pipelines.yml from repository root
2. Parse pipeline definitions (default, custom, branches)
3. List available options
4. Optionally get branching model for branch strategy

**Command to read pipeline config:**
```bash
# Use Read tool to read bitbucket-pipelines.yml
# Parse YAML for:
# - pipelines.default (runs on all branches)
# - pipelines.branches.* (branch-specific)
# - pipelines.custom.* (custom/manual pipelines)
# - pipelines.pull-requests.* (PR pipelines)
```

**For branching strategy only:**
```bash
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  get-branching-model "workspace" "repo"
```

**Present to User:**
```
Available Pipelines (from bitbucket-pipelines.yml):

Default Pipeline:
- Runs automatically on all branches

Custom Pipelines:
- deploy-production (manual trigger)
- deploy-staging (manual trigger)
- run-tests (manual trigger)

Branch-Specific:
- main: Production deployment pipeline
- develop: Development pipeline

To trigger a custom pipeline, use Pattern 8 with the pipeline name.
```

---

## Pattern 8: Trigger Pipeline Run

**User Requests:**
- "Run the pipeline on main"
- "Start pipeline X on branch Y"
- "Trigger deploy-production"

**Steps:**
1. Confirm with user: branch, pipeline type, variables
2. Use CLI to trigger pipeline
3. Display result with URL and build number
4. Optionally monitor progress (see Pattern 9)

**Command:**
```bash
# Trigger default pipeline
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  run-pipeline "workspace" "repo" "main"

# Trigger custom pipeline
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  run-pipeline "workspace" "repo" "main" "deploy-production"
```

**Example Output:**
```
Triggering Pipeline:
- Branch: main
- Pipeline: deploy-production
- Variables:
  - ENVIRONMENT=prod
  - DRY_RUN=false

✓ Pipeline started: #456
URL: https://bitbucket.org/workspace/repo/pipelines/results/456
Status: IN_PROGRESS
```

---

## Pattern 9: Monitor Running Pipeline

**User Requests:**
- "Monitor pipeline #456"
- "Watch the current build"
- "Is the build done yet?"
- "Track the pipeline progress"

**Steps:**
1. Get current pipeline status
2. Check if RUNNING/IN_PROGRESS
3. Show current step if running
4. Check again after delay if needed
5. Report when complete with final status

**Command:**
```bash
# Get current status
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-by-number "workspace" "repo" 456
```

**Parse Response:**
```json
{
  "state": {
    "name": "IN_PROGRESS",  // or "COMPLETED"
    "result": {
      "name": "SUCCESSFUL"  // Only when COMPLETED: SUCCESSFUL/FAILED/STOPPED
    }
  },
  "build_number": 456
}
```

**Present to User:**
```
Pipeline #456 Status:

Current State: IN_PROGRESS
Branch: main
Started: 5 minutes ago
Current Step: Deploy (step 3/5)

[Wait 30 seconds and check again...]

--- After completion ---
✓ Pipeline #456 COMPLETED
Result: SUCCESSFUL
Duration: 8m 32s
```

**Monitoring Loop:**
- If IN_PROGRESS: Wait 30-60 seconds, check again
- If COMPLETED: Report final result (SUCCESSFUL/FAILED/STOPPED)
- If FAILED: Offer to download logs (Pattern 4)

---

## Pattern 10: The DevOps REPL Loop (Full Debugging Workflow)

**User Requests:**
- "Fix the failing build"
- "Debug this pipeline and fix it"
- "Help me get this build green"
- "Why is my build failing?"

**This is the complete observe-analyze-fix loop that makes DevOps interactive:**

### 1. READ - Find and Analyze Failure

```bash
# Step 1a: Get latest failed pipeline
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-latest-failed "workspace" "repo"

# Step 1b: Get failed steps
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-failed-steps "workspace" "repo" "{pipeline-uuid}"

# Step 1c: Download failed logs
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  download-failed-logs "workspace" "repo" "{pipeline-uuid}" <build-number>
```

### 2. EVAL - Analyze the Logs

```bash
# Extract errors from logs
grep -i "error\|failed\|exception\|fatal" .pipeline-logs/*.log

# Show context around errors (5 lines before/after)
grep -i -A 5 -B 5 "error" .pipeline-logs/pipeline-*.log

# Analyze the error:
# - What type of error? (compilation, test failure, deployment, etc.)
# - What file/line number?
# - What's the root cause?
```

### 3. PRINT - Suggest Fix

Present findings to user:
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

### 4. LOOP - Apply Fix and Re-Test

```bash
# If user approves:
# Step 4a: Apply fix using Edit tool
# Edit src/auth/service.ts and make the change

# Step 4b: Optionally commit
git add src/auth/service.ts
git commit -m "Fix: Update User property reference from userId to id"

# Step 4c: Trigger new pipeline run
node ~/.claude/skills/bitbucket-devops/bitbucket-mcp/dist/index-cli.js \
  run-pipeline "workspace" "repo" "branch-name"

# Step 4d: Monitor the new build (Pattern 9)
node ~/.claude/skills/bitbucket-devops/lib/helpers.js \
  get-by-number "workspace" "repo" <new-build-number>
```

### 5. REPEAT or CELEBRATE

- If new build FAILS: Go back to step 1 (READ) with new logs
- If new build SUCCEEDS: ✅ Success! Build is green
- If new build IN_PROGRESS: Monitor (Pattern 9)

**Key Points:**
- **Stay in the loop** until build passes
- **Learn from patterns** across iterations
- **Keep user informed** at each step
- **Ask permission** before making code changes
- **Track progress** - "Attempt 1 failed, trying fix 2..."

**This transforms hours of manual debugging into minutes of AI-assisted iteration.**

---

## Log Storage

Logs are downloaded to `.pipeline-logs/` in the directory where VSCode is opened (your working directory).

**Path:** `.pipeline-logs/` relative to `process.cwd()` when commands execute

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

## Best Practices

1. **Always confirm workspace/repo**: Auto-detect from git or ask user:
   ```bash
   git config --get remote.origin.url
   # Parse: git@bitbucket.org:workspace/repo.git
   ```

2. **Check pipeline status before logs**: Don't request logs for running pipelines

3. **Limit initial results**: Start with 10 recent pipelines, increase if needed

4. **Smart log filtering**: Use grep to find errors first:
   ```bash
   grep -n "ERROR\|FATAL\|Exception" logfile.log
   ```

5. **Cache results**: Store JSON responses in variables to avoid redundant calls

6. **Use helper functions**: Prefer helpers.js functions for common operations

---

## Workspace Detection

Auto-detect repository information:

```bash
# Get git remote URL
git_url=$(git config --get remote.origin.url 2>/dev/null)

# Parse workspace and repo from: git@bitbucket.org:workspace/repo.git
if [[ "$git_url" =~ bitbucket.org[:/]([^/]+)/([^/.]+) ]]; then
  workspace="${BASH_REMATCH[1]}"
  repo_slug="${BASH_REMATCH[2]}"
  echo "Detected: $workspace/$repo_slug"
fi
```

---

## Configuration Variables

Default values (can be adjusted per request):

- **Max Pipeline Limit**: 50 (for searching by build number)
- **Recent Pipeline Limit**: 10 (for listing)
- **Log Directory**: `.pipeline-logs/` (relative to cwd)
- **Large Log Threshold**: 50KB (when to summarize)
