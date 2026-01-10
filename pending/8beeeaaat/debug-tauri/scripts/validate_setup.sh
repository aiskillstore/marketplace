#!/bin/bash
# Validate debug tools setup with official plugins
# Usage: ./validate_setup.sh [bundle-id]
#
# Examples:
#   TAURI_BUNDLE_ID=com.example.myapp ./validate_setup.sh
#   ./validate_setup.sh com.example.myapp

APP_NAME="${TAURI_APP_NAME:-tauri-app}"
BUNDLE_ID="${1:-${TAURI_BUNDLE_ID}}"

# Detect log file path based on platform
detect_log_path() {
  local bundle_id="$1"

  if [ -z "$bundle_id" ]; then
    return 1
  fi

  case "$(uname -s)" in
    Darwin)
      echo "$HOME/Library/Logs/$bundle_id/debug.log"
      ;;
    Linux)
      echo "$HOME/.local/share/$bundle_id/logs/debug.log"
      ;;
    MINGW*|MSYS*|CYGWIN*)
      echo "$LOCALAPPDATA/$bundle_id/logs/debug.log"
      ;;
    *)
      return 1
      ;;
  esac
}

echo "🔍 Validating debug setup..."
echo "============================"
echo ""

# Check if app is running
echo "📱 App Process:"
if pgrep -x "$APP_NAME" > /dev/null; then
  pid=$(pgrep -x "$APP_NAME")
  echo "  ✅ App is running (PID: $pid)"

  # Get process details
  if command -v ps &> /dev/null; then
    ps -p "$pid" -o pid,rss,%cpu,%mem,command 2>/dev/null | tail -1
  fi
else
  echo "  ⚠️  App not running"
  echo "  💡 Start with: tauri dev"
fi

echo ""

# Check screen recording permission (macOS only)
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "📸 Screen Recording Permission:"

  test_file="/tmp/screen_test_$$.png"
  if screencapture -x -T 0 "$test_file" 2>/dev/null; then
    rm -f "$test_file"
    echo "  ✅ Screen recording permission granted"
  else
    echo "  ❌ Screen recording permission denied"
    echo "  💡 Grant in: System Preferences > Security & Privacy > Screen Recording"
  fi

  echo ""
fi

# Check for official plugin log file
echo "📝 Official Plugin Logs (tauri-plugin-log):"
if [ -n "$BUNDLE_ID" ]; then
  PLUGIN_LOG=$(detect_log_path "$BUNDLE_ID")

  if [ -n "$PLUGIN_LOG" ] && [ -f "$PLUGIN_LOG" ]; then
    log_size=$(wc -l < "$PLUGIN_LOG" | tr -d ' ')
    echo "  ✅ Plugin log file exists ($log_size lines)"
    echo "     Location: $PLUGIN_LOG"

    if [ "$log_size" -eq 0 ]; then
      echo "  ⚠️  Log file is empty - logger may not be initialized"
      echo "  💡 Call logger.initialize() in frontend"
    fi
  else
    echo "  ⚠️  Plugin log file not found"
    echo "  💡 Expected: $PLUGIN_LOG"
    echo "  💡 Ensure tauri-plugin-log is initialized and app has been run"
  fi
else
  echo "  ℹ️  Bundle ID not provided"
  echo "  💡 Set TAURI_BUNDLE_ID or pass as argument to check plugin logs"
  echo "  💡 Example: TAURI_BUNDLE_ID=com.example.myapp ./validate_setup.sh"
fi

# Check for legacy log file
echo ""
echo "📝 Legacy Logs (consoleLogger):"
if compgen -G "/tmp/tauri_console_logs_*.jsonl" > /dev/null; then
  log_file=$(ls -t /tmp/tauri_console_logs_*.jsonl 2>/dev/null | head -1)
  log_size=$(wc -l < "$log_file" | tr -d ' ')
  echo "  ⚠️  Legacy log file exists ($log_size lines)"
  echo "  💡 Migrate to tauri-plugin-log for better persistence"
else
  echo "  ✅ No legacy logs (good - using official plugin)"
fi

# Check for screenshots
echo ""
echo "📸 Screenshots:"
screenshot_count=$(find /tmp -name "tauri_debug_*.png" -mtime -1 2>/dev/null | wc -l | tr -d ' ')
if [ "$screenshot_count" -gt 0 ]; then
  echo "  ℹ️  Found $screenshot_count legacy screenshot(s) in /tmp"
  echo "     $(ls -t /tmp/tauri_debug_*.png 2>/dev/null | head -1)"
  echo "  💡 Use captureMainWindow() from screenshotHelper for plugin API"
else
  echo "  ℹ️  No legacy screenshots found"
fi

echo ""

# Check for required tools
echo "🛠️  Tools:"

check_tool() {
  local tool=$1
  local status=$2
  local install_hint=$3

  if command -v "$tool" &> /dev/null; then
    echo "  ✅ $tool ($status)"
  else
    echo "  ⚠️  $tool not found ($status)"
    if [ -n "$install_hint" ]; then
      echo "     Install: $install_hint"
    fi
  fi
}

# Optional tools
if [[ "$OSTYPE" == "darwin"* ]]; then
  check_tool "screencapture" "legacy, optional" ""
fi

echo ""

# Check project structure (if run from project root)
echo "📁 Project Structure:"

if [ -f "tauri.conf.json" ] || [ -f "src-tauri/tauri.conf.json" ]; then
  echo "  ✅ Tauri project detected"

  # Check for debug capabilities
  if [ -f "src-tauri/capabilities/default.json" ]; then
    echo "  ✅ Capabilities file exists"

    if grep -q "debug-tools" src-tauri/capabilities/default.json 2>/dev/null; then
      echo "  ✅ Debug tools permissions found"
    else
      echo "  ⚠️  Debug tools permissions may not be configured"
    fi
  else
    echo "  ℹ️  No capabilities file found"
  fi
else
  echo "  ℹ️  Not in a Tauri project directory (or run from skill directory)"
fi

echo ""
echo "=========================================="
echo "✅ Validation complete"
echo ""

# Summary
if pgrep -x "$APP_NAME" > /dev/null && [[ "$OSTYPE" == "darwin"* ]] && screencapture -x -T 0 /tmp/test_$$.png 2>/dev/null; then
  rm -f /tmp/test_$$.png
  echo "🎉 Ready to debug!"
else
  echo "⚠️  Some issues found. Review output above."
fi
