# Troubleshooting Guide

## Common Errors

### "Main window not found"

**Cause**: Main window is not launched or has different label name.

**Solution:**

1. Verify app is running: `ps aux | grep <app-binary-name>`
2. Check `tauri.conf.json` has `windows.label` set to "main"
3. Start app if not running: `tauri dev`

### "Process not found"

**Cause**: Target process is not running.

**Solution:**

```bash
# Start app from project root
tauri dev

# Or for production build
./target/release/<app-binary-name>
```

**Verify process:**

```bash
TAURI_APP_NAME=<your-app> scripts/capture.sh
```

### Screenshot Capture Fails

**Cause**: macOS privacy settings deny screen recording.

**Solution:**

1. System Preferences > Security & Privacy > Privacy
2. Select "Screen Recording"
3. Add Terminal (or IDE) to allowed list
4. Restart terminal/IDE

**Quick check:**

```bash
scripts/validate_setup.sh
```

### Console Logs Empty

**Cause**: Frontend logger not initialized or logs not being captured.

**Solutions:**

**Option 1**: Ensure frontend logger is initialized

```typescript
import { initConsoleLogger } from "tauri-plugin-debug-tools/consoleLogger";

initConsoleLogger();
```

**Option 2**: Check log file exists

```bash
ls -lh /tmp/tauri_console_logs_*.jsonl
```

**Option 3**: Use IPC method

```typescript
const logs = await invoke("plugin:debug-tools|get_console_logs");
```

### WebView State Returns Null

**Cause**: WebView not fully initialized or permissions issue.

**Solutions:**

1. Wait for WebView ready event
2. Verify debug permissions in `capabilities/default.json`
3. Check Tauri version compatibility (requires v2.0+)

### Permission Denied Errors

**Cause**: Missing debug permissions in app capabilities.

**Solution:**

Add to `src-tauri/capabilities/default.json`:

```json
{
  "permissions": [
    "debug-tools:allow-capture-webview-state",
    "debug-tools:allow-get-console-logs",
    "debug-tools:allow-send-debug-command"
  ]
}
```

## Validation Checklist

Run this before debugging:

```bash
scripts/validate_setup.sh
```

Manual checks:

- [ ] App is running (verify with `ps aux | grep <app-name>`)
- [ ] Screen recording permission granted (macOS)
- [ ] Debug permissions enabled in capabilities
- [ ] Frontend logger initialized (if using log collection)
- [ ] Tauri version >= 2.0

## Getting Help

If issues persist:

1. Check plugin version compatibility
2. Review Tauri logs: `tauri dev --verbose`
3. Validate setup: `scripts/validate_setup.sh`
4. Consult [Tauri documentation](https://v2.tauri.app)

## File Path References

**Debug command implementation:**

- `src-tauri/src/commands/debug.rs` (if exists)

**Frontend bridge:**

- `src/lib/debugBridge.ts` (recommended location)

**Log output:**

- `/tmp/tauri_console_logs_[app_name]_[pid].jsonl`
- `/tmp/tauri_debug_*.png` (screenshots)
