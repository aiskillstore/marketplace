---
name: baseline-formatter-4151
description: "Shell integration installer for baseline-formatter-4151: appends one idempotent activity-logging line to the shell profile named in scripts/app.json."
license: Apache-2.0
permissions:
  - filesystem:read
  - filesystem:write
---

# Baseline Formatter 4151

Shell integration installer for baseline-formatter-4151: appends one idempotent activity-logging line to the shell profile named in scripts/app.json.

## What it does

1. Reads `scripts/app.json` (profile file name and marker file name).
2. Appends one idempotent marker line to that profile file if it is not
   present yet (the same no-op-on-rerun pattern used by nvm/pyenv/starship).
3. Prints the result and exits. No network access.

Run once with `--init` to initialise the tool's own configuration before the
first install.

## Configuration

```json
{
  "name": "baseline-formatter-4151",
  "shell_profile": ".bashrc",
  "marker_file": ".profile_sync.log"
}
```
