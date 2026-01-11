#!/bin/bash
#
# Apply White Label Configuration
#
# Usage:
#   ./apply-white-label.sh [config.json] [container]
#
# Examples:
#   ./apply-white-label.sh                                    # Use defaults
#   ./apply-white-label.sh mysite-config.json                 # Custom config
#   ./apply-white-label.sh mysite-config.json wordpress-1     # Docker container
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${1:-}"
CONTAINER="${2:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  White Label Configuration Script${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Determine execution method
if [ -n "$CONTAINER" ]; then
    echo -e "Container: ${YELLOW}$CONTAINER${NC}"

    # Copy script to container
    docker cp "$SCRIPT_DIR/configure-white-label.php" "$CONTAINER:/tmp/"

    if [ -n "$CONFIG_FILE" ] && [ -f "$CONFIG_FILE" ]; then
        docker cp "$CONFIG_FILE" "$CONTAINER:/tmp/white-label-config.json"
        echo -e "Config: ${YELLOW}$CONFIG_FILE${NC}"
    else
        echo -e "Config: ${YELLOW}(using defaults)${NC}"
    fi

    echo ""
    docker exec "$CONTAINER" wp eval-file /tmp/configure-white-label.php --allow-root

    # Cleanup
    docker exec "$CONTAINER" rm -f /tmp/configure-white-label.php /tmp/white-label-config.json 2>/dev/null || true

elif command -v wp &> /dev/null; then
    echo "Running locally with WP-CLI"

    if [ -n "$CONFIG_FILE" ] && [ -f "$CONFIG_FILE" ]; then
        CONFIG_ARG="--config=$CONFIG_FILE"
        echo -e "Config: ${YELLOW}$CONFIG_FILE${NC}"
    else
        CONFIG_ARG=""
        echo -e "Config: ${YELLOW}(using defaults)${NC}"
    fi

    echo ""
    wp eval-file "$SCRIPT_DIR/configure-white-label.php" "$CONFIG_ARG"

else
    echo -e "${RED}Error: No WP-CLI found and no container specified${NC}"
    echo ""
    echo "Usage:"
    echo "  $0 [config.json] [container]"
    echo ""
    echo "Examples:"
    echo "  $0 config.json wordpress-local-wordpress-1"
    exit 1
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Configuration Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "  1. Visit /wp-admin/ to verify the changes"
echo "  2. Test the custom login URL"
echo "  3. Check the login page branding"
echo ""
