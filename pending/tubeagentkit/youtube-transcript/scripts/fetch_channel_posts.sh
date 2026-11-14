#!/bin/bash
# Fetches a channel's community posts (the Posts tab), paginated, via the getyoutubetranscript.com API - 1 credit/page.
#
# Usage (first page):
#   YOUTUBE_TRANSCRIPT_API_KEY=sk_live_... ./fetch_channel_posts.sh <@handle_or_url_or_id>
# Usage (later pages - pass the previous response's data.continuation_token
# verbatim, it's opaque, don't construct it yourself):
#   YOUTUBE_TRANSCRIPT_API_KEY=sk_live_... ./fetch_channel_posts.sh "" <continuation_token>
set -euo pipefail

CHANNEL="${1:-}"
CONTINUATION="${2:-}"

if [ -z "$CHANNEL" ] && [ -z "$CONTINUATION" ]; then
    echo "Usage: fetch_channel_posts.sh <@handle_or_url_or_id> | fetch_channel_posts.sh '' <continuation_token>" >&2
    exit 1
fi

source "$(dirname "$0")/lib/key.sh"
source "$(dirname "$0")/lib/channel_page.sh"

fetch_channel_page posts "$CHANNEL" "$CONTINUATION"
