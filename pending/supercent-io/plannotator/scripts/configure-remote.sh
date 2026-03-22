#!/bin/bash
# plannotator - Remote / Devcontainer Configuration Script
# Sets up environment variables for SSH, devcontainer, or WSL usage.
#
# Usage:
#   ./configure-remote.sh              # Interactive
#   ./configure-remote.sh --port 9999  # Set port only
#   ./configure-remote.sh --show       # Show current config

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m'

SHOW_ONLY=false
PORT=""
SHELL_PROFILE=""

for arg in "$@"; do
  case $arg in
    --show) SHOW_ONLY=true ;;
    --port) PORT="$2"; shift ;;
    --port=*) PORT="${arg#*=}" ;;
    -h|--help)
      echo "Usage: $0 [--show] [--port <number>]"
      echo ""
      echo "Configures plannotator for remote/devcontainer environments."
      echo ""
      echo "Options:"
      echo "  --show         Display current plannotator environment variables"
      echo "  --port <n>     Set PLANNOTATOR_PORT to <n>"
      echo "  -h, --help     Show this help"
      exit 0
      ;;
  esac
done

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   plannotator Remote Configuration         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# ── Show current config ────────────────────────────
show_config() {
  echo -e "${BLUE}Current plannotator environment:${NC}"
  echo ""

  if [ -n "$PLANNOTATOR_REMOTE" ]; then
    echo -e "  PLANNOTATOR_REMOTE   = ${GREEN}${PLANNOTATOR_REMOTE}${NC}"
  else
    echo -e "  PLANNOTATOR_REMOTE   = ${GRAY}(not set — local mode)${NC}"
  fi

  if [ -n "$PLANNOTATOR_PORT" ]; then
    echo -e "  PLANNOTATOR_PORT     = ${GREEN}${PLANNOTATOR_PORT}${NC}"
  else
    echo -e "  PLANNOTATOR_PORT     = ${GRAY}(not set — random in local, 19432 in remote)${NC}"
  fi

  if [ -n "$PLANNOTATOR_BROWSER" ]; then
    echo -e "  PLANNOTATOR_BROWSER  = ${GREEN}${PLANNOTATOR_BROWSER}${NC}"
  else
    echo -e "  PLANNOTATOR_BROWSER  = ${GRAY}(not set — system default)${NC}"
  fi

  if [ -n "$PLANNOTATOR_SHARE_URL" ]; then
    echo -e "  PLANNOTATOR_SHARE_URL= ${GREEN}${PLANNOTATOR_SHARE_URL}${NC}"
  else
    echo -e "  PLANNOTATOR_SHARE_URL= ${GRAY}(not set — share.plannotator.ai)${NC}"
  fi

  echo ""
}

show_config

if [ "$SHOW_ONLY" = true ]; then
  exit 0
fi

# ── Detect shell profile ───────────────────────────
detect_profile() {
  if [ -n "$ZSH_VERSION" ] || [ "$(basename "$SHELL")" = "zsh" ]; then
    echo "$HOME/.zshrc"
  elif [ -n "$BASH_VERSION" ] || [ "$(basename "$SHELL")" = "bash" ]; then
    if [ -f "$HOME/.bash_profile" ]; then
      echo "$HOME/.bash_profile"
    else
      echo "$HOME/.bashrc"
    fi
  else
    echo "$HOME/.profile"
  fi
}

SHELL_PROFILE=$(detect_profile)

echo -e "${BLUE}Shell profile detected:${NC} ${SHELL_PROFILE}"
echo ""

# ── Interactive prompts ────────────────────────────
echo -e "${BLUE}Configure plannotator for remote use?${NC}"
echo ""
echo -e "  ${YELLOW}Remote mode${NC} disables auto browser open and uses a fixed port."
echo -e "  Use this when running Claude Code via SSH, devcontainer, or WSL."
echo ""
read -rp "Enable remote mode? [y/N]: " ENABLE_REMOTE
echo ""

LINES_TO_ADD=""

if [[ "$ENABLE_REMOTE" =~ ^[Yy]$ ]]; then
  LINES_TO_ADD="${LINES_TO_ADD}export PLANNOTATOR_REMOTE=1\n"
  echo -e "${GREEN}✓ Remote mode will be enabled${NC}"

  # Port
  if [ -z "$PORT" ]; then
    read -rp "Port to use [default: 19432]: " PORT
    PORT="${PORT:-19432}"
  fi
  LINES_TO_ADD="${LINES_TO_ADD}export PLANNOTATOR_PORT=${PORT}\n"
  echo -e "${GREEN}✓ Port set to ${PORT}${NC}"
  echo ""

  echo -e "${BLUE}Port forwarding setup:${NC}"
  echo ""
  echo -e "  ${GRAY}SSH config (~/.ssh/config):${NC}"
  echo -e "    Host your-server"
  echo -e "      LocalForward ${PORT} localhost:${PORT}"
  echo ""
  echo -e "  ${GRAY}VS Code devcontainer: check the 'Ports' tab (auto-forwarded)${NC}"
  echo ""
else
  # Local mode — optionally set custom browser
  read -rp "Custom browser path/app? (leave empty for default): " CUSTOM_BROWSER
  if [ -n "$CUSTOM_BROWSER" ]; then
    LINES_TO_ADD="${LINES_TO_ADD}export PLANNOTATOR_BROWSER=\"${CUSTOM_BROWSER}\"\n"
    echo -e "${GREEN}✓ Browser set to: ${CUSTOM_BROWSER}${NC}"
  fi
fi

# Share URL
read -rp "Custom share URL? (leave empty for share.plannotator.ai): " CUSTOM_SHARE
if [ -n "$CUSTOM_SHARE" ]; then
  LINES_TO_ADD="${LINES_TO_ADD}export PLANNOTATOR_SHARE_URL=\"${CUSTOM_SHARE}\"\n"
  echo -e "${GREEN}✓ Share URL set to: ${CUSTOM_SHARE}${NC}"
fi

echo ""

if [ -z "$LINES_TO_ADD" ]; then
  echo -e "${YELLOW}No changes to make.${NC}"
  exit 0
fi

# ── Write to shell profile ─────────────────────────
echo -e "${BLUE}Adding to ${SHELL_PROFILE}:${NC}"
echo ""
printf "  %b" "$LINES_TO_ADD" | sed 's/^/  /'
echo ""

read -rp "Write to ${SHELL_PROFILE}? [Y/n]: " CONFIRM
if [[ "$CONFIRM" =~ ^[Nn]$ ]]; then
  echo ""
  echo -e "${YELLOW}Not written. Add these lines manually to your shell profile:${NC}"
  echo ""
  printf "%b" "$LINES_TO_ADD"
  exit 0
fi

{
  echo ""
  echo "# plannotator configuration"
  printf "%b" "$LINES_TO_ADD"
} >> "$SHELL_PROFILE"

echo ""
echo -e "${GREEN}✓ Configuration written to ${SHELL_PROFILE}${NC}"
echo ""
echo -e "${BLUE}Apply now with:${NC}"
echo -e "  source ${SHELL_PROFILE}"
echo ""
echo -e "${BLUE}Verify with:${NC}"
echo -e "  ./check-status.sh"
echo ""
