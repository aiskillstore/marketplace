#!/bin/bash
# SiteGround Cache Buster - Installer Script
# Adds cache-busting code to a WordPress child theme's functions.php
#
# Usage: ./add-cache-buster.sh /path/to/child-theme
#
# This script:
# 1. Checks if the theme exists and has functions.php
# 2. Checks if cache buster is already installed
# 3. Appends the cache buster code to functions.php
# 4. Creates a backup before modifying

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE_BUSTER_PHP="$SCRIPT_DIR/cache-buster.php"

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide the path to your child theme${NC}"
    echo ""
    echo "Usage: $0 /path/to/child-theme"
    echo ""
    echo "Examples:"
    echo "  $0 ./wp-content/themes/my-child-theme"
    echo "  $0 /var/www/html/wp-content/themes/theme-child"
    exit 1
fi

THEME_PATH="$1"
FUNCTIONS_FILE="$THEME_PATH/functions.php"

# Validate theme path
if [ ! -d "$THEME_PATH" ]; then
    echo -e "${RED}Error: Theme directory not found: $THEME_PATH${NC}"
    exit 1
fi

if [ ! -f "$FUNCTIONS_FILE" ]; then
    echo -e "${RED}Error: functions.php not found in theme directory${NC}"
    echo "Make sure this is a valid WordPress theme directory."
    exit 1
fi

# Check if already installed
if grep -q "sg_dev_mode_banner\|sg_disable_cache_for_dev\|sg_bust_asset_cache" "$FUNCTIONS_FILE"; then
    echo -e "${YELLOW}Warning: Cache buster appears to already be installed in this theme.${NC}"
    echo "Found existing function definitions."
    read -p "Do you want to reinstall? This may cause duplicate code. (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Check if cache-buster.php exists
if [ ! -f "$CACHE_BUSTER_PHP" ]; then
    echo -e "${RED}Error: cache-buster.php not found at: $CACHE_BUSTER_PHP${NC}"
    exit 1
fi

echo -e "${CYAN}"
echo "==========================================="
echo "  SiteGround Cache Buster - Installer"
echo "==========================================="
echo -e "${NC}"

echo -e "Theme: ${GREEN}$THEME_PATH${NC}"
echo ""

# Create backup
BACKUP_FILE="$FUNCTIONS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
cp "$FUNCTIONS_FILE" "$BACKUP_FILE"
echo -e "${GREEN}Backup created: $BACKUP_FILE${NC}"

# Get the code to append (skip the first <?php line and ABSPATH check from cache-buster.php)
# We need to add just the functions, not the opening PHP tag
CACHE_CODE=$(tail -n +12 "$CACHE_BUSTER_PHP")

# Append to functions.php
echo "" >> "$FUNCTIONS_FILE"
echo "// ============================================================================" >> "$FUNCTIONS_FILE"
echo "// SITEGROUND CACHE BUSTER - Added $(date '+%Y-%m-%d %H:%M:%S')" >> "$FUNCTIONS_FILE"
echo "// Remove this section when done with development" >> "$FUNCTIONS_FILE"
echo "// ============================================================================" >> "$FUNCTIONS_FILE"
echo "$CACHE_CODE" >> "$FUNCTIONS_FILE"

echo ""
echo -e "${GREEN}Cache buster installed successfully!${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "1. Upload the modified functions.php to your server"
echo "2. Visit your site while logged in as admin"
echo "3. You should see a teal banner in the bottom-right corner"
echo "4. CSS/JS changes will now show immediately (for admins)"
echo ""
echo -e "${YELLOW}Remember to remove the cache buster code before going to production!${NC}"
echo "Use: ./remove-cache-buster.sh $THEME_PATH"
