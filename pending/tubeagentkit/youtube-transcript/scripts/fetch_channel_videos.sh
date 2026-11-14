#!/bin/bash
# Fetches a channel's full, paginated video list via the getyoutubetranscript.com API - 1 credit/page.
#
# Usage (first page):
#   YOUTUBE_TRANSCRIPT_API_KEY=sk_live_... ./fetch_channel_videos.sh <@handle_or_url_or_id> [tab] [sort]
#     tab:  videos (default), shorts or streams (the Live tab)
#     sort: latest (default), popular or oldest
# Usage (later pages - pass the previous response's data.continuation_token
# verbatim, it's opaque, don't construct it yourself; tab and sort are already in it):
#   YOUTUBE_TRANSCRIPT_API_KEY=sk_live_... ./fetch_channel_videos.sh "" <continuation_token>
set -euo pipefail

CHANNEL="${1:-}"
CONTINUATION=""
TAB=""
SORT=""
if [ -z "$CHANNEL" ]; then
    CONTINUATION="${2:-}"
else
    TAB="${2:-}"
    SORT="${3:-}"
fi

if [ -z "$CHANNEL" ] && [ -z "$CONTINUATION" ]; then
    echo "Usage: fetch_channel_videos.sh <@handle_or_url_or_id> [tab] [sort] | fetch_channel_videos.sh '' <continuation_token>" >&2
    exit 1
fi

source "$(dirname "$0")/lib/key.sh"
source "$(dirname "$0")/lib/channel_page.sh"

EXTRA=()
if [ -n "$TAB" ]; then EXTRA+=("tab=${TAB}"); fi
if [ -n "$SORT" ]; then EXTRA+=("sort=${SORT}"); fi

fetch_channel_page videos "$CHANNEL" "$CONTINUATION" ${EXTRA[@]+"${EXTRA[@]}"}
