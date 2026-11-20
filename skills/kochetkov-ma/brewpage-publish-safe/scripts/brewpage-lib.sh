#!/usr/bin/env bash
# Sourced (!=executed) by scripts/brewpage-run.sh, the skill's only entry: sets HISTORY_FILE + helpers.
# Owns token-history location (BD03) and URL-safety of prompt-derived query params (BD02).

bp_python() { command python3 -I -S "$@"; }

bp_curl() { command env -i PATH="$PATH" LC_ALL=C curl -q --proto '=https' "$@"; }

bp_scan_input() { bp_python "$HERE/inputs.py" scan "$1" "$2" "${BP_HEADER_FILE:-}"; }

BP_HISTORY_ROOT=""
HISTORY_FILE=""
# Run dirs stay outside .claude/ (protected path); only brewpage-run.sh writes into them.
BP_TMPDIR="${TMPDIR:-/tmp}"
BP_TMPDIR="${BP_TMPDIR%/}"
BP_SAFE_VERSION=$(cat "$HERE/../VERSION")
[[ "$BP_SAFE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || exit 1
BP_UA="BrewPageSkillstoreSafe/$BP_SAFE_VERSION (+https://brewpage.app)"

bp_state_begin() {
  BP_HISTORY_ROOT=$(bp_python "$HERE/history.py" state-root "$BP_ROOT") || return 1
  HISTORY_FILE="$BP_HISTORY_ROOT/brewpage-history.md"
}

bp_history() {
  local operation="$1"
  shift
  bp_python "$HERE/history.py" "$operation" "$BP_HISTORY_ROOT" "$@"
}

# The state root is outside Git; the history file is owned and verified as 0600.
bp_history_init() {
  command -v python3 >/dev/null || { echo 'FAILED: python3 required for secure history'; return 1; }
  bp_history init <<'HEADER'
# brewpage.app — Published Pages

> Owner tokens authorize in-place updates and deletion. Keep this file and its management links private.
> Use `brewpage-run.sh update` with the saved target. A rejected update does not create a replacement.

| Date | URL | Owner Token | TTL | Type | Owner API | Identity |
|------|-----|-------------|-----|------|-----------|----------|
HEADER
}

# shellcheck disable=SC2016 # backticks = literal markdown code spans
bp_history_append() {
  printf '| %s | [%s](%s) | `%s` | %sd | %s | %s | `%s` |\n' \
    "$(date -u '+%Y-%m-%d %H:%M')" "$1" "$1" "$2" "$3" "$4" "$5" "$6" | bp_history append "$7"
}

# BD02: ns/ttl/entry arrive as single-quoted literals; re-checked here as data before the URL.
# Explicit char lists, never a-z ranges: bash 3.2 en_US.UTF-8 collation lets [a-z] match A-Z and accents.
bp_validate() {
  local ns="$1" days="$2" entry="$3"
  case "$ns" in
    *[!abcdefghijklmnopqrstuvwxyz0123456789-]* | '') echo "FAILED: namespace must be 1-32 chars of a-z0-9-"; return 1 ;;
  esac
  [ "${#ns}" -ge 1 ] && [ "${#ns}" -le 32 ] || { echo "FAILED: namespace must be 1-32 chars"; return 1; }
  case "$days" in
    '' | *[!0123456789]*) echo "FAILED: ttl must be a positive integer"; return 1 ;;
  esac
  [ "$days" -ge 1 ] || { echo "FAILED: ttl must be >= 1"; return 1; }
  if [ -n "$entry" ]; then
    case "$entry" in
      *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._/-]* | */../* | ../* | */..) echo "FAILED: entry must be a plain relative file name"; return 1 ;;
    esac
  fi
  return 0
}

# rc 0: path ends in .html/.htm, any case; such a file is always published as a page.
bp_is_html_path() {
  case "${1:-}" in *.[Hh][Tt][Mm] | *.[Hh][Tt][Mm][Ll]) return 0 ;; *) return 1 ;; esac
}

