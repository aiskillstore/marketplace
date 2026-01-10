# Screenshot Capture Reference

## Official Plugin (Recommended)

Use `tauri-plugin-screenshots` for cross-platform screenshot capture.

### Quick Start

```typescript
import { captureMainWindow } from "tauri-plugin-debug-tools/screenshotHelper";

// Capture main window as base64 PNG
const screenshot = await captureMainWindow();
if (screenshot) {
  console.log("Screenshot captured successfully");
}
```

### Available Methods

#### captureMainWindow()

Captures the first available window.

```typescript
import { captureMainWindow } from "tauri-plugin-debug-tools/screenshotHelper";

const imagePath = await captureMainWindow();
```

**Returns**: `string | null` - Base64 PNG data or null if no windows

#### captureAllWindows()

Captures all application windows.

```typescript
import { captureAllWindows } from "tauri-plugin-debug-tools/screenshotHelper";

const screenshots = await captureAllWindows();
```

**Returns**: `string[]` - Array of base64 PNG data

#### capturePrimaryMonitor()

Captures the primary display.

```typescript
import { capturePrimaryMonitor } from "tauri-plugin-debug-tools/screenshotHelper";

const monitorScreenshot = await capturePrimaryMonitor();
```

**Returns**: `string | null` - Base64 PNG data or null if no monitors

### Advanced Usage

```typescript
import {
  getScreenshotableWindows,
  getWindowScreenshot,
  getScreenshotableMonitors,
  getMonitorScreenshot,
} from "tauri-plugin-screenshots-api";

// List available windows
const windows = await getScreenshotableWindows();
console.log(windows); // [{ id: 1, title: "My App" }, ...]

// Capture specific window
const screenshot = await getWindowScreenshot(windows[0].id);

// List available monitors
const monitors = await getScreenshotableMonitors();

// Capture specific monitor
const monitorShot = await getMonitorScreenshot(monitors[0].id);
```

### Platform Support

- ✅ **macOS**: Full support
- ✅ **Windows**: Full support
- ✅ **Linux**: Full support (X11/Wayland)

### Permissions

Add to app capabilities:

```json
{
  "permissions": ["screenshots:default"]
}
```

## Legacy: macOS screencapture Command

### Full Screen Capture

```bash
screencapture -x -T 0 /tmp/screenshot.png
```

**Options:**

- `-x`: Disable sound
- `-T <seconds>`: Delay time (0 = execute immediately)

### Window Selection (Interactive)

```bash
screencapture -w /tmp/window_screenshot.png
```

User clicks to select the window.

### Specific Process Window by ID

```bash
# Get window ID
osascript -e 'tell application "System Events" to get unix id of first process whose name is "<app-binary-name>"'

# Capture by ID
screencapture -l <window-id> /tmp/tauri_window.png
```

### Automated Capture (Legacy)

**Deprecated**: Use official plugin API instead.

Legacy script for macOS only:

```bash
TAURI_APP_NAME=<your-app> scripts/capture.sh
```

This script:

1. Verifies the app is running
2. Captures a timestamped screenshot
3. Returns the screenshot path

**Migration**: Replace with `captureMainWindow()` from plugin API for cross-platform support.

## Troubleshooting

### Error: Screenshot Not Captured

**Cause**: macOS privacy settings deny screen recording permission.

**Solution:**

1. System Preferences > Security & Privacy > Privacy
2. Select "Screen Recording"
3. Add Terminal (or execution source) to allowed list

### Permission Check

Run validation script:

```bash
scripts/validate_setup.sh
```

This checks screen recording permissions and other debug requirements.

## Legacy: Platform-Specific CLI Tools

**Deprecated**: Use official plugin API for unified cross-platform support.

### Linux (Legacy)

```bash
# Using scrot
scrot /tmp/screenshot.png

# Using gnome-screenshot
gnome-screenshot -f /tmp/screenshot.png
```

### Windows (Legacy)

```powershell
# Using PowerShell
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("{PRTSC}")
```

## References

- [tauri-plugin-screenshots Repository](https://github.com/ayangweb/tauri-plugin-screenshots)
- [macOS screencapture man page](https://ss64.com/osx/screencapture.html) (legacy)
