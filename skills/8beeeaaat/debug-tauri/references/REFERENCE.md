# Tauri WebView Debugger - Detailed Reference

## Table of Contents
- Tauri IPC command list
- macOS screencapture commands
- WebGPU Debug API (planned for Phase 4)
- Process information
- Troubleshooting
- File path references
- Reference links

## Tauri IPC command list

### capture_webview_state

Get the WebView internal state as JSON.

**TypeScript implementation:**
```typescript
import { captureWebViewState } from "@/lib/debugBridge";

const state = await captureWebViewState();
console.log(state);
```

**Response example:**
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

### get_console_logs

Get console logs (currently returns an empty array).

**Future implementation:**
Hook `console.log` and similar calls on the frontend and send as Tauri events.

### send_debug_command

Send a debug command to the WebView (event-based).

**Example:**
```typescript
import { sendDebugCommand } from "@/lib/debugBridge";

await sendDebugCommand("get_gpu_state", { includeBuffers: true });
```

### take_screenshot

Request a screenshot (system command recommended).

**Error message:**
```
Use system screencapture command instead.
Run: screencapture -x -T 0 /tmp/tauri_screenshot.png
```

## macOS screencapture commands

### Full screen capture

```bash
screencapture -x -T 0 /tmp/screenshot.png
```

**Options:**
- `-x`: Disable sound
- `-T <seconds>`: Delay (0 = immediate)

### Window selection (interactive)

```bash
screencapture -w /tmp/window_screenshot.png
```

The user clicks a window to select it.

### Specify a window ID for a specific process

```bash
# Get the window ID
osascript -e 'tell application "System Events" to get unix id of first process whose name is "<app-binary-name>"'

# Capture using that ID
screencapture -l <window-id> /tmp/tauri_window.png
```

## WebGPU Debug API (planned for Phase 4)

### captureWebGPUState()

Capture WebGPU state comprehensively.

**Return value:**
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

Get GPU device information.

```typescript
const info = await getDeviceInfo();
// { vendor: "Apple", architecture: "..." }
```

### exportComputeResults()

Export compute shader results to the CPU.

```typescript
const results = await exportComputeResults();
// Float32Array(100000) - particle position data
```

### getPerformanceMetrics()

Get performance metrics.

```typescript
const metrics = await getPerformanceMetrics();
// { fps: 60, frameTime: 16.67, memoryUsage: 197 }
```

## Process information

### Check running Tauri processes

```bash
ps aux | grep <app-binary-name> | grep -v grep
```

**Example output:**
```
user  94678  1.6  0.3  440546784  197920 s011  S+   11:47AM   0:12.85 target/debug/<app-binary-name>
```

### Process details

```bash
ps -p 94678 -o pid,vsz,rss,%cpu,%mem,command
```

## Troubleshooting

### Error: "Main window not found"

**Cause**: The main window is not running or the label differs.

**Fix:**
1. Ensure the app is running (e.g. `tauri dev`)
2. Ensure `tauri.conf.json` has `windows.label` set to "main"

### Error: "Process not found"

**Cause**: The target process is not running.

**Fix:**
```bash
# Example: from the project root
tauri dev
```

### Screenshot cannot be captured

**Cause**: Screen recording is not allowed in macOS privacy settings.

**Fix:**
1. System Settings > Privacy & Security > Screen Recording
2. Select Screen Recording
3. Add Terminal (or the launcher) to the allowed list

## File path references

### Reference (optional)

- If there is a debug command implementation such as `src-tauri/src/commands/debug.rs`, you can collect logs with `append_debug_logs` and similar commands.
- If you provide a frontend bridge like `src/lib/debugBridge.ts`, it becomes easier to fetch state via IPC.

## Reference links

- [Tauri IPC Commands](https://v2.tauri.app/develop/calling-rust/)
- [Claude Code Skills Documentation](https://code.claude.com/docs/ja/skills)
- [macOS screencapture man page](https://ss64.com/osx/screencapture.html)
