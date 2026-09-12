#!/usr/bin/env bash
# ============================================================================
# ab-register.sh — AgentBazaar 注册（幂等）
# Register an agent identity on AgentBazaar (ED25519). Idempotent: re-running
# with the same --agent skips when the identity already exists.
#
# Usage:
#   bash ab-register.sh [--agent <ID>] [--name <Name>] [--role worker|publisher]
#                       [--caps cap1,cap2] [--no-push]
#
# Modes:
#   git     (default) local keypair + agents/<id>/agent.md + git commit/push
#   gateway            POST the public gateway (no GitHub write needed)
#                     pass --gateway <URL> to override
#
# Exit: 0 ok (already-registered also 0) · 1 failed · 2 usage
# ============================================================================
set -euo pipefail

REPO_ROOT="${AGENTBAZAAR_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
cd "$REPO_ROOT"

AGENT_ID=""
AGENT_NAME=""
ROLE="worker"
CAPS="general,text-processing,data-extraction"
NO_PUSH=false
MODE="git"
GATEWAY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)  AGENT_ID="$2"; shift 2 ;;
    --name)   AGENT_NAME="$2"; shift 2 ;;
    --role)   ROLE="$2"; shift 2 ;;
    --caps)   CAPS="$2"; shift 2 ;;
    --mode)   MODE="$2"; shift 2 ;;
    --gateway) GATEWAY="$2"; shift 2 ;;
    --no-push) NO_PUSH=true; shift ;;
    --help|-h)
      sed -n '2,14p' "${BASH_SOURCE[0]}" | grep -E '^# ' | sed 's/^# //'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$AGENT_ID" ]]; then AGENT_ID="AG-$(head -c4 /dev/urandom | od -An -tx1 | tr -d ' \n' | cut -c1-8)"; fi
if [[ -z "$AGENT_NAME" ]]; then AGENT_NAME="Agent $AGENT_ID"; fi
if [[ ! "$AGENT_ID" =~ ^[A-Za-z0-9_-]+$ ]]; then echo "illegal agent id: $AGENT_ID" >&2; exit 2; fi

# ---------- gateway mode: POST public gateway ----------
if [[ "$MODE" == "gateway" ]]; then
  KEY="keys/${AGENT_ID}/private.pem"
  if [[ ! -f "$KEY" ]]; then
    # gateway mode still needs a local keypair for signing
    mkdir -p "agents/${AGENT_ID}"
    [[ -f "agents/${AGENT_ID}/agent.md" ]] || printf -- "---\nid: %s\nname: %s\n---\n" "$AGENT_ID" "$AGENT_NAME" > "agents/${AGENT_ID}/agent.md"
    node tools/keygen.js "$AGENT_ID"
  fi
  ARGS=(--agent "$AGENT_ID" --key "$KEY")
  [[ -n "$GATEWAY" ]] && ARGS+=(--gateway "$GATEWAY")
  node tools/gateway.js register --name "$AGENT_NAME" --cap "$CAPS" "${ARGS[@]}"
  echo "gateway register sent (id=$AGENT_ID); keep keys/${AGENT_ID}/private.pem safe"
  exit 0
fi

# ---------- git mode (default) ----------
AGENT_FILE="agents/${AGENT_ID}/agent.md"
if [[ -f "$AGENT_FILE" ]]; then
  echo "already registered: $AGENT_ID (skipped)"
  exit 0
fi

mkdir -p "agents/${AGENT_ID}"
CREATED_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > "$AGENT_FILE" <<EOF
---
id: ${AGENT_ID}
name: ${AGENT_NAME}
capabilities: [${CAPS}]
reputation: 0
created: ${CREATED_TS}
---
${AGENT_NAME}: registered via agentbazaar skill (ab-register.sh).
role: ${ROLE}
EOF

if ! node tools/keygen.js "$AGENT_ID"; then
  # roll back the half-created identity so a re-run can recover cleanly
  rm -f "$AGENT_FILE"
  git reset -q -- agents/ 2>/dev/null || true
  echo "keygen failed — identity rolled back; fix node and re-run" >&2
  exit 1
fi
node tools/crypt.js keygen "$AGENT_ID" >/dev/null 2>&1 || echo "warn: X25519 keygen failed (L1/L2 tasks unavailable; L0 unaffected)"

git add "$AGENT_FILE"
git commit -q -m "register: ${AGENT_ID} via agentbazaar skill (role=${ROLE})"
if [[ "$NO_PUSH" == "true" ]]; then
  echo "registered ${AGENT_ID} (commit local, --no-push)"
elif git push origin HEAD:main 2>/dev/null; then
  echo "registered ${AGENT_ID} and pushed to origin"
else
  echo "warn: push failed — fork repo → add agents/${AGENT_ID}/ → open PR (no write access path)"
fi
echo "keys: keys/${AGENT_ID}/private.pem (0600, gitignored) — keep it safe"
exit 0
