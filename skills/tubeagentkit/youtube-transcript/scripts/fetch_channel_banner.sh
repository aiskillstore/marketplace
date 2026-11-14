#!/bin/bash
# Gets a channel's banner and avatar (GET /channel/banner). 1 credit per successful call.
#
# Usage:
#   ./fetch_channel_banner.sh <@handle_or_url_or_id>
#
# Prints JSON: data.has_banner, data.banner (original, largest, sizes) and data.avatar.
set -euo pipefail

CHANNEL="${1:?Usage: fetch_channel_banner.sh <@handle_or_url_or_id>}"

source "$(dirname "$0")/lib/key.sh"

curl -s -G "${API_BASE}/channel/banner" \
    --data-urlencode "channel=${CHANNEL}" \
    -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
