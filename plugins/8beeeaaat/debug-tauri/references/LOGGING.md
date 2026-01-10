# Logging with tauri-plugin-log

Official Tauri logging plugin integration for automatic console collection and structured logging.

## Quick Start

```typescript
import { logger } from "tauri-plugin-debug-tools/logAdapter";

// Initialize once at app startup
const detach = await logger.initialize();

// Use structured logging
logger.trace("Detailed trace information");
logger.debug("Debug information");
logger.info("Informational message");
logger.warn("Warning message");
logger.error("Error occurred");

// Cleanup on app shutdown (optional)
detach();
```

## Configuration

Plugin is pre-configured in `src/lib.rs` with the following settings:

```rust
tauri_plugin_log::Builder::new()
    .targets([
        Target::new(TargetKind::Stdout),           // Console output
        Target::new(TargetKind::LogDir {
            file_name: Some("debug.log".to_string())
        }),                                         // File logging
        Target::new(TargetKind::Webview),          // WebView console
    ])
    .max_file_size(50_000)                         // 50KB auto-rotation
    .build()
```

## Log File Locations

Platform-specific paths where logs are automatically saved:

### macOS

```
~/Library/Logs/{bundle_identifier}/debug.log
```

Example: `~/Library/Logs/com.example.myapp/debug.log`

### Linux

```
~/.local/share/{bundle_identifier}/logs/debug.log
```

Example: `~/.local/share/com.example.myapp/logs/debug.log`

### Windows

```
{FOLDERID_LocalAppData}\{bundle_identifier}\logs\debug.log
```

Example: `C:\Users\Username\AppData\Local\com.example.myapp\logs\debug.log`

## Log Levels

Available log levels in order of severity:

1. **TRACE**: Most detailed information (e.g., function entry/exit)
2. **DEBUG**: Diagnostic information useful during development
3. **INFO**: General informational messages about app operation
4. **WARN**: Warning messages for potentially problematic situations
5. **ERROR**: Error messages for failures that don't stop the app

## Automatic Console Forwarding

The `attachConsole()` method automatically forwards all `console.*` calls to the plugin:

```typescript
await logger.initialize();

// These are now logged to file AND console
console.log("This is logged");      // → INFO level
console.warn("Warning");             // → WARN level
console.error("Error");              // → ERROR level
```

## File Rotation

Logs automatically rotate when reaching 50KB size:

- Current log: `debug.log`
- Rotated logs: `debug.log.1`, `debug.log.2`, etc.
- Old logs are preserved for historical analysis

## Reading Logs

### Via analyze_logs.sh Script

```bash
# Analyze logs with pattern detection
./scripts/analyze_logs.sh

# Custom log file path
./scripts/analyze_logs.sh /path/to/debug.log
```

### Manual Reading

```bash
# macOS
cat ~/Library/Logs/com.example.myapp/debug.log

# Linux
cat ~/.local/share/com.example.myapp/logs/debug.log

# Windows (PowerShell)
Get-Content $env:LOCALAPPDATA\com.example.myapp\logs\debug.log
```

## Troubleshooting

### Logs Not Being Created

1. **Check initialization**: Ensure `logger.initialize()` is called at app startup
2. **Verify permissions**: `log:default` must be enabled in app capabilities
3. **Check bundle ID**: Confirm correct bundle identifier in `tauri.conf.json`

### Empty Log Files

1. **No console output**: Call `logger.info()` or other methods to generate logs
2. **Console not attached**: Verify `attachConsole()` was awaited successfully
3. **Permission denied**: Check file system permissions for log directory

### Cannot Find Log Files

```bash
# Use environment variable to locate logs
echo $HOME/Library/Logs/{bundle_id}/debug.log  # macOS
echo $HOME/.local/share/{bundle_id}/logs/debug.log  # Linux
echo $env:LOCALAPPDATA\{bundle_id}\logs\debug.log  # Windows
```

## Advanced Usage

### Custom Log Targets

To modify logging targets, edit `src/lib.rs`:

```rust
use tauri_plugin_log::{Target, TargetKind};

// Add custom target
.targets([
    Target::new(TargetKind::Stdout),
    Target::new(TargetKind::LogDir {
        file_name: Some("custom.log".to_string())
    }),
    // Add more targets as needed
])
```

### Log Filtering

Filter logs by level in Rust backend:

```rust
.level(log::LevelFilter::Debug)  // Only DEBUG and above
```

### Programmatic Log Access

Access logs via filesystem APIs:

```typescript
import { readTextFile } from "@tauri-apps/plugin-fs";
import { appLogDir } from "@tauri-apps/api/path";

const logDir = await appLogDir();
const logContent = await readTextFile(`${logDir}/debug.log`);
```

## Migration from Custom Logger

See [MIGRATION.md](MIGRATION.md) for complete migration guide from `consoleLogger.ts`.

## References

- [Official tauri-plugin-log Documentation](https://v2.tauri.app/plugin/logging/)
- [Rust log crate Documentation](https://docs.rs/log/latest/log/)
- [analyze_logs.sh Script](../scripts/analyze_logs.sh)