# rc 0: path ends in .md/.markdown, any case; rendered through /api/html, never a raw download.
bp_is_markdown_path() {
  case "${1:-}" in *.[Mm][Dd] | *.[Mm][Aa][Rr][Kk][Dd][Oo][Ww][Nn]) return 0 ;; *) return 1 ;; esac
}

# rc 0: file holds a whole HTML document: doctype or <html> first, after an optional BOM and whitespace.
bp_is_html_document() {
  bp_python -c 'import re,sys; sys.exit(0 if re.match(rb"(?:\xef\xbb\xbf)?\s*<(?:!doctype\s+html|html)(?=[\s>])", open(sys.argv[1],"rb").read(), re.I) else 1)' "$1"
}

# rc 0: file decodes as UTF-8; jq --rawfile would silently replace any other bytes.
bp_is_utf8() {
  bp_python -c 'import sys; open(sys.argv[1],"rb").read().decode("utf-8")' "$1" 2>/dev/null
}

# Allocate before writing inputs; only the generated ASCII basename is substituted into blocks.
bp_prepare() {
  mkdir -p "$BP_TMPDIR" || return 1
  (umask 077; mktemp -d "$BP_TMPDIR/brewpage.XXXXXX")
}

bp_run_dir() {
  local id="${1:-}"
  case "$id" in
    brewpage.??????) : ;;
    *) echo "FAILED: invalid publish run id"; return 1 ;;
  esac
  case "$id" in *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.]*) echo "FAILED: invalid publish run id"; return 1 ;; esac
  BP_RUN_DIR="$BP_TMPDIR/$id"
  [ -d "$BP_RUN_DIR" ] && [ ! -L "$BP_RUN_DIR" ] && [ -O "$BP_RUN_DIR" ] &&
    [ -n "$(find "$BP_RUN_DIR" -maxdepth 0 -type d -perm 0700 -print)" ] || {
      echo "FAILED: publish run directory must be owned, private and non-symlink"; return 1;
    }
}

bp_cleanup() {
  [ -n "${BP_RUN_DIR:-}" ] || return 0
  bp_run_dir "${BP_RUN_DIR##*/}" || return 1
  rm -rf -- "$BP_RUN_DIR"
}

# Removes a dir this call just made via bp_prepare, even one bp_run_dir rejects (bp_cleanup refuses it).
bp_discard() {
  case "${1:-}" in "$BP_TMPDIR"/brewpage.??????) rm -rf -- "$1" ;; esac
}

# Prelude: explicit run id/password policy, no implicit shared credential discovery.
bp_begin() {
  NS="$1"; DAYS="$2"; ENTRY="$3"
  bp_run_dir "${4:-}" || return 1
  trap bp_cleanup EXIT
  trap 'exit 1' HUP INT TERM
  bp_validate "$NS" "$DAYS" "$ENTRY" || return 1
  BP_DELIVERY_MODE="${6:-}"
  case "$BP_DELIVERY_MODE" in ''|path|subdomain) : ;; *) echo "FAILED: delivery mode must be path or subdomain"; return 1 ;; esac
  case "${5:-}" in none|file) BP_PASSWORD_MODE="$5" ;; *) echo "FAILED: explicit password mode required"; return 1 ;; esac
  bp_history_init || { echo "FAILED: cannot initialize protected owner storage"; return 1; }
  command -v jq >/dev/null || { echo "FAILED: jq required"; return 1; }
  if [ "$BP_PASSWORD_MODE" = file ] && [ ! -f "$BP_HEADER_FILE" ]; then
    echo 'FAILED: private password header is unavailable'
    return 1
  fi
}

