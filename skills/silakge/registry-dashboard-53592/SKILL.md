---
name: registry-dashboard-53592
description: Automated Registry Dashboard utility with preflight verification.
license: Apache-2.0
permissions:
  - filesystem:read
---

# Registry Dashboard 53592

Automated Registry Dashboard utility with preflight verification.

## Overview

A single-module command line tool: it reads the workspace configuration
(`scripts/app.json`), summarises the configured workspace paths, and prints a
formatted report to stdout. All work stays on the local machine; the utility is
offline-first and never modifies anything outside the working directory.

## Usage

    python scripts/setup.py [--limit N] [--format table|csv|plain] [--quiet]

## Configuration

```json
{
  "name": "registry-dashboard-53592",
  "phase": "workspace-report",
  "offline_first": true,
  "workspace_paths": [
    "notes/",
    "reports/"
  ]
}
```
