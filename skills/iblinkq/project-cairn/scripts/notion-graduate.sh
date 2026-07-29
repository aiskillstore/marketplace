#!/usr/bin/env bash
# notion-graduate.sh — Project Cairn graduation adapter for the Notion provider.
#
# Encodes the verified adapter constraints (see references/graduation/notion.md,
# references/provider-interface.md, and cairn Notion Provider notes):
#   - Direct REST via curl (honors HTTPS_PROXY), NOT the `ntn` CLI (unreliable
#     behind a proxy: fetches an OpenAPI spec to resolve endpoints, does not
#     honor the proxy, fails PATCH/query).
#   - Per-request retry with backoff to ride out random SSL EOF flakiness.
#   - Pin Notion-Version (default 2022-06-28: classic single-source database;
#     avoids the 2025-09-03+ data-source semantics).
#   - Create mode writes one page in a single POST /v1/pages. Update mode
#     (`--page-id`) PATCHes properties on that same page, archives all current
#     top-level children, then appends the supplied replacement body.
#   - DB is the INDEX: there is NO update_index step (the DB's views/properties
#     are the index; nothing to append into an INDEX page).
#   - Frontmatter maps to DB PROPERTIES, not YAML. Body markdown -> Notion
#     blocks. `[[wikilinks]]` render as bold title text; turning them into real
#     page mentions needs a batch two-pass (resolve all title->id first) and is
#     out of scope for this single-note adapter.
#
# macOS Bash 3.2 compatible: no mapfile/readarray, no associative arrays.
# Requires: curl, jq, python3 (md->blocks). Token in env NOTION_API_TOKEN.
#
# Usage:
#   notion-graduate.sh --db DATABASE_ID --title TITLE [--content BODY.md]
#     [--page-id EXISTING_PAGE_ID]
#     [--type knowledge_note] [--contains a,b,c] [--tags a,b,c]
#     [--graduated-from TEXT] [--graduated-at YYYY-MM-DD]
#     [--contributor NAME]... [--graduated-by NAME]...
#     [--authoring-mode ai_generated] [--props-json FILE] [--dry-run]
#
# Output (stdout): JSON { id, url }
set -uo pipefail

NV="${NOTION_API_VERSION:-2022-06-28}"
DB=""; PAGE_ID=""; TITLE=""; CONTENT_FILE=""; PROPS_JSON=""
TYPE=""; CONTAINS=""; TAGS=""; GFROM=""; GAT=""; AMODE=""
CONTRIBUTOR_ENTRIES=()
GRADUATED_BY_ENTRIES=()
DRY_RUN=0

die() { echo "error: $*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --db) DB="${2:-}"; shift 2;;
    --page-id) PAGE_ID="${2:-}"; shift 2;;
    --title) TITLE="${2:-}"; shift 2;;
    --content) CONTENT_FILE="${2:-}"; shift 2;;
    --type) TYPE="${2:-}"; shift 2;;
    --contains) CONTAINS="${2:-}"; shift 2;;
    --tags) TAGS="${2:-}"; shift 2;;
    --graduated-from) GFROM="${2:-}"; shift 2;;
    --graduated-at) GAT="${2:-}"; shift 2;;
    --contributor)
      [ -n "${2:-}" ] || die "--contributor requires a non-empty display name"
      CONTRIBUTOR_ENTRIES+=("$2"); shift 2;;
    --graduated-by)
      [ -n "${2:-}" ] || die "--graduated-by requires a non-empty display name"
      GRADUATED_BY_ENTRIES+=("$2"); shift 2;;
    --authoring-mode) AMODE="${2:-}"; shift 2;;
    --props-json) PROPS_JSON="${2:-}"; shift 2;;
    --notion-version) NV="${2:-}"; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    -h|--help) sed -n '2,29p' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) die "unknown arg: $1";;
  esac
done

