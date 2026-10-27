#!/usr/bin/env bash
# ground-truth.sh — emit bounded live interface facts about this agy install.
#
# WHY THIS EXISTS (the core finding of the 2026-08-01 research):
# When agy was asked to research its own CLI, it confidently invented `agy run`,
# `--headless`, `--slim`, `--no-prompt`, `--workspace` and an `agy auth status --json`
# OAuth introspection endpoint. None exist. The Codex agents that shelled out to
# `agy --help` got it right. Conclusion: a model's memory of its own tooling is
# unreliable, so any agent AUTHORING agy skills must read this output first and
# treat it — not its own recollection — as ground truth.
#
# The default interface phase is deliberately safe to run before a provider or
# account review: it invokes only `agy --version` and `agy --help`. The optional
# account phase is a separate explicit action because `models`, `agents`, plugin
# discovery, and the local settings file may inspect account-owned state.
#
# Feed only the phase you intentionally ran into a skill-authoring prompt.
set -euo pipefail

phase="interface"
case "$#" in
    0) ;;
    1)
        if [[ "${1:-}" == "--account" ]]; then
            phase="account"
        else
            printf '%s\n' 'usage: ground-truth.sh [--account]' >&2
            exit 64
        fi
        ;;
    *)
        printf '%s\n' 'usage: ground-truth.sh [--account]' >&2
        exit 64
        ;;
esac

echo "# agy ground truth — generated $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo
echo "## phase"
printf '%s\n' "$phase"
echo
echo "## bounded installed interface"
RUNTIME_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
python3 -B "$RUNTIME_DIR/scripts/model_selection.py" --probe-interface

if [[ "$phase" == "account" ]]; then
    echo
    echo "## models available to --model (account phase)"
    agy models 2>&1 || echo "(agy models failed)"
    echo
    echo "## agents available to --agent (account phase)"
    agy agents 2>&1 || echo "(agy agents failed)"
    echo
    echo "## installed plugins (account phase)"
    agy plugin list 2>&1 || echo "(agy plugin list failed)"
    echo
    echo "## headless permission allowlist (account phase)"
    echo "Commands NOT in this list are auto-denied under 'agy -p' with no prompt."
    python3 - <<'PY' 2>&1 || echo "(could not read settings.json)"
import json, os
p = os.path.expanduser("~/.gemini/antigravity-cli/settings.json")
d = json.load(open(p))
perms = d.get("permissions", {})
for key in ("allow", "ask", "deny"):
    print(f"{key}: {perms.get(key)}")
PY
fi
echo
cat <<'EOF'
## interpretation limits

Required capabilities establish the local interface, not authentication, model
availability, permission, or task quality. Version text is diagnostic only.
The schema-validated answer is result.structured_output; result.json_schema is the
echoed schema. Exit zero alone is not success. Do not retry authentication,
permission, quota, or environment blockers automatically.
EOF
