# JEO Workflow — Detailed Reference

## Complete Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      JEO WORKFLOW                               │
│                                                                 │
│  [START] User activates "jeo" keyword with task description     │
│                          │                                      │
│          ┌───────────────▼──────────────────┐                  │
│          │         PHASE 1: PLAN             │                  │
│          │   ralph creates plan.md           │                  │
│          │   plannotator reviews visually    │                  │
│          │   same hash never reopens gate    │                  │
│          │   ┌──────────────────────────┐   │                  │
│          │   │  Approve → continue      │   │                  │
│          │   │  Feedback → re-plan      │   │                  │
│          │   └──────────────────────────┘   │                  │
│          └───────────────┬──────────────────┘                  │
│                          │                                      │
│          ┌───────────────▼──────────────────┐                  │
│          │         PHASE 2: EXECUTE          │                  │
│          │                                   │                  │
│          │  team available?                  │                  │
│          │  ├─ YES: /omc:team N:executor    │                  │
│          │  │       staged pipeline          │                  │
│          │  └─ NO:  /bmad /workflow-init    │                  │
│          │          Analysis→Planning→       │                  │
│          │          Solutioning→Implementation│                 │
│          └───────────────┬──────────────────┘                  │
│                          │                                      │
│          │         PHASE 3: VERIFY           │                  │
│          │   agent-browser snapshot <url>    │                  │
│          │   UI/기능 동작 확인               │                  │
│          │                                   │                  │
│          │   [annotate keyword? (agentui alias)]│                │
│          │   └─ YES: VERIFY_UI (agentation)  │                  │
│          │       wait for onSubmit first     │                  │
│          │       ack → fix → resolve         │                  │
│          └───────────────┬──────────────────┘                  │
│                          │                                      │
│          ┌───────────────▼──────────────────┐                  │
│          │         PHASE 4: CLEANUP          │                  │
│          │   bash scripts/worktree-cleanup.sh│                  │
│          │   clean worktrees only by default │                  │
│          │   git worktree prune              │                  │
│          └───────────────┬──────────────────┘                  │
│                          │                                      │
│                       [DONE]                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## annotate — agentation Watch Loop (VERIFY_UI Sub-Phase)

```
annotate keyword detected (or agentui alias — or user requests UI annotation review)
    │
    ▼
[PREFLIGHT]  3-step check before entering watch loop:
    │  1. GET /health         → server running?
    │  2. GET /sessions       → <Agentation> component mounted?
    │  3. GET /pending        → baseline annotation count
    │
    ├─ FAIL (server down) → retry 3x, 5s interval → ERROR (exit with message)
    │
    ▼  OK → update jeo-state.json: phase="verify_ui", agentation.active=true
[SUBMIT GATE]  wait for explicit Send Annotations / onSubmit
         state: agentation.submit_gate_status="waiting_for_submit"
    │
    ├─ no submit yet → stay idle, do not poll /pending
    │
    ▼  submit observed → set submit_gate_status="submitted"
[WATCH]  agentation_watch_annotations({batchWindowSeconds:10, timeoutSeconds:120})
         blocking — waits for submitted annotations or timeout
    │
    ├─ Annotations received (sorted by severity: blocking → important → suggestion):
    │   │
    │   ▼
    │  [ACK]   agentation_acknowledge_annotation({id})
    │          → status: 'acknowledged' → spinner shown in toolbar
    │   │
    │   ▼
    │  [FIND]  grep/AST search using annotation.elementPath (CSS selector)
    │          annotation.comment → understand desired change
    │   │
    │   ▼
    │  [FIX]   apply code change to matched component/file
    │   │
    │   ▼
    │  [RESOLVE] agentation_resolve_annotation({id, summary})
    │            → status: 'resolved' → green checkmark in toolbar
    │   │
    │   ▼
    │  [RE-SNAPSHOT] agent-browser snapshot <url>  ← verify fix visually
    │            → compare before/after
    │   │
    │   └─ Next annotation → repeat ACK→FIND→FIX→RESOLVE→RE-SNAPSHOT
    │
    ├─ count=0 (all resolved)
    │   └─ update jeo-state.json: agentation.exit_reason="all_resolved"
    │   └─ VERIFY_UI complete → proceed to CLEANUP
    │
    └─ timeout (120s)
        └─ update jeo-state.json: agentation.exit_reason="timeout"
        └─ summarize what was/wasn't addressed → proceed to CLEANUP
```

