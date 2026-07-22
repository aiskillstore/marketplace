#!/usr/bin/env bash
# watch-vscode.sh — universal VS Code AI extension log watcher.
# Monitors ALL AI extension logs and fires notify.sh on turn completion.
# Works on macOS, Linux, and Windows (Git Bash / WSL).
#
# Usage:
#   watch-vscode.sh              Start watching (foreground, all logs)
#   watch-vscode.sh --daemon     Start as background daemon
#   watch-vscode.sh --stop       Kill the running daemon
#   watch-vscode.sh --status     Check daemon status
#   watch-vscode.sh --list       List discovered extensions and their markers
#
# Platform notes:
#   - Windows: requires Git Bash or WSL. Native cmd/PowerShell not supported
#     (uses tail, find, pkill — standard in Git Bash).
#   - The script auto-detects VS Code log paths per platform.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NOTIFY_SCRIPT="$SCRIPT_DIR/notify.sh"
PID_FILE="$HOME/.push-notifications-vscode-watcher.pid"
LOG_FILE="$HOME/.push-notifications-vscode-watcher.log"
DEBOUNCE_SEC=3

# ── OS detection ──────────────────────────────────────────────────────────
detect_os() {
  case "$(uname -s)" in
    Darwin)  echo "macos" ;;
    Linux)   echo "linux" ;;
    MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
    *)       echo "unknown" ;;
  esac
}
OS="$(detect_os)"

# ── Extension registry ────────────────────────────────────────────────────
# Format: "extension_id|marker_pattern|label"
# marker: "time_to_response" for Claude, "_any_activity" for best-effort
declare -a KNOWN_EXTENSIONS=(
  "Anthropic.claude-code|time_to_response|Claude Code (VS Code)"
  "GitHub.copilot-chat|_any_activity|Copilot Chat (VS Code)"
  "openai.chatgpt|_any_activity|Codex (VS Code)"
)

# ── VS Code log paths per platform ────────────────────────────────────────
find_code_logs_dir() {
  case "$OS" in
    macos)
      echo "$HOME/Library/Application Support/Code/logs"
      ;;
    linux)
      # XDG spec — VS Code uses $XDG_CONFIG_HOME or ~/.config
      echo "${XDG_CONFIG_HOME:-$HOME/.config}/Code/logs"
      ;;
    windows)
      # Git Bash / MSYS maps %APPDATA% to a Unix-style path.
      # Try the env var first, then fall back to the common location.
      if [[ -n "${APPDATA:-}" ]]; then
        echo "$APPDATA/Code/logs" | sed 's|\\|/|g'
      else
        echo "$HOME/AppData/Roaming/Code/logs"
      fi
      ;;
    *)
      echo "" ;;
  esac
}

# ── Find latest session directory ─────────────────────────────────────────
find_latest_session() {
  local logs_dir
  logs_dir="$(find_code_logs_dir)"
  if [[ -z "$logs_dir" ]] || [[ ! -d "$logs_dir" ]]; then
    return 1
  fi
  find "$logs_dir" -maxdepth 1 -type d -name "202*" 2>/dev/null | sort -r | head -1
}

# ── Discover AI extension logs ────────────────────────────────────────────
discover_logs() {
  local session_dir="$1"
  for entry in "${KNOWN_EXTENSIONS[@]}"; do
    local ext_id="${entry%%|*}"
    local rest="${entry#*|}"
    local marker="${rest%|*}"
    local label="${rest##*|}"

    local log_files
    log_files=$(find "$session_dir" -path "*/exthost/${ext_id}/*.log" -type f 2>/dev/null || true)

    if [[ -n "$log_files" ]]; then
      while IFS= read -r log_path; do
        echo "${ext_id}|${log_path}|${marker}|${label}"
      done <<< "$log_files"
    fi
  done
}

# ── Watch one log file ────────────────────────────────────────────────────
watch_one_log() {
  local ext_id="$1"
  local log_path="$2"
  local marker="$3"
  local label="$4"

  if [[ ! -f "$log_path" ]]; then
    return 0
  fi

  tail -F "$log_path" 2>/dev/null | while IFS= read -r line; do
    local now
    now=$(date +%s)

    local last_file="/tmp/push-notify-debounce-${ext_id}"
    local last_fire=0
    [[ -f "$last_file" ]] && last_fire=$(cat "$last_file" 2>/dev/null) || true

    local fire=false

    if [[ "$marker" == "_any_activity" ]]; then
      fire=true
    elif echo "$line" | grep -qE "$marker" 2>/dev/null; then
      fire=true
    fi

    if $fire && (( now - last_fire >= DEBOUNCE_SEC )); then
      echo "$now" > "$last_file"
      "$NOTIFY_SCRIPT" "$label" --details &
    fi
  done
}

