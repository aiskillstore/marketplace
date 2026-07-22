#!/usr/bin/env bash
# notify.sh — send a push notification via ntfy.sh
# Works on macOS, Linux, and Windows (Git Bash / WSL).
#
# Usage: notify.sh [label] [--details]
#   label      Agent name for context (default: "Agent")
#   --details  Include git diff summary in the notification body
#
# Topic is read from ~/.push-notifications-topic (set during setup).
# Toggle all notifications off: chmod -x notify.sh
# Toggle back on:              chmod +x notify.sh

set -euo pipefail

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

# ── Parse args ────────────────────────────────────────────────────────────
LABEL=""
DETAILS=false
for arg in "$@"; do
  case "$arg" in
    --details|-d) DETAILS=true ;;
    *) LABEL="$arg" ;;
  esac
done
LABEL="${LABEL:-Agent}"

# ── Topic ─────────────────────────────────────────────────────────────────
TOPIC_FILE="$HOME/.push-notifications-topic"
DIR="${PWD##*/}"

if [[ ! -f "$TOPIC_FILE" ]]; then
  exit 0  # Silent — topic not set up yet
fi
TOPIC="$(cat "$TOPIC_FILE")"

# ── Build notification body ───────────────────────────────────────────────
if $DETAILS && command -v git &>/dev/null && git rev-parse --git-dir &>/dev/null 2>&1; then
  CHANGED=$(git status --short 2>/dev/null | wc -l | tr -d ' ')
  DIFF_SUMMARY=$(git diff --stat -- . 2>/dev/null | tail -1 || echo "")
  STAGED_SUMMARY=$(git diff --stat --cached -- . 2>/dev/null | tail -1 || echo "")

  BODY="${LABEL} done — ${DIR}"
  if [[ "$CHANGED" -gt 0 ]]; then
    BODY+=" | ${CHANGED} file(s) changed"
    if [[ -n "$DIFF_SUMMARY" ]]; then
      BODY+=" (${DIFF_SUMMARY})"
    fi
    if [[ -n "$STAGED_SUMMARY" ]]; then
      BODY+=" [staged: ${STAGED_SUMMARY}]"
    fi
  else
    BODY+=" | no file changes"
  fi
else
  BODY="${LABEL} done — ${DIR}"
fi

# ── Push notification ─────────────────────────────────────────────────────
curl -s \
  -H "Priority: default" \
  -H "Title: ${LABEL} done" \
  -d "${BODY}" \
  "ntfy.sh/${TOPIC}" \
  > /dev/null 2>&1 &

# ── Local sound ───────────────────────────────────────────────────────────
case "$OS" in
  macos)
    if command -v afplay &>/dev/null; then
      afplay /System/Library/Sounds/Glass.aiff &
    fi
    ;;
  linux)
    if command -v paplay &>/dev/null; then
      paplay /usr/share/sounds/freedesktop/stereo/complete.oga &
    elif command -v aplay &>/dev/null; then
      aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null &
    fi
    ;;
  windows)
    powershell.exe -c "
      Add-Type -AssemblyName System.Speech
      (New-Object Media.SoundPlayer 'C:\Windows\Media\Windows Notify.wav').Play()
    " 2>/dev/null &
    ;;
esac

exit 0