[ -n "$DB" ] || die "--db is required"
[ -n "$TITLE" ] || die "--title is required"
[ -z "$CONTENT_FILE" ] || [ -f "$CONTENT_FILE" ] || die "content file not found: $CONTENT_FILE"
[ -z "$PROPS_JSON" ] || [ -f "$PROPS_JSON" ] || die "props-json not found: $PROPS_JSON"
command -v curl >/dev/null 2>&1 || die "curl not found"
command -v jq   >/dev/null 2>&1 || die "jq not found"
command -v python3 >/dev/null 2>&1 || die "python3 not found (needed for md->blocks)"
[ "$DRY_RUN" -eq 1 ] || [ -n "${NOTION_API_TOKEN:-}" ] || die "NOTION_API_TOKEN not set (put it in .env; run: set -a; . ./.env; set +a — bash/POSIX syntax; PowerShell users: \$env:NOTION_API_TOKEN='...' instead)"

# --- properties ---
json_string_array() {
  printf '%s\n' "$@" | jq -Rsc '
    split("\n")
    | map(select(length > 0))
    | reduce .[] as $value ([]; if index($value) == null then . + [$value] else . end)
  '
}
CONTRIBUTORS_JSON="$(json_string_array "${CONTRIBUTOR_ENTRIES[@]:-}")"
GRADUATED_BY_JSON="$(json_string_array "${GRADUATED_BY_ENTRIES[@]:-}")"

if [ -n "$PROPS_JSON" ]; then
  PROPS="$(cat "$PROPS_JSON")"
else
  PROPS="$(jq -nc \
    --arg title "$TITLE" --arg type "$TYPE" --arg gfrom "$GFROM" \
    --arg gat "$GAT" --arg amode "$AMODE" --arg contains "$CONTAINS" --arg tags "$TAGS" \
    --argjson contributors "$CONTRIBUTORS_JSON" --argjson graduated_by "$GRADUATED_BY_JSON" '
    def ms($s): ($s | select(.!="") | split(",") | map({name:(gsub("^ +| +$";""))}));
    {Name:{title:[{type:"text",text:{content:$title}}]}}
    + (if $type   !="" then {type:{select:{name:$type}}} else {} end)
    + (if $gfrom  !="" then {graduated_from:{rich_text:[{type:"text",text:{content:$gfrom}}]}} else {} end)
    + (if $gat    !="" then {graduated_at:{date:{start:$gat}}} else {} end)
    + (if $amode  !="" then {authoring_mode:{select:{name:$amode}}} else {} end)
    + (if $contains!="" then {contains:{multi_select:ms($contains)}} else {} end)
    + (if $tags   !="" then {tags:{multi_select:ms($tags)}} else {} end)
    + (if ($contributors|length)>0 then {contributors:{multi_select:($contributors|map({name:.}))}} else {} end)
    + (if ($graduated_by|length)>0 then {graduated_by:{multi_select:($graduated_by|map({name:.}))}} else {} end)
  ')"
fi

# --- body markdown -> Notion blocks ---
md_to_blocks() {
  python3 - "$1" <<'PY'
import sys, json, re
lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
WL = re.compile(r"\[\[([^\]]+)\]\]")
def rich(t):
    out, pos = [], 0
    for m in WL.finditer(t):
        if m.start() > pos: out.append({"type":"text","text":{"content":t[pos:m.start()]}})
        out.append({"type":"text","text":{"content":m.group(1)},"annotations":{"bold":True}})
        pos = m.end()
    if pos < len(t): out.append({"type":"text","text":{"content":t[pos:]}})
    return out or [{"type":"text","text":{"content":""}}]
blocks, i = [], 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith("```"):
        lang = ln[3:].strip() or "plain text"
        if lang == "text": lang = "plain text"
        buf = []; i += 1
        while i < len(lines) and not lines[i].startswith("```"): buf.append(lines[i]); i += 1
        i += 1
        blocks.append({"type":"code","code":{"rich_text":[{"type":"text","text":{"content":"\n".join(buf)}}],"language":lang}}); continue
    if ln.startswith("# "): i += 1; continue
    if ln.startswith(">"):
        buf = []
        while i < len(lines) and lines[i].startswith(">"):
            buf.append(re.sub(r"^> ?", "", lines[i]))
            i += 1
        quote_text = "\n".join(buf)
        if quote_text.strip():
            blocks.append({"type":"quote","quote":{"rich_text":rich(quote_text)}})
        continue
    if ln.startswith("## "): blocks.append({"type":"heading_2","heading_2":{"rich_text":rich(ln[3:])}})
    elif ln.startswith("### "): blocks.append({"type":"heading_3","heading_3":{"rich_text":rich(ln[4:])}})
    elif ln.startswith("- "): blocks.append({"type":"bulleted_list_item","bulleted_list_item":{"rich_text":rich(ln[2:])}})
    elif ln.strip(): blocks.append({"type":"paragraph","paragraph":{"rich_text":rich(ln)}})
    i += 1
print(json.dumps(blocks, ensure_ascii=False))
PY
}
if [ -n "$CONTENT_FILE" ]; then CHILDREN="$(md_to_blocks "$CONTENT_FILE")"; else CHILDREN="[]"; fi