**HTTP REST API (Codex / Gemini / OpenCode fallback — no MCP):**
```
LOOP:
  GET  http://localhost:4747/pending         → {count, annotations[]}
  if count == 0 → break (done)
  for each annotation:
    PATCH .../annotations/:id {status:"acknowledged"}
    [search & fix code via elementPath]
    PATCH .../annotations/:id {status:"resolved", resolution:"<summary>"}
  sleep 5 → repeat
```

### VERIFY_UI Internal State Machine

```
  IDLE ──(annotate keyword)──► PREFLIGHT
                                  │
                     ┌────────────┤
                     │            │
                   FAIL        OK
                     │            │
                     ▼            ▼
                  RECOVER   WAIT_FOR_SUBMIT
                  (3x retry)      │
                     │      ┌─────┼───────────────┐
                     │      │     │               │
                   ERROR  submit  no submit    timeout
                     │      │     │      │
                     ▼      ▼     ▼      ▼
                   FAIL WATCHING IDLE  TIMEOUT
                          │              │
                   ACK→FIX→RESOLVE    report
                          │
                      RE-SNAPSHOT
                          │
                    issues? ─Y─► WATCHING
                          │
                          N
                          ▼
                        DONE
```

### plannotator-agentation Phase Separation

```
Phase Guard: hooks check jeo-state.json phase before executing

  PLAN phase:
    plannotator ✅ (allowed)
    agentation  ❌ (blocked by phase guard)
    rule        same hash + approved/manual_approved => skip re-entry (exit 0)
    rule        same hash + feedback_required        => skip re-entry (exit 1, NOT exit 0)
    rule        same hash + infrastructure_blocked   => skip re-entry (exit 32)
    ⚠️  feedback_required is NOT terminal — it means plan was REJECTED.
        Same hash + feedback_required must exit 1 (not approved), not exit 0.
        Only a revised plan (new hash) resets gate to pending and reopens plannotator.

  EXECUTE phase:
    plannotator ❌ (blocked by phase guard)
    agentation  ❌ (blocked by phase guard)

  VERIFY / VERIFY_UI phase:
    plannotator ❌ (blocked by phase guard)
    agentation  ✅ (allowed only after submit gate opens)
```

---

## Platform-Specific Execution Paths

### Claude Code (Primary)

```
jeo keyword detected
    │
    ├─ omc available? → /omc:team N:executor (team orchestration)
    │   ├─ team-plan: explore + planner agents
    │   ├─ team-prd: analyst agent
    │   ├─ team-exec: executor agents (parallel)
    │   ├─ team-verify: verifier + reviewers
    │   └─ team-fix: debugger/executor (loop until done)
    │
    └─ plannotator hook: ExitPlanMode → JEO plan-gate wrapper
        └─ skips same reviewed hash, otherwise opens browser UI
```

**State file**: `{worktree}/.omc/state/jeo-state.json`

### Codex CLI

```
/prompts:jeo activated
    │
    ├─ Plan: Write plan.md manually or via ralph prompt
    ├─ Execute: BMAD /workflow-init (no native team support)
    ├─ Verify: agent-browser snapshot <url>
    └─ Cleanup: bash .agent-skills/jeo/scripts/worktree-cleanup.sh
```

**Config**: `~/.codex/config.toml` (developer_instructions)
**Prompt**: `~/.codex/prompts/jeo.md`

### Gemini CLI

```
gemini --approval-mode plan
    │
    ├─ Plan mode: write plan → exit → plannotator fires
    ├─ Execute: ohmg (bunx oh-my-ag) or BMAD /workflow-init
    ├─ Verify: agent-browser snapshot <url>
    └─ Cleanup: bash .agent-skills/jeo/scripts/worktree-cleanup.sh
```

**Config**: `~/.gemini/settings.json` (AfterAgent hook)
**Instructions**: `~/.gemini/GEMINI.md`

### OpenCode

