---
name: alan-review-pr
version: 1.0.0
description: Review a GitHub pull request using Alan's GitHub MCP tools
---

## MANDATORY: Use Alan MCP Tools

The Alan MCP server provides GitHub tools that are ALREADY in your tool list.
They work exactly like Read, Bash, Edit — you call them as tool invocations.
They are named with the prefix `mcp__alan__github_`.

**Authentication is handled automatically by the MCP server.** You do NOT need
GitHub tokens, gh CLI auth, SSH keys, .netrc files, environment variables, or
any credentials. The tools work immediately with zero setup.

### NEVER do any of the following for GitHub API access:
- `curl` or `wget` to api.github.com
- `gh` CLI commands (gh pr, gh api, etc.)
- `env | grep` or scanning for tokens/secrets
- `cat ~/.netrc`, `git credential`, or `ssh -T git@github.com`
- Any attempt to find, construct, or configure GitHub authentication
- Installing packages or CLIs for GitHub access

If an MCP tool call fails, report the error to the user. Do NOT fall back to
CLI alternatives.

### Verify tools are available

Before starting, confirm you can see `mcp__alan__github_*` tools in your
available tools. If they are NOT available, STOP and tell the user:
"The GitHub MCP tools are not available. Please check the sandbox MCP configuration."

### Tool parameters

All GitHub PR tools require these parameters:
- `owner` (string): GitHub org or username, e.g. "supatest-ai"
- `repo` (string): Repository name, e.g. "alan"
- `prNumber` (integer): PR number, e.g. 42

Example tool call:
```
Tool: mcp__alan__github_get_pull_request
Parameters: { "owner": "supatest-ai", "repo": "alan", "prNumber": 42 }
```

### Resolving owner/repo

If the user only provides a PR number, run `git remote get-url origin` to get
the remote URL, then parse owner and repo from it. This is the ONLY git CLI
command you should run for GitHub operations. Everything else uses MCP tools.

### Available GitHub MCP tools

| Tool name | Purpose |
|-----------|---------|
| `mcp__alan__github_get_pull_request` | Get PR details (title, state, labels, merge status) |
| `mcp__alan__github_get_pr_diff` | Get unified diff of a PR |
| `mcp__alan__github_list_pr_comments` | List all comments on a PR |
| `mcp__alan__github_list_pr_reviews` | List all reviews on a PR |
| `mcp__alan__github_list_pr_files` | List changed files with additions/deletions |
| `mcp__alan__github_get_issue` | Get issue details |
| `mcp__alan__github_get_ci_status` | Get CI check run status for a ref |
| `mcp__alan__github_add_comment` | Add a comment to an issue or PR |
| `mcp__alan__github_create_pr_review` | Submit a review (APPROVE/REQUEST_CHANGES/COMMENT) |
| `mcp__alan__github_add_labels` | Add labels to an issue or PR |
| `mcp__alan__github_merge_pull_request` | Merge a PR |
| `mcp__alan__github_close_issue` | Close an issue or PR |
| `mcp__alan__github_request_reviewers` | Request reviewers on a PR |

---

## Task: Review a Pull Request

### Input

The user will provide one of:
- A PR number (e.g. "42" or "#42")
- A PR URL (e.g. "https://github.com/owner/repo/pull/42")
- A reference like "owner/repo#42"

### Workflow

1. **Resolve owner/repo/prNumber** from the input. If only a PR number is given,
   run `git remote get-url origin` to parse owner and repo.

2. **Fetch PR metadata** — call `mcp__alan__github_get_pull_request` with
   `{ owner, repo, prNumber }` to get title, description, state, labels, branches.

3. **Fetch the diff** — call `mcp__alan__github_get_pr_diff` to get the unified diff.

4. **Fetch changed files** — call `mcp__alan__github_list_pr_files` to see
   files modified/added/deleted with line counts.

5. **Fetch existing reviews** — call `mcp__alan__github_list_pr_reviews` to see
   prior review state.

6. **Fetch existing comments** — call `mcp__alan__github_list_pr_comments` for
   ongoing discussion context.

7. **Check CI status** — call `mcp__alan__github_get_ci_status` with the head
   branch or SHA. If a check failed, include the html_url link so the user can
   view full logs (the tool does not return log output).