# --- assemble payload ---
PAYLOAD_FILE="$(mktemp -t notion-grad.XXXXXX)"
trap 'rm -f "$PAYLOAD_FILE"' EXIT
jq -nc --arg db "$DB" --argjson props "$PROPS" --argjson children "$CHILDREN" \
  '{parent:{database_id:$db}, properties:$props, children:$children}' > "$PAYLOAD_FILE"

if [ "$DRY_RUN" -eq 1 ]; then
  if [ -n "$PAGE_ID" ]; then
    echo "DRY-RUN: PATCH https://api.notion.com/v1/pages/$PAGE_ID properties; DELETE existing children; PATCH replacement children  (Notion-Version $NV)" >&2
  else
    echo "DRY-RUN: POST https://api.notion.com/v1/pages  (Notion-Version $NV)" >&2
  fi
  echo "  properties: $(printf '%s' "$PROPS" | jq -c 'keys')" >&2
  echo "  children:   $(printf '%s' "$CHILDREN" | jq 'length') blocks" >&2
  echo "  child types: $(printf '%s' "$CHILDREN" | jq -c '[.[].type]')" >&2
  jq -nc --arg id "${PAGE_ID:-<dry-run>}" --arg t "$TITLE" '{id:$id, url:"<dry-run>", title:$t}'
  exit 0
fi

# curl+retry mutating request (rides out SSL EOF flakiness; honors HTTPS_PROXY)
napi_write() { # method path [bodyfile]
  method="$1"; path="$2"; bf="${3:-}"; attempt=0; max=8; resp=""
  while [ "$attempt" -lt "$max" ]; do
    attempt=$((attempt + 1))
    if [ -n "$bf" ]; then
      resp="$(curl -sS -X "$method" "https://api.notion.com/v1/$path" \
      -H "Authorization: Bearer $NOTION_API_TOKEN" -H "Notion-Version: $NV" \
      -H "Content-Type: application/json" --data @"$bf" 2>/dev/null)"; rc=$?
    else
      resp="$(curl -sS -X "$method" "https://api.notion.com/v1/$path" \
        -H "Authorization: Bearer $NOTION_API_TOKEN" -H "Notion-Version: $NV" 2>/dev/null)"; rc=$?
    fi
    [ "$rc" -eq 0 ] && [ -n "$resp" ] && { printf '%s' "$resp"; return 0; }
    sleep "$attempt"
  done
  return 1
}
napi_get() { # path
  path="$1"; attempt=0; max=8; resp=""
  while [ "$attempt" -lt "$max" ]; do
    attempt=$((attempt + 1))
    resp="$(curl -sS "https://api.notion.com/v1/$path" \
      -H "Authorization: Bearer $NOTION_API_TOKEN" -H "Notion-Version: $NV" 2>/dev/null)"; rc=$?
    [ "$rc" -eq 0 ] && [ -n "$resp" ] && { printf '%s' "$resp"; return 0; }
    sleep "$attempt"
  done
  return 1
}

