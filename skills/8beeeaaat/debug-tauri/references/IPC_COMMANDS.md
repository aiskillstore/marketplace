# Tauri IPC Commands Reference

## Table of Contents

- Console Log Collection
- WebView State Capture
- Debug Commands
- Screenshot Commands (Deprecated)

## Console Log Collection

### Method A: Official Plugin (Recommended)

Use `tauri-plugin-log` for automatic console collection with persistence:

```typescript
import { logger } from "tauri-plugin-debug-tools/logAdapter";

// Initialize once at app startup
const detach = await logger.initialize();

// All console.* calls are auto-forwarded
logger.info("App started");
logger.error("Something went wrong");
```

**Log Locations**:

- **macOS**: `~/Library/Logs/{bundle_id}/debug.log`
- **Linux**: `~/.local/share/{bundle_id}/logs/debug.log`
- **Windows**: `{LOCALAPPDATA}\{bundle_id}\logs\debug.log`

**Analysis**:

```bash
./scripts/analyze_logs.sh
```

### Method B: Via debugBridge API (Legacy)

If using custom `consoleLogger` implementation:

```typescript
import { getConsoleLogs, getConsoleErrors } from "tauri-plugin-debug-tools/debugBridge";

const allLogs = getConsoleLogs();
const errors = getConsoleErrors();
```

**Deprecated**: Migrate to Method A (official plugin) for persistence and cross-platform support.

### Method C: Via IPC Command (Not Recommended)

```typescript
import { invoke } from "@tauri-apps/api/core";

const logs = await invoke("plugin:debug-tools|get_console_logs");
```

**Note**: Returns empty array. Use Method A (official plugin) instead.

**Fallback**: Only ask user for logs if all automated methods fail.

## WebView State Capture

### capture_webview_state

Retrieves WebView internal state as JSON.

**TypeScript:**

```typescript
import { captureWebViewState } from "tauri-plugin-debug-tools/debugBridge";

const state = await captureWebViewState();
console.log(state);
```

**Response:**

```json
{
  "url": "http://localhost:5173",
  "title": "iori",
  "user_agent": "TauriWebView/2.0",
  "viewport": {
    "width": 1200,
    "height": 800
  }
}
```

## Debug Commands

### send_debug_command

Send debug commands to WebView (event-based).

**Usage:**

```typescript
import { sendDebugCommand } from "tauri-plugin-debug-tools/debugBridge";

await sendDebugCommand("get_gpu_state", { includeBuffers: true });
```

## Screenshot Commands (Deprecated)

### take_screenshot

**Status**: Deprecated. Use system `screencapture` command instead.

**Error message:**

```
Use system screencapture command instead.
Run: screencapture -x -T 0 /tmp/tauri_screenshot.png
```

See [SCREENSHOTS.md](SCREENSHOTS.md) for screenshot capture methods.

## WebGPU Debug API (Planned - Phase 4)

### captureWebGPUState()

Comprehensive WebGPU state capture.

**Returns:**

```typescript
{
  deviceInfo: GPUAdapterInfo,
  bufferStats: {
    particleBuffer: { size: number, usage: number },
    uniformBuffer: { size: number, usage: number },
  },
  computeResults: Float32Array,
  performanceMetrics: {
    fps: number,
    frameTime: number,
    memoryUsage: number
  }
}
```

### getDeviceInfo()

Retrieve GPU device information.

```typescript
const info = await getDeviceInfo();
// { vendor: "Apple", architecture: "..." }
```

### exportComputeResults()

Export Compute Shader results to CPU.

```typescript
const results = await exportComputeResults();
// Float32Array(100000) - particle position data
```

### getPerformanceMetrics()

Retrieve performance metrics.

```typescript
const metrics = await getPerformanceMetrics();
// { fps: 60, frameTime: 16.67, memoryUsage: 197 }
```

## Process Information

### Check Running Tauri Process

```bash
ps aux | grep <app-binary-name> | grep -v grep
```

**Example output:**

```
user  94678  1.6  0.3  440546784  197920 s011  S+   11:47AM   0:12.85 target/debug/<app-binary-name>
```

### Process Details

```bash
ps -p 94678 -o pid,vsz,rss,%cpu,%mem,command
```

## References

- [Tauri IPC Commands](https://v2.tauri.app/develop/calling-rust/)
- [tauri-plugin-debug-tools repository](https://github.com/your-org/tauri-plugin-debug-tools)
