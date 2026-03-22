#!/bin/bash
# plannotator - Installation Script
# Installs the plannotator CLI and optionally sets up AI tool integrations
#
# Usage:
#   ./install.sh                  # CLI only
#   ./install.sh --with-plugin    # CLI + Claude Code plugin
#   ./install.sh --with-gemini    # CLI + Gemini CLI hook
#   ./install.sh --with-codex     # CLI + Codex CLI setup
#   ./install.sh --with-opencode  # CLI + OpenCode plugin
#   ./install.sh --all            # CLI + all integrations

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m'

WITH_PLUGIN=false
WITH_GEMINI=false
WITH_CODEX=false
WITH_OPENCODE=false

for arg in "$@"; do
  case $arg in
    --with-plugin)   WITH_PLUGIN=true ;;
    --with-gemini)   WITH_GEMINI=true ;;
    --with-codex)    WITH_CODEX=true ;;
    --with-opencode) WITH_OPENCODE=true ;;
    --all)
      WITH_PLUGIN=true
      WITH_GEMINI=true
      WITH_CODEX=true
      WITH_OPENCODE=true
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --with-plugin    Also output Claude Code plugin install commands"
      echo "  --with-gemini    Configure Gemini CLI hook (runs setup-gemini-hook.sh)"
      echo "  --with-codex     Configure Codex CLI (runs setup-codex-hook.sh)"
      echo "  --with-opencode  Register OpenCode plugin (runs setup-opencode-plugin.sh)"
      echo "  --all            All of the above"
      echo "  -h, --help       Show this help"
      echo ""
      echo "Prerequisites:"
      echo "  Obsidian (for plan/review auto-save): https://obsidian.md/download"
      exit 0
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       plannotator Installer                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}━━ Prerequisites ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
if command -v obsidian &>/dev/null 2>&1 || [ -d "/Applications/Obsidian.app" ] || [ -d "$HOME/Applications/Obsidian.app" ]; then
  echo -e "  ${GREEN}✓ Obsidian detected${NC}"
else
  echo -e "  ${YELLOW}⚠ Obsidian not detected${NC}"
  echo -e "  ${GRAY}  plannotator can auto-save approved plans to your Obsidian vault.${NC}"
  echo -e "  ${GRAY}  Install Obsidian: ${BLUE}https://obsidian.md/download${NC}"
  echo -e "  ${GRAY}  (You can skip this and enable later via plannotator UI → gear icon)${NC}"
fi
echo ""

OS=""
case "$(uname -s)" in
  Darwin) OS="macos" ;;
  Linux)
    if grep -qi microsoft /proc/version 2>/dev/null; then
      OS="wsl"
    else
      OS="linux"
    fi
    ;;
  CYGWIN*|MINGW*|MSYS*) OS="windows" ;;
  *) OS="unknown" ;;
esac

echo -e "${BLUE}━━ Installing plannotator CLI ━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Detected OS:${NC} ${OS}"
echo ""

if command -v plannotator &>/dev/null; then
  CURRENT_VERSION=$(plannotator --version 2>/dev/null || echo "unknown")
  echo -e "${YELLOW}plannotator is already installed (version: ${CURRENT_VERSION})${NC}"
  echo -e "${GRAY}Re-running install to update to latest version...${NC}"
  echo ""
fi

case "$OS" in
  macos|linux|wsl)
    if curl -fsSL https://plannotator.ai/install.sh | bash; then
      echo ""
      echo -e "${GREEN}✓ plannotator CLI installed successfully${NC}"
    else
      echo -e "${RED}✗ Installation failed${NC}"
      echo -e "${YELLOW}Try manual install: curl -fsSL https://plannotator.ai/install.sh | bash${NC}"
      exit 1
    fi
    ;;
  windows)
    echo -e "${YELLOW}Windows detected. Run in PowerShell:${NC}"
    echo ""
    echo "    irm https://plannotator.ai/install.ps1 | iex"
    echo ""
    echo -e "${GRAY}Or for CMD:${NC}"
    echo "    curl -fsSL https://plannotator.ai/install.cmd -o install.cmd && install.cmd && del install.cmd"
    echo ""
    exit 0
    ;;
  *)
    echo -e "${RED}Unsupported OS. Visit https://plannotator.ai for manual install instructions.${NC}"
    exit 1
    ;;
