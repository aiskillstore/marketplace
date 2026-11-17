#!/bin/sh

set -eu

REPOSITORY="TseringYuu/anyviz"
ARCHIVE_URL="https://codeload.github.com/${REPOSITORY}/tar.gz/refs/heads/main"
ANYVIZ_USER_HOME="${ANYVIZ_HOME:-${HOME:-}}"
TEMP_ROOT=""
SOURCE_ROOT="${ANYVIZ_SOURCE_DIR:-}"
DETECT_COMMANDS="${ANYVIZ_DETECT_COMMANDS:-1}"
INSTALL_COUNT=0

say() {
  printf '%s\n' "$*"
}

fail() {
  printf 'anyviz: %s\n' "$*" >&2
  exit 1
}

cleanup() {
  if [ -n "$TEMP_ROOT" ] && [ -d "$TEMP_ROOT" ]; then
    rm -rf "$TEMP_ROOT"
  fi
}

trap cleanup EXIT HUP INT TERM

[ -n "$ANYVIZ_USER_HOME" ] || fail 'cannot determine user home directory'

if [ -n "$SOURCE_ROOT" ]; then
  [ -f "$SOURCE_ROOT/SKILL.md" ] || fail "SKILL.md not found in $SOURCE_ROOT"
else
  command -v tar >/dev/null 2>&1 || fail 'tar is required'
  TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/anyviz.XXXXXX")" || fail 'cannot create temporary directory'
  ARCHIVE_PATH="$TEMP_ROOT/anyviz.tar.gz"
  SOURCE_ROOT="$TEMP_ROOT/source"
  mkdir -p "$SOURCE_ROOT"

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL --retry 3 "$ARCHIVE_URL" -o "$ARCHIVE_PATH" || fail 'download failed'
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$ARCHIVE_PATH" "$ARCHIVE_URL" || fail 'download failed'
  else
    fail 'curl or wget is required'
  fi

  tar -xzf "$ARCHIVE_PATH" -C "$SOURCE_ROOT" --strip-components=1 || fail 'archive extraction failed'
fi

install_skill() {
  AGENT_NAME="$1"
  TARGET="$2"
  PARENT="$(dirname "$TARGET")"
  STAGING="$PARENT/.anyviz-install-$$"
  BACKUP="$PARENT/.anyviz-backup-$$"
  PRESERVED_BACKUP=""

  mkdir -p "$PARENT"
  rm -rf "$STAGING" "$BACKUP"
  mkdir -p "$STAGING"

  cp "$SOURCE_ROOT/SKILL.md" "$STAGING/SKILL.md"
  for DIRECTORY in aesthetics adapters guides templates scripts examples; do
    if [ -d "$SOURCE_ROOT/$DIRECTORY" ]; then
      cp -R "$SOURCE_ROOT/$DIRECTORY" "$STAGING/$DIRECTORY"
    fi
  done

  mkdir -p "$STAGING/assets"
  for ASSET in banner.svg wordmark.svg; do
    if [ -f "$SOURCE_ROOT/assets/$ASSET" ]; then
      cp "$SOURCE_ROOT/assets/$ASSET" "$STAGING/assets/$ASSET"
    fi
  done
  printf 'https://github.com/%s\n' "$REPOSITORY" > "$STAGING/.anyviz-source"

  if [ -L "$TARGET" ] && [ -f "$TARGET/SKILL.md" ]; then
    rm -rf "$STAGING"
    say "linked     $AGENT_NAME  $TARGET"
    return
  fi

  if [ -e "$TARGET" ] || [ -L "$TARGET" ]; then
    if [ -f "$TARGET/.anyviz-source" ]; then
      mv "$TARGET" "$BACKUP"
    else
      PRESERVED_BACKUP="$PARENT/anyviz.backup-$(date '+%Y%m%d%H%M%S')"
      while [ -e "$PRESERVED_BACKUP" ] || [ -L "$PRESERVED_BACKUP" ]; do
        PRESERVED_BACKUP="${PRESERVED_BACKUP}-1"
      done
      mv "$TARGET" "$PRESERVED_BACKUP"
      say "backed up $AGENT_NAME  $PRESERVED_BACKUP"
    fi
  fi

  if mv "$STAGING" "$TARGET"; then
    rm -rf "$BACKUP"
  else
    rm -rf "$STAGING"
    if [ -e "$BACKUP" ] || [ -L "$BACKUP" ]; then
      mv "$BACKUP" "$TARGET"
    elif [ -n "$PRESERVED_BACKUP" ] && { [ -e "$PRESERVED_BACKUP" ] || [ -L "$PRESERVED_BACKUP" ]; }; then
      mv "$PRESERVED_BACKUP" "$TARGET"
    fi
    fail "installation failed for $AGENT_NAME"
  fi

  INSTALL_COUNT=$((INSTALL_COUNT + 1))
  say "installed  $AGENT_NAME  $TARGET"
}

