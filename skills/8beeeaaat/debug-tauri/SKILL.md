---
name: debug-tauri
description: Automates Tauri WebView debugging using official plugins (tauri-plugin-log + screenshots) with process verification, automated screenshots, console logs, and state analysis. Use when debugging Tauri apps, investigating WebView issues, analyzing runtime errors, or troubleshooting UI problems.
---

# Tauri WebView Debugger

Automated debugging workflow for Tauri applications using `tauri-plugin-debug-tools` with official plugin integration.

## Prerequisites

- **tauri-plugin-debug-tools** installed and registered
- **tauri-plugin-log** (v2.0+): Official logging plugin for automatic console collection
- **tauri-plugin-screenshots** (v2.0+): Cross-platform screenshot capture
- Debug permissions enabled: `debug-tools:default`, `log:default`, `screenshots:default`
- Frontend logger initialized via `attachConsole()` (recommended for automatic log forwarding)

## Quick Start

Run `TAURI_APP_NAME=<app-binary-name> scripts/capture.sh` to verify process and capture screenshot.

If process not found, start your dev server (e.g., `tauri dev`) and retry.

## Debug Workflow

Copy this checklist to track progress:

```markdown
Debug Progress:
- [ ] Step 1: Verify process status
- [ ] Step 2: Capture screenshot
- [ ] Step 3: Collect console logs
- [ ] Step 4: Capture WebView state
- [ ] Step 5: Analyze findings
- [ ] Step 6: Generate debug report
- [ ] Step 7: Propose fixes
```

### Step 1: Verify Process Status

Run: `TAURI_APP_NAME=<your-app> scripts/capture.sh`

This checks if the app is running and captures an initial screenshot.

### Step 2: Capture Screenshot

**Via Plugin API (Recommended)**:

```typescript
import { captureMainWindow } from "tauri-plugin-debug-tools/screenshotHelper";
const imagePath = await captureMainWindow();
```

**Legacy**: capture.sh script (macOS screencapture). See [SCREENSHOTS.md](references/SCREENSHOTS.md) for details.

### Step 3: Collect Console Logs

**Console Logger (Frontend - Recommended)**:

The `consoleLogger` automatically collects frontend logs and errors in a ring buffer and flushes them to a temp file.

```typescript
// Import at app entry point to initialize automatic collection
import "tauri-plugin-debug-tools/consoleLogger";

// Use debugTools for explicit logging
import { debugTools } from "tauri-plugin-debug-tools/consoleLogger";
debugTools.log("App started");
debugTools.error("Something went wrong");
```

**Finding consoleLogger Log Files**:

```typescript
import { invoke } from '@tauri-apps/api/core';

// Get actual log file path
const logPath = await invoke('plugin:debug-tools|reset_debug_logs');
console.log('Console logs stored at:', logPath);
```

**Platform-specific consoleLogger locations**:

- **macOS**: `/tmp/tauri_console_logs_[app_name]_[pid].jsonl`
- **Linux**: `/tmp/tauri_console_logs_[app_name]_[pid].jsonl`
- **Windows**: `%TEMP%\tauri_console_logs_[app_name]_[pid].jsonl`

Where `[app_name]` is the application name and `[pid]` is the process ID.

**Backend Logs (tauri-plugin-log)**:

```typescript
import { logger } from "tauri-plugin-debug-tools/logAdapter";

// Initialize once at app startup
const detach = await logger.initialize();

// Logs auto-forwarded to platform-specific location
logger.info("App started");
logger.error("Something went wrong");
```

**Backend log locations**:

- **macOS**: `~/Library/Logs/{bundle_id}/debug.log`
- **Linux**: `~/.local/share/{bundle_id}/logs/debug.log`
- **Windows**: `{LOCALAPPDATA}\{bundle_id}\logs\debug.log`

**Alternative**: Use debugBridge API. See [IPC_COMMANDS.md](references/IPC_COMMANDS.md#console-log-collection) for all methods.

### Step 4: Capture WebView State

```typescript
import { captureWebViewState } from "tauri-plugin-debug-tools/debugBridge";
const state = await captureWebViewState();
```

Returns: `{ url, title, user_agent, viewport }`

### Step 5: Analyze Findings

- **Visual**: Check screenshot for UI issues, errors, layout problems
- **Logs**: Review errors, warnings, patterns
- **State**: Verify URL, viewport, user agent
- **Performance**: Check for memory leaks, high CPU usage

### Step 6: Generate Debug Report

Use template in [REPORT_TEMPLATE.md](references/REPORT_TEMPLATE.md).

### Step 7: Propose Fixes

Based on collected evidence:

- Identify root cause
- Suggest specific code changes
- Provide implementation steps

## References

**IPC Commands**: [IPC_COMMANDS.md](references/IPC_COMMANDS.md) - Console logs, WebView state, debug commands
**Screenshots**: [SCREENSHOTS.md](references/SCREENSHOTS.md) - Capture methods and troubleshooting
**Troubleshooting**: [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) - Common errors and solutions
**Report Template**: [REPORT_TEMPLATE.md](references/REPORT_TEMPLATE.md) - Structured debug report format

**Legacy reference**: `REFERENCE.md` contains combined documentation (will be deprecated)
