#!/usr/bin/env bash
# obsidian-preflight.sh — read-only environment check for the Obsidian provider.
#
# Run this BEFORE attempting any Obsidian graduation. It diagnoses what the
# obsidian adapter assumes and a user must have set up out-of-band:
#   1. the `obsidian` CLI is on PATH
#   2. the Obsidian desktop app is running and the CLI can reach it
#   3. the target vault is one Obsidian actually knows about
#   4. the CLI can actually address that specific vault
#
# Real-world behavior verified interactively (not documented anywhere):
#   - The `obsidian` CLI ships INSIDE the Obsidian.app bundle (1.12+), not as
#     a separate package. It is enabled with a toggle in the app itself:
#     Settings → General → "Command line interface" ("允许从命令行与 Obsidian
#     交互"). There is no command the agent can run for this — it's a GUI
#     click only the user can do. See $DOCS.
#   - Switching the CLI's target vault (`vault="<name>"`) is asynchronous.
#     The FIRST query against a vault that wasn't already active can return
#     an empty/zero result with exit code 0 — not an error — while Obsidian
#     loads it in the background. A one-shot check is not trustworthy; this
#     script retries with a short pause before concluding a vault is
#     unreachable.
#   - Exit codes are not reliable signals in general: `read path=<missing>`
#     also exits 0 and prints "Error: File ... not found." on stdout instead
#     of failing. Don't gate on `$?` here; inspect the actual output.
#   - Malformed vault targeting can silently report a different vault's info
#     instead of erroring. This script cross-checks that `vault info=name`
#     echoes back the exact vault name it was asked to target, as cheap
#     insurance against that failure mode.
#
# It performs NO writes. Prints a structured JSON verdict on stdout and a
# human-readable summary + recommended next action on stderr. Exit 0 iff
# status==ok.
#
# macOS Bash 3.2 compatible: no `timeout` (not present on stock macOS, no
# `gtimeout` either without extra deps) — retries + short sleeps are the only
# defense against a hung/unresponsive CLI, same tradeoff lark-preflight.sh and
# notion-preflight.sh already accept for their own underlying tools.
# Requires: jq; obsidian (the thing checked).
#
# Usage:
#   obsidian-preflight.sh --vault "<vault name>" [--target "<folder>"] [--index "<folder>/INDEX.md"]
set -uo pipefail

CLI="${OBSIDIAN_CLI:-obsidian}"
DOCS="https://help.obsidian.md/cli"
VAULT=""; TARGET=""; INDEX=""
RETRIES=4

while [ $# -gt 0 ]; do
  case "$1" in
    --vault) VAULT="${2:-}"; shift 2;;
    --target) TARGET="${2:-}"; shift 2;;
    --index) INDEX="${2:-}"; shift 2;;
    -h|--help) sed -n '2,33p' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) echo "error: unknown arg: $1" >&2; exit 1;;
  esac
done

[ -n "$VAULT" ] || { echo 'error: --vault "<vault name>" is required' >&2; exit 1; }

INSTALLED=false; APP_OK=false; VAULT_KNOWN=false; VAULT_OK=false; INDEX_EXISTS=false

emit() { # summary status next
  printf '%s\n' "$1" >&2
  jq -nc \
    --argjson installed "$INSTALLED" --argjson app_ok "$APP_OK" \
    --argjson vault_known "$VAULT_KNOWN" --argjson vault_ok "$VAULT_OK" \
    --argjson index_exists "$INDEX_EXISTS" \
    --arg status "$2" --arg next "$3" \
    '{cli_installed:$installed, app_reachable:$app_ok, vault_known:$vault_known,
      vault_reachable:$vault_ok, index_exists:$index_exists, status:$status, next:$next}'
}

command -v jq >/dev/null 2>&1 || { echo "error: jq not found (needed to parse obsidian output)" >&2; exit 1; }

