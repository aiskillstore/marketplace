#!/usr/bin/env bash
# mcp-setup.sh — Vibe Kanban MCP 서버 설정 스크립트
# 사용법: bash mcp-setup.sh [--claude|--codex|--all]
#
# 예시:
#   bash mcp-setup.sh --claude   # Claude Code 설정만
#   bash mcp-setup.sh --codex    # Codex CLI 설정만
#   bash mcp-setup.sh --all      # 모든 에이전트 설정

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}ℹ️  $*${NC}"; }
ok()    { echo -e "${GREEN}✅ $*${NC}"; }
warn()  { echo -e "${YELLOW}⚠️  $*${NC}"; }
error() { echo -e "${RED}❌ $*${NC}" >&2; }

# ─── 인자 파싱 ───────────────────────────────────────────────────────────────
SETUP_CLAUDE=false
SETUP_CODEX=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude) SETUP_CLAUDE=true; shift ;;
    --codex)  SETUP_CODEX=true; shift ;;
    --all)    SETUP_CLAUDE=true; SETUP_CODEX=true; shift ;;
    *) shift ;;
  esac
done

# 기본값: 모두 설정
if [[ "$SETUP_CLAUDE" == "false" && "$SETUP_CODEX" == "false" ]]; then
  SETUP_CLAUDE=true
  SETUP_CODEX=true
fi

echo "╔══════════════════════════════════════╗"
echo "║  Vibe Kanban MCP 설정                ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ─── MCP 설정 JSON 생성 ──────────────────────────────────────────────────────
MCP_CONFIG=$(cat <<'EOF'
{
  "vibe-kanban": {
    "command": "npx",
    "args": ["vibe-kanban", "--mcp"],
    "env": {
      "MCP_HOST": "127.0.0.1",
      "MCP_PORT": "3001"
    }
  }
}
EOF
)

# ─── Claude Code 설정 ────────────────────────────────────────────────────────
if [[ "$SETUP_CLAUDE" == "true" ]]; then
  info "Claude Code MCP 설정 중..."
  
  CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"
  CLAUDE_DIR="$HOME/.claude"
  
  # 디렉토리 생성
  mkdir -p "$CLAUDE_DIR"
  
  if [[ -f "$CLAUDE_CONFIG" ]]; then
    # 기존 설정에 병합
    if command -v jq &>/dev/null; then
      EXISTING=$(cat "$CLAUDE_CONFIG")
      MERGED=$(echo "$EXISTING" | jq --argjson vk "$MCP_CONFIG" '.mcpServers += $vk')
      echo "$MERGED" > "$CLAUDE_CONFIG"
      ok "Claude Code: 기존 설정에 병합됨"
    else
      warn "jq가 없어 수동 병합이 필요합니다."
      echo "다음 내용을 $CLAUDE_CONFIG의 mcpServers에 추가하세요:"
      echo "$MCP_CONFIG"
    fi
  else
    # 새 설정 파일 생성
    cat > "$CLAUDE_CONFIG" <<EOF
{
  "mcpServers": $MCP_CONFIG
}
EOF
    ok "Claude Code: 새 설정 파일 생성됨"
  fi
  
  echo "  설정 파일: $CLAUDE_CONFIG"
  echo ""
fi

# ─── Codex CLI 설정 ──────────────────────────────────────────────────────────
if [[ "$SETUP_CODEX" == "true" ]]; then
  info "Codex CLI MCP 설정 중..."
  
  CODEX_CONFIG="$HOME/.codex/config.toml"
  CODEX_DIR="$HOME/.codex"
  
  # 디렉토리 생성
  mkdir -p "$CODEX_DIR"
  
  # TOML 형식으로 변환
  CODEX_MCP_CONFIG=$(cat <<'EOF'

# Vibe Kanban MCP Server
[[mcp_servers]]
name = "vibe-kanban"
command = "npx"
args = ["vibe-kanban", "--mcp"]

[mcp_servers.env]
MCP_HOST = "127.0.0.1"
MCP_PORT = "3001"
EOF
)

  if [[ -f "$CODEX_CONFIG" ]]; then
    # 기존 설정에 추가
    if ! grep -q "vibe-kanban" "$CODEX_CONFIG"; then
      echo "$CODEX_MCP_CONFIG" >> "$CODEX_CONFIG"
      ok "Codex CLI: 기존 설정에 추가됨"
    else
      warn "Codex CLI: 이미 vibe-kanban 설정이 존재합니다."
    fi
  else
    # 새 설정 파일 생성
    cat > "$CODEX_CONFIG" <<EOF
# Codex CLI Configuration
$CODEX_MCP_CONFIG
EOF
    ok "Codex CLI: 새 설정 파일 생성됨"
  fi
  
  echo "  설정 파일: $CODEX_CONFIG"
  echo ""
fi

# ─── 완료 ────────────────────────────────────────────────────────────────────
ok "MCP 설정 완료!"
echo ""
echo "다음 단계:"
echo "  1. 에이전트를 재시작하세요"
echo "  2. 'npx vibe-kanban --mcp'로 MCP 서버 시작"
echo "  3. 에이전트에서 vibe-kanban MCP 도구 사용 가능"
echo ""
echo "MCP 도구 목록:"
echo "  - vk_list_cards: 카드 목록 조회"
echo "  - vk_create_card: 새 카드 생성"
echo "  - vk_move_card: 카드 이동"
echo "  - vk_get_logs: 에이전트 로그 조회"
