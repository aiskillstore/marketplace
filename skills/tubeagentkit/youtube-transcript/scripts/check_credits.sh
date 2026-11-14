#!/bin/bash
# Checks the remaining credit balance for this API key via
# getyoutubetranscript.com. Free - 0 credits, never charged.
#
# Usage:
#   YOUTUBE_TRANSCRIPT_API_KEY=sk_live_... ./check_credits.sh
set -euo pipefail

source "$(dirname "$0")/lib/key.sh"

curl -s "${API_BASE}/credits" \
    -H "Authorization: Bearer ${YOUTUBE_TRANSCRIPT_API_KEY}"
