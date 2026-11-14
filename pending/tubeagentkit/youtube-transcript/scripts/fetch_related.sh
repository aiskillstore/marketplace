#!/bin/bash
# Lists the videos YouTube suggests next to a video (GET /video/related). 1 credit per successful call.
#
# Usage:
#   ./fetch_related.sh <video_id_or_url>
#
# Prints JSON: data.related, each with id, title, link, channel, views, published_time, length.
set -euo pipefail

VIDEO="${1:?Usage: fetch_related.sh <video_id_or_url>}"

source "$(dirname "$0")/lib/key.sh"

curl -s -G "${API_BASE}/video/related" \
    --data-urlencode "v=${VIDEO}" \
    -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
