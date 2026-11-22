#!/usr/bin/env bash
set +x
set -euo pipefail
umask 077
unset CDPATH ENV BASH_ENV NODE_OPTIONS NODE_PATH
unset LD_PRELOAD LD_LIBRARY_PATH DYLD_INSERT_LIBRARIES DYLD_LIBRARY_PATH DYLD_FRAMEWORK_PATH

source_path=${BASH_SOURCE[0]}
case "$source_path" in */*) source_path=${source_path%/*} ;; *) source_path=. ;; esac
HERE="$(builtin cd "$source_path" && builtin pwd -P)"

bp_workspace() {
  local d fallback="" profile_home="" profile_config=""
  if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -d "$CLAUDE_PROJECT_DIR" ]; then
    (builtin cd "$CLAUDE_PROJECT_DIR" && builtin pwd -P)
    return
  fi
  d=$(builtin pwd -P)
  if [ -n "${HOME:-}" ]; then profile_home=$(builtin cd "$HOME" 2>/dev/null && builtin pwd -P) || true; fi
  if [ -n "${CLAUDE_CONFIG_DIR:-}" ]; then profile_config=$(builtin cd "$CLAUDE_CONFIG_DIR" 2>/dev/null && builtin pwd -P) || true; fi
  while [ "$d" != / ]; do
    if [ -e "$d/.git" ]; then printf '%s\n' "$d"; return; fi
    if [ -z "$fallback" ] && [ -d "$d/.claude" ] && [ "$d" != "$profile_home" ] && [ "$d/.claude" != "$profile_config" ]; then fallback="$d"; fi
    d="${d%/*}"
    d="${d:-/}"
  done
  if [ -n "$fallback" ]; then printf '%s\n' "$fallback"; else builtin pwd -P; fi
}

bp_external_launchers() {
  local executable target depth parent
  for executable in python3 node git jq curl zip unzip; do
    target="$1/$executable"
    [ -x "$target" ] || continue
    depth=0
    while [ -L "$target" ]; do
      depth=$((depth + 1))
      [ "$depth" -le 40 ] || return 1
      parent="${target%/*}"
      target=$(/usr/bin/readlink "$target") || return 1
      case "$target" in /*) : ;; *) target="$parent/$target" ;; esac
    done
    parent=$(builtin cd "${target%/*}" && builtin pwd -P) || return 1
    case "$parent" in "$BP_ROOT"|"$BP_ROOT/"*) return 1 ;; esac
  done
}

# Resolve the same workspace before looking up any external launcher.
BP_ROOT=$(bp_workspace)
IFS=: read -r -a runtime_dirs <<< "${PATH:-/usr/bin:/bin}:/usr/bin:/bin"
runtime_path=""
for runtime_dir in "${runtime_dirs[@]}"; do
  case "$runtime_dir" in /*) : ;; *) continue ;; esac
  runtime_dir=$(builtin cd "$runtime_dir" 2>/dev/null && builtin pwd -P) || continue
  case "$runtime_dir" in "$BP_ROOT"|"$BP_ROOT/"*) continue ;; esac
  bp_external_launchers "$runtime_dir" || continue
  runtime_path="${runtime_path:+$runtime_path:}$runtime_dir"
done
[ -n "$runtime_path" ] || { printf '%s\n' 'FAILED: trusted runtime launchers unavailable' >&2; exit 1; }
export PATH="$runtime_path"

# shellcheck source=SCRIPTDIR/brewpage-lib.sh
. "$HERE/brewpage-lib.sh"

die() { printf 'FAILED: %s\n' "$1"; exit 1; }
# rc 0 when the flag at $2 has a value after it ($1 = remaining argc).
need() { [ "$1" -ge 2 ] || die "$2 needs a value"; }

# curl's form grammar parses commas/semicolons even inside shell-quoted argv.
form_file() {
  local path="$2"
  path="${path//\\/\\\\}"
  path="${path//\"/\\\"}"
  printf '%s=@"%s"' "$1" "$path"
}

BP_FRESH=""
# Allocates a run dir, EXIT discards it until re-armed: also when bp_run_dir rejects it.
new_run() {
  BP_FRESH=$(bp_prepare) || die "cannot allocate a private run directory"
  trap 'bp_discard "$BP_FRESH"' EXIT
}

usage() {
  cat <<'USAGE'
brewpage-run.sh probe <path>
brewpage-run.sh limits
brewpage-run.sh stage --run <run_id|''> --text <chunk>
brewpage-run.sh publish <html|html-file|json|file|site-dir|site-zip> --ns <ns> [--ttl N] [--entry F]
  [--delivery-mode path|subdomain] --password-file <ABS|''> [--state JSON] [--confirmed --review-sha256 SHA256] (--text T | --run ID | --path P)
  [--anonymous | --owner-target URL]
brewpage-run.sh update <html|html-file|json|file|site-dir|site-zip> --target URL --password-file ''
  [--entry F] [--state JSON] [--confirmed --review-sha256 SHA256] (--text T | --run ID | --path P)
brewpage-run.sh owner-recover
brewpage-run.sh owner-pending
brewpage-run.sh owner-reconcile
brewpage-run.sh cleanup --run <run_id>
--ns and --password-file are required; --password-file '' explicitly selects no password.
Repeat --exclude-file ABS for additional protected files on publish or update.
--state: Page data config, a JSON object ({} = defaults); HTML pages and sites only.
Empty --ttl uses 15; empty --entry/--delivery-mode/--state are omitted. Prints OK/CONFIRM:/FAILED:; CONFIRM exits 2.
The Safe runner stores owner proof automatically in the user's private application state.
USAGE
}

# Read-only: type + source-tree estimates for Step 3; never uploads, never writes.
cmd_probe() {
  [ "$#" -eq 1 ] || die "probe takes exactly one path"
  local p="$1" abs html_files entry
  if [ -d "$p" ]; then
    abs=$(cd "$p" && pwd -P)
    # Hidden paths (root .well-known/ aside) never ship; entry = server rule: index.html, else shallowest HTML.
    html_files=$(cd "$abs" && find . -type f \( -name '*.html' -o -name '*.htm' \) | sed 's|^\./||' | LC_ALL=C sort |
      awk -F/ '{ for (i = 1; i <= NF; i++) if ($i ~ /^\./ && !(i == 1 && $i == ".well-known")) next; print }')
    if [ -f "$abs/index.html" ]; then entry=index.html; else
      entry=$(printf '%s\n' "$html_files" | awk -F/ 'NF { print NF "\t" $0 }' | LC_ALL=C sort -s -n -k1,1 | sed -n '1p' | cut -f2-)
    fi
    printf 'TYPE: site-dir\nPATH: %s\nFILES: %s\nHTML: %s\nSIZE_KB: %s\nENTRY: %s\n' "$abs" \
      "$(find "$abs" -type f | wc -l | tr -d ' ')" "$(printf '%s' "$html_files" | grep -c . || true)" \
      "$(du -sk "$abs" | cut -f1)" "${entry:-none}"
  elif [ -f "$p" ]; then
    abs="$(cd "$(dirname "$p")" && pwd -P)/$(basename "$p")"
    command node "$HERE/publish.mjs" file --path "$abs" --check-only yes --history-file "$HISTORY_FILE" || exit 1
    local type=file
    case "$p" in *.zip) type=site-zip ;; esac
    if bp_is_markdown_path "$p"; then type=markdown; fi
    if bp_is_html_path "$p"; then type=html-file; fi
    printf 'TYPE: %s\nPATH: %s\nBYTES: %s\nMIME: %s\n' "$type" "$abs" "$(wc -c < "$abs" | tr -d ' ')" \
      "$(file --mime-type -b -- "$abs" 2>/dev/null || echo unknown)"
  else
    printf 'TYPE: none\n'
  fi
}

# Read-only: the server's current user-facing upload limits (GET /api/limits), one KEY: value per line.
cmd_limits() {
  [ "$#" -eq 0 ] || die "limits takes no arguments"
  command -v jq >/dev/null || die "jq required"
  local body
  body=$(bp_curl -s -A "$BP_UA" https://brewpage.app/api/limits) || die "limits request failed"
  printf '%s' "$body" | jq -er '(.sites // empty) as $s | def mb: . / 1048576 * 10 | round / 10;
    "REQUEST_MAX_MB: \(.requestMaxBytes | mb)", "SITE_MAX_FILES: \($s.maxFiles)", "SITE_MAX_FILE_MB: \($s.maxFileBytes | mb)",
    "SITE_MAX_TOTAL_MB: \($s.maxTotalBytes | mb)", "SITE_MAX_ARCHIVE_EXPANSION_MB: \($s.maxArchiveExpansionBytes | mb)",
    "PATH_MAX_CHARS: \($s.maxPathChars)", "PATH_MAX_BYTES: \($s.maxPathBytes)", "NAME_MAX_BYTES: \($s.maxNameBytes)"' 2>/dev/null ||
    die "limits unavailable (unexpected response)"
}

# Allocates a run (empty --run) or appends to it; chunks rejoin with one newline between them.
cmd_stage() {
  local run="" text="" have_text=0 file
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --run) need "$#" "$1"; run="$2"; shift 2 ;;
      --text) need "$#" "$1"; text="$2"; have_text=1; shift 2 ;;
      *) die 'unknown stage argument' ;;
    esac
  done
  [ "$have_text" = 1 ] || die "stage needs --text"
  if [ -z "$run" ]; then
    new_run
    run="${BP_FRESH##*/}"
  fi
  bp_run_dir "$run" || exit 1
  file="$BP_RUN_DIR/brewpage-content.md"
  local bytes
  bytes=$(printf '%s' "$text" | bp_python -c '
import fcntl, os, stat, sys
fd = os.open(sys.argv[1], os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
with os.fdopen(fd, "ab") as target:
    fcntl.flock(target, fcntl.LOCK_EX)
    info = os.fstat(target.fileno())
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600:
        sys.exit(1)
    if info.st_size:
        target.write(b"\n")
    target.write(sys.stdin.buffer.read())
    target.flush()
    print(os.fstat(target.fileno()).st_size)
' "$file" 2>/dev/null) || die "staged content destination is unsafe"
  printf 'RUN: %s\nBYTES: %s\n' "$run" "$bytes"
  # Staged: the run outlives this call for the next chunk and the publish.
  trap - EXIT
}

cmd_cleanup() {
  [ "$#" -eq 2 ] && [ "$1" = --run ] || die "cleanup takes --run <run_id>"
  bp_run_dir "$2" || exit 1
  bp_cleanup
  printf 'CLEANED: %s\n' "$2"
}

lock_history() {
  bp_state_begin || return 1
  exec 9< "$BP_HISTORY_ROOT"
  export BREWPAGE_HISTORY_LOCK_FD=9
  bp_history lock
}

cmd_owner_recover() {
  [ "$#" = 0 ] || die 'owner-recover takes no arguments'
  local metadata reader owner_api
  lock_history || die 'cannot lock protected owner storage'
  new_run
  bp_run_dir "${BP_FRESH##*/}" || exit 1
  trap bp_cleanup EXIT
  local proof="$BP_RUN_DIR/recovery-owner-header.txt"
  metadata=$(bp_history recover-target "$proof") || die 'no readable protected recovery receipt'
  reader=$(printf '%s' "$metadata" | jq -er '.reader') || exit 1
  owner_api=$(printf '%s' "$metadata" | jq -er '.ownerApi') || exit 1
  bp_verify_reader "$reader" "$owner_api" "$proof" || die 'recovered reader host could not be verified'
  bp_history recover || die 'no readable protected recovery receipt'
  echo 'OWNER TOKEN RECOVERED'
}

cmd_owner_pending() {
  [ "$#" = 0 ] || die 'owner-pending takes no arguments'
  lock_history || die 'cannot lock protected owner storage'
  bp_history pending-list
}

cmd_owner_reconcile() {
  [ "$#" = 0 ] || die 'owner-reconcile takes no arguments'
  lock_history || die 'cannot lock protected owner storage'
  bp_history reconcile || die 'verified reconciliation is missing or does not match the pending create'
  echo 'OWNER RECONCILIATION RECORDED'
}

check_review() {
  if [ -n "$BREWPAGE_REVIEW_SHA256" ]; then
    [ "${#BREWPAGE_REVIEW_SHA256}" -eq 64 ] || die "review SHA256 must be 64 lowercase hex characters"
    case "$BREWPAGE_REVIEW_SHA256" in *[!0123456789abcdef]*) die "review SHA256 must be 64 lowercase hex characters" ;; esac
    [ "$BREWPAGE_CONFIRMED" = 1 ] || die "review SHA256 requires --confirmed"
  fi
}