8. **Read source files** — for complex changes, use the Read tool to read full
   source files (not just the diff) for context.

9. **Analyze** — identify issues INTRODUCED by this PR only (not pre-existing).
   For each finding, determine: severity, file path, start/end line, title,
   description, and a concrete fix prompt for agents.

10. **Post review** — call `mcp__alan__github_create_pr_review` with inline
    comments (one per finding) plus a summary body. See formats below.

### Review Dimensions (priority order)

1. **Security** — injection, auth bypass, secrets in code, input validation
2. **Correctness** — logic errors, null handling, async issues, race conditions
3. **Performance** — N+1 queries, unbounded operations, memory issues
4. **Error Handling** — silent failures, empty catch blocks, swallowed errors
5. **Maintainability** — functions >30 lines, deep nesting, magic numbers
6. **Test Coverage** — happy path tested? edge cases? meaningful assertions?

### Confidence Filter

Only include findings where:
- You can point to exact file + line
- You can describe a concrete scenario where it causes a real problem
- Confidence >= 80%

Skip: linter-catchable issues, speculative risks, style preferences, pre-existing problems.

### Inline Comment Format

Each finding becomes its own inline comment on the PR. Format the `body` of each comment like this:

```markdown
<!-- alan-review-comment {"id": "alan_review_{prNumber}_{sequential_4digit}", "file_path": "{path}", "start_line": {start}, "end_line": {end}, "side": "RIGHT"} -->

{severity_icon} **{short_title}**

{detailed_description}

<details>
<summary>Prompt for agents</summary>

\`\`\`
{concrete_fix_instructions_an_AI_agent_can_execute — specify exact file, what to change, and how}
\`\`\`

</details>

<!-- alan-review-badge-begin -->
<a href="{alan_session_url}" target="_blank">
  <img src="https://app.tryalan.ai/logo.png" alt="Open in Alan" height="20">
</a>
<!-- alan-review-badge-end -->
```

**Severity icons:**
- 🔴 = Blocking (critical bugs, security, data loss — must fix before merge)
- 🟡 = Important (real bugs/risks — should fix before merge)
- 🔵 = Nit (minor quality issues — fix if easy)

### Summary Comment Format

The `body` parameter of the review (top-level summary) should be:

```markdown
**Alan Review** found {N} potential issues.

| Severity | Count |
|----------|-------|
| 🔴 Blocking | {X} |
| 🟡 Important | {Y} |
| 🔵 Nit | {Z} |

<details>
<summary>View all findings</summary>

### 🔴 Blocking
- **{title}** — \`{file_path}:{line}\` — {one_line_description}

### 🟡 Important
- **{title}** — \`{file_path}:{line}\` — {one_line_description}

### 🔵 Nit
- **{title}** — \`{file_path}:{line}\` — {one_line_description}

</details>

<!-- alan-review-badge-begin -->
<a href="{alan_session_url}" target="_blank">
  <img src="https://app.tryalan.ai/logo.png" alt="Open in Alan" height="20">
</a>
<!-- alan-review-badge-end -->

---
*Was this helpful? React with 👍 or 👎 to provide feedback.*
```

### "Open in Alan" Badge URL

Every badge links to the current Alan session. The user/trigger will provide the
session URL. Replace `{alan_session_url}` in every badge with the actual URL.

If no session URL is provided, fall back to `https://app.tryalan.ai`.

### Posting the Review

Call `mcp__alan__github_create_pr_review` with:
- `owner`, `repo`, `prNumber`: from step 1
- `body`: the summary comment above
- `event`: "REQUEST_CHANGES" if any 🔴 blocking findings, otherwise "COMMENT"
- `comments`: array of inline comments, each with:
  - `path`: relative file path from repo root
  - `line`: the end line number of the finding
  - `body`: the formatted inline comment body above

**IMPORTANT:**
- Always post inline comments (one per finding) — do NOT bundle into one big comment
- Always include the "Prompt for agents" section in every finding
- Always include the "Open in Alan" badge on every comment and the summary
- Replace `{alan_session_url}` with the actual session URL in every badge
- If zero findings, post an approving review with a clean summary
