#!/bin/bash
# Gets a video's estimated likes and dislikes (GET /video/dislikes). 1 credit per successful call.
#
# Usage:
#   ./fetch_dislikes.sh <video_id_or_url>
#
# Prints JSON: data.likes, data.dislikes, data.rating, data.view_count. The numbers are
# estimates (YouTube no longer publishes dislikes); data.estimated is always true.
set -euo pipefail

VIDEO="${1:?Usage: fetch_dislikes.sh <video_id_or_url>}"

source "$(dirname "$0")/lib/key.sh"

curl -s -G "${API_BASE}/video/dislikes" \
    --data-urlencode "v=${VIDEO}" \
    -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