bp_selected_file() {
  local path="$1" output_dir="$2" zip_snapshot="${3:-}" staged="${4:-}"
  (umask 077; mkdir "$output_dir") || return 1
  CHECKED_PATH="$output_dir/${path##*/}"
  command node "$HERE/publish.mjs" file --path "$path" --out "$CHECKED_PATH" --history-file "$HISTORY_FILE" \
    --password-file "$pwfile" --password-identity "$password_identity" --zip-snapshot "$zip_snapshot" --staged-content "$staged" \
    ${exclusions[@]+"${exclusions[@]}"}
}

bp_selected_site() {
  local kind="$1" path="$2" rc=0 manifest
  if [ "$kind" = site-dir ]; then
    CHECKED_PATH="$BP_RUN_DIR/site.zip"
    manifest=$(command node "$HERE/publish.mjs" pack --dir "$path" --out "$CHECKED_PATH" ${ENTRY:+--entry "$ENTRY"} \
      --history-file "$HISTORY_FILE" --password-file "$pwfile" --password-identity "$password_identity" \
      ${exclusions[@]+"${exclusions[@]}"}) || rc=$?
  else
    bp_selected_file "$path" "$BP_RUN_DIR/archive" yes || return 1
    manifest=$(command node "$HERE/publish.mjs" inspect --zip "$CHECKED_PATH" ${ENTRY:+--entry "$ENTRY"} \
      --history-file "$HISTORY_FILE" --password-file "$pwfile" --password-identity "$password_identity" ${exclusions[@]+"${exclusions[@]}"}) || rc=$?
  fi
  bp_archive_gate "$rc" "$manifest" "$CHECKED_PATH"
}

