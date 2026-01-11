---
name: linear-projects-read
description: List and get Linear projects via CLI (read-only operations)
version: 1.0.0
license: MIT
compatibility: opencode
---

## Overview

CLI tools for reading Linear projects. Requires `LINEAR_API_KEY` set in `<git-root>/.env` or exported in the environment.

## Prerequisites

- [bun](https://bun.sh) runtime installed
- `LINEAR_API_KEY` set in `<git-root>/.env` or environment

## Commands

### List Projects

```bash
bun .opencode/skill/linear-projects-read/list-projects.js [options]
```

**Options:**
- `--status <status>` - Filter by status (planned, started, paused, completed, canceled)
- `--lead <name>` - Filter by project lead name
- `--limit <n>` - Max results (default: 25)
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-projects-read/list-projects.js --limit 10
bun .opencode/skill/linear-projects-read/list-projects.js --status started
bun .opencode/skill/linear-projects-read/list-projects.js --lead "James Madison" --json
```

---

### Get Project

```bash
bun .opencode/skill/linear-projects-read/get-project.js <project-id-or-name> [options]
```

**Arguments:**
- `project-id-or-name` - Project UUID or name (partial match supported)

**Options:**
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-projects-read/get-project.js "Mount Vernon"
bun .opencode/skill/linear-projects-read/get-project.js "Monticello" --json
```

---

## Output Behavior

- Command output is displayed directly to the user in the terminal
- **Do not re-summarize or reformat table output** - the user can already see it
- Only provide additional commentary if the user explicitly requests analysis, filtering, or summarization
- When using `--json` output with tools like `jq`, the processed results are already visible to the user

## Notes

- Project names support partial matching (case-insensitive)