```
/jeo-plan → /jeo-exec → /jeo-status → /jeo-cleanup
    │
    ├─ omx (oh-my-opencode): /omx:team N:executor "<task>"
    ├─ BMAD fallback: /workflow-init
    ├─ plannotator: /plannotator-review (code review)
    └─ Slash commands registered via opencode.json
```

**Config**: `opencode.json` (plugins + instructions)

---

## State Machine

```
States: plan → execute → verify → verify_ui? → cleanup → done

Transitions:
  plan     → execute  (plan approved — approved=true or manual_approved)
  plan     → plan     (feedback received, re-plan: gate=feedback_required, agent must revise plan.md)
  plan     → plan     (same hash + approved/manual_approved => skip re-entry, stay at plan→execute)
  plan     → plan     (same hash + feedback_required => exit 1, NOT exit 0 — plan rejected, revise required)
  plan     → plan     (same hash + infrastructure_blocked => exit 32 — manual gate needed)
  plan     → plan     (new hash after feedback => RESET_FOR_NEW_HASH, gate resets to pending, reopens plannotator)

  ⚠️  v1.3.1 fix: same hash + feedback_required used to incorrectly exit 0 (approved), causing JEO
      to enter EXECUTE without proper approval. Now correctly exits 1 (not approved).
  execute  → verify   (tasks complete, browser UI present)
  verify   → verify_ui (annotate keyword detected — or agentui alias — submit gate waiting)
  verify   → cleanup  (no annotate/agentui, verification passed)
  verify_ui → verify_ui (waiting_for_submit until explicit onSubmit/ANNOTATE_READY)
  verify_ui → cleanup (annotations all resolved or timeout)

  cleanup  → done     (worktrees removed, prune complete)
```

State persisted in: `.omc/state/jeo-state.json`

```json
{
  "phase": "plan",
  "task": "Implement user authentication",
  "plan_approved": false,
  "plan_gate_status": "pending",
  "plan_current_hash": null,
  "last_reviewed_plan_hash": null,
  "last_reviewed_plan_at": null,
  "plan_review_method": null,
  "team_available": true,
  "retry_count": 0,
  "last_error": null,
  "checkpoint": null,
  "created_at": "2026-02-24T00:00:00Z",
  "updated_at": "2026-02-24T00:00:00Z",
  "agentation": {
    "active": false,
    "session_id": null,
    "keyword_used": null,
    "submit_gate_status": "idle",
    "submit_signal": null,
    "submit_received_at": null,
    "submitted_annotation_count": 0,
    "started_at": null,
    "timeout_seconds": 120,
    "annotations": {
      "total": 0,
      "acknowledged": 0,
      "resolved": 0,
      "dismissed": 0,
      "pending": 0
    },
    "completed_at": null,
    "exit_reason": null
  }
}
```

**Error recovery fields:**
- `retry_count`: incremented on each Pre-flight failure; ≥ 3 triggers user confirmation
- `last_error`: most recent error message; cleared on successful step entry
- `checkpoint`: last successfully entered phase (`"plan"` | `"execute"` | `"verify"` | `"cleanup"`); used to resume after interruption

**agentation fields:**
- `active`: whether VERIFY_UI watch loop is currently running (used as guard by hooks)
- `session_id`: agentation session ID for resume via `agentation_get_session`
- `keyword_used`: `"annotate"` or `"agentui"` (tracks which keyword triggered entry)
- `submit_gate_status`: `"idle"` | `"waiting_for_submit"` | `"submitted"`; draft annotations stay blocked until submit
- `submit_signal`: which platform opened the submit gate
- `submit_received_at` / `submitted_annotation_count`: audit trail for the submitted batch
- `started_at`: ISO-8601 timestamp when VERIFY_UI watch loop started
- `timeout_seconds`: poll timeout in seconds (default: 120)
- `annotations.*`: cumulative counts by lifecycle status (`total`, `acknowledged`, `resolved`, `dismissed`, `pending`)
- `exit_reason`: `"all_resolved"` | `"timeout"` | `"user_cancelled"` | `"error"`

---

## Team vs BMAD Decision Matrix

