#!/bin/bash
# SiteGround Cache Buster - Removal Script
# Removes cache-busting code from a WordPress child theme's functions.php
#
# Usage: ./remove-cache-buster.sh /path/to/child-theme
#
# This script removes all cache buster functions that were added by add-cache-buster.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide the path to your child theme${NC}"
    echo ""
    echo "Usage: $0 /path/to/child-theme"
    exit 1
fi

THEME_PATH="$1"
FUNCTIONS_FILE="$THEME_PATH/functions.php"

# Validate
if [ ! -f "$FUNCTIONS_FILE" ]; then
    echo -e "${RED}Error: functions.php not found: $FUNCTIONS_FILE${NC}"
    exit 1
fi

# Check if cache buster is installed
if ! grep -q "sg_dev_mode_banner\|sg_disable_cache_for_dev\|sg_bust_asset_cache\|SITEGROUND CACHE BUSTER" "$FUNCTIONS_FILE"; then
    echo -e "${YELLOW}Cache buster code not found in functions.php${NC}"
    echo "Nothing to remove."
    exit 0
fi

echo -e "${CYAN}"
echo "==========================================="
echo "  SiteGround Cache Buster - Removal"
echo "==========================================="
echo -e "${NC}"

echo -e "Theme: ${GREEN}$THEME_PATH${NC}"
echo ""

# Create backup
BACKUP_FILE="$FUNCTIONS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
cp "$FUNCTIONS_FILE" "$BACKUP_FILE"
echo -e "${GREEN}Backup created: $BACKUP_FILE${NC}"

# Create a temporary file for the cleaned content
TEMP_FILE=$(mktemp)

# Use awk to remove the cache buster section
# This removes from the SITEGROUND CACHE BUSTER comment block to the end of the related functions
awk '
    /^\/\/ =+$/ && /SITEGROUND CACHE BUSTER/ { skip=1; next }
    /SITEGROUND CACHE BUSTER/ { skip=1; next }
    /^\/\/ DEVELOPMENT MODE BANNER/ { skip=1; next }
    /^\/\/ DISABLE ALL CACHING/ { skip=1; next }
    /^\/\/ BUST BROWSER CACHE/ { skip=1; next }
    /^add_action.*sg_dev_mode_banner/ { skip=1; next }
    /^function sg_dev_mode_banner/ { skip=1; infunc=1; next }
    /^add_action.*sg_disable_cache_for_dev/ { skip=1; next }
    /^function sg_disable_cache_for_dev/ { skip=1; infunc=1; next }
    /^add_filter.*sg_bust_asset_cache/ { skip=1; next }
    /^function sg_bust_asset_cache/ { skip=1; infunc=1; next }
    infunc && /^}$/ { infunc=0; skip=0; next }
    infunc { next }
    /^\/\/ =+$/ && skip { next }
    /^\/\/ Remove this section/ { next }
    skip && /^$/ { skip=0 }
    !skip { print }
' "$FUNCTIONS_FILE" > "$TEMP_FILE"

# Remove consecutive blank lines (clean up)
cat -s "$TEMP_FILE" > "$FUNCTIONS_FILE"
rm "$TEMP_FILE"

# Remove trailing whitespace at end of file
sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$FUNCTIONS_FILE" 2>/dev/null || true

echo ""
echo -e "${GREEN}Cache buster removed successfully!${NC}"
echo ""
echo -e "${CYAN}The following were removed:${NC}"
echo "  - sg_dev_mode_banner() function and action"
echo "  - sg_disable_cache_for_dev() function and action"
echo "  - sg_bust_asset_cache() function and filters"
echo "  - All related comment blocks"
echo ""
echo "Your theme is now ready for production."
echo ""
echo -e "${YELLOW}Backup saved at: $BACKUP_FILE${NC}"
