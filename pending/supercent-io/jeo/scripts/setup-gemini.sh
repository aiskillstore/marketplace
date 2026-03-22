#!/usr/bin/env bash
# JEO Skill — Gemini CLI Hook & GEMINI.md Setup
# Configures: ExitPlanMode hook in ~/.gemini/settings.json + JEO instructions in GEMINI.md
# Usage: bash setup-gemini.sh [--dry-run] [--hook-only] [--md-only]

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
info() { echo -e "${BLUE}→${NC} $*"; }

DRY_RUN=false; HOOK_ONLY=false; MD_ONLY=false
for arg in "$@"; do
  case $arg in --dry-run) DRY_RUN=true ;; --hook-only) HOOK_ONLY=true ;; --md-only) MD_ONLY=true ;; esac
done

JEO_SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

GEMINI_SETTINGS="${HOME}/.gemini/settings.json"
GEMINI_MD="${HOME}/.gemini/GEMINI.md"

echo ""
echo "JEO — Gemini CLI Setup"
echo "======================"

# ── 1. Check Gemini CLI ───────────────────────────────────────────────────────
if ! command -v gemini >/dev/null 2>&1; then
  warn "gemini CLI not found. Install via: npm install -g @google/gemini-cli"
fi

# NOTE: Gemini CLI uses AfterAgent hook (not ExitPlanMode, which is Claude Code-only).
# The primary method is agent direct blocking call — do NOT use & (background).
# Manual blocking call (same-turn feedback, auto-installs plannotator if missing):
#   bash .agent-skills/jeo/scripts/plannotator-plan-loop.sh plan.md /tmp/plannotator_feedback.txt 3

# ── 2. Configure ~/.gemini/settings.json ─────────────────────────────────────
if ! $MD_ONLY; then
  info "Configuring ~/.gemini/settings.json..."

  if $DRY_RUN; then
    echo -e "${YELLOW}[DRY-RUN]${NC} Would add AfterAgent hook to $GEMINI_SETTINGS"
  else
    mkdir -p "$(dirname "$GEMINI_SETTINGS")"
    [[ -f "$GEMINI_SETTINGS" ]] && cp "$GEMINI_SETTINGS" "${GEMINI_SETTINGS}.jeo.bak"

    # Create hook helper script (avoids plannotator plan - hanging on empty stdin)
    GEMINI_HOOK_DIR="${HOME}/.gemini/hooks"
    mkdir -p "$GEMINI_HOOK_DIR"
    cat > "${GEMINI_HOOK_DIR}/jeo-plannotator.sh" << 'HOOKEOF'
#!/usr/bin/env bash
# JEO AfterAgent backup hook — runs plannotator if plan.md exists in cwd
# Phase guard: only fire during PLAN phase to prevent conflict with agentation.
# Repeat guard: same plan hash + terminal gate status must not reopen plannotator.

JEO_STATE="${PWD}/.omc/state/jeo-state.json"
if [[ ! -f "$JEO_STATE" ]]; then
  exit 0  # JEO is not active — no state file
