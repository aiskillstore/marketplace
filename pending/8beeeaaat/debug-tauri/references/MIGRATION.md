# Migration Guide: Official Plugins Integration

Complete guide for migrating from custom implementations to official Tauri plugins.

## Overview

This migration replaces:

- **Custom `consoleLogger.ts`** → `tauri-plugin-log` (official)
- **OS-dependent `screencapture` commands** → `tauri-plugin-screenshots`
- **macOS-only support** → **Cross-platform** (macOS, Windows, Linux)

## Migration Strategy

### Recommended Approach: Parallel Deployment

1. **Add official plugins alongside existing implementation**
2. **Test in development environment**
3. **Gradually switch to plugin APIs**
4. **Remove custom implementation after validation**

### Complete Migration Timeline

- **v0.2.0**: Logging plugin added (parallel with consoleLogger)
- **v0.3.0**: Screenshots plugin added
- **v0.4.0**: Custom implementation removed
- **v1.0.0**: Full cross-platform validation

## Phase 1: Logging Migration

### Before (Custom Implementation)

```typescript
// guest-js/consoleLogger.ts
import { invoke } from "@tauri-apps/api/core";

export async function appendDebugLogs(message: string): Promise<void> {
  await invoke("plugin:debug-tools|append_debug_logs", { message });
}

export async function getConsoleLogs(): Promise<string[]> {
  return await invoke("plugin:debug-tools|get_console_logs");
}

// Usage
await appendDebugLogs("App started");
const logs = await getConsoleLogs();
```

### After (Official Plugin)

```typescript
// guest-js/logAdapter.ts
import { logger } from "tauri-plugin-debug-tools/logAdapter";

// Initialize once at app startup
const detach = await logger.initialize();

// Usage
logger.info("App started");

// Logs automatically saved to platform-specific location
// No need to manually retrieve logs
```

### Key Changes

| Aspect | Custom | Official Plugin |
|--------|---------|-----------------|
| **Setup** | No initialization required | Requires `attachConsole()` call |
| **Storage** | In-memory array | File-based with auto-rotation |
| **Retrieval** | Manual `getConsoleLogs()` | Direct file access |
| **Levels** | Single log level | trace/debug/info/warn/error |
| **Persistence** | Lost on app restart | Persistent across restarts |
| **Cross-platform** | No | Yes (macOS/Windows/Linux) |

### Migration Steps

#### 1. Add Dependencies

**Cargo.toml**:

```toml
[dependencies]
tauri-plugin-log = "2.0"
```

**package.json**:

```json
{
  "dependencies": {
    "@tauri-apps/plugin-log": "^2.0.0"
  }
}
```

#### 2. Initialize Plugin (src/lib.rs)

```rust
use tauri_plugin_log::{Target, TargetKind};

pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("debug-tools")
        .setup(|app, _api| {
            app.handle().plugin(
                tauri_plugin_log::Builder::new()
                    .targets([
                        Target::new(TargetKind::Stdout),
                        Target::new(TargetKind::LogDir {
                            file_name: Some("debug.log".to_string())
                        }),
                        Target::new(TargetKind::Webview),
                    ])
                    .max_file_size(50_000)
                    .build()
            )?;
            Ok(())
        })
        .build()
}
```

#### 3. Update Frontend Code

**Replace**:

```typescript
import { appendDebugLogs } from "tauri-plugin-debug-tools/consoleLogger";
await appendDebugLogs("Message");
```

**With**:

```typescript
import { logger } from "tauri-plugin-debug-tools/logAdapter";
logger.info("Message");
```

#### 4. Update Permissions

**Before** (`permissions/default.toml`):

```toml
permissions = [
  "allow-append-debug-logs",
  "allow-get-console-logs",
]
```

**After** (`permissions/debug-with-logging.toml`):

```toml
permissions = [
  "core:default",
  "log:default",
]
```

#### 5. Update Log Retrieval

**Before**:

```typescript
const logs = await getConsoleLogs();
console.log(logs.join("\n"));
```

**After**:

```bash
# Read from platform-specific location
cat ~/Library/Logs/{bundle_id}/debug.log  # macOS
```

Or use `analyze_logs.sh` script:

```bash
./scripts/analyze_logs.sh
```

## Phase 2: Screenshot Migration

### Before (macOS screencapture)

```bash
# scripts/capture.sh
screencapture -x -T 0 "$output_path"
```

**Limitations**:

- macOS only
- Requires Screen Recording permission
- Shell script dependency

### After (Official Plugin)

```typescript
// guest-js/screenshotHelper.ts
import { captureMainWindow } from "tauri-plugin-debug-tools/screenshotHelper";

const imagePath = await captureMainWindow();
// Returns base64 PNG data
```

**Benefits**:

- Cross-platform (macOS/Windows/Linux)
- No external dependencies
- Programmatic access from TypeScript

### Migration Steps

#### 1. Add Dependencies

**Cargo.toml**:

```toml
[dependencies]
tauri-plugin-screenshots = "2.0"
```

**package.json**:

```json
{
  "dependencies": {
    "tauri-plugin-screenshots-api": "^2.0.0"
  }
}
```

#### 2. Initialize Plugin (src/lib.rs)

```rust
pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("debug-tools")
        .setup(|app, _api| {
            app.handle().plugin(tauri_plugin_screenshots::init())?;
            Ok(())
        })
        .build()
}
```

#### 3. Update Frontend Code

**Replace**:

```bash
TAURI_APP_NAME=myapp ./scripts/capture.sh
```

**With**:

