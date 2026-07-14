#!/usr/bin/env bash
set -uo pipefail

if [[ "${1:-}" != "--" ]]; then
  echo "usage: $0 -- <monitor command...>" >&2
  exit 64
fi
shift
if [[ "$#" -eq 0 ]]; then
  echo "monitor command is required" >&2
  exit 64
fi

OUTPUT_FILE="${MONITOR_OUTPUT_FILE:?MONITOR_OUTPUT_FILE is required}"
MAX_ATTEMPTS="${MONITOR_MAX_ATTEMPTS:-2}"
RETRY_DELAY_SECONDS="${MONITOR_RETRY_DELAY_SECONDS:-15}"

if ! [[ "$MAX_ATTEMPTS" =~ ^[1-9][0-9]*$ ]]; then
  echo "MONITOR_MAX_ATTEMPTS must be a positive integer" >&2
  exit 64
fi
if ! [[ "$RETRY_DELAY_SECONDS" =~ ^[0-9]+$ ]]; then
  echo "MONITOR_RETRY_DELAY_SECONDS must be a non-negative integer" >&2
  exit 64
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"
: > "$OUTPUT_FILE"
attempt_log=""
cleanup() {
  [[ -z "$attempt_log" ]] || rm -f "$attempt_log"
}
trap cleanup EXIT

for ((attempt = 1; attempt <= MAX_ATTEMPTS; attempt++)); do
  attempt_log=$(mktemp)
  echo "Source monitor attempt $attempt/$MAX_ATTEMPTS" | tee -a "$OUTPUT_FILE"

  "$@" 2>&1 | tee "$attempt_log" | tee -a "$OUTPUT_FILE"
  statuses=("${PIPESTATUS[@]}")
  command_status="${statuses[0]}"
  first_tee_status="${statuses[1]}"
  second_tee_status="${statuses[2]}"

  if [[ "$first_tee_status" -ne 0 || "$second_tee_status" -ne 0 ]]; then
    echo "Failed to persist source monitor output" >&2
    exit 74
  fi
  if [[ "$command_status" -eq 0 ]]; then
    exit 0
  fi

  if [[ "$attempt" -lt "$MAX_ATTEMPTS" ]] \
    && grep -Fqi 'unknown certificate verification error' "$attempt_log"; then
    echo "Transient certificate verification error detected; retrying once after ${RETRY_DELAY_SECONDS}s" \
      | tee -a "$OUTPUT_FILE"
    rm -f "$attempt_log"
    attempt_log=""
    sleep "$RETRY_DELAY_SECONDS"
    continue
  fi

  exit "$command_status"
done
