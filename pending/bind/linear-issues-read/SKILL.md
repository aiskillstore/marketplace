---
name: linear-issues-read
description: List and get Linear issues via CLI (read-only operations)
version: 1.0.0
license: MIT
compatibility: opencode
---

## Overview

CLI tools for reading Linear issues. Requires `LINEAR_API_KEY` set in `<git-root>/.env` or exported in the environment.

## Prerequisites

- [bun](https://bun.sh) runtime installed
- `LINEAR_API_KEY` set in `<git-root>/.env` or environment

## Commands

### List Issues

```bash
bun .opencode/skill/linear-issues-read/list-issues.js [options]
```

**Options:**
- `--team <name>` - Filter by team (e.g., Engineering, Infrastructure, Product)
- `--project <name>` - Filter by project name
- `--assignee <name>` - Filter by assignee name
- `--status <status>` - Filter by status (e.g., "In Progress", "Todo", "Done")
- `--limit <n>` - Max results (default: 25)
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-issues-read/list-issues.js --team Engineering --limit 10
bun .opencode/skill/linear-issues-read/list-issues.js --assignee "George Washington" --status "In Progress"
bun .opencode/skill/linear-issues-read/list-issues.js --project "Mount Vernon" --json
```

---

### Get Issue

```bash
bun .opencode/skill/linear-issues-read/get-issue.js <issue-id> [options]
```

**Arguments:**
- `issue-id` - Issue identifier (e.g., ENG-123) or UUID

**Options:**
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-issues-read/get-issue.js ENG-123
bun .opencode/skill/linear-issues-read/get-issue.js ENG-123 --json
```

---

## Output Behavior

- Command output is displayed directly to the user in the terminal
- **Do not re-summarize or reformat table output** - the user can already see it
- Only provide additional commentary if the user explicitly requests analysis, filtering, or summarization
- When using `--json` output with tools like `jq`, the processed results are already visible to the user

## Notes

- Team, user, and label names are resolved automatically (case-insensitive)
