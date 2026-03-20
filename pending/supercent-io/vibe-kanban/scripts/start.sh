#!/usr/bin/env bash
# vibe-kanban-start.sh — Vibe Kanban 서버 시작 래퍼
# 사용법: bash scripts/vibe-kanban-start.sh [--port 3000] [--remote]
#
# 예시:
#   bash scripts/vibe-kanban-start.sh
#   bash scripts/vibe-kanban-start.sh --port 3001
#   bash scripts/vibe-kanban-start.sh --remote

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}ℹ️  $*${NC}"; }
ok()    { echo -e "${GREEN}✅ $*${NC}"; }
warn()  { echo -e "${YELLOW}⚠️  $*${NC}"; }
error() { echo -e "${RED}❌ $*${NC}" >&2; }

# ─── 인자 파싱 ───────────────────────────────────────────────────────────────
PORT="${VIBE_KANBAN_PORT:-3000}"
REMOTE="${VIBE_KANBAN_REMOTE:-false}"
OPEN_BROWSER=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)   PORT="$2"; shift 2 ;;
    --remote) REMOTE=true; shift ;;
    --no-open) OPEN_BROWSER=false; shift ;;
    *) shift ;;
  esac
done

echo "╔══════════════════════════════════════╗"
echo "║  Vibe Kanban 시작                     ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ─── Node.js 확인 ────────────────────────────────────────────────────────────
if ! command -v node &>/dev/null; then
  error "Node.js가 필요합니다. https://nodejs.org 에서 설치하세요."
  exit 1
fi

NODE_MAJOR=$(node --version | sed 's/v//' | cut -d. -f1)
if [[ $NODE_MAJOR -lt 18 ]]; then
  error "Node.js 18+ 필요 (현재: $(node --version))"
  exit 1
fi
ok "Node.js: $(node --version)"

# ─── npx 확인 ────────────────────────────────────────────────────────────────
if ! command -v npx &>/dev/null; then
  error "npx가 필요합니다 (Node.js와 함께 설치됩니다)"
  exit 1
fi

# ─── 에이전트 인증 확인 ──────────────────────────────────────────────────────
echo ""
info "에이전트 인증 상태 확인..."

if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  ok "ANTHROPIC_API_KEY: 설정됨 (Claude 사용 가능)"
else
  warn "ANTHROPIC_API_KEY: 미설정 (Claude 에이전트 사용 불가)"
fi

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  ok "OPENAI_API_KEY: 설정됨 (Codex/GPT 사용 가능)"
else
  warn "OPENAI_API_KEY: 미설정 (Codex 에이전트 사용 불가)"
fi

echo ""

# ─── 환경 변수 설정 ──────────────────────────────────────────────────────────
export VIBE_KANBAN_PORT="$PORT"
export VIBE_KANBAN_REMOTE="$REMOTE"

# .env 파일 로드 (존재하는 경우)
if [[ -f ".env" ]]; then
  info ".env 파일 로드 중..."
  set -a
  source .env
  set +a
fi

# ─── 실행 정보 ───────────────────────────────────────────────────────────────
echo "설정:"
echo "  포트   : $PORT"
echo "  원격   : $REMOTE"
echo "  URL    : http://localhost:$PORT"
if [[ "$REMOTE" == "true" ]]; then
  warn "원격 연결 허용됨. 신뢰할 수 있는 네트워크에서만 사용하세요."
fi
echo ""

# ─── 브라우저 자동 오픈 (백그라운드) ────────────────────────────────────────
if [[ "$OPEN_BROWSER" == "true" ]]; then
  (
    sleep 3
    if command -v open &>/dev/null; then
      open "http://localhost:$PORT" 2>/dev/null || true
    elif command -v xdg-open &>/dev/null; then
      xdg-open "http://localhost:$PORT" 2>/dev/null || true
    fi
  ) &
fi

# ─── vibe-kanban 실행 ────────────────────────────────────────────────────────
info "Vibe Kanban 시작 중 (npx vibe-kanban)..."
echo "종료하려면 Ctrl+C"
echo ""

exec npx vibe-kanban
