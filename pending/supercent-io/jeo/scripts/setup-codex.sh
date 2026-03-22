#!/usr/bin/env bash
# JEO Skill — Codex CLI Setup
# Configures: developer_instructions + agentation MCP in ~/.codex/config.toml + /prompts:jeo
# Usage: bash setup-codex.sh [--dry-run]

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
info() { echo -e "${BLUE}→${NC} $*"; }

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

JEO_SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CODEX_CONFIG="${HOME}/.codex/config.toml"
CODEX_PROMPTS_DIR="${HOME}/.codex/prompts"
JEO_PROMPT_FILE="${CODEX_PROMPTS_DIR}/jeo.md"

echo ""
echo "JEO — Codex CLI Setup"
echo "======================"

# ── 1. Check Codex CLI ────────────────────────────────────────────────────────
if ! command -v codex >/dev/null 2>&1; then
  warn "codex CLI not found. Install via: npm install -g @openai/codex"
fi

# ── 2. Configure ~/.codex/config.toml ────────────────────────────────────────
info "Configuring ~/.codex/config.toml..."

HOOK_DIR="${HOME}/.codex/hooks"
HOOK_FILE="${HOOK_DIR}/jeo-notify.py"

if $DRY_RUN; then
  echo -e "${YELLOW}[DRY-RUN]${NC} Would create/update $CODEX_CONFIG"
  echo -e "${YELLOW}[DRY-RUN]${NC} Would create $JEO_PROMPT_FILE"
else
  mkdir -p "$(dirname "$CODEX_CONFIG")" "$CODEX_PROMPTS_DIR"

  # Backup existing config
  [[ -f "$CODEX_CONFIG" ]] && cp "$CODEX_CONFIG" "${CODEX_CONFIG}.jeo.bak"

  JEO_INSTRUCTION=$(cat <<JEOEOF
# JEO Orchestration Workflow
# Keyword: jeo | Platforms: Codex, Claude, Gemini, OpenCode
#
# JEO provides integrated AI orchestration:
#   1. PLAN: ralph+plannotator for visual plan review
#   2. EXECUTE: team (if available) or bmad workflow
#   3. VERIFY: agent-browser snapshot for UI verification
#   4. CLEANUP: auto worktree cleanup after completion
#
# Trigger with: jeo "<task description>"
# Use /prompts:jeo for full workflow activation
#
# PLAN phase protocol (Codex):
#   1. Write plan to plan.md
#   2. Run mandatory PLAN gate (auto-installs plannotator if missing, blocks for feedback/approve, retries dead sessions up to 3):
#      bash ${JEO_SKILL_DIR}/scripts/plannotator-plan-loop.sh plan.md /tmp/plannotator_feedback.txt 3
#      Rule: if the current plan hash already has a terminal gate result
#      (approved/manual_approved/feedback_required/infrastructure_blocked), do not reopen plannotator.
#      Only a revised plan.md resets the gate to pending.
#   3. Write signal file AND output PLAN_READY (two-path detection for notify hook reliability):
#      mkdir -p .omc/state && echo "PLAN_READY" > .omc/state/plan-signal.txt
#      echo "PLAN_READY"
#   4. Check result:
#      - approved=true -> EXECUTE
#      - approved=false -> re-plan
#      - exit 32 -> localhost bind blocked (sandbox/CI). run PLAN gate in local TTY
#   5. Never emit PLAN_READY in execute/verify phases.
#
# VERIFY_UI submit gate protocol:
#   1. Enter verify_ui and set agentation.submit_gate_status="waiting_for_submit"
#   2. Wait until the user clicks Send Annotations / onSubmit in agentation
#   3. Only then emit "ANNOTATE_READY" (or "AGENTUI_READY" for compatibility)
#   4. notify hook may fetch /pending only after that explicit submit signal
#
# BMAD commands (fallback when team unavailable):
#   /workflow-init   — initialize BMAD workflow
#   /workflow-status — check current BMAD phase
#
# Tools: agent-browser, playwriter, plannotator
JEOEOF
)

  python3 - <<PYEOF
import re, os