fi
PHASE=$(python3 -c "
import json, sys
try:
    d = json.load(open('$JEO_STATE'))
    print(d.get('phase', 'unknown'))
except Exception:
    print('unknown')
" 2>/dev/null || echo "unknown")

# 화이트리스트: "plan"일 때만 실행, 그 외(unknown, done, execute 등) 모두 종료
if [[ "$PHASE" != "plan" ]]; then
  exit 0
fi

# AfterAgent 이중 실행 방지: 에이전트가 직접 호출한 턴이면 건너뜀
LOCK_FILE="/tmp/jeo-plannotator-direct.lock"
if [[ -f "$LOCK_FILE" ]]; then
  rm -f "$LOCK_FILE"
  exit 0
fi

PLAN_FILE="$(pwd)/plan.md"
test -f "$PLAN_FILE" || exit 0
LOOP_SCRIPT_CANDIDATES=(
  "$(pwd)/.agent-skills/jeo/scripts/plannotator-plan-loop.sh"
  "$HOME/.codex/skills/jeo/scripts/plannotator-plan-loop.sh"
  "$HOME/.agent-skills/jeo/scripts/plannotator-plan-loop.sh"
)

LOOP_SCRIPT=""
for candidate in "${LOOP_SCRIPT_CANDIDATES[@]}"; do
  if [[ -f "$candidate" ]]; then
    LOOP_SCRIPT="$candidate"
    break
  fi
done

if [[ -n "$LOOP_SCRIPT" ]]; then
  set +e
  bash "$LOOP_SCRIPT" "$PLAN_FILE" /tmp/plannotator_feedback.txt 3
  LOOP_RC=$?
  set -e
  if [[ "$LOOP_RC" -eq 0 ]]; then
    echo "[JEO] plannotator approved=true (written to jeo-state.json)"
  elif [[ "$LOOP_RC" -eq 10 ]]; then
    echo "[JEO] plannotator approved=false — feedback written to jeo-state.json"
  elif [[ "$LOOP_RC" -eq 32 ]]; then
    echo "[JEO] plannotator unavailable: localhost bind blocked (sandbox/CI)." >&2
    echo "[JEO] run PLAN gate in local TTY to use manual fallback approve/feedback." >&2
  fi
else
  PLANNOTATOR_RUNTIME_HOME="/tmp/jeo-$(python3 -c "import hashlib,os; print(f'/tmp/jeo-{hashlib.md5(os.getcwd().encode()).hexdigest()[:8]}')")/.plannotator"
  mkdir -p "$PLANNOTATOR_RUNTIME_HOME"
  python3 -c "
import json, sys
plan = open(sys.argv[1]).read()
sys.stdout.write(json.dumps({'tool_input': {'plan': plan, 'permission_mode': 'acceptEdits'}}))
" "$PLAN_FILE" | env HOME="$PLANNOTATOR_RUNTIME_HOME" PLANNOTATOR_HOME="$PLANNOTATOR_RUNTIME_HOME" plannotator > /tmp/plannotator_feedback.txt 2>&1 || true
fi
HOOKEOF
    chmod +x "${GEMINI_HOOK_DIR}/jeo-plannotator.sh"

    # Create agentation AfterAgent hook (phase-guarded + submit-gated)
    cat > "${GEMINI_HOOK_DIR}/jeo-agentation.sh" << 'AGENTHOOKEOF'
#!/usr/bin/env bash
# JEO AfterAgent hook — check pending agentation annotations during VERIFY_UI phase
# Submit gate: only process annotations after explicit Send Annotations / onSubmit confirmation.

# Phase guard: only fire during verify_ui phase
JEO_STATE="${PWD}/.omc/state/jeo-state.json"
if [[ -f "$JEO_STATE" ]]; then
  PHASE=$(python3 -c "import json; print(json.load(open('$JEO_STATE')).get('phase',''))" 2>/dev/null || echo "")
  SUBMIT_GATE=$(python3 -c "import json; print(json.load(open('$JEO_STATE')).get('agentation',{}).get('submit_gate_status',''))" 2>/dev/null || echo "")
  if [[ "$PHASE" != "verify_ui" ]]; then
    exit 0
  fi
  if [[ "$SUBMIT_GATE" != "submitted" ]]; then
    exit 0
  fi
else
  exit 0  # No state file means JEO is not active
fi

# Check agentation server and report pending annotations
PENDING=$(curl -sf --connect-timeout 2 http://localhost:4747/pending 2>/dev/null) || exit 0
COUNT=$(echo "$PENDING" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('count',0))" 2>/dev/null || echo 0)

if [ "$COUNT" -gt 0 ]; then
  echo "=== AGENTATION: ${COUNT} annotations pending ==="
  echo "$PENDING" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for i, a in enumerate(d.get('annotations', [])):
    sev = a.get('severity', 'suggestion')
    print(f'  [{i+1}] [{sev}] {a.get(\"element\",\"?\")} ({a.get(\"elementPath\",\"?\")[:60]})')
    print(f'      {a.get(\"comment\",\"\")[:80]}')
" 2>/dev/null
  echo "=== END ==="
fi
AGENTHOOKEOF
    chmod +x "${GEMINI_HOOK_DIR}/jeo-agentation.sh"

    python3 - <<PYEOF
import json, os

settings_path = os.path.expanduser("~/.gemini/settings.json")
hook_path = os.path.expanduser("~/.gemini/hooks/jeo-plannotator.sh")
try:
    with open(settings_path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

hooks = settings.setdefault("hooks", {})
# AfterAgent is the correct Gemini CLI hook (ExitPlanMode is Claude Code-only)
after_agent = hooks.setdefault("AfterAgent", [])

# Migrate old-format entries (flat {"type":"command",...}) to new matcher format
migrated = False
new_after_agent = []
for entry in after_agent:
    if "matcher" in entry and "hooks" in entry:
        # Ensure timeout on plannotator hooks (1800s for blocking UI wait)
        for h in entry.get("hooks", []):
            if "plannotator" in h.get("command", "") and "timeout" not in h:
                h["timeout"] = 1800
                migrated = True
        new_after_agent.append(entry)
    elif entry.get("type") == "command":
        # Old format -> wrap in new matcher format
        if "timeout" not in entry:
            entry["timeout"] = 300
        new_after_agent.append({"matcher": "", "hooks": [entry]})
        migrated = True
    else:
        new_after_agent.append(entry)
if migrated:
    hooks["AfterAgent"] = new_after_agent
    after_agent = new_after_agent
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    print("\\u2713 AfterAgent hooks migrated to new matcher format with timeouts")

# Check if jeo plannotator hook already exists (old or new form)
planno_exists = any(
    any(
        h.get("command", "").startswith("plannotator") or "jeo-plannotator" in h.get("command", "")
        for h in entry.get("hooks", [])
    )
    for entry in after_agent
)

if not planno_exists:
    after_agent.append({
        "matcher": "",
        "hooks": [{
            "name": "plannotator-review",
            "type": "command",
            "command": f"bash {hook_path}",
            "timeout": 1800,
            "description": "PLAN phase backup gate with no-repeat hash guard"
        }]
    })
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    print("✓ plannotator AfterAgent hook added to ~/.gemini/settings.json")
else:
    print("\u2713 plannotator hook already present")

# Add agentation AfterAgent hook (phase-guarded + submit-gated)
agentation_hook_path = os.path.expanduser("~/.gemini/hooks/jeo-agentation.sh")
agentation_exists = any(
    any(
        "jeo-agentation" in h.get("command", "")
        for h in entry.get("hooks", [])
    )
    for entry in after_agent
)
if not agentation_exists:
    after_agent.append({
        "matcher": "",
        "hooks": [{
            "name": "agentation-check",
            "type": "command",
            "command": f"bash {agentation_hook_path}",
            "timeout": 300,
            "description": "VERIFY_UI submit gate opened: check pending agentation annotations"
        }]
    })
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    print("\u2713 agentation AfterAgent hook added to ~/.gemini/settings.json")
else:
    print("\u2713 agentation hook already present")

# Add agentation MCP server if missing
mcp_servers = settings.setdefault("mcpServers", {})
if "agentation" not in mcp_servers:
    mcp_servers["agentation"] = {
        "command": "npx",
        "args": ["-y", "agentation-mcp", "server"]
    }
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    print("\u2713 agentation MCP server added to ~/.gemini/settings.json")
else:
    print("\u2713 agentation MCP already present")
PYEOF
    ok "Gemini CLI settings updated"
  fi
fi

# ── 3. Update GEMINI.md ───────────────────────────────────────────────────────
if ! $HOOK_ONLY; then
  info "Updating ~/.gemini/GEMINI.md..."

  JEO_SECTION='
## JEO Orchestration Workflow

Keyword: `jeo` | Tool: Gemini CLI

JEO provides integrated AI agent orchestration across all AI tools.

### Workflow Phases

**PLAN** (plannotator — 직접 blocking 호출 필수):
1. `plan.md` 작성 (목표, 단계, 리스크, 완료 기준 포함)
2. PLAN gate 실행 (& 절대 금지, plannotator 없으면 자동 설치 후 계속 진행):
  bash .agent-skills/jeo/scripts/plannotator-plan-loop.sh plan.md /tmp/plannotator_feedback.txt 3
  # 동작 보장:
  # - approve/feedback 입력까지 반드시 대기
  # - 같은 plan hash 에 이미 approved/feedback/infrastructure_blocked가 기록돼 있으면 재실행 금지
  # - plan.md 내용이 바뀔 때만 gate_status를 pending으로 리셋
  # - 세션 종료 시 자동 재시작 (최대 3회)
  # - 3회 종료 시 PLAN 종료 여부를 사용자에게 확인
  # - exit 32 시 localhost bind 차단(sandbox/CI): local TTY에서 수동 PLAN gate 실행
3. /tmp/plannotator_feedback.txt 읽기
4. "approved":true → EXECUTE 진입 / 미승인 → 피드백 반영 후 plan.md 수정 후 2번 반복
5. PLAN gate exit 32면 인프라 차단이므로 local TTY에서 PLAN gate 재실행
NEVER skip plannotator. NEVER proceed to EXECUTE without approved=true.

**EXECUTE** (BMAD for Gemini):
- BMAD is the primary orchestration fallback when omc team is unavailable
- `/workflow-init` — Initialize BMAD structured workflow
- `/workflow-status` — Check current phase
- Phases: Analysis → Planning → Solutioning → Implementation

**VERIFY** (agent-browser):
- `agent-browser snapshot http://localhost:3000`
- UI/기능 정상 여부 확인

**CLEANUP** (worktree):
- After all work: `bash '"${JEO_SKILL_DIR}"'/scripts/worktree-cleanup.sh`

**ANNOTATE** (agentation watch loop — HTTP API 폴백):
When user says "annotate" or "agentui" (deprecated alias) or asks to process UI annotations:
1. Set `.omc/state/jeo-state.json` → `phase="verify_ui"` and `agentation.submit_gate_status="waiting_for_submit"`
2. Wait for the human to click **Send Annotations** / trigger `onSubmit`
3. Only after that explicit submit signal, reply `ANNOTATE_READY` and update `agentation.submit_gate_status="submitted"`
4. Then GET http://localhost:4747/pending — check count
5. For each annotation: PATCH status:acknowledged, fix code via elementPath, PATCH status:resolved + resolution
6. Repeat until count=0. Emit `AGENTUI_READY` when done.
NEVER poll `/pending` before submit gate opens. NEVER treat draft annotations as actionable.

### ohmg Integration
For Gemini multi-agent orchestration:
```bash
bunx oh-my-ag           # Initialize ohmg
/coordinate "<task>"    # Coordinate multi-agent task
```
'

  if $DRY_RUN; then
    echo -e "${YELLOW}[DRY-RUN]${NC} Would append JEO section to $GEMINI_MD"
  else
    mkdir -p "$(dirname "$GEMINI_MD")"
    [[ -f "$GEMINI_MD" ]] && cp "$GEMINI_MD" "${GEMINI_MD}.jeo.bak"

    if [[ -f "$GEMINI_MD" ]] && grep -q "^## JEO Orchestration Workflow" "$GEMINI_MD"; then
      GEMINI_MD="$GEMINI_MD" JEO_SECTION="$JEO_SECTION" python3 - <<'PYEOF'
import os
import re

path = os.environ["GEMINI_MD"]
section = os.environ["JEO_SECTION"].strip()
text = open(path, encoding="utf-8").read()
pattern = re.compile(r"\n## JEO Orchestration Workflow\n.*?\Z", re.S)
updated = pattern.sub("\n" + section + "\n", text.rstrip() + "\n")
with open(path, "w", encoding="utf-8") as f:
    f.write(updated)
PYEOF
      ok "JEO section synced in ~/.gemini/GEMINI.md"
    else
      echo "$JEO_SECTION" >> "$GEMINI_MD"
      ok "JEO instructions added to ~/.gemini/GEMINI.md"
    fi
  fi
fi

echo ""
echo "Gemini CLI usage after setup:"
echo "  gemini --approval-mode plan    ← Plan mode (plannotator fires on exit)"
echo "  /workflow-init                 ← BMAD orchestration"
echo "  bunx oh-my-ag                  ← ohmg multi-agent (Gemini)"
echo ""
ok "Gemini CLI setup complete"
echo ""
