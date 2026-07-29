#!/usr/bin/env bash
# notion-preflight.sh — read-only environment check for the Notion provider.
#
# Run this BEFORE attempting any Notion graduation. It diagnoses what the
# notion-graduate adapter assumes and a user must set up out-of-band:
#   1. curl + jq are available
#   2. NOTION_API_TOKEN is set (an internal-integration token; keep it in .env)
#   3. the token can actually READ the target database (i.e. the DB — or its
#      parent page — is shared with the integration)
#   4. the database has the property columns Cairn maps frontmatter onto, with
#      the exact compatible Notion types (wrong types are reported separately
#      as db_prop_type_mismatch with property/expected/actual details)
#
# It performs NO writes. Prints a structured JSON verdict on stdout and a
# human-readable summary + next action on stderr. Exit 0 iff status==ok.
#
# Transport note (verified): the official `ntn` CLI is unreliable behind an
# HTTPS proxy (it fetches an OpenAPI spec to resolve endpoints, does not honor
# HTTPS_PROXY, and fails PATCH/query). This adapter uses direct REST via curl,
# which honors the proxy, with per-request retry to ride out random SSL EOFs.
#
# macOS Bash 3.2 compatible. Requires: curl, jq.
#
# Usage: NOTION_API_TOKEN=... notion-preflight.sh --db DATABASE_ID
set -uo pipefail

NV="${NOTION_API_VERSION:-2022-06-28}"
DB=""
REQUIRED_PROP_SPECS="Name:title type:select contains:multi_select tags:multi_select graduated_from:rich_text graduated_at:date authoring_mode:select contributors:multi_select graduated_by:multi_select"

while [ $# -gt 0 ]; do
  case "$1" in
    --db) DB="${2:-}"; shift 2;;
    --notion-version) NV="${2:-}"; shift 2;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) echo "error: unknown arg: $1" >&2; exit 1;;
  esac
done

INSTALLED=false; TOKEN_SET=false; DB_READ=false; MISSING_PROPS=""; TYPE_MISMATCHES='[]'

emit() { # summary status next
  printf '%s\n' "$1" >&2
  jq -nc \
    --argjson deps "$INSTALLED" --argjson token "$TOKEN_SET" \
    --argjson db_read "$DB_READ" --arg missing "$MISSING_PROPS" \
    --argjson mismatches "$TYPE_MISMATCHES" --arg status "$2" --arg next "$3" \
    '{deps_ok:$deps, token_set:$token, db_readable:$db_read,
      missing_props:($missing | if .=="" then [] else split(" ") end),
      property_type_mismatches:$mismatches, status:$status, next:$next}'
}

# curl+retry: GET /v1/<path>. Echoes body on transport success (may be an API
# error JSON — caller inspects .object). Empty + rc!=0 on give-up.
napi_get() {
  path="$1"; attempt=0; max=8; resp=""
  while [ "$attempt" -lt "$max" ]; do
    attempt=$((attempt + 1))
    resp="$(curl -sS "https://api.notion.com/v1/$path" \
      -H "Authorization: Bearer ${NOTION_API_TOKEN:-}" -H "Notion-Version: $NV" 2>/dev/null)"
    rc=$?
    [ "$rc" -eq 0 ] && [ -n "$resp" ] && { printf '%s' "$resp"; return 0; }
    sleep "$attempt"   # backoff for SSL EOF flakiness
  done
  return 1
}

# 1) deps
command -v curl >/dev/null 2>&1 || { echo "error: curl not found" >&2; exit 1; }
command -v jq   >/dev/null 2>&1 || { echo "error: jq not found" >&2; exit 1; }
INSTALLED=true

# 2) token present
if [ -z "${NOTION_API_TOKEN:-}" ]; then
  emit "✗ NOTION_API_TOKEN not set." not_authed \
    "Create an internal integration at https://www.notion.so/profile/integrations (Read+Insert+Update content), put its ntn_ token in .env as NOTION_API_TOKEN, then: set -a; . ./.env; set +a (bash/POSIX syntax; PowerShell users: \$env:NOTION_API_TOKEN='...' instead)"
  exit 1