config_path = os.path.expanduser("~/.codex/config.toml")
jeo_instruction = """${JEO_INSTRUCTION}"""

try:
    content = open(config_path).read() if os.path.exists(config_path) else ""
except Exception:
    content = ""

content = re.sub(r'(?ms)^\[developer_instructions\]\s*\n.*?(?=^\[|\Z)', '', content).strip() + "\n"
# Only strip legacy bare JEO block if it is NOT inside a developer_instructions value
if not re.search(r'(?ms)^developer_instructions\s*=\s*"""', content):
    content = re.sub(r'(?ms)^# JEO Orchestration Workflow\n.*?^"""\s*\n', '', content)

def parse_existing_instructions(text: str) -> str:
    m = re.search(r'(?ms)^developer_instructions\s*=\s*"""\n?(.*?)\n?"""\s*$', text)
    if m:
        return m.group(1)

    m = re.search(r'(?m)^developer_instructions\s*=\s*"(.*)"\s*$', text)
    if m:
        return bytes(m.group(1), "utf-8").decode("unicode_escape")

    return ""

existing = parse_existing_instructions(content)
jeo_pattern = re.compile(
    r'(?ms)^# JEO Orchestration Workflow\n.*?^# Tools: agent-browser, playwriter, plannotator\s*$'
)
if jeo_pattern.search(existing):
    merged = jeo_pattern.sub(jeo_instruction.strip(), existing).strip()
else:
    merged = (existing.rstrip() + "\n\n" if existing.strip() else "") + jeo_instruction.strip()

new_assignment = 'developer_instructions = """\n' + merged + '\n"""\n'

if re.search(r'(?m)^developer_instructions\s*=', content):
    content = re.sub(r'(?ms)^developer_instructions\s*=\s*(""".*?"""|".*?")\s*$', new_assignment, content, count=1)
else:
    first_table = re.search(r'(?m)^\[', content)
    if first_table:
        content = content[:first_table.start()] + new_assignment + "\n" + content[first_table.start():]
    else:
        content = new_assignment + "\n" + content

with open(config_path, "w") as f:
    f.write(content)

# Post-write: validate TOML and auto-fix stray standalone " lines
try:
    import tomllib as _toml
    with open(config_path, "rb") as f:
        _toml.load(f)
except Exception:
    with open(config_path) as f:
        raw = f.read()
    cleaned = re.sub(r'(?m)^"$\n', '', raw)
    with open(config_path, "w") as f:
        f.write(cleaned)

print("✓ JEO developer_instructions synced (top-level string)")
PYEOF
  ok "JEO developer_instructions synced in ~/.codex/config.toml"

  # ── 3. Create /prompts:jeo prompt file ──────────────────────────────────────
  cat > "$JEO_PROMPT_FILE" <<'PROMPTEOF'
# JEO — Integrated Agent Orchestration Prompt

You are now operating in **JEO mode** — Integrated AI Agent Orchestration.

## Your Workflow