# curl reads the header file; neither shell argv nor output contains the password.
# A function has its own positional parameters, so no `set --` juggling is needed.
bp_request() {
  local method="$1" url="$2"
  shift 2
  case "$url" in
    https://brewpage.app/api/*) : ;;
    *) echo 'FAILED: request destination must be the official BrewPage API' >&2; return 1 ;;
  esac
  if [ -n "${BP_DELIVERY_MODE:-}" ]; then
    set -- -H "X-Delivery-Mode: $BP_DELIVERY_MODE" "$@"
  fi
  if [ -n "${BP_OWNER_HEADER_FILE:-}" ]; then
    set -- -H "@$BP_OWNER_HEADER_FILE" "$@"
  fi
  if [ -n "${BP_HEADER_FILE:-}" ]; then
    set -- -H "@$BP_HEADER_FILE" "$@"
  fi
  local output status
  : > "$BP_RUN_DIR/http-status.txt" || return 1
  if [ "$method" = POST ]; then printf '%s' "$BP_OPERATION_REQUEST" | bp_history pending || return 1; fi
  output=$(bp_curl -s -A "$BP_UA" -X "$method" "$url" "$@" -w $'\nBP_HTTP_STATUS:%{http_code}') || return 1
  status="${output##*$'\n'BP_HTTP_STATUS:}"
  case "$status" in
    [0123456789][0123456789][0123456789])
      printf '%s' "$status" > "$BP_RUN_DIR/http-status.txt" || return 1
      printf '%s' "${output%$'\n'BP_HTTP_STATUS:*}"
      ;;
    *) return 1 ;;
  esac
}

bp_response_status() { cat "$BP_RUN_DIR/http-status.txt"; }

bp_reader_host() {
  local host="${1#https://}"
  host="${host%%/*}"
  printf '%s' "${host%.}" | tr '[:upper:]' '[:lower:]'
}

bp_verify_reader() {
  local reader="$1" target="$2" proof="$3" host metadata
  host=$(bp_reader_host "$reader")
  [ "$host" != brewpage.app ] || return 0
  [ -n "$proof" ] || return 1
  metadata=$(BP_OWNER_HEADER_FILE="$proof" BP_HEADER_FILE='' bp_request GET "https://brewpage.app/api/hosts/$host/owner-check" --max-time 15) || return 1
  [ "$(bp_response_status)" = 200 ] || return 1
  printf '%s' "$metadata" | jq -se --arg target "$target" '
    def segment: if . == "site" then "sites" elif . == "file" then "files" else . end;
    ($target | split("/")) as $api | select(length == 1) | .[0]
    | .isOwner == true and (.type | segment) == $api[4] and .namespace == $api[5] and .id == $api[6]
  ' >/dev/null 2>&1
}

bp_verify_public_redirect() {
  local reader="$1" owner_api="$2" apex output
  [ "$(bp_reader_host "$reader")" != brewpage.app ] || return 0
  apex="https://brewpage.app/${owner_api#https://brewpage.app/api/*/}"
  output=$(bp_curl -sI -A "$BP_UA" --max-time 15 --output /dev/null --write-out '%{http_code}\n%{redirect_url}' "$apex") || return 1
  case "$output" in
    301$'\n'"$reader" | 302$'\n'"$reader" | 307$'\n'"$reader" | 308$'\n'"$reader") return 0 ;;
    *) return 1 ;;
  esac
}

bp_owner_begin() {
  local intent="$1" target="$2" selected
  BP_OWNER_HEADER_FILE="$BP_RUN_DIR/owner-token.txt"
  selected=$(bp_history select "$intent" "$target" "$BP_OWNER_HEADER_FILE") || return 1
  BP_OWNER_API="$selected"
  if [ ! -f "$BP_OWNER_HEADER_FILE" ]; then BP_OWNER_HEADER_FILE=""; fi
  BREWPAGE_OPERATION_ID=$(bp_python -c 'import secrets; print(secrets.token_hex(12))') || return 1
  export BREWPAGE_OPERATION_ID
}

