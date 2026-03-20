#!/usr/bin/env bash
# health-check.sh — Vibe Kanban 서버 상태 확인 스크립트
# 사용법: bash health-check.sh [--port 3000] [--json]
#
# 예시:
#   bash health-check.sh
#   bash health-check.sh --port 3001
#   bash health-check.sh --json

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}ℹ️  $*${NC}"; }
ok()    { echo -e "${GREEN}✅ $*${NC}"; }
warn()  { echo -e "${YELLOW}⚠️  $*${NC}"; }
error() { echo -e "${RED}❌ $*${NC}" >&2; }

# ─── 인자 파싱 ───────────────────────────────────────────────────────────────
PORT="${VIBE_KANBAN_PORT:-3000}"
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --json) JSON_OUTPUT=true; shift ;;
    *) shift ;;
  esac
done

BASE_URL="http://localhost:$PORT"

# ─── JSON 출력 모드 ──────────────────────────────────────────────────────────
if [[ "$JSON_OUTPUT" == "true" ]]; then
  RESULT='{}'
  
  # 서버 상태
  if curl -s "$BASE_URL/api/health" &>/dev/null; then
    RESULT=$(echo "$RESULT" | jq '. + {"server": "running", "port": '"$PORT"'}')
  else
    RESULT=$(echo "$RESULT" | jq '. + {"server": "stopped", "port": '"$PORT"'}')
    echo "$RESULT"
    exit 1
  fi
  
  # 카드 수
  CARDS=$(curl -s "$BASE_URL/api/cards" 2>/dev/null | jq 'length' 2>/dev/null || echo "0")
  RESULT=$(echo "$RESULT" | jq '. + {"cards": '"$CARDS"'}')
  
  # Worktree 수
  if git rev-parse --git-dir &>/dev/null; then
    WT_COUNT=$(git worktree list | wc -l | tr -d ' ')
    RESULT=$(echo "$RESULT" | jq '. + {"worktrees": '"$WT_COUNT"'}')
  fi
  
  echo "$RESULT"
  exit 0
fi

# ─── 일반 출력 모드 ──────────────────────────────────────────────────────────
echo "╔══════════════════════════════════════╗"
echo "║  Vibe Kanban 상태 확인               ║"
echo "╚══════════════════════════════════════╝"
echo ""

# 서버 상태
info "서버 상태 확인: $BASE_URL"
if curl -s --connect-timeout 2 "$BASE_URL/api/health" &>/dev/null; then
  ok "서버: 실행 중 (포트 $PORT)"
else
  error "서버: 응답 없음"
  echo ""
  echo "서버를 시작하려면:"
  echo "  npx vibe-kanban"
  echo "  또는"
  echo "  bash scripts/start.sh"
  exit 1
fi

# 카드 상태
echo ""
info "카드 상태:"
CARDS_JSON=$(curl -s "$BASE_URL/api/cards" 2>/dev/null || echo "[]")

if command -v jq &>/dev/null; then
  TODO=$(echo "$CARDS_JSON" | jq '[.[] | select(.column == "todo")] | length')
  IN_PROGRESS=$(echo "$CARDS_JSON" | jq '[.[] | select(.column == "in_progress")] | length')
  REVIEW=$(echo "$CARDS_JSON" | jq '[.[] | select(.column == "review")] | length')
  DONE=$(echo "$CARDS_JSON" | jq '[.[] | select(.column == "done")] | length')
  
  echo "  To Do:       $TODO"
  echo "  In Progress: $IN_PROGRESS"
  echo "  Review:      $REVIEW"
  echo "  Done:        $DONE"
else
  TOTAL=$(echo "$CARDS_JSON" | grep -o '"id"' | wc -l | tr -d ' ')
  echo "  총 카드 수: $TOTAL"
fi

# Git worktree 상태
echo ""
info "Git Worktree 상태:"
if git rev-parse --git-dir &>/dev/null; then
  git worktree list | while read -r line; do
    if [[ "$line" == *"vk-"* ]] || [[ "$line" == *"vibe-kanban-"* ]]; then
      echo "  [VK] $line"
    fi
  done
  
  VK_COUNT=$(git worktree list | grep -E "(vk-|vibe-kanban-)" | wc -l | tr -d ' ')
  if [[ "$VK_COUNT" -eq 0 ]]; then
    echo "  Vibe Kanban worktree 없음"
  else
    echo "  총 VK worktree: $VK_COUNT"
  fi
else
  warn "Git 저장소가 아닙니다."
fi

# MCP 상태
echo ""
info "MCP 상태:"
MCP_PORT="${MCP_PORT:-3001}"
if curl -s --connect-timeout 2 "http://localhost:$MCP_PORT" &>/dev/null; then
  ok "MCP 서버: 실행 중 (포트 $MCP_PORT)"
else
  echo "  MCP 서버: 실행 안함"
  echo "  시작하려면: npx vibe-kanban --mcp"
fi

echo ""
ok "상태 확인 완료"
