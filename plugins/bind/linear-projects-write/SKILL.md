---
name: linear-projects-write
description: Create and update Linear projects via CLI (write operations)
version: 1.0.0
license: MIT
compatibility: opencode
---

## Overview

CLI tools for creating and updating Linear projects. Requires `LINEAR_API_KEY` set in `<git-root>/.env` or exported in the environment.

## Prerequisites

- [bun](https://bun.sh) runtime installed
- `LINEAR_API_KEY` set in `<git-root>/.env` or environment

## Commands

### Create Project

```bash
bun .opencode/skill/linear-projects-write/create-project.js --name "..." --teams <teams> [options]
```

**Required:**
- `--name <name>` - Project name
- `--teams <teams>` - Comma-separated team names (e.g., "Engineering,Product")

**Options:**
- `--description <text>` - Project description
- `--lead <name>` - Project lead name
- `--status <status>` - Initial status (planned, started, paused, completed, canceled)
- `--start-date <date>` - Start date (YYYY-MM-DD)
- `--target-date <date>` - Target date (YYYY-MM-DD)
- `--priority <0-4>` - Priority: 0=none, 1=urgent, 2=high, 3=normal, 4=low
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-projects-write/create-project.js --name "New Feature" --teams Engineering
bun .opencode/skill/linear-projects-write/create-project.js --name "Q1 Initiative" --teams "Engineering,Product" --lead "James Monroe"
bun .opencode/skill/linear-projects-write/create-project.js --name "Security Audit" --teams Engineering --start-date 2025-01-15 --target-date 2025-03-01
```

---

### Update Project

```bash
bun .opencode/skill/linear-projects-write/update-project.js <project-id-or-name> [options]
```

**Arguments:**
- `project-id-or-name` - Project UUID or name (partial match supported)

**Options:**
- `--name <name>` - New project name
- `--description <text>` - New description
- `--lead <name>` - New project lead (use "none" to remove)
- `--status <status>` - New status
- `--start-date <date>` - New start date (YYYY-MM-DD)
- `--target-date <date>` - New target date (YYYY-MM-DD)
- `--priority <0-4>` - New priority
- `--json` - Output as JSON

**Examples:**
```bash
bun .opencode/skill/linear-projects-write/update-project.js "Mount Vernon" --status completed
bun .opencode/skill/linear-projects-write/update-project.js "Monticello" --lead "John Quincy Adams" --target-date 2025-03-01
bun .opencode/skill/linear-projects-write/update-project.js "Old Project" --name "Hermitage"
```

---

## Notes

- Project names support partial matching (case-insensitive)
- User names are resolved automatically
- Use `--json` flag for machine-readable output
- All commands support `--help` for detailed usage information