cmd_publish() {
  local action="$1"; shift
  local type="${1:-}" ns="" days=15 entry="" mode="" pwfile="" state="" text="" run="" path="" have_text=0 sources=0 have_password=0
  local target="" owner_target="" anonymous=0 ttl_set=0 CHECKED_PATH=""
  local -a exclusions=()
  if [ "$#" -gt 0 ]; then shift; fi
  BREWPAGE_CONFIRMED=0
  BREWPAGE_REVIEW_SHA256=""
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --ns) need "$#" "$1"; ns="$2"; shift 2 ;;
      --ttl) need "$#" "$1"; days="${2:-15}"; ttl_set=1; shift 2 ;;
      --entry) need "$#" "$1"; entry="$2"; shift 2 ;;
      --delivery-mode) need "$#" "$1"; mode="$2"; shift 2 ;;
      --password-file) need "$#" "$1"; pwfile="$2"; have_password=1; shift 2 ;;
      --state) need "$#" "$1"; state="$2"; shift 2 ;;
      --text) need "$#" "$1"; text="$2"; have_text=1; sources=$((sources + 1)); shift 2 ;;
      --run) need "$#" "$1"; run="$2"; sources=$((sources + 1)); shift 2 ;;
      --path) need "$#" "$1"; path="$2"; sources=$((sources + 1)); shift 2 ;;
      --confirmed) BREWPAGE_CONFIRMED=1; shift ;;
      --review-sha256) need "$#" "$1"; BREWPAGE_REVIEW_SHA256="$2"; shift 2 ;;
      --target) need "$#" "$1"; target="$2"; shift 2 ;;
      --owner-target) need "$#" "$1"; owner_target="$2"; shift 2 ;;
      --exclude-file) need "$#" "$1"; exclusions+=(--exclude-file "$2"); shift 2 ;;
      --anonymous) anonymous=1; shift ;;
      *) die 'unknown publish argument' ;;
    esac
  done
  [ "$have_password" -eq 1 ] || die "explicit --password-file choice required (empty means no password)"
  command -v python3 >/dev/null || die "python3 required for secure history"
  [ "$sources" -eq 1 ] || die "publish needs exactly one of --text, --run, --path"
  check_review
  if [ "$action" = update ]; then
    [ -n "$target" ] || die "update needs --target with the exact publication URL"
    [ "$anonymous$ttl_set" = 00 ] && [ -z "$owner_target$mode$pwfile" ] || die "update needs owner proof and keeps existing visibility and expiry"
  else
    [ -z "$target" ] || die "--target applies to update only"
    if [ "$anonymous" = 1 ]; then [ -z "$owner_target" ] || die "--anonymous cannot be combined with saved owner proof"; fi
  fi
  # A .html/.htm or markdown path is a page whichever of these a caller names.
  if [ -n "$path" ] && bp_is_html_path "$path"; then case "$type" in file | html) type=html-file ;; esac; fi
  if [ -n "$path" ] && [ "$type" = file ] && bp_is_markdown_path "$path"; then type=html; fi
  case "$type" in
    html) : ;;
    html-file) bp_is_html_path "$path" || die "html-file takes a .html or .htm --path" ;;
    json) [ -z "$path" ] || die "json takes --text or --run" ;;
    file | site-dir | site-zip) [ -n "$path" ] || die "$type takes --path" ;;
    *) die 'unknown publish type' ;;
  esac
  case "$type" in site-dir | site-zip) : ;; *) [ -z "$entry" ] || die "--entry applies to sites only" ;; esac
  case "$type" in site-dir | site-zip) : ;; *) [ -z "$BREWPAGE_REVIEW_SHA256" ] || die "review SHA256 applies to sites only" ;; esac
  if [ -n "$path" ]; then
    case "$type" in site-dir) [ -d "$path" ] || die 'selected directory is missing' ;; *) [ -f "$path" ] || die 'selected file is missing' ;; esac
  fi
  # Slot errors fail before the run is touched, so a staged run survives any bad flag or password file.
  if [ "$action" = update ]; then bp_validate "${ns:-target}" "$days" "$entry" || exit 1; else bp_validate "$ns" "$days" "$entry" || exit 1; fi
  case "$mode" in '' | path | subdomain) : ;; *) die "delivery mode must be path or subdomain" ;; esac
  # Page data config travels as one compact JSON object; JSON and plain files take none.
  if [ -n "$state" ]; then
    case "$type" in html | html-file | site-dir | site-zip) : ;; *) die "--state applies to UTF-8 HTML pages and sites only" ;; esac
    state=$(printf '%s' "$state" | jq -cse 'if length == 1 and (.[0] | type) == "object" then .[0] else false end' 2>/dev/null) ||
      die "--state must be one JSON object, e.g. {}"
  fi

  local id pwmode=none password_identity=""
  BP_HEADER_FILE=""
  if [ -n "$run" ]; then
    id="$run"
  else
    new_run
    id="${BP_FRESH##*/}"
  fi
  # An EXISTING run bp_run_dir rejects is left as is; only a fresh one is discarded.
  bp_run_dir "$id" || exit 1
  if [ -n "$pwfile" ]; then
    pwmode="file"
    BP_HEADER_FILE="$BP_RUN_DIR/password-header.txt"
    password_identity=$(bp_python "$HERE/inputs.py" password "$pwfile" "$BP_HEADER_FILE") || exit 1
  fi
  trap bp_cleanup EXIT
  local content="$BP_RUN_DIR/brewpage-content.md" ENTRY="$entry" resolved_entry=""
  if [ "$have_text" = 1 ]; then
    (umask 077; printf '%s' "$text" > "$content")
  elif [ -n "$run" ]; then
    [ -f "$content" ] || die "run $id has no staged text"
    bp_selected_file "$content" "$BP_RUN_DIR/checked" '' yes || exit 1
    content="$CHECKED_PATH"
  elif [ -n "$path" ]; then
    case "$type" in
      site-dir | site-zip) bp_selected_site "$type" "$path" || exit $?; resolved_entry="$ENTRY" ;;
      *)
        bp_selected_file "$path" "$BP_RUN_DIR/checked" || exit 1
        content="$CHECKED_PATH"
        case "$type" in
          html | html-file)
            if ! bp_is_utf8 "$content"; then
              [ "$action" != update ] || die "HTML update needs UTF-8 source"
              [ -z "$state" ] || die "--state applies to UTF-8 HTML pages and sites only"
              type=file
            fi
            ;;
        esac
        ;;
    esac
  fi

  if [ -n "$state" ]; then printf '%s' "$state" | bp_scan_input - json || exit 1; fi
  case "$type" in
    site-dir | site-zip) : ;;
    *) bp_scan_input "$content" "$type" || exit 1 ;;
  esac

  lock_history || die 'cannot lock protected owner storage'
  local intent=create method=POST endpoint="" kind response
  if [ "$action" = update ]; then
    intent=update
    method=PUT
  elif [ "$anonymous" = 1 ]; then
    intent=anonymous
  else
    target="$owner_target"
  fi
  bp_begin "${ns:-target}" "$days" "$entry" "$id" "$pwmode" "$mode" || exit 1
  ENTRY="$resolved_entry"
  bp_owner_begin "$intent" "$target" || exit 1
  if [ -n "$target" ]; then
    bp_verify_reader "$target" "$BP_OWNER_API" "$BP_OWNER_HEADER_FILE" || die 'saved reader host does not match the selected publication'
  fi
  bp_history receipt-ready || die "cannot prepare protected owner recovery; run owner-recover if pending"
  case "$type" in html | html-file) kind=html ;; site-dir | site-zip) kind=sites ;; file) kind=files ;; *) kind="$type" ;; esac
  if [ "$action" = update ]; then
    [ -n "$BP_OWNER_HEADER_FILE" ] || die "update requires owner proof"
    case "$BP_OWNER_API" in https://brewpage.app/api/"$kind"/*) : ;; *) die "replacement type must match the targeted publication kind" ;; esac
    if [ -n "$ns" ]; then
      case "$BP_OWNER_API" in https://brewpage.app/api/"$kind/$ns"/*) : ;; *) die "--ns must match the targeted publication namespace" ;; esac
    fi
    endpoint="$BP_OWNER_API"
  else
    endpoint="https://brewpage.app/api/$kind?ns=$NS&ttl=$DAYS"
  fi

  local unknown="request failed; outcome unknown, reconcile this write before trying again"
  case "$type" in
    html | html-file)
      local format=markdown
      if [ "$type" = html-file ] || { [ -z "$path" ] && bp_is_html_document "$content"; }; then format=html; fi
      jq -n --rawfile c "$content" --arg s "$state" '{content: $c} + (if $s == "" then {} else {state: ($s | fromjson)} end)' \
        > "$BP_RUN_DIR/payload.json"
      if [ "$action" = publish ]; then endpoint="$endpoint&format=$format"; elif [ "$format" = html ]; then endpoint="$endpoint?format=html"; fi
      if [ "$format" = html ] || [ "$action" = update ]; then
        case "$endpoint" in *\?*) endpoint="$endpoint&verbatim=true" ;; *) endpoint="$endpoint?verbatim=true" ;; esac
      fi
      bp_operation_request "$method" "$endpoint" "$kind" "$BP_RUN_DIR/payload.json" || die "cannot preserve request fingerprint before dispatch"
      response=$(bp_request "$method" "$endpoint" -H "Content-Type: application/json" --data-binary @"$BP_RUN_DIR/payload.json") || die "$unknown"
      bp_finish "$response" "$DAYS" html "$method" "$endpoint"
      ;;
    json)
      jq empty "$content" 2>/dev/null || die "payload is not valid JSON"
      bp_operation_request "$method" "$endpoint" "$kind" "$content" || die "cannot preserve request fingerprint before dispatch"
      response=$(bp_request "$method" "$endpoint" -H "Content-Type: application/json" --data-binary @"$content") || die "$unknown"
      bp_finish "$response" "$DAYS" json "$method" "$endpoint"
      ;;
    file)
      bp_operation_request "$method" "$endpoint" "$kind" "$content" || die "cannot preserve request fingerprint before dispatch"
      response=$(bp_request "$method" "$endpoint" -F "$(form_file file "$content")") || die "$unknown"
      bp_finish "$response" "$DAYS" file "$method" "$endpoint"
      ;;
    site-dir | site-zip)
      local separator='&'
      if [ "$action" = update ]; then
        separator='?'
        if [ -z "$entry" ]; then
          local metadata
          metadata=$(bp_request GET "$endpoint") || die "cannot verify existing site entry; no replacement sent"
          [ "$(bp_response_status)" = 200 ] || die "cannot verify existing site entry; no replacement sent"
          ENTRY=$(printf '%s' "$metadata" | jq -er '.entryFile | strings | select(length > 0)' 2>/dev/null) || die "existing site entry is unresolved; no replacement sent"
          bp_python -c 'import sys,zipfile; p=sys.argv[2]; safe=not p.startswith("/") and not any(s in ("",".","..") for s in p.split("/")) and not any(ord(c)<32 or ord(c)==127 for c in p); sys.exit(0 if safe and p in zipfile.ZipFile(sys.argv[1]).namelist() else 1)' "$CHECKED_PATH" "$ENTRY" || die "existing entry is absent or invalid in replacement; resolve the entry choice before publishing"
        fi
      fi
      endpoint="$endpoint${separator}entry=$(jq -nr --arg e "$ENTRY" '$e | @uri')"
      bp_operation_request "$method" "$endpoint" "$kind" "$CHECKED_PATH" "$state" || die "cannot preserve request fingerprint before dispatch"
      response=$(bp_request "$method" "$endpoint" -F "$(form_file archive "$CHECKED_PATH")" ${state:+--form-string "state=$state"}) || die "$unknown"
      bp_finish "$response" "$DAYS" site "$method" "$endpoint"
      ;;
  esac
}

cmd="${1:-}"
if [ "$#" -gt 0 ]; then shift; fi
case "$cmd" in
  probe) cmd_probe "$@" ;;
  limits) cmd_limits "$@" ;;
  stage) cmd_stage "$@" ;;
  publish | update) cmd_publish "$cmd" "$@" ;;
  owner-recover) cmd_owner_recover "$@" ;;
  owner-pending) cmd_owner_pending "$@" ;;
  owner-reconcile) cmd_owner_reconcile "$@" ;;
  cleanup) cmd_cleanup "$@" ;;
  -h | --help) usage ;;
  *) usage; die 'unknown subcommand' ;;
esac
