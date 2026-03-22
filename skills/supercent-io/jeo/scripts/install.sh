#!/usr/bin/env bash
# JEO Skill — Master Installation Script
# Installs and configures: ralph, omc, omx, ohmg, bmad, agent-browser, playwriter, plannotator, agentation
# Usage: bash install.sh [--all] [--with-omc] [--with-plannotator] [--with-browser] [--with-agentation] [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SKILLS_ROOT="$(dirname "$SKILL_DIR")"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
err()  { echo -e "${RED}✗${NC} $*"; }
info() { echo -e "${BLUE}→${NC} $*"; }

DRY_RUN=false
INSTALL_ALL=false
INSTALL_OMC=false
INSTALL_PLANNOTATOR=false
INSTALL_AGENTATION=false
INSTALL_BROWSER=false
INSTALL_BMAD=false
INSTALL_OMX=false
INSTALL_OHMG=false

for arg in "$@"; do
  case $arg in
    --all)             INSTALL_ALL=true ;;
    --with-omc)        INSTALL_OMC=true ;;
    --with-plannotator) INSTALL_PLANNOTATOR=true ;;
    --with-browser)    INSTALL_BROWSER=true ;;
    --with-bmad)       INSTALL_BMAD=true ;;
    --with-omx)        INSTALL_OMX=true ;;
    --with-ohmg)       INSTALL_OHMG=true ;;
    --with-agentation) INSTALL_AGENTATION=true ;;
    --dry-run)         DRY_RUN=true ;;
    -h|--help)
      echo "JEO Master Installer"
      echo "Usage: bash install.sh [options]"
      echo "Options:"
      echo "  --all              Install all components"
      echo "  --with-omc         Install oh-my-claudecode (Claude Code)"
      echo "  --with-plannotator Install plannotator CLI"
      echo "  --with-browser     Install agent-browser + playwriter"
      echo "  --with-bmad        Install BMAD orchestrator"
      echo "  --with-omx         Install omx (OpenCode multi-agent)"
      echo "  --with-ohmg        Install ohmg (Gemini multi-agent)"
      echo "  --with-agentation  Install agentation MCP (UI annotation \u2194 agent)"
      echo "  --dry-run          Preview without executing"
      exit 0
      ;;
  esac
done

if $INSTALL_ALL; then
  INSTALL_OMC=true; INSTALL_PLANNOTATOR=true
  INSTALL_BROWSER=true; INSTALL_BMAD=true; INSTALL_OMX=true; INSTALL_OHMG=true; INSTALL_AGENTATION=true
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   JEO Skill — Integrated Orchestration  ║"
echo "║   Version 1.1.0                          ║"
echo "╚══════════════════════════════════════════╝"
echo ""

run() {
  if $DRY_RUN; then
    echo -e "${YELLOW}[DRY-RUN]${NC} $*"
  else
    eval "$@"
  fi
}

# ── Detect OS ─────────────────────────────────────────────────────────────────
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then OS="macos"
elif [[ "$OSTYPE" == "linux"* ]]; then OS="linux"
elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]]; then OS="windows"
fi
info "Detected OS: $OS"

# ── Check prerequisites ────────────────────────────────────────────────────────
info "Checking prerequisites..."
MISSING_DEPS=()
if command -v node >/dev/null 2>&1; then
  NODE_VER=$(node --version 2>/dev/null | grep -oE '[0-9]+' | head -1)
  if [[ -z "$NODE_VER" ]] || [[ "$NODE_VER" -lt 18 ]]; then
    MISSING_DEPS+=("node >=18 (현재: $(node --version 2>/dev/null || echo 'unknown'))")
  fi
else
  MISSING_DEPS+=("node >=18")
fi
command -v npm >/dev/null 2>&1  || MISSING_DEPS+=("npm")
command -v git >/dev/null 2>&1  || MISSING_DEPS+=("git")
command -v bash >/dev/null 2>&1 || MISSING_DEPS+=("bash")

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
  err "Missing required dependencies: ${MISSING_DEPS[*]}"
  echo "Install them first, then re-run this script."
  exit 1
fi
ok "Prerequisites satisfied"

# ── 1. omc (oh-my-claudecode) ──────────────────────────────────────────────────
if $INSTALL_OMC; then
  echo ""
  info "Installing omc (oh-my-claudecode)..."
  if command -v claude >/dev/null 2>&1; then
    echo "  Run these commands inside Claude Code:"
    echo "  /plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode"
    echo "  /plugin install oh-my-claudecode"
    echo "  /omc:omc-setup"
    ok "omc install instructions shown (Claude Code required)"
  else
    warn "claude CLI not found — install Claude Code first, then run omc setup manually"
  fi
fi

# ── 2. omx (oh-my-opencode) ───────────────────────────────────────────────────
if $INSTALL_OMX; then
  echo ""
  info "Installing omx (oh-my-opencode)..."
  if command -v bun >/dev/null 2>&1; then
    run "bunx oh-my-opencode setup 2>/dev/null || true"
    ok "omx (oh-my-opencode) configured"
  elif command -v npx >/dev/null 2>&1; then
    run "npx oh-my-opencode setup 2>/dev/null || true"
    ok "omx configured via npx"
  else
    warn "bun/npx not found — install bun first: curl -fsSL https://bun.sh/install | bash"
  fi
