#!/bin/bash
# Status and one page of results for a batch from submit_batch.sh (GET /batch). Free.
#
# Usage:
#   ./fetch_batch.sh <batch_id> [offset] [limit]
#
# Poll until data.status is "completed", then page with data.next_offset
# (null on the last page). limit is 1-50, default 20.
set -euo pipefail

BATCH_ID="${1:?Usage: fetch_batch.sh <batch_id> [offset] [limit]}"
OFFSET="${2:-0}"
LIMIT="${3:-20}"

source "$(dirname "$0")/lib/key.sh"

curl -s -G "${API_BASE}/batch" \
    --data-urlencode "id=${BATCH_ID}" \
    --data-urlencode "offset=${OFFSET}" \
    --data-urlencode "limit=${LIMIT}" \
    -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
