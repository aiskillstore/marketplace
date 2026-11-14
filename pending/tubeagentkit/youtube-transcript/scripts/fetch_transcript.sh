#!/bin/bash
# Fetches a YouTube video's transcript via the getyoutubetranscript.com API.
#
# Usage:
#   YOUTUBE_TRANSCRIPT_API_KEY=sk_live_... ./fetch_transcript.sh <video_id_or_url> [language] [timestamps]
#
# Pass `timestamps` as the third argument to also get data.segments
# ({start, duration, text} per caption line, seconds).
#
# Prints the raw JSON response to stdout. A non-2xx response is still valid
# JSON with a "code" field to branch on - see SKILL.md's Errors table.
set -euo pipefail

VIDEO="${1:?Usage: fetch_transcript.sh <video_id_or_url> [language] [timestamps]}"
LANGUAGE="${2:-en}"
TIMESTAMPS="false"
if [ "${3:-}" = "timestamps" ]; then TIMESTAMPS="true"; fi

source "$(dirname "$0")/lib/key.sh"

curl -s -G "${API_BASE}/transcript" \
    --data-urlencode "v=${VIDEO}" \
    --data-urlencode "language=${LANGUAGE}" \
    --data-urlencode "timestamps=${TIMESTAMPS}" \
    -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