```typescript
import { captureMainWindow } from "tauri-plugin-debug-tools/screenshotHelper";

const screenshot = await captureMainWindow();
if (screenshot) {
  // screenshot is base64 PNG data
  console.log("Screenshot captured");
}
```

#### 4. Update Permissions

Add to capabilities:

```json
{
  "permissions": [
    "screenshots:default"
  ]
}
```

## Common Migration Patterns

### Pattern 1: App Initialization

**Before**:

```typescript
// No special initialization
```

**After**:

```typescript
import { logger } from "tauri-plugin-debug-tools/logAdapter";

async function initializeApp() {
  const detach = await logger.initialize();

  logger.info("App initialized");

  // Store detach function for cleanup
  window.addEventListener("beforeunload", () => detach());
}
```

### Pattern 2: Error Logging

**Before**:

```typescript
import { appendDebugLogs } from "./consoleLogger";

try {
  await riskyOperation();
} catch (error) {
  await appendDebugLogs(`Error: ${error.message}`);
}
```

**After**:

```typescript
import { logger } from "tauri-plugin-debug-tools/logAdapter";

try {
  await riskyOperation();
} catch (error) {
  logger.error(`Error: ${error.message}`);
}
```

### Pattern 3: Debug Snapshot

**Before**:

```typescript
import { writeDebugSnapshot } from "./debugBridge";

const logs = await getConsoleLogs();
await writeDebugSnapshot({
  timestamp: new Date().toISOString(),
  logs,
});
```

**After**:

```typescript
// Logs already persisted to file
// Use writeDebugSnapshot for additional metadata only
import { writeDebugSnapshot } from "./debugBridge";

await writeDebugSnapshot({
  timestamp: new Date().toISOString(),
  // No need to include logs - already in debug.log
});
```

## Rollback Strategy

If migration causes issues, follow these steps:

### 1. Keep Old Implementation

Do not delete `consoleLogger.ts` until full validation:

```typescript
// Temporarily support both
import { logger as newLogger } from "./logAdapter";
import { appendDebugLogs as oldLogger } from "./consoleLogger";

// Use feature flag
const useOfficialPlugin = import.meta.env.VITE_USE_OFFICIAL_LOG === "true";

export const logger = useOfficialPlugin ? newLogger : {
  info: (msg) => oldLogger(msg),
  error: (msg) => oldLogger(`ERROR: ${msg}`),
  // ... other levels
};
```

### 2. Gradual Feature Flag Rollout

```typescript
// Enable for specific environments
const ENABLE_OFFICIAL_PLUGINS = {
  development: true,
  staging: true,
  production: false, // Keep false until validated
};

const usePlugins = ENABLE_OFFICIAL_PLUGINS[import.meta.env.MODE];
```

### 3. Monitoring & Validation

Before removing old implementation:

- [ ] Verify logs appear in expected platform-specific locations
- [ ] Confirm log rotation works (create 50KB+ logs)
- [ ] Test screenshot capture on all target platforms
- [ ] Validate permissions configuration
- [ ] Check error handling for plugin initialization failures

## Breaking Changes

### Log Format

**Before**: Plain strings in array

```json
["2024-01-01 12:00:00 - Message 1", "2024-01-01 12:00:01 - Message 2"]
```

**After**: Structured log lines in file

```
2024-01-01T12:00:00.123Z INFO  app_name: Message 1
2024-01-01T12:00:01.456Z ERROR app_name: Message 2
```

### Log Access

**Before**: Synchronous in-memory access

```typescript
const logs = await getConsoleLogs(); // Returns immediately
```

**After**: File system access required

```typescript
// Read from filesystem
import { readTextFile } from "@tauri-apps/plugin-fs";
import { appLogDir } from "@tauri-apps/api/path";

const logDir = await appLogDir();
const logs = await readTextFile(`${logDir}/debug.log`);
```

## Platform-Specific Considerations

### macOS

- **Log Location**: `~/Library/Logs/{bundle_id}/debug.log`
- **Permissions**: No special permissions required for logging
- **Screenshots**: Works without Screen Recording permission (captures own windows)

### Windows

- **Log Location**: `%LOCALAPPDATA%\{bundle_id}\logs\debug.log`
- **Permissions**: Standard file write permissions
- **Screenshots**: Works with standard permissions

### Linux

- **Log Location**: `~/.local/share/{bundle_id}/logs/debug.log`
- **Permissions**: Standard file write permissions
- **Screenshots**: May require Wayland/X11 specific permissions

## Validation Checklist

Before marking migration complete:

- [ ] Official plugins added to Cargo.toml and package.json
- [ ] Plugins initialized in src/lib.rs
- [ ] Permissions updated in capabilities
- [ ] Frontend code updated to use new APIs
- [ ] Log files created in correct platform-specific locations
- [ ] Log rotation tested (50KB threshold)
- [ ] Screenshots work on all target platforms
- [ ] Error handling tested (plugin init failures)
- [ ] Documentation updated
- [ ] Old implementation removed (or feature-flagged)

## Support

For migration issues:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common problems
2. Review [LOGGING.md](LOGGING.md) for plugin configuration details
3. See [SCREENSHOTS.md](SCREENSHOTS.md) for screenshot API usage
4. Open issue on GitHub repository with migration context

## References

- [tauri-plugin-log Documentation](https://v2.tauri.app/plugin/logging/)
- [tauri-plugin-screenshots Repository](https://github.com/ayangweb/tauri-plugin-screenshots)
- [Migration Plan](../../../../.claude/plans/shiny-knitting-squirrel.md)