fi

# ── 3. ohmg (oh-my-ag / Gemini) ───────────────────────────────────────────────
if $INSTALL_OHMG; then
  echo ""
  info "Installing ohmg (oh-my-ag for Gemini CLI)..."
  if command -v bun >/dev/null 2>&1; then
    run "bunx oh-my-ag 2>/dev/null || true"
    ok "ohmg configured"
  else
    warn "bun not found — install bun first: curl -fsSL https://bun.sh/install | bash"
  fi
fi

# ── 4. plannotator ─────────────────────────────────────────────────────────────
if $INSTALL_PLANNOTATOR; then
  echo ""
  info "Installing plannotator..."
  PLANNOTATOR_INSTALL="$SKILLS_ROOT/plannotator/scripts/install.sh"
  PLANNOTATOR_INSTALLED=false
  if [[ -f "$PLANNOTATOR_INSTALL" ]]; then
    if run "bash '$PLANNOTATOR_INSTALL' --all"; then
      PLANNOTATOR_INSTALLED=true
      ok "plannotator installed via skills script"
    else
      err "plannotator install script failed: $PLANNOTATOR_INSTALL"
    fi
  else
    # Fallback: direct install
    if run "curl -fsSL https://plannotator.ai/install.sh | bash"; then
      PLANNOTATOR_INSTALLED=true
      ok "plannotator installed"
    else
      err "plannotator install failed — check https://plannotator.ai"
    fi
  fi

  export PATH="$HOME/.local/bin:$HOME/bin:$PATH"
  if ! $PLANNOTATOR_INSTALLED || ! command -v plannotator >/dev/null 2>&1; then
    err "plannotator is still unavailable after install attempt"
    exit 1
  fi
fi

# ── 5. agent-browser ──────────────────────────────────────────────────────────
if $INSTALL_BROWSER; then
  echo ""
  info "Installing agent-browser..."
  if command -v npm >/dev/null 2>&1; then
    run "npm install -g agent-browser 2>/dev/null || npx agent-browser --version 2>/dev/null || true"
    ok "agent-browser installed"
  else
    warn "npm not found"
  fi

  echo ""
  info "Installing playwriter..."
  if command -v npm >/dev/null 2>&1; then
    run "npm install -g playwriter 2>/dev/null || true"
    ok "playwriter installed"
  else
    warn "npm not found"
  fi
fi

# ── 7. bmad ───────────────────────────────────────────────────────────────────
if $INSTALL_BMAD; then
  echo ""
  info "Configuring BMAD orchestrator..."
  BMAD_SKILL="$SKILLS_ROOT/bmad-orchestrator/SKILL.md"
  if [[ -f "$BMAD_SKILL" ]]; then
    ok "BMAD skill available at: $BMAD_SKILL"
  else
    warn "BMAD skill not found — ensure skills-template is properly installed"
  fi
fi

# ── 8. agentation MCP ────────────────────────────────────────────────────────────────────────────
if $INSTALL_AGENTATION; then
  echo ""
  info "Installing agentation MCP..."
  if command -v npx >/dev/null 2>&1; then
    run "npx -y agentation-mcp doctor 2>/dev/null || npx -y agentation-mcp --version 2>/dev/null || true"
    ok "agentation-mcp (server) available via npx"
    info "Start server: npx agentation-mcp server"
    info "React component: auto-installed + injected by ensure-agentation.sh at VERIFY_UI time"
    info "Manual install: cd <your-app> && npm install agentation --save-dev"
    info "Manual inject:  import { Agentation } from 'agentation'; <Agentation endpoint=\"http://localhost:4747\" />"
  else
    warn "npx not found — install Node.js first"
  fi
fi

# ── 9. Setup platform integrations ────────────────────────────────────────────────────────────────────────────
if $INSTALL_ALL; then
  echo ""
  info "Setting up platform integrations..."
  run "bash '$SCRIPT_DIR/setup-claude.sh' 2>/dev/null || true"
  run "bash '$SCRIPT_DIR/setup-codex.sh' 2>/dev/null || true"
  run "bash '$SCRIPT_DIR/setup-gemini.sh' 2>/dev/null || true"
  run "bash '$SCRIPT_DIR/setup-opencode.sh' 2>/dev/null || true"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   JEO Installation Complete!             ║"
echo "╚══════════════════════════════════════════╝"
echo ""
ok "JEO skill installed successfully"
echo ""
echo "Next steps:"
echo "  1. bash scripts/check-status.sh    — Verify all integrations"
echo "  2. Restart your AI tools (Claude Code, Gemini CLI, OpenCode, Codex)"
echo "  3. Use keyword 'jeo' to activate the orchestration workflow"
echo "  4. Use keyword 'annotate' inside jeo to start agentation watch loop (agentui is a deprecated alias)"
echo ""