### Step 1: PLAN (plannotator — blocking loop)
Before writing any code, create and review a plan:
1. Write a detailed implementation plan in \`plan.md\` (objectives, steps, risks, acceptance criteria)
2. Run plannotator PLAN gate (blocking, mandatory; auto-installs plannotator if missing):
   \`\`\`bash
   bash .agent-skills/jeo/scripts/plannotator-plan-loop.sh plan.md /tmp/plannotator_feedback.txt 3
   # Write signal file (reliable fallback for notify hook) AND emit inline signal
   mkdir -p .omc/state && echo "PLAN_READY" > .omc/state/plan-signal.txt
   echo "PLAN_READY"
   \`\`\`
   Same-hash guard:
   - if \`plan_gate_status\` is already terminal for the current plan hash, do not reopen plannotator
   - only a modified plan resets the gate to \`pending\`
3. Read /tmp/plannotator_feedback.txt
4. If \`"approved":true\` → proceed to EXECUTE
5. If NOT approved → read annotations, revise plan.md, repeat from step 2
6. **If PLAN gate exits with 32 → CONVERSATION APPROVAL MODE (MANDATORY)**:
   - Output the full contents of \`plan.md\` to the user in the conversation
   - Ask explicitly: "⚠️ plannotator UI unavailable in this environment. Please review the plan above and reply 'approve' to proceed, or provide feedback."
   - **STOP and wait for user response. Do NOT proceed to EXECUTE until user approves.**
   - On 'approve'/'yes'/'ok': update \`jeo-state.json\` \`plan_approved=true, plan_gate_status="manual_approved"\` → EXECUTE
   - On feedback text: revise \`plan.md\`, retry \`plannotator-plan-loop.sh\`, repeat
NEVER skip plannotator. NEVER proceed to EXECUTE without approved=true or explicit user approval in conversation.

### Step 2: EXECUTE (BMAD workflow for Codex)
Use BMAD structured phases:
- \`/workflow-init\` — Initialize BMAD for this project
- Analysis phase: understand requirements fully
- Planning phase: detailed technical plan
- Solutioning phase: architecture decisions
- Implementation phase: write code

### Step 3: VERIFY (agent-browser)
If the task has browser UI:
- Run: \`agent-browser snapshot http://localhost:3000\`
- Check UI elements via accessibility tree (-i flag)
- Save screenshot: \`agent-browser screenshot <url> -o verify.png\`

### Step 3.1: VERIFY_UI (agentation submit gate)
If \`annotate\` / \`agentui\` is requested:
1. Update \`.omc/state/jeo-state.json\` to \`phase="verify_ui"\`
2. Set \`agentation.submit_gate_status="waiting_for_submit"\`
3. Wait until the human actually clicks **Send Annotations** / triggers \`onSubmit\`
4. Only then emit \`ANNOTATE_READY\`
5. Process agentation annotations after the notify hook reports submitted items
Never read \`/pending\` before the submit gate opens.

### Step 4: CLEANUP (worktree)
After all tasks complete:
- Run: git worktree prune
- Run: bash ${JEO_SKILL_DIR}/scripts/worktree-cleanup.sh

## Key Commands
- Plan review — run plannotator BLOCKING (no &), then output PLAN_READY:
  Mandatory behavior:
  - If plannotator is missing, the PLAN gate auto-runs \`ensure-plannotator.sh\` first
  - Wait for approve/feedback every time
  - If session dies, restart up to 3 times
  - After 3 dead sessions, stop and ask whether PLAN should be terminated
  - If loop exits 32: localhost bind blocked. use local TTY/manual PLAN gate
  \`\`\`bash
  bash .agent-skills/jeo/scripts/plannotator-plan-loop.sh plan.md /tmp/plannotator_feedback.txt 3
  # Output PLAN_READY to trigger notify hook as backup signal
  echo "PLAN_READY"
  # Check result
  python3 -c "
import json, sys
try:
    d = json.load(open('/tmp/plannotator_feedback.txt'))
    sys.exit(0 if d.get('approved') is True else 1)
except Exception:
    sys.exit(1)
" && echo "PLAN_APPROVED — proceed to EXECUTE" || cat /tmp/plannotator_feedback.txt
  \`\`\`
- Browser verify: \`agent-browser snapshot http://localhost:3000\`
- BMAD init: \`/workflow-init\`
- Worktree cleanup: \`bash ${JEO_SKILL_DIR}/scripts/worktree-cleanup.sh\`

## State File
Save progress to: \`.omc/state/jeo-state.json\`
\`\`\`json
{
  "phase": "plan|execute|verify|verify_ui|cleanup|done",
  "task": "current task description",
  "plan_approved": false,
  "plan_gate_status": "pending",
  "plan_current_hash": null,
  "last_reviewed_plan_hash": null,
  "plan_review_method": null,
  "team_available": false,
  "retry_count": 0,
  "last_error": null,
  "checkpoint": null,
  "agentation": {
    "submit_gate_status": "idle",
    "submit_signal": null,
    "submit_received_at": null,
    "submitted_annotation_count": 0
  }
}
\`\`\`

Always check state file on resume to continue from last phase.
PROMPTEOF

  # Fix absolute paths in prompt file (replace relative .agent-skills paths with absolute JEO_SKILL_DIR)
  sed -i.bak \
    -e "s|bash .agent-skills/jeo/scripts/plannotator-plan-loop.sh|bash ${JEO_SKILL_DIR}/scripts/plannotator-plan-loop.sh|g" \
    -e "s|\\\${JEO_SKILL_DIR}|${JEO_SKILL_DIR}|g" \
    "$JEO_PROMPT_FILE"
  rm -f "${JEO_PROMPT_FILE}.bak"
  ok "JEO prompt file created: $JEO_PROMPT_FILE"

  # ── 4. Create plannotator notify hook ────────────────────────────────────────
  info "Setting up plannotator notify hook..."
  mkdir -p "$HOOK_DIR"

  cat > "$HOOK_FILE" << 'HOOKEOF'
#!/usr/bin/env python3
"""JEO Codex notify hook — detects PLAN_READY / ANNOTATE_READY and triggers plannotator / agentation."""
import hashlib, json, os, re, subprocess, sys, urllib.request, urllib.error, time

# Exact signal strings (matched as standalone lines, allowing surrounding whitespace)
PLAN_SIGNALS = ["PLAN_READY"]
ANNOTATE_SIGNALS = ["ANNOTATE_READY", "AGENTUI_READY"]
PLAN_TERMINAL_STATUSES = {"approved", "manual_approved", "feedback_required", "infrastructure_blocked"}

def get_jeo_phase(cwd: str) -> str:
    """Read current JEO phase from state file. Returns empty string if not available."""
    state_path = os.path.join(cwd, ".omc", "state", "jeo-state.json")
    try:
        with open(state_path) as f:
            return json.load(f).get("phase", "")
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return ""


def get_state_path(cwd: str) -> str:
    return os.path.join(cwd, ".omc", "state", "jeo-state.json")


def load_state(cwd: str) -> dict:
    state_path = get_state_path(cwd)
    try:
        with open(state_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def update_state(cwd: str, mutator) -> None:
    state_path = get_state_path(cwd)
    if not os.path.exists(state_path):
        return
    try:
        import fcntl, datetime

        with open(state_path, "r+") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                try:
                    data = json.load(fh)
                except Exception:
                    data = {}
                mutator(data)
                data["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
                fh.seek(0)
                json.dump(data, fh, indent=2)
                fh.truncate()
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)
    except Exception:
        pass

def get_feedback_file(cwd: str) -> str:
    """Return session-isolated feedback file path based on cwd MD5."""
    _session_key = hashlib.md5(cwd.encode()).hexdigest()[:8]
    feedback_dir = f"/tmp/jeo-{_session_key}"
    os.makedirs(feedback_dir, exist_ok=True)
    return os.path.join(feedback_dir, "plannotator_feedback.txt")


def get_plannotator_env(cwd: str) -> dict:
    _session_key = hashlib.md5(cwd.encode()).hexdigest()[:8]
    runtime_home = f"/tmp/jeo-{_session_key}/.plannotator"
    os.makedirs(runtime_home, exist_ok=True)
    env = os.environ.copy()
    # Do NOT override HOME — plannotator-plan-loop.sh uses $HOME for PATH construction
    # (export PATH="$HOME/.local/bin:$HOME/bin:$PATH"), so overriding HOME would prevent
    # discovery of plannotator when it is installed in ~/.local/bin.
    # PLANNOTATOR_HOME controls plannotator's state directory independently.
    env["PLANNOTATOR_HOME"] = runtime_home
    return env


def get_plan_loop_script(cwd: str):
    candidates = [
        os.path.join(cwd, ".agent-skills", "jeo", "scripts", "plannotator-plan-loop.sh"),
        os.path.expanduser("~/.codex/skills/jeo/scripts/plannotator-plan-loop.sh"),
        os.path.expanduser("~/.agent-skills/jeo/scripts/plannotator-plan-loop.sh"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def compute_plan_hash(plan_path: str) -> str:
    try:
        with open(plan_path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except Exception:
        return ""


def should_skip_plan_gate(cwd: str, plan_path: str) -> bool:
    state = load_state(cwd)
    current_hash = compute_plan_hash(plan_path)
    if not current_hash:
        return False
    return (
        state.get("phase") == "plan"
        and state.get("plan_gate_status") in PLAN_TERMINAL_STATUSES
        and state.get("last_reviewed_plan_hash") == current_hash
    )

def write_plan_gate_result(cwd: str, rc: int, feedback_file: str) -> None:
    """Write plannotator gate result to jeo-state.json."""
    state_path = os.path.join(cwd, '.omc', 'state', 'jeo-state.json')
    if not os.path.exists(state_path):
        return
    try:
        import fcntl, datetime
        with open(state_path, 'r+') as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                d = json.load(fh)
                if rc == 0:
                    d['plan_approved'] = True
                    d['phase'] = 'execute'
                    d['plan_gate_status'] = 'approved'
                elif rc == 10:
                    d['plan_approved'] = False
                    d['plan_gate_status'] = 'feedback_required'
                    try:
                        d['plannotator_feedback'] = json.load(open(feedback_file))
                    except Exception:
                        pass
                elif rc == 32:
                    d['plan_gate_status'] = 'infrastructure_blocked'
                    d['last_error'] = 'localhost bind unavailable (sandbox/CI)'
                d['updated_at'] = datetime.datetime.utcnow().isoformat() + 'Z'
                fh.seek(0); json.dump(d, fh, indent=2); fh.truncate()
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)
    except Exception:
        pass


def main() -> int:
    try:
        notification = json.loads(sys.argv[1])
    except (IndexError, json.JSONDecodeError):
        return 0

    if notification.get("type") != "agent-turn-complete":
        return 0

    msg = notification.get("last-assistant-message", "").strip()
    cwd = notification.get("cwd", os.getcwd())
    phase = get_jeo_phase(cwd)

    # PLAN_READY: trigger plannotator (only during plan phase)
    if phase in ("plan",):
        if any(re.search(rf'(?m)^{re.escape(sig)}\s*$', msg or '') for sig in PLAN_SIGNALS):
            plan_candidates = ["plan.md", ".omc/plans/jeo-plan.md", "docs/plan.md"]
            plan_path = None
            for candidate in plan_candidates:
                p = os.path.join(cwd, candidate)
                if os.path.exists(p):
                    plan_path = p
                    break
            if plan_path is None:
                print("[JEO] plan.md not found in known locations")
                return 0
            if should_skip_plan_gate(cwd, plan_path):
                state = load_state(cwd)
                print(
                    f"[JEO] plan gate skipped: current hash already reviewed ({state.get('plan_gate_status', 'unknown')})"
                )
                return 0
            feedback_file = get_feedback_file(cwd)
            loop_script = get_plan_loop_script(cwd)
            if loop_script:
                result = subprocess.run(
                    ["bash", loop_script, plan_path, feedback_file, "3"],
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=get_plannotator_env(cwd),
                )
                if result.stdout:
                    print(result.stdout.strip())
                write_plan_gate_result(cwd, result.returncode, feedback_file)
                if result.returncode == 32:
                    print("[JEO] plannotator unavailable: localhost bind blocked (sandbox/CI).")
                    print("[JEO] CONVERSATION APPROVAL MODE: agent must output plan.md and request explicit user approval.")
                print(f"[JEO] plannotator loop result code={result.returncode} feedback={feedback_file}")
            else:
                plan_content = open(plan_path).read()
                payload = json.dumps({"tool_input": {"plan": plan_content, "permission_mode": "acceptEdits"}})
                try:
                    with open(feedback_file, "w") as f:
                        subprocess.run(["plannotator"], input=payload, stdout=f, stderr=f, text=True, env=get_plannotator_env(cwd))
                    print(f"[JEO] plannotator feedback \u2192 {feedback_file}")
                except FileNotFoundError:
                    print("[JEO] plannotator not found \u2014 skipping")
            return 0

    # ANNOTATE_READY: poll agentation HTTP API only after explicit submit signal in VERIFY_UI
    if phase == "verify_ui":
        if any(re.search(rf'(?m)^{re.escape(sig)}\s*$', msg or '') for sig in ANNOTATE_SIGNALS):
            state = load_state(cwd)
            agentation = state.get("agentation", {})
            if agentation.get("submit_gate_status") == "submitted":
                print("[JEO] agentation submit gate already opened for this turn")
            else:
                def mark_submitted(data):
                    agentation_state = data.setdefault("agentation", {})
                    agentation_state["submit_gate_status"] = "submitted"
                    agentation_state["submit_signal"] = "codex-notify"
                    agentation_state["submit_received_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

                update_state(cwd, mark_submitted)
            base_url = "http://localhost:4747"
            try:
                with urllib.request.urlopen(f"{base_url}/pending", timeout=2) as r:
                    data = json.loads(r.read())
                count = data.get("count", 0)
                annotations = data.get("annotations", [])
                def record_count(state_data):
                    agentation_state = state_data.setdefault("agentation", {})
                    agentation_state["submitted_annotation_count"] = count
                    if count == 0:
                        agentation_state["submit_gate_status"] = "waiting_for_submit"
                update_state(cwd, record_count)
                if count == 0:
                    print("[JEO] agentation: no pending annotations")
                else:
                    print(f"[JEO] agentation: {count} pending annotations")
                    for ann in annotations:
                        sev = ann.get("severity", "suggestion")
                        print(f"  [{sev}] {ann.get('element','?')} | {ann.get('comment','')[:80]}")
                        print(f"    elementPath: {ann.get('elementPath','?')}")
            except (urllib.error.URLError, Exception) as e:
                print(f"[JEO] agentation server not reachable ({base_url}): {e}")
            return 0

    return 0
if __name__ == "__main__":
    sys.exit(main())
HOOKEOF

  chmod +x "$HOOK_FILE"
  # Inject absolute JEO script path as first candidate in get_plan_loop_script()
  sed -i.bak \
    "s|os.path.join(cwd, \".agent-skills\", \"jeo\", \"scripts\", \"plannotator-plan-loop.sh\")|\"${JEO_SKILL_DIR}/scripts/plannotator-plan-loop.sh\",\n        os.path.join(cwd, \".agent-skills\", \"jeo\", \"scripts\", \"plannotator-plan-loop.sh\")|" \
    "$HOOK_FILE"
  rm -f "${HOOK_FILE}.bak"
  ok "JEO notify hook created: $HOOK_FILE"

  # Add notify + tui to config.toml
  python3 - <<PYEOF
import re, os

config_path = os.path.expanduser("~/.codex/config.toml")
hook_path = os.path.expanduser("~/.codex/hooks/jeo-notify.py")

try:
    content = open(config_path).read() if os.path.exists(config_path) else ""
except Exception:
    content = ""

# Use a dispatcher so multiple skills (JEO, OMU, …) can each register a notify hook
# without the last setup overwriting the previous one's notify entry.
import json as _json
dispatcher_path = os.path.expanduser("~/.codex/hooks/dispatcher.py")
registry_path = os.path.expanduser("~/.codex/hooks/registry.json")

# Ensure dispatcher script exists
if not os.path.exists(dispatcher_path):
    os.makedirs(os.path.dirname(dispatcher_path), exist_ok=True)
    with open(dispatcher_path, "w") as _f:
        _f.write(
            '#!/usr/bin/env python3\n'
            '"""Codex notify dispatcher — fans out to all registered skill hooks.\n'
            'Register hooks in ~/.codex/hooks/registry.json: {"hooks": ["/path/to/hook.py"]}\n"""\n'
            'import json, os, subprocess, sys\n'
            'REGISTRY = os.path.expanduser("~/.codex/hooks/registry.json")\n'
            'def main():\n'
            '    raw = sys.argv[1] if len(sys.argv) > 1 else ""\n'
            '    try:\n'
            '        hooks = json.load(open(REGISTRY)).get("hooks", [])\n'
            '    except Exception:\n'
            '        return 0\n'
            '    for h in hooks:\n'
            '        if os.path.isfile(h):\n'
            '            try:\n'
            '                subprocess.run(["python3", h, raw], check=False)\n'
            '            except Exception as e:\n'
            '                print(f"[dispatcher] {h}: {e}", flush=True)\n'
            '    return 0\n'
            'if __name__ == "__main__":\n'
            '    raise SystemExit(main())\n'
        )
    print("✓ dispatcher.py created")

# Register jeo-notify.py in dispatcher registry
try:
    registry = _json.load(open(registry_path)) if os.path.exists(registry_path) else {"hooks": []}
except Exception:
    registry = {"hooks": []}
if hook_path not in registry.get("hooks", []):
    registry.setdefault("hooks", []).append(hook_path)
    with open(registry_path, "w") as _f:
        _json.dump(registry, _f, indent=2)
    print("✓ jeo-notify.py registered in dispatcher registry")
else:
    print("✓ jeo-notify.py already in dispatcher registry")

# Point config.toml notify to dispatcher (skip if already pointing there)
dispatcher_line = f'notify = ["python3", "{dispatcher_path}"]'
notify_match = re.search(r'(?m)^notify\s*=.*$', content)
if notify_match:
    if "dispatcher.py" not in notify_match.group(0):
        content = re.sub(r'(?m)^notify\s*=.*$', dispatcher_line, content, count=1)
        print("✓ notify updated to use dispatcher in config.toml")
    else:
        print("✓ notify already uses dispatcher in config.toml")
else:
    first_table = re.search(r'^\[', content, re.MULTILINE)
    if first_table:
        content = content[:first_table.start()] + dispatcher_line + "\n\n" + content[first_table.start():]
    else:
        content = dispatcher_line + "\n" + content
    print("✓ notify dispatcher registered in config.toml")

# Add agentation [[mcp_servers]] if missing (check both array-of-tables and table formats)
if not re.search(r'(?ms)^\[\[mcp_servers\]\]\s*\nname\s*=\s*"agentation"\s*\n', content) and \
   not re.search(r'(?m)^\[mcp_servers\.agentation\]', content):
    agentation_block = '\n[mcp_servers.agentation]\ncommand = "npx"\nargs = ["-y", "agentation-mcp", "server"]\n'
    content = content.rstrip() + agentation_block
    print("\u2713 agentation MCP server added to config.toml")
else:
    print("\u2713 agentation MCP already in config.toml")

# Add or sync [tui] section
tui_match = re.search(r'(?ms)^\[tui\]\s*\n(.*?)(?=^\[|\Z)', content)
if not tui_match:
    content = content.rstrip() + '\n\n[tui]\nnotifications = ["agent-turn-complete"]\nnotification_method = "osc9"\n'
    print("✓ [tui] section added")
else:
    tui_body = tui_match.group(1)
    notif_match = re.search(r'(?m)^notifications\s*=\s*\[(.*?)\]\s*$', tui_body)
    notifications = []
    if notif_match:
        notifications = re.findall(r'"([^"]+)"', notif_match.group(1))
    if "agent-turn-complete" not in notifications:
        notifications.append("agent-turn-complete")
    notifications_line = 'notifications = [' + ', '.join(f'"{item}"' for item in notifications) + ']'
    if notif_match:
        tui_body = re.sub(r'(?m)^notifications\s*=\s*\[(.*?)\]\s*$', notifications_line, tui_body, count=1)
    else:
        tui_body = notifications_line + '\n' + tui_body

    if re.search(r'(?m)^notification_method\s*=', tui_body):
        tui_body = re.sub(r'(?m)^notification_method\s*=.*$', 'notification_method = "osc9"', tui_body, count=1)
    else:
        tui_body = tui_body.rstrip() + '\nnotification_method = "osc9"\n'

    content = content[:tui_match.start(1)] + tui_body + content[tui_match.end(1):]
    print("✓ [tui] notifications synced")

with open(config_path, "w") as f:
    f.write(content)
PYEOF

  ok "Codex config.toml updated (notify hook + agentation MCP + tui)"
fi

echo ""
echo "Codex CLI usage after setup:"
echo "  /prompts:jeo             ← Activate JEO orchestration workflow"
echo "  notify hook: ~/.codex/hooks/jeo-notify.py"
echo "    fires on: PLAN_READY / ANNOTATE_READY signals in agent output (AGENTUI_READY also accepted)"
echo "    writes to: /tmp/plannotator_feedback.txt"
echo ""
ok "Codex CLI setup complete"
echo ""
