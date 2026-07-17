#!/usr/bin/env bash
set -euo pipefail

stale_only=false
if [[ "${1:-}" == "--stale-only" ]]; then
  stale_only=true
  shift
fi
if [[ "$#" -ne 0 ]]; then
  echo "Usage: $0 [--stale-only]" >&2
  exit 2
fi

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "::error::Security research refresh requires $1"
    exit 1
  fi
}

require_command curl
require_command python3

if [[ -z "${SKILLSTORE_API_URL:-}" ]]; then
  echo "::error::SKILLSTORE_API_URL is required for the security research refresh"
  exit 1
fi
if [[ -z "${SECURITY_RESEARCH_AUTOMATION_KEY:-}" ]]; then
  echo "::error::SECURITY_RESEARCH_AUTOMATION_KEY is required for the security research refresh"
  exit 1
fi
if [[ "$SECURITY_RESEARCH_AUTOMATION_KEY" == *$'\n'* || "$SECURITY_RESEARCH_AUTOMATION_KEY" == *$'\r'* ]]; then
  echo "::error::SECURITY_RESEARCH_AUTOMATION_KEY must be a single-line value"
  exit 1
fi

site_url="${SKILLSTORE_API_URL%/}"
public_url="$site_url/api/security/research-stats"
refresh_url="$site_url/api/automation/security/research-stats/refresh"
response_file="$(mktemp)"
trap 'rm -f "$response_file"' EXIT

append_summary() {
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    printf '%s\n' "$1" >> "$GITHUB_STEP_SUMMARY"
  fi
}

json_field() {
  local file="$1"
  local path="$2"
  python3 - "$file" "$path" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    value = json.load(handle)
for part in sys.argv[2].split("."):
    if not isinstance(value, dict) or part not in value:
        raise SystemExit(f"missing JSON field: {sys.argv[2]}")
    value = value[part]
if not isinstance(value, (str, int, float)) or isinstance(value, bool):
    raise SystemExit(f"invalid JSON field: {sys.argv[2]}")
print(value)
PY
}

safe_error_message() {
  python3 - "$1" <<'PY'
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        payload = json.load(handle)
    message = payload.get("error") if isinstance(payload, dict) else None
except Exception:
    message = None
message = "request failed" if not isinstance(message, str) else message
print(" ".join(message.split())[:300])
PY
}

if [[ "$stale_only" == "true" ]]; then
  set +e
  probe_status="$(
    curl --disable --silent --show-error \
      --retry 0 \
      --connect-timeout 10 \
      --max-time 30 \
      --output "$response_file" \
      --write-out '%{http_code}' \
      "$public_url"
  )"
  probe_rc=$?
  set -e

  if [[ "$probe_rc" -ne 0 || "$probe_status" != "200" ]]; then
    echo "::error::Security research stale probe failed (curl=$probe_rc, http=${probe_status:-000})"
    append_summary "- ❌ Stale probe failed; no refresh was attempted."
    exit 1
  fi

  if ! snapshot_state="$(json_field "$response_file" snapshot_state 2>/dev/null)"; then
    echo "::error::Security research stale probe returned an invalid response"
    append_summary "- ❌ Stale probe returned an invalid response; no refresh was attempted."
    exit 1
  fi

  case "$snapshot_state" in
    current)
      echo "::notice::Security research snapshot is current; stale-only refresh skipped"
      append_summary "- ✅ Snapshot is current; stale-only refresh skipped."
      exit 0
      ;;
    stale)
      echo "::notice::Security research snapshot is stale; starting bounded refresh"
      ;;
    *)
      echo "::error::Security research stale probe returned unexpected state: $snapshot_state"
      append_summary "- ❌ Unexpected snapshot state; no refresh was attempted."
      exit 1
      ;;
  esac
fi

for attempt in 1 2 3; do
  : > "$response_file"
  set +e
  refresh_status="$(
    printf 'Authorization: Bearer %s\n' "$SECURITY_RESEARCH_AUTOMATION_KEY" \
      | curl --disable --silent --show-error \
        --retry 0 \
        --header @- \
        --header 'Accept: application/json' \
        --connect-timeout 10 \
        --max-time 120 \
        --request POST \
        --output "$response_file" \
        --write-out '%{http_code}' \
        "$refresh_url"
  )"
  refresh_rc=$?
  set -e

  if [[ "$refresh_rc" -eq 0 && "$refresh_status" == "200" ]]; then
    if ! snapshot_state="$(json_field "$response_file" data.snapshot_state 2>/dev/null)" \
      || [[ "$snapshot_state" != "current" ]]; then
      echo "::error::Security research refresh returned HTTP 200 without a current snapshot"
      append_summary "- ❌ Refresh returned an invalid success response."
      exit 1
    fi

    captured_at="$(json_field "$response_file" data.captured_at 2>/dev/null || echo unknown)"
    source_version="$(json_field "$response_file" data.source.version 2>/dev/null || echo unknown)"
    echo "::notice::Security research snapshot refreshed (captured_at=$captured_at, source_version=$source_version)"
    append_summary "- ✅ Snapshot refreshed: captured_at=\`$captured_at\`, source_version=\`$source_version\`."
    exit 0
  fi

  message="$(safe_error_message "$response_file")"
  echo "::warning::Security research refresh failed (attempt=$attempt/3, curl=$refresh_rc, http=${refresh_status:-000}, error=$message)"

  if [[ "$attempt" -lt 3 ]] && {
    [[ "$refresh_rc" -ne 0 ]] || [[ "$refresh_status" =~ ^(429|500|502|503|504)$ ]];
  }; then
    sleep $((attempt * 5))
    continue
  fi
  break
done

echo "::error::Security research snapshot refresh did not complete; the source write remains committed and the safety-net workflow can retry"
append_summary "- ⚠️ Source write succeeded, but the research snapshot refresh failed after bounded retries."
exit 1
