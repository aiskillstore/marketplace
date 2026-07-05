#!/bin/bash
# Tauri app screenshot helper script (DEPRECATED)
# Usage: ./capture.sh
#
# ⚠️  DEPRECATED: This script is legacy and macOS-only.
#
# 💡 Migrate to official plugin API:
#    import { captureMainWindow } from "tauri-plugin-debug-tools/screenshotHelper";
#    const screenshot = await captureMainWindow();
#
# Benefits of plugin API:
#   - Cross-platform (macOS/Windows/Linux)
#   - No screen recording permissions required
#   - Programmatic access from TypeScript
#   - Base64 PNG data returned directly

APP_NAME="${TAURI_APP_NAME:-tauri-app}"
OUTPUT_DIR="/tmp"

# Show deprecation warning
echo "⚠️  WARNING: This script is deprecated"
echo "═══════════════════════════════════════"
echo ""
echo "This legacy script only works on macOS and requires Screen Recording permissions."
echo ""
echo "💡 Recommended: Use the official tauri-plugin-screenshots API instead:"
echo ""
echo "   import { captureMainWindow } from 'tauri-plugin-debug-tools/screenshotHelper';"
echo "   const screenshot = await captureMainWindow();"
echo ""
echo "Benefits:"
echo "  ✅ Cross-platform (macOS/Windows/Linux)"
echo "  ✅ No special permissions required"
echo "  ✅ Programmatic access from TypeScript"
echo ""
echo "Press Enter to continue with legacy script, or Ctrl+C to cancel..."
read -r
echo ""

function check_app_running() {
  if ! pgrep -x "$APP_NAME" > /dev/null; then
    echo "❌ Error: $APP_NAME is not running"
    echo "💡 Start the app with your dev command (e.g., tauri dev)"
    exit 1
  fi
  echo "✅ $APP_NAME is running"
}

function capture_screenshot() {
  local timestamp=$(date +%s)
  local output_path="$OUTPUT_DIR/tauri_debug_$timestamp.png"

  echo "📸 Capturing screenshot..."

  if ! screencapture -x -T 0 "$output_path" 2>/dev/null; then
    echo "❌ Failed to capture screenshot"
    echo "💡 Check System Preferences > Security & Privacy > Screen Recording"
    exit 1
  fi

  if [ ! -f "$output_path" ]; then
    echo "❌ Screenshot file not created"
    exit 1
  fi

  echo "✅ Screenshot saved: $output_path"
  echo "$output_path"
}

function get_process_info() {
  echo "🔍 Process information:"
  ps aux | grep "$APP_NAME" | grep -v grep | head -1
}

function main() {
  echo "🚀 Tauri Debug Helper"
  echo "===================="
  echo ""

  check_app_running
  echo ""

  get_process_info
  echo ""

  capture_screenshot
}

main
