#!/usr/bin/env bash
# notion-init-db.sh — create a Notion knowledge-base database with the Cairn schema.
#
# Creates a database under a parent page, with the property columns Cairn maps
# frontmatter onto (the same schema notion-preflight.sh checks for). The DB is
# both the knowledge-base container and the INDEX (its views/properties index
# the notes) — there is no separate INDEX page.
#
# Direct REST via curl (honors HTTPS_PROXY) + retry; pinned Notion-Version.
# The parent page must be shared with the integration first.
#
# macOS Bash 3.2 compatible. Requires: curl, jq. Token in env NOTION_API_TOKEN.
#
# Usage:
#   notion-init-db.sh --parent-page-id PAGE_ID --title "<knowledge base name>" [--dry-run]
# Output (stdout): JSON { database_id, url }
set -uo pipefail

NV="${NOTION_API_VERSION:-2022-06-28}"
PARENT=""; TITLE=""; DRY_RUN=0

die() { echo "error: $*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --parent-page-id) PARENT="${2:-}"; shift 2;;
    --title) TITLE="${2:-}"; shift 2;;
    --notion-version) NV="${2:-}"; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    -h|--help) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) die "unknown arg: $1";;
  esac
done

[ -n "$PARENT" ] || die "--parent-page-id is required (a page shared with the integration)"
[ -n "$TITLE" ] || die "--title is required (the knowledge-base database name, e.g. \"<Project Name> Knowledge Base\")"
command -v curl >/dev/null 2>&1 || die "curl not found"
command -v jq   >/dev/null 2>&1 || die "jq not found"
[ "$DRY_RUN" -eq 1 ] || [ -n "${NOTION_API_TOKEN:-}" ] || die "NOTION_API_TOKEN not set (put it in .env; run: set -a; . ./.env; set +a — bash/POSIX syntax; PowerShell users: \$env:NOTION_API_TOKEN='...' instead)"

# Cairn property schema (matches notion-preflight.sh REQUIRED_PROPS).
PAYLOAD_FILE="$(mktemp -t notion-initdb.XXXXXX)"
trap 'rm -f "$PAYLOAD_FILE"' EXIT
jq -nc --arg parent "$PARENT" --arg title "$TITLE" '{
  parent: {type:"page_id", page_id:$parent},
  title: [{type:"text", text:{content:$title}}],
  properties: {
    "Name": {title:{}},
    "type": {select:{options:[{name:"knowledge_note"},{name:"playbook"},{name:"reference"}]}},
    "contains": {multi_select:{options:[{name:"decision"},{name:"experience"},{name:"lesson"},{name:"procedure"},{name:"reference"},{name:"open_question"}]}},
    "tags": {multi_select:{}},
    "graduated_from": {rich_text:{}},
    "graduated_at": {date:{}},
    "authoring_mode": {select:{options:[{name:"ai_generated"},{name:"human_written"},{name:"ai_assisted"}]}},
    "contributors": {multi_select:{}},
    "graduated_by": {multi_select:{}},
    "source": {url:{}}
  }
}' > "$PAYLOAD_FILE"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "DRY-RUN: POST https://api.notion.com/v1/databases (Notion-Version $NV)" >&2
  echo "  parent page: $PARENT  title: $TITLE" >&2
  echo "  properties: $(jq -c '.properties | keys' "$PAYLOAD_FILE")" >&2
  jq -nc '{database_id:"<dry-run>", url:"<dry-run>"}'
  exit 0
fi

# curl+retry POST
attempt=0; max=8; RESP=""
while [ "$attempt" -lt "$max" ]; do
  attempt=$((attempt + 1))
  RESP="$(curl -sS -X POST "https://api.notion.com/v1/databases" \
    -H "Authorization: Bearer $NOTION_API_TOKEN" -H "Notion-Version: $NV" \
    -H "Content-Type: application/json" --data @"$PAYLOAD_FILE" 2>/dev/null)"; rc=$?
  [ "$rc" -eq 0 ] && [ -n "$RESP" ] && break
  sleep "$attempt"
done
[ -n "$RESP" ] || die "network give-up creating database (proxy/SSL); retry"
if [ "$(printf '%s' "$RESP" | jq -r '.object // ""')" = "error" ]; then
  CODE="$(printf '%s' "$RESP" | jq -r '.code')"
  case "$CODE" in
    object_not_found|restricted_resource) die "parent page not shared with the integration ($CODE) — share it in Notion → ••• → Connections";;
    *) die "Notion API error: $CODE: $(printf '%s' "$RESP" | jq -r '.message')";;
  esac
fi
DBID="$(printf '%s' "$RESP" | jq -r '.id')"
URL="$(printf '%s' "$RESP" | jq -r '.url')"
[ -n "$DBID" ] && [ "$DBID" != "null" ] || die "create returned no id: $RESP"

jq -nc --arg id "$DBID" --arg url "$URL" '{database_id:$id, url:$url}'
