#!/bin/bash
# Resolves a channel handle/URL/id to its channel ID via the
# getyoutubetranscript.com API. 1 credit per successful call.
#
# Usage:
#   YOUTUBE_TRANSCRIPT_API_KEY=sk_live_... ./resolve_channel.sh <@handle_or_url_or_id>
set -euo pipefail

HANDLE="${1:?Usage: resolve_channel.sh <@handle_or_url_or_id>}"

source "$(dirname "$0")/lib/key.sh"

curl -s -G "${API_BASE}/resolve" \
    --data-urlencode "handle=${HANDLE}" \
    -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
