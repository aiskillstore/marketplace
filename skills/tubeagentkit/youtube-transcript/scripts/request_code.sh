#!/bin/bash
# Step 1 of API key setup: asks getyoutubetranscript.com to email a 6-digit
# sign-in code to the address the user gave you. Works for new and existing
# accounts. No API key needed. Prints the JSON response (it contains no secret).
#
# Usage:
#   ./request_code.sh <email>
set -euo pipefail

EMAIL="${1:?Usage: request_code.sh <email>}"
API_BASE="https://getyoutubetranscript.com/api/v1"

curl -s -X POST "${API_BASE}/signup" \
    -H "Content-Type: application/json" \
    -H "User-Agent: youtube-transcript-skill/1.2" \
    --data "$(printf '{"email": "%s"}' "$EMAIL")"
echo
