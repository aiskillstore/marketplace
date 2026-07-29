#!/usr/bin/env bash
# lark-preflight.sh — read-only environment check for the Lark/Feishu wiki provider.
#
# Run this BEFORE attempting any Lark graduation. It diagnoses the three things
# the lark-wiki adapter assumes and that a user must set up out-of-band:
#   1. lark-cli is installed and runnable
#   2. the user identity is authorized (auth login done; refreshable session)
#   3. the user token can actually read a wiki space (wiki:wiki effective)
#
# It performs NO writes. It prints a structured JSON verdict on stdout and a
# human-readable summary + recommended next action on stderr. The agent reads
# the verdict and guides the user (the one inherently-manual step — opening a
# scope in the Feishu developer console — cannot be scripted).
#
# Source of truth for the wiki check is a read PROBE (wiki spaces get my_library),
# not the token's advertised scope: the probe auto-refreshes a stale token and
# reflects what the server actually authorizes.
#
# macOS Bash 3.2 compatible. Requires: jq; lark-cli (the thing checked).
# Exit code: 0 if status==ok, 1 otherwise (so callers can gate on it).

set -uo pipefail

CLI="${LARK_CLI:-lark-cli}"
DOCS="https://github.com/larksuite/cli"
Q="LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1"

INSTALLED=false; VERSION=""; AUTHED=false; USER_NAME=""; HAS_WIKI=false; MYLIB_OK=false

emit() { # summary, status, next
  printf '%s\n' "$1" >&2
  jq -nc \
    --argjson installed "$INSTALLED" --arg version "$VERSION" \
    --argjson authed "$AUTHED" --arg user "$USER_NAME" \
    --argjson wiki_scope "$HAS_WIKI" --argjson my_library_ok "$MYLIB_OK" \
    --arg status "$2" --arg next "$3" \
    '{cli_installed:$installed, version:$version, user_authed:$authed, user_name:$user,
      has_wiki_scope:$wiki_scope, my_library_ok:$my_library_ok, status:$status, next:$next}'
}

command -v jq >/dev/null 2>&1 || { echo "error: jq not found (needed to parse lark-cli output)" >&2; exit 1; }

# 1) Installed?
if ! command -v "$CLI" >/dev/null 2>&1; then
  emit "✗ lark-cli not installed." cli_missing \
    "Install then re-run: npm install -g @larksuite/cli && npx skills add larksuite/cli -y -g ; then lark-cli config init && lark-cli auth login --recommend. Docs: $DOCS"
  exit 1
fi
INSTALLED=true
VERSION="$("$CLI" --version 2>&1 | grep -oiE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || true)"

# 2) User session present? (ready or needs_refresh both count — refresh is automatic)
STATUS_JSON="$(env $Q "$CLI" auth status --json 2>/dev/null || true)"
USER_STATE="$(printf '%s' "$STATUS_JSON" | jq -r '.identities.user.status // "none"' 2>/dev/null || echo none)"
USER_NAME="$(printf '%s' "$STATUS_JSON" | jq -r '.identities.user.userName // ""' 2>/dev/null || echo "")"
SCOPES="$(printf '%s' "$STATUS_JSON" | jq -r '.identities.user.scope // ""' 2>/dev/null || echo "")"
case "$USER_STATE" in ready|needs_refresh) AUTHED=true;; *) AUTHED=false;; esac
case " $SCOPES " in *" wiki:wiki "*) HAS_WIKI=true;; *) HAS_WIKI=false;; esac

if [ "$AUTHED" != true ]; then
  emit "✗ lark-cli installed (${VERSION:-?}) but no authorized user session." not_authed \
    "Run: $CLI auth login --recommend (or $CLI auth login --scope wiki:wiki for the wiki provider). Docs: $DOCS"
  exit 1
fi

# 3) Effective wiki read? Probe (auto-refreshes the token; reflects server truth).
PROBE="$(env $Q "$CLI" wiki spaces get --params '{"space_id":"my_library"}' --as user --json 2>/dev/null || true)"
if [ "$(printf '%s' "$PROBE" | jq -r '.ok // false' 2>/dev/null || echo false)" = "true" ]; then
  MYLIB_OK=true
  emit "✓ lark-cli ready (${VERSION:-?}), user '${USER_NAME}', wiki read works." ok \
    "Good to graduate. Use scripts/lark-wiki-graduate.sh (wiki:wiki + native API)."
  exit 0
fi

SUB="$(printf '%s' "$PROBE" | jq -r '.error.subtype // .error.type // ""' 2>/dev/null || echo "")"
if [ "$SUB" = "missing_scope" ]; then
  emit "✗ Authorized as '${USER_NAME}' but user token cannot read wiki (missing scope)." missing_wiki_scope \
    "Open the coarse 'wiki:wiki' scope for USER identity on the app in the developer console — find it by scope name, not by matching a UI label, since the label text differs between consoles (on the Feishu (China) console it's '查看、评论、编辑和管理知识库'; the international Lark console shows different English wording for the same permission) — then re-authorize: $CLI auth login --scope wiki:wiki. Granular read scopes (wiki:space:*) may not enter the user token; wiki:wiki does. Diagnostic: if '--as bot' reads succeed but '--as user' fails, the gap is the user-authorization path, not the app's published permissions. Docs: $DOCS"
  exit 1
fi

emit "✗ Authorized as '${USER_NAME}' but wiki read probe failed (token/identity issue: ${SUB:-unknown})." not_authed \
  "Re-authorize and retry: $CLI auth login --scope wiki:wiki. If it persists, $CLI auth logout then $CLI auth login --recommend. Docs: $DOCS"
exit 1