fi
TOKEN_SET=true

# require --db to check reachability + schema
[ -n "$DB" ] || { emit "✗ --db DATABASE_ID required to check reachability." not_authed \
  "Re-run with --db <notion database id>."; exit 1; }

# 3) DB readable? (share dependency)
BODY="$(napi_get "databases/$DB")" || { emit "✗ Network give-up reaching Notion API (proxy/SSL flakiness)." net_error \
  "Check HTTPS_PROXY reachability and retry; curl honors the proxy env."; exit 1; }
OBJ="$(printf '%s' "$BODY" | jq -r '.object // ""' 2>/dev/null || echo "")"
if [ "$OBJ" = "error" ]; then
  CODE="$(printf '%s' "$BODY" | jq -r '.code // ""')"
  case "$CODE" in
    unauthorized) emit "✗ Token rejected (unauthorized)." not_authed \
      "Token invalid/expired. Re-copy the integration secret into .env." ; exit 1;;
    object_not_found|restricted_resource) emit "✗ Integration cannot see database $DB (not shared)." db_unshared \
      "Open the DB (or its parent page) in Notion → ••• → Connections → add your integration, then re-run." ; exit 1;;
    *) emit "✗ Notion API error: $CODE" db_unshared \
      "$(printf '%s' "$BODY" | jq -r '.message // "see raw error"')" ; exit 1;;
  esac
fi
[ "$OBJ" = "database" ] || { emit "✗ Unexpected response reading database." db_unshared "Verify the --db id is a database."; exit 1; }
DB_READ=true

# 4) required property columns present?
# Missing names stay a separate status from incompatible existing columns.
HAVE="$(printf '%s' "$BODY" | jq -r '.properties | keys[]' 2>/dev/null || true)"
for spec in $REQUIRED_PROP_SPECS; do
  p="${spec%%:*}"
  case "
$HAVE
" in
    *"
$p
"*) : ;;
    *) MISSING_PROPS="${MISSING_PROPS:+$MISSING_PROPS }$p";;
  esac
done
if [ -n "$MISSING_PROPS" ]; then
  emit "✗ Database missing property columns: $MISSING_PROPS" db_props_missing \
    "Add these columns to the DB (type/authoring_mode=Select, contains/tags/contributors/graduated_by=Multi-select, graduated_from=Text, graduated_at=Date), or let the agent create the DB with the full schema after confirmation."
  exit 1
fi

for spec in $REQUIRED_PROP_SPECS; do
  p="${spec%%:*}"; expected="${spec#*:}"
  actual="$(printf '%s' "$BODY" | jq -r --arg p "$p" '.properties[$p].type // ""')"
  if [ "$actual" != "$expected" ]; then
    TYPE_MISMATCHES="$(printf '%s' "$TYPE_MISMATCHES" | jq -c \
      --arg property "$p" --arg expected "$expected" --arg actual "$actual" \
      '. + [{property:$property, expected:$expected, actual:$actual}]')"
  fi
done
if [ "$(printf '%s' "$TYPE_MISMATCHES" | jq 'length')" -gt 0 ]; then
  details="$(printf '%s' "$TYPE_MISMATCHES" | jq -r 'map(.property + " expected=" + .expected + " actual=" + .actual) | join("; ")')"
  emit "✗ Database property type mismatch: $details" db_prop_type_mismatch \
    "Change each listed property to the expected Notion type before graduation; do not write into an incompatible schema."
  exit 1
fi

TITLE="$(printf '%s' "$BODY" | jq -r '.title[0].plain_text // "?"')"
emit "✓ Notion ready: DB '$TITLE' readable, all Cairn property columns present." ok \
  "Good to graduate. Use scripts/notion-graduate.sh (direct REST + retry, Notion-Version $NV)."
exit 0
