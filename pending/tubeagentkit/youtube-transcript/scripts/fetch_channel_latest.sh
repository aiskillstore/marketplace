#!/bin/bash
# Fetches the channel's details plus its 15 newest uploads
# via the getyoutubetranscript.com API. 1 credit per successful call. For the complete,
# paginated upload history use fetch_channel_videos.sh instead.
#
# Usage:
#   YOUTUBE_TRANSCRIPT_API_KEY=sk_live_... ./fetch_channel_latest.sh <@handle_or_url_or_id>
set -euo pipefail

CHANNEL="${1:?Usage: fetch_channel_latest.sh <@handle_or_url_or_id>}"

source "$(dirname "$0")/lib/key.sh"

curl -s -G "${API_BASE}/channel/latest" \
    --data-urlencode "channel=${CHANNEL}" \
    -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
