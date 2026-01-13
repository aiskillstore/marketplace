---
name: linear-milestones-write
description: Create and update Linear project milestones via CLI (write operations)
version: 1.0.0
license: MIT
compatibility: opencode
---

## Overview

CLI tools for creating and updating Linear project milestones. Requires `LINEAR_API_KEY` set in `<git-root>/.env` or exported in the environment.

## Prerequisites

- [bun](https://bun.sh) runtime installed
- `LINEAR_API_KEY` set in `<git-root>/.env` or environment

## Commands

### Create Milestone

```bash
bun .opencode/skill/linear-milestones-write/create-milestone.js --name "..." --project "..." [options]
```

**Required:**
- `--name <name>` - Milestone name
- `--project <name>` - Project name or UUID

**Options:**
- `--description <text>` - Milestone description
- `--target-date <date>` - Target date (YYYY-MM-DD)
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-milestones-write/create-milestone.js --name "Alpha Release" --project "Mount Vernon"
bun .opencode/skill/linear-milestones-write/create-milestone.js --name "Beta" --project "Monticello" --target-date 2025-02-01
bun .opencode/skill/linear-milestones-write/create-milestone.js --name "GA" --project "Hermitage" --description "General availability release"
```

---

### Update Milestone

```bash
bun .opencode/skill/linear-milestones-write/update-milestone.js <milestone-id> [options]
```

**Arguments:**
- `milestone-id` - Milestone UUID

**Options:**
- `--name <name>` - New milestone name
- `--description <text>` - New description
- `--target-date <date>` - New target date (YYYY-MM-DD)
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-milestones-write/update-milestone.js abc123 --name "Beta Release"
bun .opencode/skill/linear-milestones-write/update-milestone.js abc123 --target-date 2025-03-15
bun .opencode/skill/linear-milestones-write/update-milestone.js abc123 --name "v1.0" --target-date 2025-04-01
```

---

## Notes

- Project names support partial matching (case-insensitive)
- Milestone IDs are UUIDs (use `list-milestones.js` to find them)
- Use `--json` flag for machine-readable output
- All commands support `--help` for detailed usage information