| Condition | Executor | Notes |
|-----------|----------|-------|
| Claude Code + omc + AGENT_TEAMS=1 | **team** | Best option — parallel staged pipeline |
| Claude Code + omc (no teams) | **blocked** | Re-run setup and enable experimental teams; JEO should not silently downgrade |
| Codex CLI | **BMAD** | Structured phases, no native team |
| Gemini CLI + ohmg | **ohmg** | Multi-agent via oh-my-ag |
| Gemini CLI (basic) | **BMAD** | Fallback structured workflow |
| OpenCode + omx | **omx team** | oh-my-opencode team orchestration |
| OpenCode (basic) | **BMAD** | Fallback structured workflow |

---

## agent-browser Verify Pattern

```bash
# 앱 실행 중인 URL에서 스냅샷 캡처
agent-browser snapshot http://localhost:3000

# 특정 요소 확인 (accessibility tree ref 방식)
agent-browser snapshot http://localhost:3000 -i
# → @eN ref 번호로 요소 상태 확인

# 스크린샷 저장
agent-browser screenshot http://localhost:3000 -o verify.png
```

---

## Worktree Manual Cleanup

```bash
# List all worktrees
git worktree list

# Remove specific worktree
git worktree remove /path/to/worktree --force

# Prune stale references
git worktree prune
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Enable native team orchestration | `1` |
| `PLANNOTATOR_REMOTE` | Remote mode (no auto browser open) | unset |
| `PLANNOTATOR_PORT` | Fixed plannotator port | auto |
| `JEO_MAX_ITERATIONS` | Max ralph loop iterations | `20` |

| `AGENTATION_PORT` | agentation MCP server port | `4747` |
| `AGENTATION_TIMEOUT` | annotate watch loop timeout (seconds) | `120` |
---

## Troubleshooting

### plannotator feedback loop: accept not registering / subsequent feedback skipped

**Root cause (v1.3.1 fix)**: When plan hash matched and `plan_gate_status == "feedback_required"`,
the pre-flight guard in SKILL.md incorrectly exited 0 (approved), causing JEO to enter EXECUTE
without a real approval. This affected Codex / Gemini / OpenCode platforms.

**Symptom**: After giving feedback, the plan appears "accepted" but feedback items are missing
on the next round, or plannotator skips re-opening for subsequent feedback rounds.

**Fix applied in v1.3.1**: The guard now exits 1 (not approved) for `feedback_required` + same hash.

**Manual recovery** (if stuck in wrong state):
```bash
# Check current gate state
python3 -c "import json; s=json.load(open('.omc/state/jeo-state.json')); print(s.get('plan_gate_status'), s.get('last_reviewed_plan_hash','')[:8])"

# Force reset gate to pending (allows re-review of same plan)
python3 -c "
import json, datetime
f='.omc/state/jeo-state.json'
s=json.load(open(f))
s['plan_gate_status']='pending'
s['last_reviewed_plan_hash']=None
s['updated_at']=datetime.datetime.utcnow().isoformat()+'Z'
open(f,'w').write(json.dumps(s,indent=2))
print('reset done')
"
```

**Best practice**: Always make substantive content changes to `plan.md` when incorporating feedback.
The gate uses SHA-256 content hash — even a single character change produces a new hash.

### plannotator not opening on plan exit
```bash
# Check hook is configured
bash scripts/check-status.sh

# Re-run hook setup
bash scripts/setup-claude.sh  # or setup-gemini.sh

# Verify plannotator CLI is installed
which plannotator || plannotator --version
```

### team mode not working
```bash
# Ensure env variable is set
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Or add to ~/.claude/settings.json:
# "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" }

# Fall back to ralph:
/ralph "<task>" --max-iterations=20
```

### worktree removal fails
```bash
# Force remove
git worktree remove /path/to/wt --force

# If git objects missing
git worktree prune --verbose

# Manual directory removal
rm -rf /path/to/worktree
git worktree prune
```

### annotate (agentation) watch loop not triggering
```bash
# Verify agentation-mcp server is running
curl -sf http://localhost:4747/pending
# Should return: {"count": N, "annotations": [...]}

# Check MCP registration (Claude Code)
cat ~/.claude/settings.json | python3 -c "import sys,json; s=json.load(sys.stdin); print(s.get('mcpServers', {}))"

# Restart agentation-mcp server
npx agentation-mcp server
```
