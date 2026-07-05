#!/bin/bash
# Analyze Tauri console logs for errors and patterns
# Usage: ./analyze_logs.sh [log-file] [bundle-id]
#
# Examples:
#   ./analyze_logs.sh                              # Auto-detect from TAURI_BUNDLE_ID
#   ./analyze_logs.sh /path/to/debug.log           # Custom path
#   ./analyze_logs.sh "" com.example.myapp         # Specify bundle ID

# Auto-detect log file path based on platform and bundle ID
detect_log_path() {
  local bundle_id="${1:-${TAURI_BUNDLE_ID}}"

  if [ -z "$bundle_id" ]; then
    echo "⚠️  Bundle ID not provided. Set TAURI_BUNDLE_ID or pass as argument."
    return 1
  fi

  case "$(uname -s)" in
    Darwin)  # macOS
      echo "$HOME/Library/Logs/$bundle_id/debug.log"
      ;;
    Linux)
      echo "$HOME/.local/share/$bundle_id/logs/debug.log"
      ;;
    MINGW*|MSYS*|CYGWIN*)  # Windows
      echo "$LOCALAPPDATA/$bundle_id/logs/debug.log"
      ;;
    *)
      echo "⚠️  Unsupported platform: $(uname -s)"
      return 1
      ;;
  esac
}

# Determine log file
if [ -n "$1" ]; then
  LOG_FILE="$1"
else
  LOG_FILE=$(detect_log_path "${2}")
  if [ $? -ne 0 ] || [ -z "$LOG_FILE" ]; then
    echo "❌ Could not determine log file path"
    echo "💡 Usage: $0 [log-file] [bundle-id]"
    echo "   Example: $0 \"\" com.example.myapp"
    echo "   Or set: export TAURI_BUNDLE_ID=com.example.myapp"
    exit 1
  fi
fi

if [ ! -f "$LOG_FILE" ]; then
  echo "❌ Log file not found: $LOG_FILE"
  echo "💡 Ensure tauri-plugin-log is initialized and app has been run"
  echo "💡 Expected locations:"
  echo "   macOS:   ~/Library/Logs/{bundle_id}/debug.log"
  echo "   Linux:   ~/.local/share/{bundle_id}/logs/debug.log"
  echo "   Windows: %LOCALAPPDATA%\\{bundle_id}\\logs\\debug.log"
  exit 1
fi

echo "🔍 Analyzing logs from: $LOG_FILE"
echo "=========================================="
echo ""

# Count log levels (tauri-plugin-log format: YYYY-MM-DDTHH:MM:SS.sssZ LEVEL app: message)
echo "📊 Log Statistics:"
total_lines=$(wc -l < "$LOG_FILE" | tr -d ' ')
error_count=$(grep -c " ERROR " "$LOG_FILE" 2>/dev/null || echo "0")
warn_count=$(grep -c " WARN " "$LOG_FILE" 2>/dev/null || echo "0")
info_count=$(grep -c " INFO " "$LOG_FILE" 2>/dev/null || echo "0")
debug_count=$(grep -c " DEBUG " "$LOG_FILE" 2>/dev/null || echo "0")
trace_count=$(grep -c " TRACE " "$LOG_FILE" 2>/dev/null || echo "0")

echo "  Total lines: $total_lines"
echo "  ERROR: $error_count"
echo "  WARN:  $warn_count"
echo "  INFO:  $info_count"
echo "  DEBUG: $debug_count"
echo "  TRACE: $trace_count"

echo ""
echo "❌ Recent Errors (last 5):"
if [ "$error_count" -eq 0 ]; then
  echo "  ✅ No errors found"
else
  grep " ERROR " "$LOG_FILE" | tail -5
fi

echo ""
echo "⚠️  Recent Warnings (last 5):"
if [ "$warn_count" -eq 0 ]; then
  echo "  ✅ No warnings found"
else
  grep " WARN " "$LOG_FILE" | tail -5
fi

echo ""
echo "📈 Pattern Analysis:"

# Common error patterns
echo "  Searching for common issues..."

# Network errors
net_errors=$(grep -i "network\|fetch\|xhr\|cors" "$LOG_FILE" 2>/dev/null | wc -l | tr -d ' ')
if [ "$net_errors" -gt 0 ]; then
  echo "    🌐 Network-related issues: $net_errors"
fi

# Type errors
type_errors=$(grep -i "typeerror\|undefined\|null" "$LOG_FILE" 2>/dev/null | wc -l | tr -d ' ')
if [ "$type_errors" -gt 0 ]; then
  echo "    🔤 Type/undefined errors: $type_errors"
fi

# WebGPU errors
gpu_errors=$(grep -i "webgpu\|gpu\|shader" "$LOG_FILE" 2>/dev/null | wc -l | tr -d ' ')
if [ "$gpu_errors" -gt 0 ]; then
  echo "    🎮 WebGPU-related issues: $gpu_errors"
fi

echo ""
echo "✅ Analysis complete"
echo ""
echo "💡 For full log review:"
echo "   cat $LOG_FILE"
echo ""
echo "💡 Monitor logs in real-time:"
echo "   tail -f $LOG_FILE"
