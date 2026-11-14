#!/bin/bash
# Queues transcripts for up to 100 videos in one call (POST /batch).
#
# Usage:
#   ./submit_batch.sh [--language <code>] [--timestamps] <video_id_or_url> [more videos...]
#
# Prints the JSON response; data.batch_id is what fetch_batch.sh needs.
# Submitting is free; 1 credit is charged per video that returns a transcript.
set -euo pipefail

LANGUAGE="en"
TIMESTAMPS="false"
VIDEOS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --language) LANGUAGE="${2:?--language needs a value}"; shift 2 ;;
        --timestamps) TIMESTAMPS="true"; shift ;;
        *) VIDEOS+=("$1"); shift ;;
    esac
done
if [ ${#VIDEOS[@]} -eq 0 ]; then
    echo "Usage: submit_batch.sh [--language <code>] [--timestamps] <video_id_or_url> [more videos...]" >&2
    exit 1
fi

json_string() {
    local value="${1//\\/\\\\}"
    printf '"%s"' "${value//\"/\\\"}"
}

VIDEO_LIST=""
for video in "${VIDEOS[@]}"; do
    VIDEO_LIST+="${VIDEO_LIST:+,}$(json_string "$video")"
done

source "$(dirname "$0")/lib/key.sh"

curl -s -X POST "${API_BASE}/batch" \
    -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"videos\":[${VIDEO_LIST}],\"language\":$(json_string "$LANGUAGE"),\"timestamps\":${TIMESTAMPS}}"
