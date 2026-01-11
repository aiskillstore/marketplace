---
name: linear-milestones-read
description: List Linear project milestones via CLI (read-only operations)
version: 1.0.0
license: MIT
compatibility: opencode
---

## Overview

CLI tools for reading Linear project milestones. Requires `LINEAR_API_KEY` set in `<git-root>/.env` or exported in the environment.

## Prerequisites

- [bun](https://bun.sh) runtime installed
- `LINEAR_API_KEY` set in `<git-root>/.env` or environment

## Commands

### List Milestones

```bash
bun .opencode/skill/linear-milestones-read/list-milestones.js [options]
```

**Options:**
- `--project <name>` - Filter by project name (required unless using --all)
- `--all` - List milestones across all projects
- `--limit <n>` - Max results (default: 25)
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-milestones-read/list-milestones.js --project "Mount Vernon"
bun .opencode/skill/linear-milestones-read/list-milestones.js --all --limit 10
bun .opencode/skill/linear-milestones-read/list-milestones.js --project "Monticello" --json
```

---

## Output Behavior

- Command output is displayed directly to the user in the terminal
- **Do not re-summarize or reformat table output** - the user can already see it
- Only provide additional commentary if the user explicitly requests analysis, filtering, or summarization
- When using `--json` output with tools like `jq`, the processed results are already visible to the user

## Notes

- Project names support partial matching (case-insensitive)