# ── Start watching ────────────────────────────────────────────────────────
do_start() {
  local session_dir
  session_dir=$(find_latest_session)

  if [[ -z "$session_dir" ]]; then
    echo "No VS Code log session found." >&2
    echo "Platform: $OS" >&2
    echo "Expected logs at: $(find_code_logs_dir)" >&2
    return 1
  fi

  if [[ ! -x "$NOTIFY_SCRIPT" ]]; then
    echo "notify.sh is not executable — notifications are toggled off" >&2
    return 1
  fi

  echo "Platform: $OS"
  echo "Session: $(basename "$session_dir")"
  echo "Discovering AI extensions..."

  local discovered
  discovered=$(discover_logs "$session_dir")

  if [[ -z "$discovered" ]]; then
    echo "No AI extension logs found in this session." >&2
    return 1
  fi

  rm -f /tmp/push-notify-debounce-*

  local pids=()

  while IFS='|' read -r ext_id log_path marker label; do
    echo "  Watching: $label ($ext_id)"
    echo "    Log: $log_path"
    echo "    Marker: $marker"
    watch_one_log "$ext_id" "$log_path" "$marker" "$label" &
    pids+=($!)
  done <<< "$discovered"

  echo "Watching ${#pids[@]} extension(s). PID: $$"
  echo "Debounce: ${DEBOUNCE_SEC}s between notifications"

  for pid in "${pids[@]}"; do
    wait "$pid" 2>/dev/null || true
  done
}

# ── List discovered extensions ────────────────────────────────────────────
do_list() {
  echo "Platform: $OS"
  local session_dir
  session_dir=$(find_latest_session)
  echo "Session: ${session_dir:-not found}"
  echo ""

  local discovered
  discovered=$(discover_logs "$session_dir")

  if [[ -z "$discovered" ]]; then
    echo "No AI extension logs found."
    return 0
  fi

  printf "%-35s %-25s %s\n" "EXTENSION" "MARKER" "LABEL"
  printf "%-35s %-25s %s\n" "---------" "------" "-----"
  while IFS='|' read -r ext_id log_path marker label; do
    printf "%-35s %-25s %s\n" "$ext_id" "$marker" "$label"
  done <<< "$discovered"
}

# ── Daemon management ─────────────────────────────────────────────────────
do_daemon() {
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "Watcher daemon is already running (PID $(cat "$PID_FILE"))"
    do_status
    return 0
  fi

  echo "Starting universal VS Code watcher daemon..."
  echo "Platform: $OS"
  nohup bash "$0" start > "$LOG_FILE" 2>&1 &
  local PID=$!
  echo "$PID" > "$PID_FILE"

  sleep 1
  if kill -0 "$PID" 2>/dev/null; then
    echo "Daemon started (PID $PID)"
    cat "$LOG_FILE"
    echo "Stop with: $0 --stop"
  else
    echo "Daemon failed to start. Check log:"
    cat "$LOG_FILE"
    rm -f "$PID_FILE"
    return 1
  fi
}

do_stop() {
  if [[ -f "$PID_FILE" ]]; then
    local PID
    PID=$(cat "$PID_FILE")
    if kill "$PID" 2>/dev/null; then
      echo "Watcher daemon stopped (PID $PID)"
    else
      echo "Watcher daemon not running (stale PID file)"
    fi
    rm -f "$PID_FILE"
  fi
  pkill -f "watch-vscode.sh.*start" 2>/dev/null || true
  pkill -f "tail -F.*exthost.*\.log" 2>/dev/null || true
}

do_status() {
  if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    local PID
    PID=$(cat "$PID_FILE")
    echo "Watcher daemon: RUNNING (PID $PID)"
    echo "Platform: $OS"
    local session_dir
    session_dir=$(find_latest_session)
    echo "Session: $(basename "${session_dir:-unknown}")"
    echo "Notifications: $([[ -x "$NOTIFY_SCRIPT" ]] && echo 'enabled' || echo 'DISABLED')"

    if [[ -f "$LOG_FILE" ]]; then
      echo ""
      echo "Recent log:"
      tail -5 "$LOG_FILE"
    fi
    return 0
  else
    echo "Watcher daemon: NOT RUNNING"
    echo "Platform: $OS"
    if [[ -f "$PID_FILE" ]]; then
      echo "(stale PID file: $(cat "$PID_FILE"))"
    fi
    return 1
  fi
}

# ── CLI dispatch ──────────────────────────────────────────────────────────
case "${1:-start}" in
  start)       do_start ;;
  --daemon|-d) do_daemon ;;
  --stop|-s)   do_stop ;;
  --status)    do_status ;;
  --list|-l)   do_list ;;
  --help|-h)
    echo "Usage: $0 [start|--daemon|--stop|--status|--list]"
    echo ""
    echo "Platform: $OS"
    echo "VS Code logs: $(find_code_logs_dir 2>/dev/null || echo 'unknown')"
    echo ""
    echo "Commands:"
    echo "  start      Start watching in the foreground"
    echo "  --daemon   Start as a background daemon"
    echo "  --stop     Stop the background daemon"
    echo "  --status   Check daemon status"
    echo "  --list     List discovered AI extensions and their markers"
    echo ""
    echo "Watched extensions:"
    for entry in "${KNOWN_EXTENSIONS[@]}"; do
      printf "  %-30s → %s\n" "${entry%%|*}" "${entry##*|}"
    done
    ;;
  *)
    echo "Unknown option: $1"
    echo "Usage: $0 [start|--daemon|--stop|--status|--list]"
    exit 1
    ;;
esac