esac

# Verify installation
echo ""
echo -e "${BLUE}Verifying installation...${NC}"

# Reload PATH in case plannotator was added to a new location
export PATH="$HOME/.local/bin:$HOME/bin:$PATH"

if command -v plannotator &>/dev/null; then
  VERSION=$(plannotator --version 2>/dev/null || echo "unknown")
  echo -e "${GREEN}✓ plannotator ${VERSION} is ready${NC}"
  echo -e "${GRAY}  Location: $(which plannotator)${NC}"
else
  echo -e "${YELLOW}⚠ plannotator installed but not in PATH${NC}"
  echo -e "${YELLOW}  Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)${NC}"
fi

if [ "$WITH_PLUGIN" = true ]; then
  echo ""
  echo -e "${BLUE}━━ Claude Code Plugin Setup ━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
  echo -e "Run these commands inside Claude Code:"
  echo ""
  echo -e "  ${GREEN}/plugin marketplace add backnotprop/plannotator${NC}"
  echo -e "  ${GREEN}/plugin install plannotator@plannotator${NC}"
  echo ""
  echo -e "${YELLOW}⚠ IMPORTANT: Restart Claude Code after plugin install${NC}"
  echo ""
  echo -e "${GRAY}Alternative (manual hook): run ./setup-hook.sh${NC}"
fi

if [ "$WITH_GEMINI" = true ]; then
  echo ""
  echo -e "${BLUE}━━ Gemini CLI Integration ━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
  if [ -f "${SCRIPT_DIR}/setup-gemini-hook.sh" ]; then
    bash "${SCRIPT_DIR}/setup-gemini-hook.sh"
  else
    echo -e "${YELLOW}⚠ setup-gemini-hook.sh not found at ${SCRIPT_DIR}${NC}"
    echo -e "${GRAY}  Run it manually from the scripts/ directory${NC}"
  fi
fi

if [ "$WITH_CODEX" = true ]; then
  echo ""
  echo -e "${BLUE}━━ Codex CLI Integration ━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
  if [ -f "${SCRIPT_DIR}/setup-codex-hook.sh" ]; then
    bash "${SCRIPT_DIR}/setup-codex-hook.sh"
  else
    echo -e "${YELLOW}⚠ setup-codex-hook.sh not found at ${SCRIPT_DIR}${NC}"
    echo -e "${GRAY}  Run it manually from the scripts/ directory${NC}"
  fi
fi

if [ "$WITH_OPENCODE" = true ]; then
  echo ""
  echo -e "${BLUE}━━ OpenCode Plugin Integration ━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
  if [ -f "${SCRIPT_DIR}/setup-opencode-plugin.sh" ]; then
    bash "${SCRIPT_DIR}/setup-opencode-plugin.sh"
  else
    echo -e "${YELLOW}⚠ setup-opencode-plugin.sh not found at ${SCRIPT_DIR}${NC}"
    echo -e "${GRAY}  Run it manually from the scripts/ directory${NC}"
  fi
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo -e "${GRAY}Next steps:${NC}"

if [ "$WITH_PLUGIN" = false ] && [ "$WITH_GEMINI" = false ] && [ "$WITH_CODEX" = false ] && [ "$WITH_OPENCODE" = false ]; then
  echo -e "  ${BLUE}1.${NC} Run ${GREEN}./setup-hook.sh${NC} to configure Claude Code hooks"
  echo -e "  ${BLUE}   ${NC} Or run ${GREEN}./install.sh --all${NC} to set up all AI tool integrations"
  echo -e "  ${BLUE}2.${NC} Run ${GREEN}./check-status.sh${NC} to verify everything is working"
  echo -e "  ${BLUE}3.${NC} Install Obsidian for plan auto-save: ${BLUE}https://obsidian.md/download${NC}"
else
  echo -e "  ${BLUE}1.${NC} Run ${GREEN}./check-status.sh${NC} to verify all integrations"
  echo -e "  ${BLUE}2.${NC} Restart any AI tools that were configured above"
  if ! command -v obsidian &>/dev/null 2>&1 && [ ! -d "/Applications/Obsidian.app" ]; then
    echo -e "  ${BLUE}3.${NC} Install Obsidian for plan auto-save: ${BLUE}https://obsidian.md/download${NC}"
  fi
fi
echo ""