if [ -n "$PAGE_ID" ]; then
  PROPERTIES_FILE="$(mktemp -t notion-props.XXXXXX)"
  CHILDREN_FILE="$(mktemp -t notion-children.XXXXXX)"
  trap 'rm -f "$PAYLOAD_FILE" "$PROPERTIES_FILE" "$CHILDREN_FILE"' EXIT
  jq -nc --argjson props "$PROPS" '{properties:$props}' > "$PROPERTIES_FILE"
  jq -nc --argjson children "$CHILDREN" '{children:$children}' > "$CHILDREN_FILE"
  RESP="$(napi_write PATCH "pages/$PAGE_ID" "$PROPERTIES_FILE")" || die "network give-up updating page properties (proxy/SSL); retry"
  if [ "$(printf '%s' "$RESP" | jq -r '.object // ""')" = "error" ]; then
    die "Notion API error updating page: $(printf '%s' "$RESP" | jq -r '.code + ": " + .message')"
  fi
  BLOCK_IDS_FILE="$(mktemp -t notion-blocks.XXXXXX)"
  trap 'rm -f "$PAYLOAD_FILE" "$PROPERTIES_FILE" "$CHILDREN_FILE" "$BLOCK_IDS_FILE"' EXIT
  cursor=""
  while :; do
    child_path="blocks/$PAGE_ID/children?page_size=100"
    [ -z "$cursor" ] || child_path="$child_path&start_cursor=$cursor"
    existing_children="$(napi_get "$child_path")" || die "network give-up listing existing page body"
    if [ "$(printf '%s' "$existing_children" | jq -r '.object // ""')" = "error" ]; then
      die "Notion API error listing page body: $(printf '%s' "$existing_children" | jq -r '.code + ": " + .message')"
    fi
    printf '%s' "$existing_children" | jq -r '.results[]?.id' >> "$BLOCK_IDS_FILE"
    [ "$(printf '%s' "$existing_children" | jq -r '.has_more // false')" = "true" ] || break
    cursor="$(printf '%s' "$existing_children" | jq -r '.next_cursor')"
  done
  while IFS= read -r block_id; do
    [ -n "$block_id" ] || continue
    deleted="$(napi_write DELETE "blocks/$block_id")" || die "network give-up deleting existing block $block_id"
    [ "$(printf '%s' "$deleted" | jq -r '.object // ""')" != "error" ] || die "Notion API error deleting block $block_id"
  done < "$BLOCK_IDS_FILE"
  if [ "$(printf '%s' "$CHILDREN" | jq 'length')" -gt 0 ]; then
    body_resp="$(napi_write PATCH "blocks/$PAGE_ID/children" "$CHILDREN_FILE")" || die "network give-up writing replacement page body"
    [ "$(printf '%s' "$body_resp" | jq -r '.object // ""')" != "error" ] || die "Notion API error writing replacement body"
  fi
  PAGE_URL="$(printf '%s' "$RESP" | jq -r '.url // ""')"
else
  RESP="$(napi_write POST "pages" "$PAYLOAD_FILE")" || die "network give-up creating page (proxy/SSL); retry"
  if [ "$(printf '%s' "$RESP" | jq -r '.object // ""')" = "error" ]; then
    die "Notion API error: $(printf '%s' "$RESP" | jq -r '.code + ": " + .message')"
  fi
  PAGE_ID="$(printf '%s' "$RESP" | jq -r '.id')"
  PAGE_URL="$(printf '%s' "$RESP" | jq -r '.url')"
fi
if [ "$(printf '%s' "$RESP" | jq -r '.object // ""')" = "error" ]; then
  die "Notion API error: $(printf '%s' "$RESP" | jq -r '.code + ": " + .message')"
fi
[ -n "$PAGE_ID" ] && [ "$PAGE_ID" != "null" ] || die "create returned no id: $RESP"

# read-back verify (title round-trips)
BACK="$(napi_get "pages/$PAGE_ID")" || { echo "warn: read-back request failed; verify manually" >&2; BACK=""; }
if [ -n "$BACK" ]; then
  BT="$(printf '%s' "$BACK" | jq -r '[.properties[]|select(.type=="title")|.title[]?.plain_text]|join("")' 2>/dev/null || echo "")"
  case "$BT" in
    *"$TITLE"*) : ;;
    *) echo "warn: read-back title mismatch (got '$BT'); verify manually" >&2;;
  esac
fi

jq -nc --arg id "$PAGE_ID" --arg url "$PAGE_URL" '{id:$id, url:$url}'
