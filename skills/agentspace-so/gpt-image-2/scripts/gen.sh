#!/usr/bin/env bash
# Generate an image via Codex CLI's imagegen tool, reusing the user's
# ChatGPT subscription session. Supports text-to-image and image-to-image.
#
# Implementation note: on codex-cli 0.111.0 the `imagegen` tool does NOT
# write a PNG file to disk. The generated image is embedded as base64 inside
# the session rollout jsonl under ~/.codex/sessions/YYYY/MM/DD/. This script
# captures the new session file created by the run and decodes the image
# out of it. Flags: `--enable image_generation` turns the under-development
# tool on; `--ephemeral` is intentionally NOT passed so the session is
# persisted and we can read it back.
#
# Usage:
#   gen.sh --prompt "<text>" --out <path.png> [--ref <image>]... [--timeout-sec N]
#
# Exit codes:
#   0 success (path printed on stdout)
#   2 bad args
#   3 required CLI missing (codex / python3)
#   4 reference image not found
#   5 codex exec failed
#   6 no new session file detected
#   7 image payload not found in session file (imagegen likely did not run)

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

PROMPT=""
OUT=""
REF_IMAGES=()
TIMEOUT_SEC=300

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt)      PROMPT="$2"; shift 2 ;;
    --out)         OUT="$2"; shift 2 ;;
    --ref)         REF_IMAGES+=("$2"); shift 2 ;;
    --timeout-sec) TIMEOUT_SEC="$2"; shift 2 ;;
    -h|--help)     sed -n '2,24p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ -z "$PROMPT" ]] && { echo "Missing --prompt" >&2; exit 2; }
[[ -z "$OUT" ]]    && { echo "Missing --out" >&2; exit 2; }

command -v codex >/dev/null 2>&1 || {
  echo "codex CLI not found. Install Codex CLI and run 'codex login' first." >&2
  exit 3
}
command -v python3 >/dev/null 2>&1 || { echo "python3 not found" >&2; exit 3; }

SESSIONS_ROOT="$HOME/.codex/sessions"
mkdir -p "$SESSIONS_ROOT"

before="$(mktemp)"; after="$(mktemp)"
stdout_log="$(mktemp)"; stderr_log="$(mktemp)"
trap 'rm -f "$before" "$after" "$stdout_log" "$stderr_log"' EXIT

find "$SESSIONS_ROOT" -type f -name 'rollout-*.jsonl' -print 2>/dev/null | sort > "$before" || true

# Intentionally NOT using --ephemeral: we need the session rollout on disk.
args=(exec --skip-git-repo-check --sandbox read-only --color never --enable image_generation)
if [[ ${#REF_IMAGES[@]} -gt 0 ]]; then
  for img in "${REF_IMAGES[@]}"; do
    [[ -f "$img" ]] || { echo "Reference image not found: $img" >&2; exit 4; }
    args+=(-i "$img")
  done
fi

instruction="Use the imagegen tool to generate the image for the following request."
if [[ ${#REF_IMAGES[@]} -gt 0 ]]; then
  instruction+=" Use the attached image(s) as visual reference / input for image-to-image."
fi
instruction+=$'\nRequirements: generate the image directly, return only the image, no explanation.\n\nRequest:\n'"$PROMPT"

# `-i` is a variadic flag (<FILE>...), so passing the prompt as the trailing
# positional would be consumed as another image file. Feed the prompt via
# stdin instead (codex exec reads from stdin when no prompt positional is
# given).

TO=""
if   command -v timeout  >/dev/null 2>&1; then TO="timeout"
elif command -v gtimeout >/dev/null 2>&1; then TO="gtimeout"
fi

set +e
if [[ -n "$TO" ]]; then
  printf '%s' "$instruction" | "$TO" "$TIMEOUT_SEC" codex "${args[@]}" >"$stdout_log" 2>"$stderr_log"
else
  printf '%s' "$instruction" | codex "${args[@]}" >"$stdout_log" 2>"$stderr_log"
fi
rc=$?
set -e

if [[ $rc -ne 0 ]]; then
  echo "codex exec failed (exit=$rc). stderr tail:" >&2
  tail -n 40 "$stderr_log" >&2 || true
  exit 5
fi

find "$SESSIONS_ROOT" -type f -name 'rollout-*.jsonl' -print 2>/dev/null | sort > "$after" || true

# Collect ALL new session files. A single `codex exec` call can spawn more
# than one session rollout (e.g. when the imagegen tool runs in a sub-turn),
# so we must scan every new one rather than blindly picking the last.
new_sessions_file="$(mktemp)"
trap 'rm -f "$before" "$after" "$stdout_log" "$stderr_log" "$new_sessions_file"' EXIT
comm -13 "$before" "$after" > "$new_sessions_file" || true

if [[ ! -s "$new_sessions_file" ]]; then
  echo "No new session rollout file under $SESSIONS_ROOT" >&2
  tail -n 40 "$stderr_log" >&2 || true
  exit 6
fi

# Extract the image from the new session rollout(s). Extraction logic lives
# in a separate Python module; see scripts/extract_image.py for details.
set +e
python3 "$SCRIPT_DIR/extract_image.py" "$OUT" "$new_sessions_file"
py_rc=$?
set -e

if [[ $py_rc -ne 0 ]]; then
  echo "Image payload not found in any new session file" >&2
  echo "(imagegen likely did not run; stderr tail:)" >&2
  tail -n 30 "$stderr_log" >&2 || true
  exit 7
fi