# 1) Installed? No one-line install command exists — see header note.
if ! command -v "$CLI" >/dev/null 2>&1; then
  emit "✗ obsidian CLI not found on PATH." cli_missing \
    "In Obsidian: Settings → General → \"Command line interface\", turn it on. This ships inside the app itself; it's a one-click GUI setting the agent cannot toggle for you. See $DOCS."
  exit 1
fi
INSTALLED=true

# 2) App reachable + fetch the known-vaults registry (tab-separated name/path
#    lines). A closed/unreachable app surfaces as an empty response, not a
#    distinct error — retry past transient emptiness before concluding.
VAULTS_RAW=""
attempt=0
while [ "$attempt" -lt "$RETRIES" ]; do
  attempt=$((attempt + 1))
  VAULTS_RAW="$("$CLI" vaults verbose 2>/dev/null || true)"
  [ -n "$VAULTS_RAW" ] && break
  sleep "$attempt"
done
if [ -z "$VAULTS_RAW" ]; then
  emit "✗ obsidian CLI installed but got no response (Obsidian may not be running, or its CLI toggle may be off)." app_unreachable \
    "Open the Obsidian desktop app and confirm Settings → General → \"Command line interface\" is on — the CLI talks to a running instance over that interface — then retry."
  exit 1
fi
APP_OK=true

# 3) Target vault registered with Obsidian at all?
if ! printf '%s\n' "$VAULTS_RAW" | cut -f1 | grep -Fxq "$VAULT"; then
  emit "✗ Vault '$VAULT' is not registered in Obsidian on this machine." vault_unknown \
    "Open it once in Obsidian (File → Open vault) so it's registered, then retry."
  exit 1
fi
VAULT_KNOWN=true

# 4) Can the CLI actually address it right now? Switching vaults is async —
#    retry past the empty-first-response race documented above.
attempt=0; COUNT=""
while [ "$attempt" -lt "$RETRIES" ]; do
  attempt=$((attempt + 1))
  RAW="$("$CLI" vault="$VAULT" files total 2>/dev/null | tail -1 || true)"
  case "$RAW" in ''|*[!0-9]*) RAW="";; esac   # keep only a bare integer count
  COUNT="$RAW"
  [ -n "$COUNT" ] && break
  sleep "$attempt"
done
if [ -z "$COUNT" ]; then
  emit "✗ Vault '$VAULT' is known but the CLI could not load it (no numeric file count after $RETRIES tries)." vault_unreachable \
    "Open '$VAULT' manually in Obsidian once — a vault it hasn't loaded recently can be slow to become addressable by the CLI — then retry."
  exit 1
fi

# 5) Identity cross-check: confirm the CLI is targeting the vault we asked
#    for, not silently reporting whatever vault was already active.
GOT_NAME="$("$CLI" vault="$VAULT" vault info=name 2>/dev/null | tail -1 || true)"
if [ "$GOT_NAME" != "$VAULT" ]; then
  emit "✗ Asked for vault '$VAULT' but the CLI reports '$GOT_NAME' as active." vault_unreachable \
    "Vault targeting did not take effect. Re-run; if it persists, open '$VAULT' manually in Obsidian first."
  exit 1
fi
VAULT_OK=true

# 6) Index file presence — informational only, never a failure. A fresh
#    graduation target legitimately has no INDEX yet on first use. Exit code
#    is not trustworthy here (see header note); inspect the output text.
if [ -n "$TARGET" ] && [ -n "$INDEX" ]; then
  READ_OUT="$("$CLI" vault="$VAULT" read path="$INDEX" 2>/dev/null || true)"
  if ! printf '%s' "$READ_OUT" | grep -q '^Error: File .* not found\.'; then
    INDEX_EXISTS=true
  fi
fi

SUMMARY="✓ Obsidian ready: vault '$VAULT' reachable ($COUNT files)"
if [ -n "$INDEX" ]; then
  if [ "$INDEX_EXISTS" = true ]; then SUMMARY="$SUMMARY, index exists."; else SUMMARY="$SUMMARY, index not yet created (fine on first graduation)."; fi
else
  SUMMARY="$SUMMARY."
fi
emit "$SUMMARY" ok "Good to graduate."
exit 0
