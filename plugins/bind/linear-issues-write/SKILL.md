---
name: linear-issues-write
description: Create and update Linear issues via CLI (write operations)
version: 1.0.0
license: MIT
compatibility: opencode
---

## Overview

CLI tools for creating and updating Linear issues. Requires `LINEAR_API_KEY` set in `<git-root>/.env` or exported in the environment.

## Prerequisites

- [bun](https://bun.sh) runtime installed
- `LINEAR_API_KEY` set in `<git-root>/.env` or environment

## Commands

### Create Issue

```bash
bun .opencode/skill/linear-issues-write/create-issue.js --title "..." --team <team> [options]
```

**Required:**
- `--title <title>` - Issue title
- `--team <name>` - Team name (e.g., Engineering)

**Options:**
- `--description <text>` - Issue description
- `--assignee <name>` - Assignee name
- `--priority <0-4>` - Priority: 0=none, 1=urgent, 2=high, 3=medium, 4=low
- `--labels <labels>` - Comma-separated labels (e.g., "Bug,SOC2")
- `--project <name>` - Project name
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-issues-write/create-issue.js --title "Fix login bug" --team Engineering --priority 2
bun .opencode/skill/linear-issues-write/create-issue.js --title "New feature" --team Engineering --labels "Feature" --assignee "John Adams"
bun .opencode/skill/linear-issues-write/create-issue.js --title "Security fix" --team Engineering --project "Monticello" --priority 1
```

---

### Update Issue

```bash
bun .opencode/skill/linear-issues-write/update-issue.js <issue-id> [options]
```

**Arguments:**
- `issue-id` - Issue identifier (e.g., ENG-123) or UUID

**Options:**
- `--title <title>` - New title
- `--description <text>` - New description
- `--status <status>` - New status (e.g., "In Progress", "Done")
- `--assignee <name>` - New assignee (use "none" to unassign)
- `--priority <0-4>` - New priority
- `--labels <labels>` - Replace all labels
- `--add-labels <labels>` - Add labels without removing existing
- `--project <name>` - Set project (use "none" to remove)
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-issues-write/update-issue.js ENG-123 --status "In Progress"
bun .opencode/skill/linear-issues-write/update-issue.js ENG-123 --assignee "Thomas Jefferson" --priority 2
bun .opencode/skill/linear-issues-write/update-issue.js ENG-123 --add-labels "Bug,Urgent"
bun .opencode/skill/linear-issues-write/update-issue.js ENG-123 --assignee none
```

---

## Notes

- Team, user, and label names are resolved automatically (case-insensitive)
- Use `--json` flag for machine-readable output suitable for scripting
- All commands support `--help` for detailed usage information
