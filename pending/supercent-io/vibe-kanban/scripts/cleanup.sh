#!/usr/bin/env bash
# cleanup.sh — Vibe Kanban worktree 정리 스크립트
# 사용법: bash cleanup.sh [--all] [--dry-run]
#
# 예시:
#   bash cleanup.sh              # 병합된 worktree만 정리
#   bash cleanup.sh --all        # 모든 vibe-kanban worktree 정리
#   bash cleanup.sh --dry-run    # 정리할 항목만 표시 (실제 삭제 안함)

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}ℹ️  $*${NC}"; }
ok()    { echo -e "${GREEN}✅ $*${NC}"; }
warn()  { echo -e "${YELLOW}⚠️  $*${NC}"; }
error() { echo -e "${RED}❌ $*${NC}" >&2; }

# ─── 인자 파싱 ───────────────────────────────────────────────────────────────
CLEAN_ALL=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)     CLEAN_ALL=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) shift ;;
  esac
done

echo "╔══════════════════════════════════════╗"
echo "║  Vibe Kanban Worktree 정리           ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ─── Git 저장소 확인 ─────────────────────────────────────────────────────────
if ! git rev-parse --git-dir &>/dev/null; then
  error "Git 저장소가 아닙니다."
  exit 1
fi

# ─── Worktree 목록 조회 ──────────────────────────────────────────────────────
info "현재 worktree 목록:"
git worktree list
echo ""

# ─── 정리 대상 식별 ──────────────────────────────────────────────────────────
WORKTREES=$(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2-)
VK_WORKTREES=()

while IFS= read -r wt; do
  if [[ "$wt" == *"vk-"* ]] || [[ "$wt" == *"vibe-kanban-"* ]]; then
    VK_WORKTREES+=("$wt")
  fi
done <<< "$WORKTREES"

if [[ ${#VK_WORKTREES[@]} -eq 0 ]]; then
  ok "정리할 Vibe Kanban worktree가 없습니다."
  exit 0
fi

info "Vibe Kanban worktree 발견: ${#VK_WORKTREES[@]}개"
for wt in "${VK_WORKTREES[@]}"; do
  echo "  - $wt"
done
echo ""

# ─── 정리 실행 ───────────────────────────────────────────────────────────────
CLEANED=0

for wt in "${VK_WORKTREES[@]}"; do
  # 브랜치명 추출
  BRANCH=$(git worktree list | grep "$wt" | awk '{print $3}' | tr -d '[]')
  
  # 병합 여부 확인 (--all이 아닌 경우)
  if [[ "$CLEAN_ALL" == "false" ]]; then
    if ! git branch --merged main 2>/dev/null | grep -q "$BRANCH"; then
      warn "스킵: $wt (병합되지 않음)"
      continue
    fi
  fi
  
  if [[ "$DRY_RUN" == "true" ]]; then
    info "[DRY-RUN] 삭제 예정: $wt"
  else
    info "정리 중: $wt"
    git worktree remove "$wt" --force 2>/dev/null || true
    git branch -D "$BRANCH" 2>/dev/null || true
    ((CLEANED++))
  fi
done

echo ""

# ─── Worktree prune ──────────────────────────────────────────────────────────
if [[ "$DRY_RUN" == "false" ]]; then
  info "git worktree prune 실행..."
  git worktree prune
fi

# ─── 결과 출력 ───────────────────────────────────────────────────────────────
if [[ "$DRY_RUN" == "true" ]]; then
  info "DRY-RUN 모드: 실제 삭제 없음"
else
  ok "정리 완료: ${CLEANED}개 worktree 삭제됨"
fi

echo ""
info "현재 worktree 목록:"
git worktree list
