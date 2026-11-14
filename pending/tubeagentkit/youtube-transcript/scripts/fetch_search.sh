#!/bin/bash
# Searches YouTube via the getyoutubetranscript.com API.
#
# Usage (first page):
#   YOUTUBE_TRANSCRIPT_API_KEY=sk_live_... ./fetch_search.sh <query> [video|channel]
# Usage (later pages - pass the previous response's data.continuation_token
# verbatim, it's opaque, don't construct it yourself):
#   YOUTUBE_TRANSCRIPT_API_KEY=sk_live_... ./fetch_search.sh "" "" <page_token>
#
# Prints the raw JSON response to stdout. A non-2xx response is still valid
# JSON with a "code" field to branch on - see SKILL.md's Errors table.
set -euo pipefail

QUERY="${1:-}"
TYPE="${2:-video}"
PAGE_CURSOR="${3:-}"

if [ -z "$QUERY" ] && [ -z "$PAGE_CURSOR" ]; then
    echo "Usage: fetch_search.sh <query> [video|channel] | fetch_search.sh '' '' <page_token>" >&2
    exit 1
fi

source "$(dirname "$0")/lib/key.sh"

if [ -n "$PAGE_CURSOR" ]; then
    curl -s -G "${API_BASE}/search" \
        --data-urlencode "page_token=${PAGE_CURSOR}" \
        -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
else
    curl -s -G "${API_BASE}/search" \
        --data-urlencode "q=${QUERY}" \
        --data-urlencode "type=${TYPE}" \
        -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
fi
