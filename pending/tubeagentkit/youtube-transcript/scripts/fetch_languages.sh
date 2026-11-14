#!/bin/bash
# Lists the caption languages a video offers (GET /transcript/languages). 1 credit per successful call.
#
# Usage:
#   ./fetch_languages.sh <video_id_or_url>
#
# Prints JSON: data.languages (language_code, name, caption_type) and
# data.default_language_code (what fetch_transcript.sh gets with no language).
set -euo pipefail

VIDEO="${1:?Usage: fetch_languages.sh <video_id_or_url>}"

source "$(dirname "$0")/lib/key.sh"

curl -s -G "${API_BASE}/transcript/languages" \
    --data-urlencode "v=${VIDEO}" \
    -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
