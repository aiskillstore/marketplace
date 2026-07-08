#!/usr/bin/env bash
#
# fetch-gasp.sh - Convenience script for fetching GASP metrics
#
# Usage:
#   fetch-gasp.sh <hostname> [port]
#
# Examples:
#   fetch-gasp.sh hyperion
#   fetch-gasp.sh accelerated.local
#   fetch-gasp.sh proxmox1 8080
#   fetch-gasp.sh 192.168.1.100
#
# Note: This script is optional. Claude can fetch GASP metrics directly using
# web_fetch, so this is just a convenience for manual testing or automation.

set -euo pipefail

# Default port
PORT="${2:-8080}"
HOSTNAME="${1:-}"

if [[ -z "$HOSTNAME" ]]; then
    echo "Usage: $0 <hostname> [port]"
    echo ""
    echo "Examples:"
    echo "  $0 hyperion"
    echo "  $0 accelerated.local"
    echo "  $0 proxmox1 8080"
    exit 1
fi

# Construct URL
URL="http://${HOSTNAME}:${PORT}/metrics"

echo "Fetching GASP metrics from ${URL}..." >&2
echo "" >&2

# Fetch metrics
if command -v curl >/dev/null 2>&1; then
    curl -sf "$URL"
elif command -v wget >/dev/null 2>&1; then
    wget -qO- "$URL"
else
    echo "Error: Neither curl nor wget found" >&2
    exit 1
fi

EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    echo "" >&2
    echo "Error: Failed to fetch GASP metrics from ${HOSTNAME}" >&2
    echo "Possible causes:" >&2
    echo "  - GASP is not running (try: ssh ${HOSTNAME} 'systemctl status gasp')" >&2
    echo "  - Wrong port (default is 8080)" >&2
    echo "  - Host is unreachable" >&2
    echo "  - Firewall blocking port ${PORT}" >&2
    exit $EXIT_CODE
fi