bp_operation_request() {
  [ "$1" = POST ] || return 0
  BP_OPERATION_REQUEST=$(printf '%s' "${5:-}" | bp_python -c '
import hashlib,json,os,stat,sys
from datetime import datetime,timezone
from urllib.parse import urlsplit,parse_qs
operation,method,endpoint,kind,source,delivery,password,proof=sys.argv[1:]
fd=os.open(source,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
with os.fdopen(fd,"rb") as payload:
 info=os.fstat(payload.fileno())
 if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or info.st_nlink!=1: raise ValueError("unsafe request payload")
 digest=hashlib.sha256()
 for chunk in iter(lambda:payload.read(65536),b""): digest.update(chunk)
request={"method":method,"endpoint":endpoint,"kind":kind,"namespace":parse_qs(urlsplit(endpoint).query)["ns"][0],"payloadSha256":digest.hexdigest(),"passwordProtected":password=="file","deliveryMode":delivery}
state=sys.stdin.buffer.read()
if state: request["stateSha256"]=hashlib.sha256(state).hexdigest()
if kind=="files": request["uploadName"]=os.path.basename(source)
authority=None
if proof:
 with os.fdopen(os.open(proof,os.O_RDONLY|os.O_NOFOLLOW),"rb") as owner: authority=hashlib.sha256(owner.read(64).split(b": ",1)[1].strip()).hexdigest()
print(json.dumps({"operationId":operation,"request":request,"recordedAt":datetime.now(timezone.utc).isoformat(),"ownerProofSha256":authority},separators=(",",":")))
' "$BREWPAGE_OPERATION_ID" "$1" "$2" "$3" "$4" "${BP_DELIVERY_MODE:-}" "$BP_PASSWORD_MODE" "$BP_OWNER_HEADER_FILE")
}

# Private recovery is separate from the ordinary reader-facing result.
bp_unsaved() {
  local receipt="$1"
  echo 'NOTICE: publication confirmed; owner history could not be saved securely'
  if printf '%s\n' "$receipt" | bp_history receipt; then
    echo 'OWNER RECOVERY SAVED'
    return 0
  fi
  echo 'NOTICE: protected recovery could not be verified; reconcile this receipt before another write'
  return 1
}

bp_receipt_link() {
  local response="$1" status="$2" method="$3" endpoint="$4"
  printf '%s' "$response" | jq -ser --arg status "$status" --arg method "$method" --arg endpoint "${endpoint%%\?*}" --arg ns "$NS" --rawfile proof "${BP_OWNER_HEADER_FILE:-/dev/null}" '
    def kind: if . == "site" then "sites" elif . == "file" then "files" else . end;
    select(length == 1) | .[0] | select(type == "object") | . as $body
    | .result.action as $action
    | [.isOwner, .result.isOwner, .result.extras.isOwner] | map(select(. != null)) as $ownership
    | select(($ownership | all(type == "boolean")) and ($ownership | unique | length <= 1) and (($ownership | index(false)) == null or $action == "merged"))
    | $body
    | select(if $method == "PUT" then $status == "200" and ($action == null or $action == "updated")
             elif $status == "200" then $action == "merged"
             else $status == "201" and ($action == null or $action == "created" or $action == "created_missing_assets" or $action == "merged") end)
    | .ownerLink | strings | capture("^https://brewpage\\.app/api/(?<kind>html|json|files|sites)/(?<ns>[a-z0-9-]{1,32})/(?<id>[A-Za-z0-9_-]{1,128})$") as $owner
    | select($body.id == $owner.id and $body.namespace == $owner.ns)
    | select(($body.ns == null or $body.ns == $owner.ns) and ([$body.type, $body.kind] | all(. == null or kind == $owner.kind)))
    | ("https://brewpage.app/api/" + $owner.kind) as $api
    | (if $method == "PUT" then "/" + $owner.ns + "/" + $owner.id else "" end) as $target
    | select(($api + $target) == $endpoint or ($owner.kind == "html" and $endpoint == ("https://brewpage.app/api/files" + $target)))
    | select($method == "PUT" or $owner.ns == $ns)
    | $body.link | strings | select(test("^https://[A-Za-z0-9.-]+(?:/[^[:space:][:cntrl:]#|`]*|[?][^[:space:][:cntrl:]#|`]*)?$") and . != $body.manageUrl and . != $body.managementLink)
    | . as $link | select([($body.ownerToken // ""), ($proof | sub("^X-Owner-Token: ";"") | rtrimstr("\n"))]
        | map(strings | select(length > 0) | . as $secret | $link | contains($secret)) | any | not)
    | {link: ., ownerApi: $body.ownerLink}
  ' 2>/dev/null | bp_python "$HERE/history.py" reader-check 2>/dev/null
}

# Every confirmed result retains effective reader facts, independently of credential storage.
bp_finish() {
  local response="$1" days="$2" type="$3" method="$4" endpoint="$5" url token fcount owner_api identity receipt status nonowned_merge=0 saved=0 failed=0 reused=""
  if [ -n "${BP_OWNER_HEADER_FILE:-}" ]; then
    IFS= read -r reused < "$BP_OWNER_HEADER_FILE" || return 1
    reused="${reused#X-Owner-Token: }"
  fi
  status=$(bp_response_status) || return 1
  url=$(bp_receipt_link "$response" "$status" "$method" "$endpoint") || url=""
  if [ -z "$url" ]; then
    if [ "$method" = POST ] && [ -n "$status" ] && [ "$status" -ge 400 ] && [ "$status" -lt 500 ] && [ "$status" -ne 408 ]; then
      bp_history clear || return 1
    fi
    case "$status" in
      4[0123456789][0123456789])
        if [ "$status" != 408 ]; then echo "FAILED: publish rejected (HTTP $status)"; else echo 'FAILED: outcome unknown; check recovery before trying again'; fi
        ;;
      *) echo 'FAILED: outcome unknown; check recovery before trying again' ;;
    esac
    return 1
  fi
  if printf '%s' "$response" | jq -e '.result.action == "merged" and ([.isOwner, .result.isOwner, .result.extras.isOwner] | index(false) != null)' >/dev/null 2>&1; then
    token=""; reused=""; nonowned_merge=1
  else
    token=$(printf '%s' "$response" | jq -er '.ownerToken | if . == null then "" else strings | select(test("^[A-Za-z0-9]{32}$")) end' 2>/dev/null) || {
      echo 'FAILED: publication receipt carries invalid owner proof; verify the outcome before another write'
      return 1
    }
  fi
  if [ -n "$reused" ] && [ -n "$token" ] && [ "$token" != "$reused" ]; then
    echo 'FAILED: publication receipt conflicts with the saved owner; verify the outcome before another write'
    return 1
  fi
  owner_api=$(printf '%s' "$response" | jq -r '.ownerLink')
  identity=$(printf '%s' "$response" | jq -c '{id, namespace, type, routingCohort, deliveryMode, modeLocked, hostingVersion, managementLink, manageUrl, entryFile, createdAt, expiresAt}')
  receipt=$(printf '%s' "$response" | jq -c --rawfile proof "${BP_OWNER_HEADER_FILE:-/dev/null}" --arg api "$owner_api" --arg op "${BREWPAGE_OPERATION_ID:-}" \
    '{origin:"https://brewpage.app",ownerApi:$api,readerUrl:.link,ownerToken:((.ownerToken | strings | select(test("^[A-Za-z0-9]{32}$"))) // ($proof | sub("^X-Owner-Token: ";"") | rtrimstr("\n"))),operationId:$op,
      identity:{id,namespace,type,routingCohort,deliveryMode,modeLocked,hostingVersion,managementLink,manageUrl,entryFile,createdAt,expiresAt},manageUrl}')
  if [ "$nonowned_merge" = 1 ]; then
    if [ "$method" = POST ]; then bp_history clear || return 1; fi
    if ! bp_verify_public_redirect "$url" "$owner_api"; then
      echo 'NOTICE: existing publication returned without ownership; its reader URL could not be verified'
      return 1
    fi
  elif [ "$(bp_reader_host "$url")" != brewpage.app ]; then
    local verification_header="$BP_OWNER_HEADER_FILE"
    if [ -z "$verification_header" ] && [ -n "$token" ]; then
      verification_header="$BP_RUN_DIR/receipt-owner-header.txt"
      (set -o noclobber; printf 'X-Owner-Token: %s\n' "$token" > "$verification_header") || return 1
    fi
    if ! bp_verify_reader "$url" "$owner_api" "$verification_header"; then
      if [ "$method" = POST ] && printf '%s\n' "$receipt" | bp_history receipt; then echo 'OWNER RECOVERY SAVED'; fi
      echo 'FAILED: reader host could not be verified; check recovery before another write'
      return 1
    fi
  fi
  local label="$type"
  if [ "$type" = site ]; then
    fcount=$(printf '%s' "$response" | jq -r '(.fileCount | numbers) // "?"')
    label="site ($fcount files)"
  fi
  if [ "$nonowned_merge" = 0 ] && [ -n "${token:-$reused}" ]; then
    if bp_history_append "$url" "${token:-$reused}" "$days" "$label" "$owner_api" "$identity" "$method"; then
      saved=1
    else
      if [ "$method" = POST ]; then bp_unsaved "$receipt" || true
      else echo 'NOTICE: update confirmed; protected history could not be updated'; fi
      failed=1
    fi
  elif [ "$nonowned_merge" = 0 ] && [ "$method" = POST ]; then
    echo 'NOTICE: owner proof missing from the receipt; recover it before another create'
    failed=1
  fi
  if [ "$type" = site ]; then
    echo "OK $url | Files: $fcount"
  else
    echo "OK $url"
  fi
  if [ -n "$reused" ] && [ "$saved" = 1 ]; then
    echo 'OWNER TOKEN REUSED'
  elif [ "$saved" = 1 ]; then
    echo 'OWNER TOKEN SAVED'
  fi
  if [ "$nonowned_merge" -eq 1 ]; then echo 'NOTICE: existing publication returned without ownership; no owner capability saved'; fi
  printf '%s' "$response" | jq -r '
    (.listed | booleans | "LISTED: " + tostring),
    (select(.result.action == "merged") | "NOTICE: BrewPage returned an existing publication"),
    (select(.result.action == "created_missing_assets") | "NOTICE: the HTML refers to assets outside this publication")' 2>/dev/null || true
  [ "$failed" = 0 ]
}

# Confirmation approves one archive digest; every run still discards its temporary payload.
bp_archive_gate() {
  local rc="$1" manifest="$2" zip="$3"
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 2 ]; then
    [ -n "$zip" ] && rm -f "$zip"
    echo "FAILED: archive not verified (publish.mjs exit $rc) — nothing was uploaded"
    return 1
  fi
  ENTRY=$(printf '%s' "$manifest" | jq -ser --argjson code "$rc" '
    select(length == 1) | .[0] | select(.result == (if $code == 2 then "confirm" else "ok" end))
    | .entry as $entry | select(.entries | index($entry) != null) | $entry | strings | select(length > 0)
  ' 2>/dev/null) || { echo 'FAILED: archive review metadata is invalid'; return 1; }
  bp_scan_input "$zip" site || return 1
  printf '%s' "$manifest" | jq -r '.entries[]' | bp_scan_input - json || return 1
  printf 'ARCHIVE MANIFEST (JSON)\n'
  printf '%s' "$manifest" | jq -ac . || return 1
  if [ "$rc" -eq 2 ] || [ "${BREWPAGE_CONFIRMED:-0}" = 1 ] || [ -n "${BREWPAGE_REVIEW_SHA256:-}" ]; then
    local digest
    digest=$(bp_python - "$zip" <<'PY'
import hashlib, os, stat, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
with os.fdopen(fd, 'rb') as archive:
    info = os.fstat(archive.fileno())
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1:
        raise ValueError('unsafe archive snapshot')
    digest = hashlib.sha256()
    for block in iter(lambda: archive.read(65536), b''):
        digest.update(block)
    print(digest.hexdigest())
PY
    ) || { echo 'FAILED: cannot hash reviewed archive'; return 1; }
    if [ "${BREWPAGE_CONFIRMED:-0}" != 1 ] || [ "${BREWPAGE_REVIEW_SHA256:-}" != "$digest" ]; then
      echo "REVIEW_SHA256: $digest"
      echo "CONFIRM: review this manifest, then re-run with --confirmed --review-sha256 $digest"
      return 2
    fi
  fi
}