install_if_detected() {
  AGENT_NAME="$1"
  MARKER="$2"
  TARGET="$3"
  COMMAND_NAME="$4"

  if [ -e "$MARKER" ] || { [ "$DETECT_COMMANDS" = "1" ] && [ -n "$COMMAND_NAME" ] && command -v "$COMMAND_NAME" >/dev/null 2>&1; }; then
    install_skill "$AGENT_NAME" "$TARGET"
  fi
}

# Shared Agent Skills path. Current Codex, Cursor, OpenCode, OpenClaw, Cline,
# Kimi Code CLI, Warp, Zed, and other compatible agents discover this path.
install_skill "Universal agents" "$ANYVIZ_USER_HOME/.agents/skills/anyviz"

# Agents with their own global skill roots. Install only when their config or
# executable is present, so the installer does not create dozens of unused dirs.
install_if_detected "Claude Code" "$ANYVIZ_USER_HOME/.claude" "$ANYVIZ_USER_HOME/.claude/skills/anyviz" "claude"
install_if_detected "Hermes Agent" "$ANYVIZ_USER_HOME/.hermes" "$ANYVIZ_USER_HOME/.hermes/skills/anyviz" "hermes"
install_if_detected "Gemini CLI" "$ANYVIZ_USER_HOME/.gemini" "$ANYVIZ_USER_HOME/.gemini/skills/anyviz" "gemini"
install_if_detected "GitHub Copilot" "$ANYVIZ_USER_HOME/.copilot" "$ANYVIZ_USER_HOME/.copilot/skills/anyviz" "copilot"
install_if_detected "Windsurf" "$ANYVIZ_USER_HOME/.codeium/windsurf" "$ANYVIZ_USER_HOME/.codeium/windsurf/skills/anyviz" "windsurf"
install_if_detected "Goose" "$ANYVIZ_USER_HOME/.config/goose" "$ANYVIZ_USER_HOME/.config/goose/skills/anyviz" "goose"
install_if_detected "Continue" "$ANYVIZ_USER_HOME/.continue" "$ANYVIZ_USER_HOME/.continue/skills/anyviz" "cn"
install_if_detected "Kiro CLI" "$ANYVIZ_USER_HOME/.kiro" "$ANYVIZ_USER_HOME/.kiro/skills/anyviz" "kiro-cli"
install_if_detected "OpenHands" "$ANYVIZ_USER_HOME/.openhands" "$ANYVIZ_USER_HOME/.openhands/skills/anyviz" "openhands"
install_if_detected "Qwen Code" "$ANYVIZ_USER_HOME/.qwen" "$ANYVIZ_USER_HOME/.qwen/skills/anyviz" "qwen"
install_if_detected "Roo Code" "$ANYVIZ_USER_HOME/.roo" "$ANYVIZ_USER_HOME/.roo/skills/anyviz" "roo"
install_if_detected "Trae" "$ANYVIZ_USER_HOME/.trae" "$ANYVIZ_USER_HOME/.trae/skills/anyviz" "trae"
install_if_detected "Droid" "$ANYVIZ_USER_HOME/.factory" "$ANYVIZ_USER_HOME/.factory/skills/anyviz" "droid"
install_if_detected "Junie" "$ANYVIZ_USER_HOME/.junie" "$ANYVIZ_USER_HOME/.junie/skills/anyviz" "junie"
install_if_detected "Kilo Code" "$ANYVIZ_USER_HOME/.kilocode" "$ANYVIZ_USER_HOME/.kilocode/skills/anyviz" "kilo"

say "anyviz ready in $INSTALL_COUNT skill root(s). Restart agents that were already running."
